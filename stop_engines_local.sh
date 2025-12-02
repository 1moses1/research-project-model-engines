#!/bin/bash
# Stop all local engines (not Redis/Postgres)

echo "🛑 Stopping all local engines..."
echo ""

# Kill all uvicorn processes for our engines
pkill -9 -f "uvicorn.*app.main:app.*800[1-7]" 2>/dev/null && echo "  ✅ Stopped engines 1, 3, 4, 5, 7"
pkill -9 -f "uvicorn.*backend.api:app.*8006" 2>/dev/null && echo "  ✅ Stopped engine 6 (Web UI)"

sleep 1

# Check if any are still running
RUNNING=$(ps aux | grep -E "uvicorn.*(app.main|backend.api)" | grep -v grep | wc -l | tr -d ' ')

if [ "$RUNNING" -eq 0 ]; then
    echo ""
    echo "✅ All engines stopped successfully"
else
    echo ""
    echo "⚠️  Warning: $RUNNING engine process(es) still running"
    echo "   Use: ps aux | grep uvicorn"
fi

echo ""
echo "ℹ️  Redis and Postgres containers are still running"
echo "   To stop them: docker-compose -f docker-compose.infra.yml down"
echo ""
