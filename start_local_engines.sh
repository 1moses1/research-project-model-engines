#!/bin/bash
# Start all engines locally (not in Docker)
# Only Postgres and Redis run in Docker

set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║   Rwanda NCSA Compliance Auditor - Local Development Mode             ║"
echo "║   Starting all engines as local Python processes                      ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Base directory
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGS_DIR="$BASE_DIR/logs"
mkdir -p "$LOGS_DIR"

# Environment variables
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="compliance_db"
export POSTGRES_USER="compliance_user"
export POSTGRES_PASSWORD="compliance_pass"

# OpenAI API Key (optional)
if [ -f "$BASE_DIR/.env" ]; then
    source "$BASE_DIR/.env"
fi

# Check if Redis and Postgres are running
echo "🔍 Checking infrastructure..."
if ! docker ps | grep -q rwanda-ncsa-redis; then
    echo "❌ Redis container not running. Starting infrastructure..."
    docker-compose -f docker-compose.infra.yml up -d
    sleep 3
fi

if ! docker ps | grep -q rwanda-ncsa-postgres; then
    echo "❌ Postgres container not running. Starting infrastructure..."
    docker-compose -f docker-compose.infra.yml up -d
    sleep 3
fi

echo "✅ Redis: localhost:6379"
echo "✅ Postgres: localhost:5432"
echo ""

# Kill any existing engine processes
echo "🧹 Cleaning up old processes..."
pkill -f "uvicorn.*engine1" || true
pkill -f "uvicorn.*engine2" || true
pkill -f "uvicorn.*engine3" || true
pkill -f "uvicorn.*engine4" || true
pkill -f "uvicorn.*engine5" || true
pkill -f "uvicorn.*engine6" || true
pkill -f "uvicorn.*engine7" || true
sleep 2
echo ""

# Function to start an engine
start_engine() {
    local engine_num=$1
    local engine_name=$2
    local port=$3
    local app_path=$4

    echo "🚀 Starting Engine $engine_num ($engine_name) on port $port..."

    cd "$BASE_DIR/engines/engine$engine_num-$engine_name"

    # Activate virtual environment if it exists, otherwise use system Python
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Start uvicorn in background using python3 -m
    PYTHONPATH="$BASE_DIR/engines:$PYTHONPATH" \
    python3 -m uvicorn "$app_path:app" \
        --host 0.0.0.0 \
        --port "$port" \
        --log-level info \
        > "$LOGS_DIR/engine$engine_num.log" 2>&1 &

    local pid=$!
    echo "  ✅ Engine $engine_num started (PID: $pid) - http://localhost:$port"
    echo "     Logs: $LOGS_DIR/engine$engine_num.log"

    cd "$BASE_DIR"
}

# Start all engines
echo "🔧 Starting engines..."
echo ""

start_engine "1" "log-collector" "8001" "app.main"
sleep 2

start_engine "2" "document-processor" "8002" "app.main"
sleep 2

start_engine "3" "xgboost-classifier" "8003" "app.main"
sleep 2

start_engine "4" "decision-engine" "8004" "app.main"
sleep 2

start_engine "5" "report-generator" "8005" "app.main"
sleep 2

start_engine "6" "web-ui" "8006" "backend.api"
sleep 2

start_engine "7" "auth-engine" "8007" "app.main"
sleep 2

echo ""
echo "⏳ Waiting for engines to initialize (10 seconds)..."
sleep 10

# Health checks
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏥 Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_health() {
    local engine_num=$1
    local port=$2
    local name=$3

    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "  ✅ Engine $engine_num ($name): http://localhost:$port"
    else
        echo "  ❌ Engine $engine_num ($name): NOT RESPONDING on port $port"
    fi
}

check_health "1" "8001" "Log Collector"
check_health "2" "8002" "Document Processor"
check_health "3" "8003" "XGBoost Classifier"
check_health "4" "8004" "Decision Engine"
check_health "5" "8005" "Report Generator"
check_health "6" "8006" "Web UI"
check_health "7" "8007" "Auth Engine"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All engines started in LOCAL mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Engine URLs:"
echo "   Engine 1 (Log Collector):      http://localhost:8001"
echo "   Engine 2 (Document Processor): http://localhost:8002"
echo "   Engine 3 (XGBoost Classifier): http://localhost:8003"
echo "   Engine 4 (Decision Engine):    http://localhost:8004"
echo "   Engine 5 (Report Generator):   http://localhost:8005"
echo "   Engine 6 (Web UI):             http://localhost:8006"
echo "   Engine 7 (Auth Engine):        http://localhost:8007"
echo ""
echo "📝 Logs: $LOGS_DIR/"
echo ""
echo "🛑 To stop all engines: pkill -f uvicorn"
echo "📋 To view logs: tail -f $LOGS_DIR/engine*.log"
echo ""
