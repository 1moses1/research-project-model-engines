# ENGINE 1: Log Collection Engine

**Rwanda NCSA Compliance Auditor v3.0.0**

Real-time log collection, parsing, normalization, and streaming engine with MCP protocol integration. The foundational engine that feeds the entire compliance auditing pipeline.

## Features

### Log Collection
- **Multi-Source Support**: System, Application, Network, Security, Database, Web logs
- **MCP Protocol Integration**: Connect to MCP servers for log collection
- **Real-Time Streaming**: WebSocket support for live log monitoring
- **Batch Processing**: Efficient batch ingestion for high-volume environments

### Log Processing Pipeline
- **Intelligent Parsing**: Pattern-based parsing for syslog, Apache, Nginx, JSON formats
- **Normalization**: Standardized format for downstream processing
- **Event Enrichment**: Geolocation, user context, risk scoring, anomaly detection
- **Compliance Context**: Automatic mapping to NIST/Rwanda NCSA controls

### Integration
- **ENGINE 3 Integration**: Automatic classification of log events
- **ENGINE 4 Integration**: Decision routing and compliance scoring
- **WebSocket Streaming**: Real-time events to web clients
- **Background Processing**: Async batch processing for performance

## Architecture

```
Log Sources → Ingest API → Parser → Normalizer → Enricher
                                                      ↓
                                            Streaming Pipeline
                                                      ↓
                           ┌─────────────────────────┴──────────────┐
                           ↓                                        ↓
                    ENGINE 3 (Classify)                     WebSocket Clients
                           ↓
                    ENGINE 4 (Decision)
```

## API Endpoints

### Log Ingestion

#### `POST /ingest/log`
Ingest single log event

**Request:**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "source": "system_logs",
  "raw_message": "Jan 15 10:30:00 server01 sshd: Failed password for admin from 192.168.1.100",
  "severity": "WARNING",
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "event_id": "a1b2c3d4-e5f6-7890",
  "source": "system_logs",
  "normalized": {
    "event_id": "a1b2c3d4-e5f6-7890",
    "timestamp": "2025-01-15T10:30:00Z",
    "log_message": "Action: FAILED | User: admin | IP: 192.168.1.100 | Failed password for admin from 192.168.1.100",
    "user": "admin",
    "ip_address": "192.168.1.100",
    "action": "FAILED",
    "severity": "WARNING",
    "metadata": {
      "event_type": "authentication_failure",
      "risk_score": 0.8,
      "anomaly_detected": true,
      "anomaly_reason": "failed_authentication"
    }
  },
  "processing_time": 0.015
}
```

#### `POST /ingest/batch`
Ingest batch of log events

**Request:**
```json
{
  "events": [
    {
      "source": "web_logs",
      "raw_message": "192.168.1.50 - user1 [15/Jan/2025:10:30:00 +0000] \"GET /api/users HTTP/1.1\" 200 1024"
    },
    ...
  ]
}
```

**Response:**
```json
{
  "success": true,
  "events_processed": 100,
  "processing_time": 0.25,
  "events_per_second": 400
}
```

### Real-Time Streaming

#### `WebSocket /stream/logs`
Real-time log event stream

**Client → Server (Commands):**
```json
{"type": "ping"}
{"type": "get_stats"}
```

**Server → Client (Events):**
```json
{
  "type": "new_event",
  "event": {...}
}

{
  "type": "batch_events",
  "count": 10,
  "events": [...]
}

