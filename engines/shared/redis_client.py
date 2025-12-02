"""
Redis Client for Rwanda NCSA Compliance Auditor Engines
Provides unified Redis connectivity for all engines

Supports:
- Host machine Redis (localhost:6379)
- Docker network Redis (redis:6379)
- Kubernetes Redis (redis-service:6379)
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class RedisClient:
    """
    Redis client wrapper that supports pub/sub and state management
    Works with host, docker, or k8s Redis deployments
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: int = 0,
        password: Optional[str] = None,
        engine_name: str = "unknown"
    ):
        # Auto-detect Redis connection from environment
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db or int(os.getenv("REDIS_DB", "0"))
        self.password = password or os.getenv("REDIS_PASSWORD", None)
        self.engine_name = engine_name

        self._redis = None
        self._pubsub = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Redis server"""
        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )

            # Test connection
            await self._redis.ping()
            self._connected = True
            print(f"[{self.engine_name}] Connected to Redis at {self.host}:{self.port}")
            return True

        except ImportError:
            print(f"[{self.engine_name}] Redis client not installed. Install with: pip install redis")
            return False
        except Exception as e:
            print(f"[{self.engine_name}] Redis connection failed: {str(e)}")
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
            self._connected = False
            print(f"[{self.engine_name}] Disconnected from Redis")

    def is_connected(self) -> bool:
        """Check if connected to Redis"""
        return self._connected

    # =========================================================================
    # Key-Value Operations
    # =========================================================================

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair"""
        if not self._connected:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            if ttl:
                await self._redis.setex(key, ttl, value)
            else:
                await self._redis.set(key, value)
            return True
        except Exception as e:
            print(f"[{self.engine_name}] Redis SET error: {str(e)}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        if not self._connected:
            return None
        try:
            value = await self._redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"[{self.engine_name}] Redis GET error: {str(e)}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete a key"""
        if not self._connected:
            return False
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            print(f"[{self.engine_name}] Redis DELETE error: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        if not self._connected:
            return False
        try:
            return await self._redis.exists(key) > 0
        except Exception:
            return False

    # =========================================================================
    # Pub/Sub Operations for Real-time Updates
    # =========================================================================

    async def publish(self, channel: str, message: Any) -> int:
        """Publish a message to a channel"""
        if not self._connected:
            return 0
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            return await self._redis.publish(channel, message)
        except Exception as e:
            print(f"[{self.engine_name}] Redis PUBLISH error: {str(e)}")
            return 0

    async def subscribe(self, channel: str):
        """Subscribe to a channel"""
        if not self._connected:
            return None
        try:
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe(channel)
            return self._pubsub
        except Exception as e:
            print(f"[{self.engine_name}] Redis SUBSCRIBE error: {str(e)}")
            return None

    async def get_message(self, timeout: float = 0.1) -> Optional[Dict]:
        """Get a message from subscribed channels"""
        if not self._pubsub:
            return None
        try:
            message = await self._pubsub.get_message(timeout=timeout)
            if message and message['type'] == 'message':
                data = message['data']
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return {'data': data}
            return None
        except Exception:
            return None

    # =========================================================================
    # Audit State Management
    # =========================================================================

    async def set_audit_state(
        self,
        audit_id: str,
        stage: str,
        progress: int,
        message: str,
        details: Optional[Dict] = None
    ) -> bool:
        """Set the current state of an audit"""
        state = {
            "audit_id": audit_id,
            "stage": stage,
            "progress": progress,
            "message": message,
            "details": details or {},
            "engine": self.engine_name,
            "timestamp": datetime.now().isoformat()
        }

        # Store state
        key = f"audit:{audit_id}:state"
        success = await self.set(key, state, ttl=3600)  # 1 hour TTL

        # Publish state update to subscribers
        if success:
            await self.publish(f"audit:{audit_id}:updates", state)

        return success

    async def get_audit_state(self, audit_id: str) -> Optional[Dict]:
        """Get the current state of an audit"""
        key = f"audit:{audit_id}:state"
        return await self.get(key)

    async def add_audit_log(self, audit_id: str, log_entry: Dict) -> bool:
        """Add a log entry to the audit history"""
        if not self._connected:
            return False
        try:
            key = f"audit:{audit_id}:logs"
            log_entry['timestamp'] = datetime.now().isoformat()
            await self._redis.rpush(key, json.dumps(log_entry))
            await self._redis.expire(key, 3600)  # 1 hour TTL
            return True
        except Exception as e:
            print(f"[{self.engine_name}] Redis log error: {str(e)}")
            return False

    async def get_audit_logs(self, audit_id: str, limit: int = 100) -> List[Dict]:
        """Get audit logs"""
        if not self._connected:
            return []
        try:
            key = f"audit:{audit_id}:logs"
            logs = await self._redis.lrange(key, -limit, -1)
            return [json.loads(log) for log in logs]
        except Exception:
            return []

    # =========================================================================
    # Engine Status Management
    # =========================================================================

    async def register_engine(self, engine_id: str, engine_info: Dict) -> bool:
        """Register an engine's status"""
        engine_info['last_heartbeat'] = datetime.now().isoformat()
        engine_info['status'] = 'online'
        return await self.set(f"engine:{engine_id}", engine_info, ttl=60)

    async def heartbeat(self, engine_id: str) -> bool:
        """Send a heartbeat for an engine"""
        if not self._connected:
            return False
        try:
            key = f"engine:{engine_id}"
            data = await self.get(key)
            if data:
                data['last_heartbeat'] = datetime.now().isoformat()
                return await self.set(key, data, ttl=60)
            return False
        except Exception:
            return False

    async def get_engine_status(self, engine_id: str) -> Optional[Dict]:
        """Get an engine's status"""
        return await self.get(f"engine:{engine_id}")

    async def get_all_engines(self) -> List[Dict]:
        """Get all registered engines"""
        if not self._connected:
            return []
        try:
            keys = await self._redis.keys("engine:*")
            engines = []
            for key in keys:
                data = await self.get(key)
                if data:
                    engines.append(data)
            return engines
        except Exception:
            return []


# Singleton instance
_redis_client: Optional[RedisClient] = None


def get_redis_client(engine_name: str = "unknown") -> RedisClient:
    """Get or create a Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient(engine_name=engine_name)
    return _redis_client


async def init_redis(
    engine_name: str = "unknown",
    host: Optional[str] = None,
    port: Optional[int] = None,
    db: int = 0
) -> RedisClient:
    """
    Initialize and connect Redis client

    Args:
        engine_name: Name of the engine (for logging)
        host: Redis host (defaults to REDIS_HOST env var or 'localhost')
        port: Redis port (defaults to REDIS_PORT env var or 6379)
        db: Redis database number

    Returns:
        Connected Redis client instance
    """
    # Get or create client with specified parameters
    if host or port:
        client = RedisClient(host=host, port=port, db=db, engine_name=engine_name)
    else:
        client = get_redis_client(engine_name)

    await client.connect()
    return client
