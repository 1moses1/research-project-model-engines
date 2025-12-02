#!/bin/bash
# Rwanda NCSA Compliance Auditor - Local Development Setup
# Run engines locally while using Docker for PostgreSQL + Redis

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "Rwanda NCSA Compliance Auditor"
echo "Local Development Setup"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not installed.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Create Python virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi
echo -e "${GREEN}✅ Virtual environment ready${NC}"

# Activate venv
source venv/bin/activate

# Install dependencies
echo ""
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --quiet --upgrade pip

# Core dependencies
pip install --quiet fastapi uvicorn redis asyncpg httpx python-dotenv pydantic pydantic-settings aiofiles python-multipart

# Engine-specific dependencies
pip install --quiet websockets python-dateutil  # Engine 1
pip install --quiet PyPDF2 python-docx openpyxl numpy  # Engine 2
pip install --quiet xgboost scikit-learn pandas  # Engine 3
pip install --quiet openai  # LLM integration
pip install --quiet reportlab matplotlib  # Engine 5
pip install --quiet PyJWT "passlib[bcrypt]" cryptography  # Engine 7
pip install --quiet python-socketio  # Engine 6

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Ensure Docker infrastructure is running
echo ""
echo "========================================"
echo "Checking Docker Infrastructure"
echo "========================================"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Start PostgreSQL if not running
if docker ps | grep -q "rwanda-ncsa-postgres"; then
    echo -e "${GREEN}✅ PostgreSQL already running (localhost:5432)${NC}"
else
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    docker compose up -d postgres
    sleep 3
fi

# Start Redis if not running
if docker ps | grep -q "rwanda-ncsa-redis"; then
    echo -e "${GREEN}✅ Redis already running (localhost:6379)${NC}"
else
    echo -e "${YELLOW}Starting Redis...${NC}"
    docker compose up -d redis
    sleep 2
fi

# Test connections using Python (no need for CLI tools!)
echo ""
echo "========================================"
echo "Verifying Connections"
echo "========================================"

# Test PostgreSQL connection
python3 -c "
import asyncio
import asyncpg

async def test_pg():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='rwanda_admin',
            password='rwanda_secure_2024',
            database='rwanda_ncsa'
        )
        await conn.execute('SELECT 1')
        await conn.close()
        print('✅ PostgreSQL connected (localhost:5432)')
        return True
    except Exception as e:
        print(f'❌ PostgreSQL connection failed: {e}')
        return False

asyncio.run(test_pg())
" 2>/dev/null || echo -e "${RED}❌ PostgreSQL connection failed${NC}"

# Test Redis connection
python3 -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379)
    r.ping()
    print('✅ Redis connected (localhost:6379)')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
" 2>/dev/null || echo -e "${RED}❌ Redis connection failed${NC}"

echo ""
echo "========================================"
echo -e "${GREEN}Local Development Environment Ready!${NC}"
echo "========================================"
echo ""
echo -e "${BLUE}Environment variables to set in each terminal:${NC}"
echo ""
echo "  export REDIS_HOST=localhost"
echo "  export REDIS_PORT=6379"
echo "  export POSTGRES_URL=postgresql://rwanda_admin:rwanda_secure_2024@localhost:5432/rwanda_ncsa"
echo "  export OPENAI_API_KEY=your-key-here  # Optional for LLM features"
echo ""
echo -e "${BLUE}Quick start (copy-paste this):${NC}"
echo ""
cat << 'EOF'
# Activate virtual environment first
source venv/bin/activate

# Set environment variables
export REDIS_HOST=localhost
export REDIS_PORT=6379
export POSTGRES_URL=postgresql://rwanda_admin:rwanda_secure_2024@localhost:5432/rwanda_ncsa
EOF
echo ""
echo -e "${BLUE}To start individual engines:${NC}"
echo ""
echo "  # Engine 7 (Auth) - Start first"
echo "  cd engines/engine7-auth-engine && python -m uvicorn app.main:app --port 8007 --reload"
echo ""
echo "  # Engine 3 (XGBoost Classifier)"
echo "  cd engines/engine3-xgboost-classifier && python -m uvicorn app.main:app --port 8003 --reload"
echo ""
echo "  # Engine 4 (Decision Engine)"
echo "  cd engines/engine4-decision-engine && python -m uvicorn app.main:app --port 8004 --reload"
echo ""
echo "  # Engine 1 (Log Collector)"
echo "  cd engines/engine1-log-collector && python -m uvicorn app.main:app --port 8001 --reload"
echo ""
echo "  # Engine 2 (Document Processor)"
echo "  cd engines/engine2-document-processor && python -m uvicorn app.main:app --port 8002 --reload"
echo ""
echo "  # Engine 5 (Report Generator)"
echo "  cd engines/engine5-report-generator && python -m uvicorn app.main:app --port 8005 --reload"
echo ""
echo "  # Engine 6 (Web UI)"
echo "  cd engines/engine6-web-ui/backend && python -m uvicorn api:socket_app --port 8006 --reload"
echo ""
echo -e "${GREEN}Access the dashboard at: http://localhost:8006${NC}"
echo ""