{
  "type": "stats_update",
  "data": {...}
}
```

### Log Sources

#### `GET /sources`
Get available log collection sources

**Response:**
```json
{
  "total_sources": 6,
  "sources": [
    {
      "source_id": "system_logs",
      "name": "System Logs",
      "type": "syslog",
      "description": "Operating system and kernel logs",
      "enabled": true,
      "event_count": 15234
    }
  ]
}
```

### MCP Protocol

#### `POST /mcp/connect`
Connect to MCP server

**Request:**
```json
{
  "server_url": "ws://mcp-server:9000"
}
```

#### `POST /mcp/subscribe`
Subscribe to MCP log source

**Request:**
```json
{
  "log_source": "security_events"
}
```

### System Information

#### `GET /health`
Health check endpoint

#### `GET /stats`
Get collection statistics

**Response:**
```json
{
  "total_events_collected": 50000,
  "total_events_parsed": 49850,
  "total_events_classified": 48000,
  "events_per_second": 125.5,
  "collection_sources": ["system", "application", "network", "security", "database", "web"],
  "active_connections": 3
}
```

## Log Parsing

### Supported Formats

**Syslog Format:**
```
Jan 15 10:30:00 server01 sshd[1234]: Failed password for admin from 192.168.1.100
```

**Apache/Nginx Logs:**
```
192.168.1.50 - user1 [15/Jan/2025:10:30:00] "GET /api HTTP/1.1" 200 1024
```

**JSON Logs:**
```json
{"timestamp": "2025-01-15T10:30:00Z", "user": "admin", "action": "login", "status": "success"}
```

**Key-Value Pairs:**
```
user=admin action=login ip=192.168.1.100 status=failed
```

### Extracted Fields

- `timestamp`: Event timestamp (normalized to ISO format)
- `user`: Username/account
- `ip_address`: Source IP address
- `action`: Action/event type (LOGIN, LOGOUT, ACCESS, etc.)
- `resource`: File/path/resource accessed
- `status_code`: HTTP status or result code
- `message`: Parsed/formatted log message

## Event Enrichment

### Geolocation
- IP address geolocation lookup
- Private/public IP detection
- Country and city information

### Risk Scoring
Risk score (0.0-1.0) based on:
- Failed authentication attempts (+0.3)
- Error status codes (+0.2-0.3)
- Privileged user actions (+0.2)
- External IP addresses (+0.2)
- Critical/Error severity (+0.3)

### Anomaly Detection
- Failed authentication attempts
- Privilege escalation attempts
- Sensitive file access (/etc/shadow, credentials)
- Port scanning
- SQL injection attempts

### Compliance Mapping
Automatic mapping to NIST/Rwanda NCSA controls:
- Authentication → AC-2, IA-2, IA-3
- Authentication Failure → AC-7, AU-2, SI-4
- Access Control → AC-3, AC-6, AU-2
- Data Access → AC-4, AU-9, SC-28
- Configuration Change → CM-2, CM-3, AU-2

## Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- ACCESS to ENGINE 3 and ENGINE 4

### Local Development

```bash
cd engines/log_collector

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export ENGINE3_URL="http://localhost:8000"
export ENGINE4_URL="http://localhost:8001"

uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### Docker Deployment

```bash
docker-compose up -d log-collector

docker-compose logs -f log-collector
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENGINE3_URL` | XGBoost Classifier URL | `http://xgboost-api:8000` |
| `ENGINE4_URL` | Decision Engine URL | `http://decision-engine:8001` |
| `PORT` | Server port | 8004 |

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8004/health

# Ingest single log
curl -X POST "http://localhost:8004/ingest/log" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "system_logs",
    "raw_message": "Failed password for admin from 192.168.1.100",
    "severity": "WARNING"
  }'

# Get sources
curl http://localhost:8004/sources

# Get stats
curl http://localhost:8004/stats

# WebSocket connection
websocat ws://localhost:8004/stream/logs
```

### Performance

| Operation | Avg Time | Throughput |
|-----------|----------|------------|
| Single event ingestion | 10-20ms | 50-100 eps |
| Batch ingestion (100) | 200-300ms | 300-500 eps |
| Parse syslog | <1ms | - |
| Normalize event | <1ms | - |
| Enrich event | 1-2ms | - |
| ENGINE 3 classification | 50-100ms | - |

## Integration with Other Engines

### ENGINE 3: XGBoost Classifier
```python
# Automatic classification
normalized_event = {...}
classification = await engine3.classify(normalized_event)
# Result: {prediction: "compliant", confidence: 0.92}
```

### ENGINE 4: Decision Engine
```python
# Automatic routing
classified_event = {...}
decision = await engine4.process_event(classified_event)
# Result: {route_decision: "auto_accept"}
```

### ENGINE 6: Web UI
```javascript
// Real-time log streaming
const ws = new WebSocket('ws://localhost:8004/stream/logs');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'new_event') {
    displayLogEvent(data.event);
  }
};
```

## Directory Structure

```
engines/log_collector/
├── app/
│   ├── main.py                      # FastAPI application (450+ lines)
│   ├── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── mcp_client.py            # MCP protocol client (120 lines)
│       ├── log_parser.py            # Multi-format parser (220 lines)
│       ├── log_normalizer.py        # Event normalizer (200 lines)
│       ├── event_enricher.py        # Enrichment service (250 lines)
│       └── streaming_pipeline.py    # Pipeline orchestrator (200 lines)
├── requirements.txt
├── Dockerfile
└── README.md
```

## Future Enhancements

- [ ] Additional log format support (Windows Event Log, CEF)
- [ ] Advanced threat intelligence integration
- [ ] Machine learning-based anomaly detection
- [ ] Log retention and archival
- [ ] Compression and encryption
- [ ] Custom parsing rules
- [ ] Rate limiting and backpressure
- [ ] Distributed deployment support

## Contributors

**Rwanda NCSA Compliance Auditor Team**
- ENGINE 1: Log Collection Engine

## License

Internal use only - Rwanda NCSA Compliance Auditor v3.0.0

---

**ENGINE 1 Status:** ✅ COMPLETE
**Port:** 8004
**Dependencies:** ENGINE 3, ENGINE 4
**Integration:** All Engines (foundation of the system)
