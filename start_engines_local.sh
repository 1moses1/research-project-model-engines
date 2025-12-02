#!/bin/bash
# Start all engines locally (not in Docker)
# Only Postgres and Redis run in Docker

set -e

BASE_DIR="/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"
LOGS_DIR="$BASE_DIR/logs"
mkdir -p "$LOGS_DIR"

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║   Rwanda NCSA - Local Engine Startup                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if venv exists and is ready
if [ -d "$BASE_DIR/venv" ] && [ -f "$BASE_DIR/venv/bin/activate" ]; then
    echo "✅ Using project virtual environment"
    source "$BASE_DIR/venv/bin/activate"
    PYTHON_CMD="python3"
else
    echo "❌ Virtual environment not found at $BASE_DIR/venv"
    echo "   Please create it first with: python3 -m venv venv"
    exit 1
fi

# Environment variables
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="compliance_db"
export POSTGRES_USER="compliance_user"
export POSTGRES_PASSWORD="compliance_pass"

# Check if Redis and Postgres are running
echo "🔍 Checking infrastructure..."
if ! docker ps | grep -q rwanda-ncsa-redis; then
    echo "⚠️  Redis container not running"
    echo "   Start with: docker-compose -f docker-compose.infra.yml up -d"
fi

if ! docker ps | grep -q rwanda-ncsa-postgres; then
    echo "⚠️  Postgres container not running"
    echo "   Start with: docker-compose -f docker-compose.infra.yml up -d"
fi

echo "✅ Redis: localhost:6379"
echo "✅ Postgres: localhost:5432"
echo ""

# Kill old processes
echo "🧹 Cleaning up old engine processes..."
pkill -9 -f "uvicorn.*app.main:app.*800[1-7]" 2>/dev/null || true
pkill -9 -f "uvicorn.*backend.api:app.*8006" 2>/dev/null || true
sleep 2
echo ""

# Start engines
cd "$BASE_DIR"

echo "🚀 Starting engines..."
echo ""

# Engine 1: Log Collector (port 8001)
echo "  [1/7] Log Collector (port 8001)..."
cd "$BASE_DIR/engines/engine1-log-collector"
PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8001 \
  > "$LOGS_DIR/engine1.log" 2>&1 &
ENGINE1_PID=$!
echo "        PID: $ENGINE1_PID | Logs: $LOGS_DIR/engine1.log"
sleep 2

# Engine 2: Document Processor (port 8002)
echo "  [2/7] Document Processor (port 8002)..."
cd "$BASE_DIR/engines/engine2-document-processor"
PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8002 \
  > "$LOGS_DIR/engine2.log" 2>&1 &
ENGINE2_PID=$!
echo "        PID: $ENGINE2_PID | Logs: $LOGS_DIR/engine2.log"
sleep 2

# Engine 3: XGBoost Classifier (port 8003)
echo "  [3/7] XGBoost Classifier (port 8003)..."
cd "$BASE_DIR/engines/engine3-xgboost-classifier"
PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8003 \
  > "$LOGS_DIR/engine3.log" 2>&1 &
ENGINE3_PID=$!
echo "        PID: $ENGINE3_PID | Logs: $LOGS_DIR/engine3.log"
sleep 2

# Engine 4: Decision Engine (port 8004)
echo "  [4/7] Decision Engine (port 8004)..."
cd "$BASE_DIR/engines/engine4-decision-engine"
PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8004 \
  > "$LOGS_DIR/engine4.log" 2>&1 &
ENGINE4_PID=$!
echo "        PID: $ENGINE4_PID | Logs: $LOGS_DIR/engine4.log"
sleep 2

# Engine 5: Report Generator (port 8005)
echo "  [5/7] Report Generator (port 8005)..."
cd "$BASE_DIR/engines/engine5-report-generator"
PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8005 \
  > "$LOGS_DIR/engine5.log" 2>&1 &
ENGINE5_PID=$!
echo "        PID: $ENGINE5_PID | Logs: $LOGS_DIR/engine5.log"
sleep 2

# Engine 6: Web UI (port 8006) - Using socket_app for WebSocket support
echo "  [6/7] Web UI (port 8006)..."
cd "$BASE_DIR/engines/engine6-web-ui"
PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
$PYTHON_CMD -m uvicorn backend.api:socket_app --host 0.0.0.0 --port 8006 \
  > "$LOGS_DIR/engine6.log" 2>&1 &
ENGINE6_PID=$!
echo "        PID: $ENGINE6_PID | Logs: $LOGS_DIR/engine6.log"
sleep 2

# Engine 7: Auth Engine (port 8007)
echo "  [7/7] Auth Engine (port 8007)..."
cd "$BASE_DIR/engines/engine7-auth-engine"
PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8007 \
  > "$LOGS_DIR/engine7.log" 2>&1 &
ENGINE7_PID=$!
echo "        PID: $ENGINE7_PID | Logs: $LOGS_DIR/engine7.log"
sleep 2

cd "$BASE_DIR"

echo ""
echo "⏳ Waiting for engines to initialize (15 seconds)..."
sleep 15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏥 Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_health() {
    local engine_num=$1
    local port=$2
    local name=$3

    if curl -s --max-time 2 "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "  ✅ Engine $engine_num ($name): HEALTHY"
        return 0
    elif curl -s --max-time 2 "http://localhost:$port/" > /dev/null 2>&1; then
        echo "  ✅ Engine $engine_num ($name): RUNNING"
        return 0
    else
        echo "  ❌ Engine $engine_num ($name): NOT RESPONDING"
        return 1
    fi
}

FAILED=0
check_health 1 8001 "Log Collector" || FAILED=$((FAILED+1))
check_health 2 8002 "Document Processor" || FAILED=$((FAILED+1))
check_health 3 8003 "XGBoost Classifier" || FAILED=$((FAILED+1))
check_health 4 8004 "Decision Engine" || FAILED=$((FAILED+1))
check_health 5 8005 "Report Generator" || FAILED=$((FAILED+1))
check_health 6 8006 "Web UI" || FAILED=$((FAILED+1))
check_health 7 8007 "Auth Engine" || FAILED=$((FAILED+1))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -eq 0 ]; then
    echo "✅ All engines started successfully!"
else
    echo "⚠️  $FAILED engine(s) failed to start. Check logs for details."
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Engine URLs:"
echo "   • Engine 1 (Log Collector):      http://localhost:8001"
echo "   • Engine 2 (Document Processor): http://localhost:8002"
echo "   • Engine 3 (XGBoost):            http://localhost:8003"
echo "   • Engine 4 (Decision Engine):    http://localhost:8004"
echo "   • Engine 5 (Report Generator):   http://localhost:8005"
echo "   • Engine 6 (Web UI):             http://localhost:8006"
echo "   • Engine 7 (Auth Engine):        http://localhost:8007"
echo ""
echo "📝 View logs:     tail -f $LOGS_DIR/engine*.log"
echo "🛑 Stop engines:  pkill -f 'uvicorn.*app.main'"
echo "🔄 Restart:       $0"
echo ""
