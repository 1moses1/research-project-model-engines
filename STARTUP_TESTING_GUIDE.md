# Rwanda NCSA Compliance Auditor v3.0.0
# Startup & Testing Guide

## Environment Variables Setup

### Required Variables: NONE (system works without any env vars!)

### Optional Variables: Only 1

**OPENAI_API_KEY** - Optional, for enhanced LLM features
- Used by: ENGINE 2 (Document Processing), ENGINE 5 (Report Generation), ENGINE 6 (Web UI)
- If not set: Engines use mock/fallback modes (still fully functional)
- To set: Create `.env` file in project root

```bash
# Create .env file (optional)
cp .env.example .env

# Edit .env and add your OpenAI key (if you have one)
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here
```

**Important:** The system is fully functional WITHOUT the OpenAI API key!
- ENGINE 2 will use mock document processing
- ENGINE 5 will use mock report generation
- All other engines work normally

### All Other Variables (Auto-configured)

These are automatically set in `docker-compose.yml` - **NO ACTION NEEDED**:
- `POSTGRES_URL` - Database connection (set by Docker Compose)
- `REDIS_URL` - Cache connection (set by Docker Compose)
- `ENGINE3_URL` - XGBoost API URL (internal Docker network)
- `ENGINE4_URL` - Decision Engine URL (internal Docker network)

---

## Step-by-Step Startup

### Step 1: Check Prerequisites

```bash
# Check Docker is running
docker --version
# Expected: Docker version 20.x or higher

# Check Docker Compose is available
docker-compose --version
# Expected: Docker Compose version 2.x or higher

# Check current directory
pwd
# Expected: /Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine
```

### Step 2: (Optional) Set OpenAI API Key

```bash
# Option A: Using .env file (recommended)
cp .env.example .env
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Option B: Export in terminal (temporary)
export OPENAI_API_KEY="sk-your-key-here"

# Option C: Skip this step - system works without it!
```

### Step 3: Build All Services

```bash
# Build all Docker images
docker-compose build

# This will build:
# - ENGINE 1 (log-collector)
# - ENGINE 2 (document-processor)
# - ENGINE 3 (xgboost-api)
# - ENGINE 4 (decision-engine)
# - ENGINE 5 (report-generator)
# - ENGINE 6 (web-ui-backend + web-ui-frontend)
# - PostgreSQL
# - Redis

# Expected time: 3-5 minutes
```

### Step 4: Start All Services

```bash
# Start all services in background
docker-compose up -d

# This will start all 9 containers:
# 1. rwanda-ncsa-logs (ENGINE 1)
# 2. rwanda-ncsa-document (ENGINE 2)
# 3. rwanda-ncsa-xgboost (ENGINE 3)
# 4. rwanda-ncsa-decision (ENGINE 4)
# 5. rwanda-ncsa-reports (ENGINE 5)
# 6. rwanda-ncsa-web-backend (ENGINE 6 Backend)
# 7. rwanda-ncsa-web-frontend (ENGINE 6 Frontend)
# 8. rwanda-ncsa-postgres (Database)
# 9. rwanda-ncsa-redis (Cache)
```

### Step 5: Check All Services Are Running

```bash
# View all running containers
docker-compose ps

# Expected output: All containers should show "Up" status
# NAME                          STATUS
# rwanda-ncsa-logs             Up (healthy)
# rwanda-ncsa-document         Up (healthy)
# rwanda-ncsa-xgboost          Up (healthy)
# rwanda-ncsa-decision         Up (healthy)
# rwanda-ncsa-reports          Up (healthy)
# rwanda-ncsa-web-backend      Up
# rwanda-ncsa-web-frontend     Up
# rwanda-ncsa-postgres         Up
# rwanda-ncsa-redis            Up
```

### Step 6: Wait for Health Checks (30-60 seconds)

```bash
# Watch container status
watch -n 2 docker-compose ps

# Wait until all show "healthy" status
# This usually takes 30-60 seconds

# Or check logs to see when services are ready
docker-compose logs -f | grep "ready\|healthy\|started"
```

---

## Health Check Tests

### Test All Engines Individually

