"""
ENGINE 1: Log Collection Engine
Rwanda NCSA Compliance Auditor v3.0.0

Real-time log collection, parsing, and streaming with MCP protocol integration
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
import json
import uuid
import os

from .services.mcp_client import MCPClient
from .services.log_parser import LogParser
from .services.log_normalizer import LogNormalizer
from .services.event_enricher import EventEnricher
from .services.streaming_pipeline import StreamingPipeline
from .services.llm_log_analyzer import LLMLogAnalyzer
from .services.evidence_converter import EvidenceConverter, get_evidence_converter

# Import shared models for unified pipeline
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
try:
    from shared import (
        RedisClient, get_redis_client, init_redis,
        ComplianceEvidence, EvidenceSourceType, EvidenceBatch,
        EvidenceManager, create_evidence_manager
    )
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    print("⚠️ Shared module not available - running in standalone mode")

# Initialize FastAPI app
app = FastAPI(
    title="ENGINE 1: Log Collection Engine (LLM-Powered)",
    description="Real-time log collection and streaming with LLM semantic analysis for Rwanda NCSA compliance",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ENGINE3_URL = os.getenv("ENGINE3_URL", "http://xgboost-api:8000")
ENGINE4_URL = os.getenv("ENGINE4_URL", "http://decision-engine:8001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CONTROL_TAXONOMY_PATH = os.getenv("CONTROL_TAXONOMY_PATH")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Initialize LLM analyzer (optional - works without API key in regex-only mode)
llm_analyzer = LLMLogAnalyzer(
    api_key=OPENAI_API_KEY,
    control_taxonomy_path=CONTROL_TAXONOMY_PATH
)

# Initialize services with LLM support
mcp_client = MCPClient()
log_parser = LogParser(llm_analyzer=llm_analyzer)
log_normalizer = LogNormalizer()
event_enricher = EventEnricher()
streaming_pipeline = StreamingPipeline(
    engine3_url=ENGINE3_URL,
    engine4_url=ENGINE4_URL
)

# Initialize evidence converter and manager (for unified pipeline)
evidence_converter = get_evidence_converter()
evidence_manager = None  # Will be initialized in startup event

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"⚠️ WebSocket send error: {str(e)}")

manager = ConnectionManager()


# ============================================================================
# Pydantic Models
# ============================================================================

class LogEvent(BaseModel):
    """Raw log event"""
    timestamp: Optional[str] = Field(None, description="Event timestamp")
    source: str = Field(..., description="Log source (system, application, network)")
    raw_message: str = Field(..., description="Raw log message")
    severity: Optional[str] = Field(None, description="Log severity level")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class NormalizedEvent(BaseModel):
    """Normalized log event"""
    event_id: str
    timestamp: str
    source: str
    log_message: str
    user: Optional[str] = None
    ip_address: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    status_code: Optional[int] = None
    severity: str
    raw_message: str
    metadata: Dict[str, Any] = {}


class CollectionStats(BaseModel):
    """Collection statistics"""
    total_events_collected: int
    total_events_parsed: int
    total_events_classified: int
    events_per_second: float
    collection_sources: List[str]
    active_connections: int


class StreamConfig(BaseModel):
    """Stream configuration"""
    source: str = Field(..., description="Log source identifier")
    enabled: bool = Field(default=True, description="Enable/disable stream")
    auto_classify: bool = Field(default=True, description="Auto-classify events")
    batch_size: int = Field(default=10, description="Batch size for processing")
    interval_seconds: int = Field(default=5, description="Processing interval")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ENGINE 1: Log Collection Engine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Real-time log collection and streaming for Rwanda NCSA compliance",
        "endpoints": {
            "ingest_log": "POST /ingest/log",
            "ingest_batch": "POST /ingest/batch",
            "stream_logs": "WebSocket /stream/logs",
            "collection_sources": "GET /sources",
            "stats": "GET /stats",
            "health": "GET /health"
        }
    }


@app.post("/ingest/log")
async def ingest_single_log(event: LogEvent, background_tasks: BackgroundTasks):
    """
    Ingest a single log event

    Flow:
    1. Parse raw log message
    2. Normalize event format
    3. Enrich with context
    4. Send to streaming pipeline
    5. Broadcast to WebSocket clients
    """
    try:
        start_time = datetime.now()

        # Generate event ID
        event_id = str(uuid.uuid4())

        print(f"📥 Ingesting log from {event.source}: {event.raw_message[:100]}")

        # Step 1: Parse raw log
        parsed_data = log_parser.parse(event.raw_message, event.source)

        # Step 2: Normalize event
        normalized_event = log_normalizer.normalize(
            event_id=event_id,
            timestamp=event.timestamp or datetime.now().isoformat(),
            source=event.source,
            parsed_data=parsed_data,
            raw_message=event.raw_message,
            severity=event.severity or "INFO",
            metadata=event.metadata
        )

        # Step 3: Enrich event
        enriched_event = event_enricher.enrich(normalized_event)

        # Step 4: Add to streaming pipeline (background)
        background_tasks.add_task(
            streaming_pipeline.process_event,
            enriched_event
        )

        # Step 5: Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "new_event",
            "event": enriched_event
        })

        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "event_id": event_id,
            "source": event.source,
            "normalized": enriched_event,
            "processing_time": round(processing_time, 3)
        }

    except Exception as e:
        print(f"⚠️ Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/ingest/batch")
async def ingest_batch_logs(events: List[LogEvent], background_tasks: BackgroundTasks):
    """
    Ingest a batch of log events

    Processes multiple events efficiently
    """
    try:
        start_time = datetime.now()
        processed_events = []

        print(f"📥 Ingesting batch of {len(events)} events")

        for event in events:
            event_id = str(uuid.uuid4())

            # Parse, normalize, enrich
            parsed_data = log_parser.parse(event.raw_message, event.source)
            normalized_event = log_normalizer.normalize(
                event_id=event_id,
                timestamp=event.timestamp or datetime.now().isoformat(),
                source=event.source,
                parsed_data=parsed_data,
                raw_message=event.raw_message,
                severity=event.severity or "INFO",
                metadata=event.metadata
            )
            enriched_event = event_enricher.enrich(normalized_event)

            processed_events.append(enriched_event)

        # Add batch to streaming pipeline (background)
        background_tasks.add_task(
            streaming_pipeline.process_batch,
            processed_events
        )

        # Broadcast batch to WebSocket clients
        await manager.broadcast({
            "type": "batch_events",
            "count": len(processed_events),
            "events": processed_events[:10]  # Send first 10 for preview
        })

        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "events_processed": len(processed_events),
            "processing_time": round(processing_time, 3),
            "events_per_second": round(len(processed_events) / processing_time, 2)
        }

    except Exception as e:
        print(f"⚠️ Batch ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch ingestion failed: {str(e)}")


@app.websocket("/stream/logs")
async def stream_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming

    Clients receive:
    - New events as they arrive
    - Batch event notifications
    - Classification results
    - Statistics updates
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to log stream",
            "timestamp": datetime.now().isoformat()
        })

        # Keep connection alive and handle client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle client commands
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "get_stats":
                    stats = streaming_pipeline.get_stats()
                    await websocket.send_json({
                        "type": "stats",
                        "data": stats
                    })

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"⚠️ WebSocket error: {str(e)}")
                break

    finally:
        manager.disconnect(websocket)
        print(f"🔌 WebSocket client disconnected")


@app.get("/sources")
async def get_sources():
    """
    Get available log collection sources
    """
    sources = [
        {
            "source_id": "system_logs",
            "name": "System Logs",
            "type": "syslog",
            "description": "Operating system and kernel logs",
            "enabled": True,
            "event_count": streaming_pipeline.stats.get("system_logs", 0)
        },
        {
            "source_id": "application_logs",
            "name": "Application Logs",
            "type": "application",
            "description": "Application and service logs",
            "enabled": True,
            "event_count": streaming_pipeline.stats.get("application_logs", 0)
        },
        {
            "source_id": "network_logs",
            "name": "Network Logs",
            "type": "network",
            "description": "Firewall, router, and network device logs",
            "enabled": True,
            "event_count": streaming_pipeline.stats.get("network_logs", 0)
        },
        {
            "source_id": "security_logs",
            "name": "Security Logs",
            "type": "security",
            "description": "Security events, IDS/IPS, authentication logs",
            "enabled": True,
            "event_count": streaming_pipeline.stats.get("security_logs", 0)
        },
        {
            "source_id": "database_logs",
            "name": "Database Logs",
            "type": "database",
            "description": "Database access and query logs",
            "enabled": True,
            "event_count": streaming_pipeline.stats.get("database_logs", 0)
        },
        {
            "source_id": "web_logs",
            "name": "Web Server Logs",
            "type": "web",
            "description": "HTTP access and error logs",
            "enabled": True,
            "event_count": streaming_pipeline.stats.get("web_logs", 0)
        }
    ]

    return {
        "total_sources": len(sources),
        "sources": sources
    }


@app.get("/stats", response_model=CollectionStats)
async def get_stats():
    """Get collection statistics"""
    stats = streaming_pipeline.get_stats()

    return CollectionStats(
        total_events_collected=stats.get("total_collected", 0),
        total_events_parsed=stats.get("total_parsed", 0),
        total_events_classified=stats.get("total_classified", 0),
        events_per_second=stats.get("events_per_second", 0.0),
        collection_sources=["system", "application", "network", "security", "database", "web"],
        active_connections=len(manager.active_connections)
    )


@app.post("/mcp/connect")
async def connect_mcp_server(server_url: str):
    """
    Connect to MCP server for log collection

    Args:
        server_url: MCP server URL
    """
    try:
        result = await mcp_client.connect(server_url)
        return {
            "success": True,
            "message": "Connected to MCP server",
            "server_url": server_url,
            "connection_id": result.get("connection_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP connection failed: {str(e)}")


@app.post("/mcp/subscribe")
async def subscribe_mcp_logs(log_source: str):
    """
    Subscribe to MCP log source

    Args:
        log_source: Log source identifier
    """
    try:
        result = await mcp_client.subscribe(log_source)
        return {
            "success": True,
            "message": f"Subscribed to {log_source}",
            "subscription_id": result.get("subscription_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP subscription failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Log Collection Engine",
        "version": "1.0.0",
        "mcp_connected": mcp_client.is_connected(),
        "active_streams": len(manager.active_connections),
        "pipeline_active": streaming_pipeline.is_active(),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Unified Pipeline Evidence Endpoints
# ============================================================================

@app.post("/api/v1/evidence/submit")
async def submit_evidence(
    audit_id: str,
    event: LogEvent,
    control_id: Optional[str] = None
):
    """
    Submit log evidence to unified pipeline.

    This endpoint:
    1. Parses and normalizes the log event
    2. Converts to ComplianceEvidence format
    3. Stores in Redis via EvidenceManager
    4. Returns evidence ID for tracking

    Args:
        audit_id: Parent audit ID
        event: Raw log event
        control_id: Optional pre-identified control ID
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available - shared module or Redis not initialized"
        )

    try:
        # Parse raw log
        parsed_data = log_parser.parse(event.raw_message, event.source)

        # Normalize event
        event_id = str(uuid.uuid4())
        normalized_event = log_normalizer.normalize(
            event_id=event_id,
            timestamp=event.timestamp or datetime.now().isoformat(),
            source=event.source,
            parsed_data=parsed_data,
            raw_message=event.raw_message,
            severity=event.severity or "INFO",
            metadata=event.metadata
        )

        # Get control info from LLM if not provided
        control_info = {}
        if not control_id and llm_analyzer.is_enabled():
            llm_result = await llm_analyzer.analyze_log(event.raw_message, parsed_data, event.source)
            # Extract first mapped control if available
            if llm_result.get("mapped_controls"):
                control_id = llm_result["mapped_controls"][0]["control_id"]
                control_info = {
                    "control_id": control_id,
                    "name": llm_result["mapped_controls"][0].get("name", ""),
                    "confidence": llm_result["mapped_controls"][0].get("confidence", 0.5)
                }
            else:
                # No control mapped - will use default later
                control_info = {}

        # Convert to ComplianceEvidence
        evidence = evidence_converter.convert_event(
            normalized_event=normalized_event,
            audit_id=audit_id,
            control_id=control_id,
            control_info=control_info
        )

        # Store in Redis
        success = await evidence_manager.store_evidence(evidence)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store evidence in Redis")

        print(f"✅ Evidence {evidence.evidence_id} stored for audit {audit_id}, control {control_id}")

        return {
            "success": True,
            "evidence_id": evidence.evidence_id,
            "audit_id": audit_id,
            "control_id": evidence.control_id,
            "source_type": evidence.source_type.value,
            "timestamp": evidence.timestamp.isoformat()
        }

    except Exception as e:
        print(f"⚠️ Evidence submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evidence submission failed: {str(e)}")


