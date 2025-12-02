#!/bin/bash
# Rwanda NCSA Compliance Auditor - Infrastructure Startup Script
# Starts PostgreSQL and Redis with persistent storage
#
# Usage:
#   ./scripts/start-infra.sh         # Start services
#   ./scripts/start-infra.sh status  # Check status
#   ./scripts/start-infra.sh stop    # Stop services
#   ./scripts/start-infra.sh logs    # View logs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.infra.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Rwanda NCSA - Infrastructure Manager${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running!${NC}"
        echo "Please start Docker Desktop and try again."
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is running${NC}"
}

# Start services
start_services() {
    echo -e "\n${YELLOW}Starting PostgreSQL and Redis...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d

    echo -e "\n${YELLOW}Waiting for services to be healthy...${NC}"
    sleep 5

    # Check PostgreSQL
    if docker exec rwanda-ncsa-postgres pg_isready -U rwanda_admin -d rwanda_ncsa > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready (127.0.0.1:5432)${NC}"
    else
        echo -e "${RED}✗ PostgreSQL is not ready${NC}"
    fi

    # Check Redis
    if docker exec rwanda-ncsa-redis redis-cli ping | grep -q PONG; then
        echo -e "${GREEN}✓ Redis is ready (127.0.0.1:6379)${NC}"
    else
        echo -e "${RED}✗ Redis is not ready${NC}"
    fi

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Infrastructure is ready!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "PostgreSQL: ${YELLOW}127.0.0.1:5432${NC}"
    echo -e "  Database: rwanda_ncsa"
    echo -e "  User: rwanda_admin"
    echo -e "  Password: rwanda_secure_2024"
    echo -e ""
    echo -e "Redis: ${YELLOW}127.0.0.1:6379${NC}"
    echo -e ""
    echo -e "Connect to PostgreSQL:"
    echo -e "  ${YELLOW}psql -h 127.0.0.1 -U rwanda_admin -d rwanda_ncsa${NC}"
    echo -e ""
    echo -e "Connect to Redis:"
    echo -e "  ${YELLOW}redis-cli -h 127.0.0.1${NC}"
}

# Stop services
stop_services() {
    echo -e "\n${YELLOW}Stopping PostgreSQL and Redis...${NC}"
    docker-compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✓ Services stopped (data is preserved)${NC}"
}

# Show status
show_status() {
    echo -e "\n${YELLOW}Service Status:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps

    echo -e "\n${YELLOW}Connection Test:${NC}"

    # Test PostgreSQL
    if nc -z 127.0.0.1 5432 2>/dev/null; then
        echo -e "${GREEN}✓ PostgreSQL port 5432 is accessible${NC}"
    else
        echo -e "${RED}✗ PostgreSQL port 5432 is not accessible${NC}"
    fi

    # Test Redis
    if nc -z 127.0.0.1 6379 2>/dev/null; then
        echo -e "${GREEN}✓ Redis port 6379 is accessible${NC}"
    else
        echo -e "${RED}✗ Redis port 6379 is not accessible${NC}"
    fi

    echo -e "\n${YELLOW}Volume Info:${NC}"
    docker volume ls | grep rwanda || echo "No Rwanda volumes found"
}

# Show logs
show_logs() {
    echo -e "\n${YELLOW}Following logs (Ctrl+C to exit)...${NC}"
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Main
check_docker

case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    restart)
        stop_services
        start_services
        ;;
    *)
        echo "Usage: $0 {start|stop|status|logs|restart}"
        exit 1
        ;;
esac