```bash
# ENGINE 1: Log Collection (Port 8004)
curl http://localhost:8004/health
# Expected: {"status":"healthy","service":"Log Collection Engine",...}

# ENGINE 2: Document Processing (Port 8002)
curl http://localhost:8002/health
# Expected: {"status":"healthy","service":"Document Processing Engine",...}

# ENGINE 3: XGBoost Classifier (Port 8000)
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"XGBoost Compliance Classifier",...}

# ENGINE 4: Decision & Scoring (Port 8001)
curl http://localhost:8001/health
# Expected: {"status":"healthy","service":"Decision & Scoring Engine",...}

# ENGINE 5: Report Generation (Port 8003)
curl http://localhost:8003/health
# Expected: {"status":"healthy","service":"Report Generation Engine",...}

# ENGINE 6: Web UI Backend (Port 8006)
curl http://localhost:8006/health
# Expected: {"status":"healthy","service":"Web UI Backend",...}

# Web UI Frontend (Port 3000)
curl http://localhost:3000
# Expected: HTML response (React app)
```

### Quick Health Check Script

```bash
# Create a health check script
cat > check_health.sh << 'EOF'
#!/bin/bash
echo "🏥 Checking all engines..."
echo ""

echo "ENGINE 1 (Log Collection):"
curl -s http://localhost:8004/health | jq -r '.status' || echo "❌ Not responding"

echo "ENGINE 2 (Document Processing):"
curl -s http://localhost:8002/health | jq -r '.status' || echo "❌ Not responding"

echo "ENGINE 3 (XGBoost):"
curl -s http://localhost:8000/health | jq -r '.status' || echo "❌ Not responding"

echo "ENGINE 4 (Decision):"
curl -s http://localhost:8001/health | jq -r '.status' || echo "❌ Not responding"

echo "ENGINE 5 (Reports):"
curl -s http://localhost:8003/health | jq -r '.status' || echo "❌ Not responding"

echo "ENGINE 6 (Web UI):"
curl -s http://localhost:8006/health | jq -r '.status' || echo "❌ Not responding"

echo ""
echo "✅ All engines checked!"
EOF

chmod +x check_health.sh
./check_health.sh
```

---

## Access the Web UI

Once all services are healthy:

```bash
# Open web browser to the UI
open http://localhost:3000

# Or manually navigate to: http://localhost:3000
```

**Expected:** You should see the Rwanda NCSA Compliance Auditor 3D dashboard

---

## Testing Capabilities

### 1. Test Log Ingestion (ENGINE 1)

```bash
# Test single log ingestion
curl -X POST http://localhost:8004/ingest/log \
  -H "Content-Type: application/json" \
  -d '{
    "source": "system_logs",
    "raw_message": "Jan 15 10:30:00 server01 sshd: Failed password for admin from 192.168.1.100 port 22 ssh2",
    "severity": "WARNING"
  }'

# Expected:
# {
#   "success": true,
#   "event_id": "...",
#   "source": "system_logs",
#   "normalized": {...},
#   "processing_time": 0.015
# }
```

### 2. Test Classification (ENGINE 3)

```bash
# Test XGBoost classification
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "log_message": "User admin successfully authenticated from 192.168.1.100",
    "user": "admin",
    "ip_address": "192.168.1.100",
    "action": "LOGIN",
    "status_code": 200
  }'

# Expected:
# {
#   "prediction": "compliant",
#   "confidence": 0.95,
#   "probabilities": {...}
# }
```

### 3. Test Document Upload (ENGINE 2) - FROM WEB UI

**This is what you'll do from the UI:**

1. Navigate to http://localhost:3000
2. Find the "Document Upload" or "Policy Upload" section
3. Click "Upload Document"
4. Select your company policy PDF files
5. Click "Process" or "Submit"
6. Wait for processing (3-8 seconds per document)
7. View extracted controls

**Manual API Test (if needed):**

```bash
# Test document processing via API
curl -X POST http://localhost:8002/process/document \
  -F "file=@/path/to/policy.pdf" \
  -F "company_name=Test Corporation" \
  -F "framework=Rwanda-NCSA"

# Expected:
# {
#   "success": true,
#   "filename": "policy.pdf",
#   "controls_extracted": 12,
#   "controls_mapped": 10,
#   ...
# }
```

