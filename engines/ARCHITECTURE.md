# Rwanda NCSA Compliance Auditor - Engine Architecture

## Overview

The Rwanda NCSA Compliance Auditor is a microservices-based platform with 7 specialized engines that work together to perform compliance auditing.

## Engine Ordering

| Engine # | Name | Port | Directory | Purpose |
|----------|------|------|-----------|---------|
| ENGINE 1 | Log Collector | 8001 | engine1-log-collector | Collects audit logs from target systems |
| ENGINE 2 | Document Processor | 8002 | engine2-document-processor | Processes policy documents with LLM |
| ENGINE 3 | XGBoost Classifier | 8003 | engine3-xgboost-classifier | ML classification of logs to controls |
| ENGINE 4 | Decision Engine | 8004 | engine4-decision-engine | Makes compliance decisions |
| ENGINE 5 | Report Generator | 8005 | engine6-report-generator | Generates PDF compliance reports |
| ENGINE 6 | Web UI | 8006 | engine5-web-ui | Dashboard with real-time updates |
| ENGINE 7 | Auth Engine | 8007 | engine7-auth-engine | Authentication & machine connection |

> Note: ENGINE 5 (Report Generator) uses the `engine6-report-generator` directory, and ENGINE 6 (Web UI) uses the `engine5-web-ui` directory. This is intentional to avoid file moves while keeping the correct logical ordering.

## Audit Flow

```
[User/CLI]
    |
    v
[ENGINE 7: Auth] --> Authenticate to platform & target machine
    |
    v
[ENGINE 1: Log Collector] --> Collect audit logs using whitelisted commands
    |
    v
[ENGINE 3: XGBoost] --> Classify logs to NCSA/NIST controls
    |
    v
[ENGINE 4: Decision] --> Determine compliance status
    |
    v
[ENGINE 5: Report] --> Generate PDF compliance report
    |
    v
[ENGINE 6: Web UI] <-- Real-time progress via WebSocket/Redis
```

## Redis Integration

All engines connect to Redis for:

1. **State Management**: Store audit state across the pipeline
2. **Pub/Sub**: Real-time updates for WebSocket clients
3. **Engine Registration**: Track engine status and heartbeats

### Redis Channels

- `audit:{audit_id}:state` - Current audit state (key)
- `audit:{audit_id}:updates` - Pub/sub channel for audit updates
- `audit:{audit_id}:logs` - Audit log history (list)
- `audit:global:updates` - Global channel for all audit updates
- `engine:{engine_id}` - Engine registration and status

### Environment Variables

All engines support these Redis environment variables:

```bash
REDIS_HOST=localhost      # Redis host (default: localhost)
REDIS_PORT=6379          # Redis port (default: 6379)
REDIS_DB=0               # Redis database (default: 0)
REDIS_PASSWORD=          # Redis password (optional)
ENGINE_NAME=engine1-log  # Engine identifier
```

## WebSocket Real-time Updates

ENGINE 6 (Web UI) provides WebSocket endpoints for real-time audit progress:

### WebSocket Endpoints

- `ws://host:8006/ws/audit/{audit_id}` - Subscribe to specific audit
- `ws://host:8006/ws/system-status` - System status updates
- `ws://host:8006/ws/global` - All updates

### Socket.IO Events

- `audit_started` - New audit started
- `audit_update` - Audit progress update
- `system_status` - Engine status update
- `upload_progress` - Document upload progress

## Audit Stages

| Stage | Progress | Engine | Description |
|-------|----------|--------|-------------|
| initialized | 0% | - | Audit created |
| authenticating | 5% | ENGINE 7 | Authenticating to target |
| authenticated | 10% | ENGINE 7 | Successfully authenticated |
| collecting_logs | 15% | ENGINE 1 | Collecting audit logs |
| logs_collected | 30% | ENGINE 1 | Logs collected |
| processing_documents | 35% | ENGINE 2 | Processing policy docs (optional) |
| classifying | 50% | ENGINE 3 | Classifying to controls |
| classified | 65% | ENGINE 3 | Classification complete |
| making_decisions | 70% | ENGINE 4 | Determining compliance |
| decisions_made | 85% | ENGINE 4 | Decisions complete |
| generating_report | 90% | ENGINE 5 | Generating PDF report |
| report_generated | 98% | ENGINE 5 | Report ready |
| completed | 100% | - | Audit complete |

## Docker Deployment

```bash
# Start all engines with Redis
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web-ui
```

### Service Dependencies

```
redis
  └── auth-engine
  └── xgboost-classifier
  └── document-processor
  └── decision-engine (depends on xgboost-classifier)
  └── log-collector (depends on auth, xgboost, decision)
  └── report-generator (depends on decision)
  └── web-ui (depends on all engines)
```

## Kubernetes Deployment

Redis and all engines can be deployed to Kubernetes:

```bash
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/engines/
```

## Shared Utilities

The `engines/shared/` directory contains common utilities:

- `redis_client.py` - Redis client wrapper with pub/sub support
- `audit_state.py` - Audit state management and stage tracking

### Using Shared Utilities

```python
from engines.shared import RedisClient, AuditState, AuditStage

# Initialize Redis
redis = RedisClient(engine_name="engine3-xgboost")
await redis.connect()

# Update audit state
await redis.set_audit_state(
    audit_id="AUDIT-20251121-123456",
    stage="classifying",
    progress=50,
    message="Processing 100 log entries..."
)
```

## Health Checks

All engines expose a `/health` endpoint:

```bash
curl http://localhost:8001/health  # ENGINE 1
curl http://localhost:8002/health  # ENGINE 2
curl http://localhost:8003/health  # ENGINE 3
curl http://localhost:8004/health  # ENGINE 4
curl http://localhost:8005/health  # ENGINE 5
curl http://localhost:8006/health  # ENGINE 6
curl http://localhost:8007/health  # ENGINE 7
```

## API Documentation

Each engine exposes OpenAPI documentation:

- ENGINE 1: http://localhost:8001/docs
- ENGINE 2: http://localhost:8002/docs
- ENGINE 3: http://localhost:8003/docs
- ENGINE 4: http://localhost:8004/docs
- ENGINE 5: http://localhost:8005/docs
- ENGINE 6: http://localhost:8006/docs
- ENGINE 7: http://localhost:8007/docs