@app.post("/api/v1/evidence/submit-batch")
async def submit_evidence_batch(
    audit_id: str,
    events: List[LogEvent]
):
    """
    Submit batch of log evidence to unified pipeline.

    Args:
        audit_id: Parent audit ID
        events: List of raw log events
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available - shared module or Redis not initialized"
        )

    try:
        normalized_events = []
        control_mappings = {}

        # Process each event
        for event in events:
            event_id = str(uuid.uuid4())

            # Parse and normalize
            parsed_data = log_parser.parse(event.raw_message, event.source)
            normalized_event = log_normalizer.normalize(
                event_id=event_id,
                timestamp=event.timestamp or datetime.now().isoformat(),
                source=event.source,
                parsed_data=parsed_data,
                raw_message=event.raw_message,
                severity=event.severity or "INFO",
                metadata=event.metadata
            )

            # Get control info from LLM
            if llm_analyzer.is_enabled():
                llm_result = await llm_analyzer.analyze_log(event.raw_message, parsed_data, event.source)
                if llm_result.get("mapped_controls"):
                    control_mappings[event_id] = {
                        "control_id": llm_result["mapped_controls"][0]["control_id"],
                        "name": llm_result["mapped_controls"][0].get("name", ""),
                        "confidence": llm_result["mapped_controls"][0].get("confidence", 0.5)
                    }

            normalized_events.append(normalized_event)

        # Convert to EvidenceBatch
        batch = evidence_converter.convert_batch(
            normalized_events=normalized_events,
            audit_id=audit_id,
            control_mappings=control_mappings
        )

        # Store batch in Redis
        success = await evidence_manager.store_evidence_batch(batch)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store evidence batch in Redis")

        print(f"✅ Evidence batch {batch.batch_id} stored: {batch.processed_count} items for audit {audit_id}")

        return {
            "success": True,
            "batch_id": batch.batch_id,
            "audit_id": audit_id,
            "total_count": batch.total_count,
            "processed_count": batch.processed_count,
            "failed_count": batch.failed_count
        }

    except Exception as e:
        print(f"⚠️ Batch submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch submission failed: {str(e)}")


@app.get("/api/v1/evidence/audit/{audit_id}")
async def get_audit_evidence(
    audit_id: str,
    source_type: Optional[str] = None,
    control_id: Optional[str] = None
):
    """
    Retrieve evidence for an audit.

    Args:
        audit_id: Audit ID
        source_type: Optional filter by source type (log, document, config)
        control_id: Optional filter by control ID
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available"
        )

    try:
        # Get evidence based on filters
        if control_id:
            evidence_list = await evidence_manager.get_evidence_by_control(audit_id, control_id)
        elif source_type:
            evidence_list = await evidence_manager.get_evidence_by_source(
                audit_id,
                EvidenceSourceType(source_type)
            )
        else:
            evidence_list = await evidence_manager.get_all_evidence(audit_id)

        return {
            "audit_id": audit_id,
            "total_count": len(evidence_list),
            "filters": {
                "source_type": source_type,
                "control_id": control_id
            },
            "evidence": [e.model_dump() if hasattr(e, 'model_dump') else e for e in evidence_list]
        }

    except Exception as e:
        print(f"⚠️ Evidence retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evidence retrieval failed: {str(e)}")


