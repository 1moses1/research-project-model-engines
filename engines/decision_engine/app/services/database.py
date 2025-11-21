"""
Database Service
Manages PostgreSQL connections and data persistence
"""

from typing import Dict, List, Optional
from datetime import datetime
import asyncpg
import os


class DatabaseService:
    """Manages database operations"""

    def __init__(self):
        self.pool = None
        self.db_url = os.getenv(
            "POSTGRES_URL",
            "postgresql://compliance_user:compliance_pass@postgres:5432/compliance_db"
        )

    async def initialize(self):
        """Initialize database connection pool and create tables"""
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=2,
                max_size=10
            )

            # Create tables
            await self._create_tables()

            print("✅ Database initialized")

        except Exception as e:
            print(f"⚠️ Database initialization error: {str(e)}")
            print("⚠️ Using in-memory storage (no persistence)")
            self.pool = None

    async def _create_tables(self):
        """Create necessary database tables"""
        if not self.pool:
            return

        async with self.pool.acquire() as conn:
            # Classifications table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS classifications (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(255) UNIQUE,
                    log_message TEXT,
                    prediction VARCHAR(50),
                    confidence FLOAT,
                    route_decision VARCHAR(50),
                    timestamp TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')

            # Risk scores table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS risk_scores (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(255),
                    risk_score FLOAT,
                    risk_level VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (event_id) REFERENCES classifications(event_id)
                )
            ''')

            # Feedback table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(255),
                    predicted_label VARCHAR(50),
                    correct_label VARCHAR(50),
                    reviewer VARCHAR(255),
                    notes TEXT,
                    timestamp TIMESTAMP,
                    used_for_training BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')

            print("✅ Database tables created/verified")

    async def is_healthy(self) -> bool:
        """Check if database connection is healthy"""
        if not self.pool:
            return False

        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            return True
        except Exception:
            return False

    async def store_classification(
        self,
        event_id: str,
        log_message: str,
        prediction: str,
        confidence: float,
        route_decision: str,
        timestamp: str
    ):
        """Store classification result"""
        if not self.pool:
            return  # Skip if no database

        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO classifications (event_id, log_message, prediction, confidence, route_decision, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (event_id) DO UPDATE
                    SET prediction = $3, confidence = $4, route_decision = $5
                ''', event_id, log_message, prediction, confidence, route_decision, timestamp)
        except Exception as e:
            print(f"⚠️ Error storing classification: {str(e)}")

    async def store_risk_score(
        self,
        event_id: str,
        risk_score: float,
        risk_level: str
    ):
        """Store risk score"""
        if not self.pool:
            return

        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO risk_scores (event_id, risk_score, risk_level)
                    VALUES ($1, $2, $3)
                ''', event_id, risk_score, risk_level)
        except Exception as e:
            print(f"⚠️ Error storing risk score: {str(e)}")

    async def get_high_risk_events(self, limit: int = 10) -> List[Dict]:
        """Get top high-risk events"""
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT c.event_id, c.log_message, c.prediction, c.confidence,
                           r.risk_score, r.risk_level, c.timestamp
                    FROM classifications c
                    JOIN risk_scores r ON c.event_id = r.event_id
                    WHERE r.risk_level IN ('high', 'critical')
                    ORDER BY r.risk_score DESC
                    LIMIT $1
                ''', limit)

                return [dict(row) for row in rows]
        except Exception as e:
            print(f"⚠️ Error fetching high-risk events: {str(e)}")
            return []

    async def count_events(self) -> int:
        """Count total events processed"""
        if not self.pool:
            return 0

        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval('SELECT COUNT(*) FROM classifications')
                return count or 0
        except Exception:
            return 0

    async def get_confidence_stats(self) -> Dict:
        """Get confidence statistics"""
        if not self.pool:
            return {"total": 0, "high_confidence": 0}

        try:
            async with self.pool.acquire() as conn:
                total = await conn.fetchval('SELECT COUNT(*) FROM classifications')
                high_conf = await conn.fetchval('SELECT COUNT(*) FROM classifications WHERE confidence >= 0.90')

                return {
                    "total": total or 0,
                    "high_confidence": high_conf or 0
                }
        except Exception:
            return {"total": 0, "high_confidence": 0}

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
