#!/bin/bash

echo "=========================================="
echo "ENGINE 6: Web Dashboard Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}[1/5]${NC} Setting up backend..."
cd backend

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating backend .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Backend .env created (update with your API keys)"
fi

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✓${NC} Backend setup complete"

echo ""
echo -e "${BLUE}[2/5]${NC} Setting up frontend..."
cd ../frontend

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating frontend .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Frontend .env created"
fi

# Install Node dependencies
echo -e "${BLUE}Installing Node.js dependencies...${NC}"
npm install

# Install additional required packages
echo -e "${BLUE}Installing additional dependencies...${NC}"
npm install tailwindcss-animate

echo -e "${GREEN}✓${NC} Frontend setup complete"

echo ""
echo -e "${BLUE}[3/5]${NC} Verifying project structure..."
cd ../..

# Check if required files exist
FILES=(
    "engines/web_ui/backend/api.py"
    "engines/web_ui/backend/requirements.txt"
    "engines/web_ui/backend/Dockerfile"
    "engines/web_ui/frontend/package.json"
    "engines/web_ui/frontend/src/App.tsx"
    "engines/web_ui/frontend/src/components/DocumentUpload.tsx"
    "engines/web_ui/frontend/src/components/SystemHealthMonitor.tsx"
    "engines/web_ui/frontend/src/components/ArchitectureDiagram.tsx"
    "engines/web_ui/frontend/Dockerfile"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${YELLOW}✗${NC} $file (missing)"
    fi
done

echo ""
echo -e "${BLUE}[4/5]${NC} Creating uploads directory..."
mkdir -p engines/web_ui/backend/uploads
echo -e "${GREEN}✓${NC} Uploads directory created"

echo ""
echo -e "${BLUE}[5/5]${NC} Setup complete!"
echo ""
echo "=========================================="
echo -e "${GREEN}ENGINE 6 is ready!${NC}"
echo "=========================================="
echo ""
echo "To start development:"
echo ""
echo "  ${YELLOW}Backend:${NC}"
echo "    cd engines/web_ui/backend"
echo "    uvicorn api:socket_app --reload --port 8006"
echo ""
echo "  ${YELLOW}Frontend:${NC}"
echo "    cd engines/web_ui/frontend"
echo "    npm start"
echo ""
echo "  ${YELLOW}Access:${NC}"
echo "    http://localhost:3000"
echo ""
echo "To start with Docker:"
echo ""
echo "    docker-compose up -d web-ui-backend web-ui-frontend"
echo ""
echo "=========================================="