# ============================================================================
# Background Tasks
# ============================================================================

async def periodic_stats_broadcast():
    """Broadcast statistics periodically to WebSocket clients"""
    while True:
        await asyncio.sleep(10)  # Every 10 seconds
        stats = streaming_pipeline.get_stats()
        await manager.broadcast({
            "type": "stats_update",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global evidence_manager

    print("=" * 80)
    print("ENGINE 1: Log Collection Engine (LLM-Powered)")
    print("Rwanda NCSA Compliance Auditor v2.0.0")
    print("=" * 80)
    print(f"🔗 ENGINE 3 URL: {ENGINE3_URL}")
    print(f"🔗 ENGINE 4 URL: {ENGINE4_URL}")
    print(f"🧠 LLM Analyzer: {'Enabled (GPT-4)' if llm_analyzer.is_enabled() else 'Disabled (Regex-only mode)'}")
    print(f"📊 MCP Client: Initialized (Read-only command execution)")
    print(f"🔍 Log Parser: Ready (LLM-enhanced)")
    print(f"📋 Syslog Adapter: Ready (RFC 5424 & 3164)")
    print(f"🪟 Windows Event Adapter: Ready (XML & Text)")
    print(f"⚙️  Log Normalizer: Ready")
    print(f"✨ Event Enricher: Ready")
    print(f"🌊 Streaming Pipeline: Active")
    print("=" * 80)

    # Initialize unified pipeline components
    if SHARED_AVAILABLE:
        try:
            # Initialize Redis client
            redis_client = await init_redis("engine1-log-collector")

            # Create evidence manager
            evidence_manager = create_evidence_manager(redis_client)

            print(f"🔄 Unified Pipeline: Active")
            print(f"   - Redis: Connected ({REDIS_HOST}:{REDIS_PORT})")
            print(f"   - Evidence Manager: Initialized")
            print(f"   - Evidence Converter: Ready")
            print(f"   - ComplianceEvidence format: Enabled")
        except Exception as e:
            print(f"⚠️  Unified Pipeline: Failed to initialize - {str(e)}")
            print(f"   - Running in standalone mode")
            evidence_manager = None
    else:
        print(f"⚠️  Unified Pipeline: Not available (shared module not found)")
        print(f"   - Running in standalone mode")

    print("=" * 80)
    print(f"🎯 Features:")
    print(f"   - Semantic log understanding (LLM)")
    print(f"   - Automatic control mapping (196 controls)")
    print(f"   - Multi-format support (syslog, Windows, JSON)")
    print(f"   - Read-only command execution (MCP)")
    print(f"   - Real-time compliance classification")
    if SHARED_AVAILABLE and evidence_manager:
        print(f"   - Unified evidence pipeline (Redis-backed)")
        print(f"   - Gap analysis support (policy vs logs)")
    print("=" * 80)

    # Start periodic stats broadcast
    asyncio.create_task(periodic_stats_broadcast())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Log Collection Engine shutting down...")
    await mcp_client.disconnect()
    await streaming_pipeline.shutdown()
