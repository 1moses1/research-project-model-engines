# ENGINE 6: Interactive Web Dashboard

**Version**: 3.0.0
**Purpose**: Modern web interface for Rwanda NCSA Compliance Auditor

## Features

### 1. Document Upload Interface
- Drag & drop file upload (PDF, DOCX, XLSX)
- Real-time upload progress tracking
- WebSocket-based processing updates
- Automatic control extraction via LLM

### 2. System Health Monitor
- Real-time MCP server status
- Database connection monitoring (PostgreSQL, Redis)
- Cache performance metrics
- All processing engines status
- Live updates every 2 seconds

### 3. Interactive 3D Architecture Diagram
- Floating animated nodes for all system components
- Visual connection flow between engines
- Click nodes for detailed metrics
- Auto-rotating camera with zoom/pan controls
- Real-time status color coding

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **shadcn/ui** - Modern component library
- **Tailwind CSS** - Utility-first CSS framework
- **React Three Fiber** - 3D visualization (Three.js for React)
- **Socket.IO Client** - Real-time bidirectional communication
- **Zustand** - State management
- **React Dropzone** - File upload
- **Axios** - HTTP client

### Backend
- **FastAPI** (Python 3.11) - High-performance async API
- **Socket.IO Server** - WebSocket communication
- **Uvicorn** - ASGI server
- **Aiofiles** - Async file operations

## Quick Start

### Development Mode

#### Backend
```bash
cd engines/web_ui/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run server
uvicorn api:socket_app --reload --port 8006
```

#### Frontend
```bash
cd engines/web_ui/frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run development server
npm start
```

Access the UI at: http://localhost:3000

### Production Mode (Docker)

```bash
# From project root
docker-compose up -d web-ui-backend web-ui-frontend

# Access UI
open http://localhost:3000
```

## Project Structure

```
engines/web_ui/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUpload.tsx          # File upload component
│   │   │   ├── SystemHealthMonitor.tsx     # System status dashboard
│   │   │   ├── ArchitectureDiagram.tsx     # 3D visualization
│   │   │   └── ui/                         # shadcn/ui components
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts             # WebSocket hook
│   │   ├── types/
│   │   │   └── index.ts                    # TypeScript types
│   │   ├── App.tsx                         # Main application
│   │   ├── index.tsx                       # Entry point
│   │   └── index.css                       # Global styles
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── backend/
│   ├── api.py                              # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
└── README.md
```

## API Endpoints

### REST API

#### `GET /`
Health check endpoint

#### `GET /api/v3/system/status`
Get current system status for all engines and infrastructure

**Response:**
```json
{
  "mcp_server": {
    "status": "connected",
    "logs_per_second": 1234,
    "active_connectors": ["AWS CloudTrail", "Syslog"],
    "uptime_seconds": 86400
  },
  "databases": { ... },
  "engines": { ... },
  "cache_performance": { ... }
}
```

#### `POST /api/v3/documents/upload`
Upload policy document for processing

**Parameters:**
- `file`: Document file (PDF, DOCX, XLSX)
- `company_name`: Company/organization name
- `framework`: Compliance framework (Rwanda-NCSA, NIST, etc.)

**Response:**
```json
{
  "status": "accepted",
  "filename": "policy.pdf",
  "file_path": "uploads/Demo Company/20241119/policy.pdf",
  "message": "Document uploaded successfully. Processing started."
}
```

### WebSocket Events

#### Client → Server
No client-initiated events currently

#### Server → Client

**`system_status`** - Real-time system status updates (every 2 seconds)
```json
{
  "mcp_server": { ... },
  "databases": { ... },
  "engines": { ... }
}
```

**`upload_progress`** - Document processing progress
```json
{
  "filename": "policy.pdf",
  "status": "processing",
  "progress": 100,
  "message": "Extracting controls...",
  "extracted_controls": 42
}
```

## Environment Variables

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8006
REACT_APP_WS_URL=ws://localhost:8006
```

### Backend (.env)
```bash
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_URL=postgresql://user:pass@postgres:5432/compliance
REDIS_URL=redis://redis:6379
```

## Development

### Adding New Components

1. Create component in `frontend/src/components/`
2. Add TypeScript types to `frontend/src/types/index.ts`
3. Import and use in `App.tsx`

### Adding New API Endpoints

1. Add endpoint to `backend/api.py`
2. Update frontend service/hook to call the endpoint
3. Update this README with endpoint documentation

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend (already production-ready with FastAPI)
# Just run with uvicorn in production mode (without --reload)
```

## Troubleshooting

### WebSocket Not Connecting
1. Check backend is running: `curl http://localhost:8006/`
2. Check CORS settings in `backend/api.py`
3. Verify `REACT_APP_WS_URL` in frontend `.env`

### File Upload Fails
1. Check file type is supported (PDF, DOCX, XLSX)
2. Verify backend `uploads/` directory exists and is writable
3. Check backend logs for errors

### 3D Diagram Not Rendering
1. Ensure browser supports WebGL
2. Check console for Three.js errors
3. Try disabling hardware acceleration if issues persist

## Performance Notes

- WebSocket updates: 2-second interval (configurable in `backend/api.py`)
- File size limit: Default 100MB (configurable in FastAPI)
- Concurrent uploads: Handled asynchronously
- 3D diagram: 60 FPS target on modern browsers

## Next Steps

1. **Integration**: Connect to actual ENGINE 1-5 APIs
2. **Authentication**: Add JWT-based authentication
3. **Monitoring**: Add Prometheus metrics
4. **Logging**: Structured logging with correlation IDs
5. **Testing**: Unit tests (Jest) + E2E tests (Playwright)

## Support

For issues or questions:
1. Check this README
2. Review `ARCHITECTURE_V3_UPDATED.md` in project root
3. Check backend logs: `docker logs rwanda-ncsa-web-backend`
4. Check frontend logs in browser DevTools console
