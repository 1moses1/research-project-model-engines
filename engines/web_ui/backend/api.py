"""
FastAPI Backend for ENGINE 6: Web UI
Provides REST API and WebSocket endpoints for the React frontend
"""

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import os
from typing import List, Dict, Optional
import aiofiles
from datetime import datetime
import socketio
import random

app = FastAPI(
    title="Rwanda NCSA Web UI API",
    version="3.0.0",
    description="Backend API for ENGINE 6 Web Dashboard"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80"],  # React dev + production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO for real-time updates
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:3000', 'http://localhost:80']
)
socket_app = socketio.ASGIApp(sio, app)

# In-memory store for system status (in production, use Redis)
system_status = {
    "mcp_server": {
        "status": "connected",
        "logs_per_second": 1234,
        "active_connectors": ["AWS CloudTrail", "Syslog", "Kubernetes"],
        "uptime_seconds": 86400
    },
    "databases": {
        "postgresql": {
            "status": "healthy",
            "connections": 25,
            "query_latency_ms": 2
        },
        "redis": {
            "status": "healthy",
            "memory_usage_mb": 128,
            "hit_rate_percent": 92
        }
    },
    "engines": {
        "Log Collection (MCP)": {
            "status": "running",
            "requests_per_minute": 1234,
            "avg_latency_ms": 5
        },
        "Document Processing": {
            "status": "running",
            "requests_per_minute": 45,
            "avg_latency_ms": 2500
        },
        "XGBoost Classifier": {
            "status": "running",
            "requests_per_minute": 5678,
            "avg_latency_ms": 1
        },
        "Decision Engine": {
            "status": "running",
            "requests_per_minute": 5678,
            "avg_latency_ms": 3
        },
        "Report Generator": {
            "status": "running",
            "requests_per_minute": 12,
            "avg_latency_ms": 15000
        }
    },
    "cache_performance": {
        "hit_rate": 92,
        "total_size_mb": 128,
        "evictions_per_minute": 5
    }
}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Rwanda NCSA Web UI API",
        "version": "3.0.0",
        "status": "running"
    }


@app.get("/api/v3/system/status")
async def get_system_status():
    """
    Get current system status for all engines and infrastructure
    """
    return system_status


@app.post("/api/v3/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    company_name: str = "Demo Company",
    framework: str = "Rwanda-NCSA"
):
    """
    Upload policy document for processing

    Args:
        file: Document file (PDF, DOCX, XLSX)
        company_name: Company/organization name
        framework: Compliance framework (Rwanda-NCSA, NIST, etc.)

    Returns:
        Upload confirmation with processing task ID
    """
    # Validate file type
    allowed_types = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: PDF, DOCX, XLSX"
        )

    # Create upload directory
    upload_dir = f"uploads/{company_name}/{datetime.now().strftime('%Y%m%d')}"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = f"{upload_dir}/{file.filename}"

    # Save file asynchronously
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Emit progress via WebSocket
    await sio.emit('upload_progress', {
        'filename': file.filename,
        'status': 'processing',
        'progress': 100,
        'message': 'File uploaded, starting LLM processing...'
    })

    # Trigger document processing asynchronously (ENGINE 2)
    asyncio.create_task(
        process_document_async(file_path, framework, file.filename)
    )

    return {
        "status": "accepted",
        "filename": file.filename,
        "file_path": file_path,
        "message": "Document uploaded successfully. Processing started."
    }


async def process_document_async(file_path: str, framework: str, filename: str):
    """
    Async task to process document with ENGINE 2 (Document Processor)

    In production, this would call the actual ENGINE 2 API.
    For demo, we simulate the processing workflow.
    """
    try:
        # Step 1: Text extraction
        await asyncio.sleep(2)
        await sio.emit('upload_progress', {
            'filename': filename,
            'status': 'processing',
            'message': 'Extracting text from document...'
        })

        # Step 2: LLM processing (GPT-4)
        await asyncio.sleep(3)
        await sio.emit('upload_progress', {
            'filename': filename,
            'status': 'processing',
            'message': 'Processing with GPT-4... Extracting controls'
        })

        # Step 3: Control mapping
        await asyncio.sleep(2)

        # Simulate extracted controls (in production, from ENGINE 2)
        extracted_controls = random.randint(35, 50)

        await sio.emit('upload_progress', {
            'filename': filename,
            'status': 'completed',
            'message': f'Processing complete! Extracted {extracted_controls} controls.',
            'extracted_controls': extracted_controls
        })

        print(f"✅ Document processed: {filename} ({extracted_controls} controls)")

    except Exception as e:
        await sio.emit('upload_progress', {
            'filename': filename,
            'status': 'error',
            'error': str(e)
        })
        print(f"❌ Error processing {filename}: {str(e)}")


@app.websocket("/ws/system-status")
async def websocket_system_status(websocket: WebSocket):
    """
    WebSocket endpoint for real-time system status updates
    Alternative to Socket.IO for simpler clients
    """
    await websocket.accept()

    try:
        while True:
            # Send system status every 2 seconds
            await websocket.send_json(system_status)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")


# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Client connected to Socket.IO"""
    print(f"✅ Socket.IO client connected: {sid}")


@sio.event
async def disconnect(sid):
    """Client disconnected from Socket.IO"""
    print(f"❌ Socket.IO client disconnected: {sid}")


# Background task to update system metrics
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup"""
    print("🚀 Starting Rwanda NCSA Web UI Backend v3.0.0")
    print("📡 Socket.IO server initialized")
    print("🔄 Starting system metrics updater...")
    asyncio.create_task(update_system_metrics())


async def update_system_metrics():
    """
    Background task to fetch and update system metrics

    In production, this would:
    1. Query PostgreSQL for database stats
    2. Query Redis for cache stats
    3. Call ENGINE 1-5 APIs for their metrics
    4. Query MCP server for log collection stats

    For demo, we simulate changing metrics.
    """
    while True:
        try:
            # Simulate metric changes
            system_status["mcp_server"]["logs_per_second"] = random.randint(1000, 2000)
            system_status["mcp_server"]["uptime_seconds"] += 2

            system_status["databases"]["redis"]["hit_rate_percent"] = random.randint(88, 95)
            system_status["databases"]["redis"]["memory_usage_mb"] = random.randint(120, 140)

            system_status["cache_performance"]["hit_rate"] = system_status["databases"]["redis"]["hit_rate_percent"]
            system_status["cache_performance"]["total_size_mb"] = system_status["databases"]["redis"]["memory_usage_mb"]

            # Update engine metrics
            for engine_name in system_status["engines"]:
                current_rpm = system_status["engines"][engine_name]["requests_per_minute"]
                variation = random.randint(-100, 100)
                system_status["engines"][engine_name]["requests_per_minute"] = max(0, current_rpm + variation)

            # Broadcast to all connected Socket.IO clients
            await sio.emit('system_status', system_status)

        except Exception as e:
            print(f"⚠️  Error updating metrics: {str(e)}")

        await asyncio.sleep(2)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down Rwanda NCSA Web UI Backend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        socket_app,
        host="0.0.0.0",
        port=8006,
        log_level="info"
    )
