#!/bin/bash
#
# Embedded Security Testing Lab - Startup Script
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "=============================================="
echo "   Embedded Security Testing Lab"
echo "   Educational Environment"
echo "=============================================="
echo -e "${NC}"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Determine compose command
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Create samples directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/samples"

show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    Start the lab (default)"
    echo "  stop     Stop the lab"
    echo "  restart  Restart the lab"
    echo "  status   Show lab status"
    echo "  logs     Show lab logs"
    echo "  build    Rebuild the lab container"
    echo "  shell    Open a shell in the lab container"
    echo "  clean    Stop and remove all lab data"
    echo ""
}

start_lab() {
    echo -e "${YELLOW}Building and starting the lab...${NC}"
    $COMPOSE_CMD up -d --build

    echo ""
    echo -e "${GREEN}Lab started successfully!${NC}"
    echo ""
    echo -e "Access the lab at: ${BLUE}http://localhost:8080${NC}"
    echo ""
    echo -e "${YELLOW}Disclaimer:${NC} This lab is for educational purposes only."
    echo ""
}

stop_lab() {
    echo -e "${YELLOW}Stopping the lab...${NC}"
    $COMPOSE_CMD down
    echo -e "${GREEN}Lab stopped.${NC}"
}

restart_lab() {
    echo -e "${YELLOW}Restarting the lab...${NC}"
    $COMPOSE_CMD restart
    echo -e "${GREEN}Lab restarted.${NC}"
}

show_status() {
    echo -e "${YELLOW}Lab status:${NC}"
    $COMPOSE_CMD ps
}

show_logs() {
    $COMPOSE_CMD logs -f
}

build_lab() {
    echo -e "${YELLOW}Rebuilding the lab container...${NC}"
    $COMPOSE_CMD build --no-cache
    echo -e "${GREEN}Build complete.${NC}"
}

open_shell() {
    echo -e "${YELLOW}Opening shell in lab container...${NC}"
    docker exec -it est-lab /bin/bash
}

clean_lab() {
    echo -e "${YELLOW}Stopping and removing lab containers...${NC}"
    $COMPOSE_CMD down -v --remove-orphans 2>/dev/null || true
    docker rm -f est-lab 2>/dev/null || true
    docker rmi est-lab:latest 2>/dev/null || true
    echo -e "${GREEN}Lab cleaned.${NC}"
}

# Parse command
case "${1:-start}" in
    start)
        start_lab
        ;;
    stop)
        stop_lab
        ;;
    restart)
        restart_lab
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    build)
        build_lab
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_lab
        ;;
    -h|--help|help)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