### 4. Test Report Generation (ENGINE 5)

```bash
# Generate a compliance scorecard
curl -X POST http://localhost:8003/generate/report \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "scorecard",
    "compliance_data": {
      "company_name": "Test Corporation",
      "total_controls": 100,
      "compliant_controls": 75,
      "non_compliant_controls": 25
    },
    "include_charts": true
  }'

# Expected:
# {
#   "success": true,
#   "report_id": "...",
#   "file_path": "/reports/...",
#   "pages": 8,
#   ...
# }

# Download the generated report
REPORT_ID="..." # Use ID from above response
curl "http://localhost:8003/reports/${REPORT_ID}" -o compliance_report.pdf
```

### 5. Test Real-Time Streaming (WebSocket)

```bash
# Install websocat if not already installed
# brew install websocat (macOS)
# or download from: https://github.com/vi/websocat

# Connect to log stream
websocat ws://localhost:8004/stream/logs

# Expected: Connection established message, then real-time log events
```

---

## View Logs

### View All Logs

```bash
# View all service logs
docker-compose logs -f

# View specific engine logs
docker-compose logs -f log-collector
docker-compose logs -f document-processor
docker-compose logs -f xgboost-api
docker-compose logs -f decision-engine
docker-compose logs -f report-generator
docker-compose logs -f web-ui-backend
docker-compose logs -f web-ui-frontend
```

### Check for Errors

```bash
# Check for errors across all services
docker-compose logs | grep -i "error\|failed\|exception"

# Check specific engine for errors
docker-compose logs log-collector | grep -i error
```

---

## Troubleshooting

### Issue: Services not starting

```bash
# Check Docker is running
docker info

# Rebuild services
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Port already in use

```bash
# Check what's using the ports
lsof -i :3000  # Web UI Frontend
lsof -i :8000  # ENGINE 3
lsof -i :8001  # ENGINE 4
lsof -i :8002  # ENGINE 2
lsof -i :8003  # ENGINE 5
lsof -i :8004  # ENGINE 1
lsof -i :8006  # ENGINE 6 Backend

# Stop conflicting service or change port in docker-compose.yml
```

### Issue: Model not found (ENGINE 3)

```bash
# Check if model files exist
ls -la models/compliance_auditor_final/

# Should see:
# - rwanda_ncsa_compliance_auditor.json
# - label_encoder.pkl
# - vectorizer.pkl
# - features.json
```

### Issue: Database connection failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

---

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Stop specific service
docker-compose stop log-collector
```

---

## Summary of Ports

| Service | Port | URL |
|---------|------|-----|
| Web UI Frontend | 3000 | http://localhost:3000 |
| ENGINE 3 (XGBoost) | 8000 | http://localhost:8000 |
| ENGINE 4 (Decision) | 8001 | http://localhost:8001 |
| ENGINE 2 (Documents) | 8002 | http://localhost:8002 |
| ENGINE 5 (Reports) | 8003 | http://localhost:8003 |
| ENGINE 1 (Logs) | 8004 | http://localhost:8004 |
| ENGINE 6 Backend | 8006 | http://localhost:8006 |
| PostgreSQL | 5432 | postgresql://localhost:5432 |
| Redis | 6379 | redis://localhost:6379 |

---

## Next Steps After Startup

1. ✅ All services healthy
2. ✅ Access Web UI at http://localhost:3000
3. ✅ Upload policy documents through the UI
4. ✅ View real-time compliance dashboard
5. ✅ Generate compliance reports

---

## Quick Start Checklist

- [ ] Docker & Docker Compose installed
- [ ] In project directory: `cd /Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine`
- [ ] (Optional) Set OPENAI_API_KEY in `.env` file
- [ ] Run: `docker-compose build`
- [ ] Run: `docker-compose up -d`
- [ ] Wait 60 seconds for health checks
- [ ] Run: `./check_health.sh` (or manual health checks)
- [ ] Open: http://localhost:3000
- [ ] Upload policy documents from UI
- [ ] View compliance dashboard

---

**Ready to start!** 🚀
