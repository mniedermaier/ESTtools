#!/bin/bash
#
# Embedded Security Testing - CLI Launcher
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

IMAGE_NAME="est-cli"
CONTAINER_NAME="est-cli"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Create directories
mkdir -p "$SCRIPT_DIR/samples"
mkdir -p "$SCRIPT_DIR/extracted"
mkdir -p "$SCRIPT_DIR/build"
mkdir -p "$SCRIPT_DIR/buildroot/src"
mkdir -p "$SCRIPT_DIR/reports"

show_help() {
    echo "Embedded Security Testing - CLI Tool"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  (default)  Launch interactive TUI"
    echo "  build      Build/rebuild the Docker image"
    echo "  shell      Open a shell in the container"
    echo "  clean      Remove Docker image"
    echo "  help       Show this help"
    echo ""
}

build_image() {
    echo -e "${YELLOW}Building EST CLI image...${NC}"
    echo "This may take several minutes on first run (building MIPS toolchain)..."
    echo ""
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR/cli"
    echo ""
    echo -e "${GREEN}Build complete!${NC}"
}

run_cli() {
    # Check if image exists
    if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
        echo -e "${YELLOW}Docker image not found. Building...${NC}"
        echo ""
        build_image
    fi

    # Run interactive CLI
    docker run -it --rm \
        --name "$CONTAINER_NAME" \
        -v "$SCRIPT_DIR/samples:/work/samples" \
        -v "$SCRIPT_DIR/extracted:/work/extracted" \
        -v "$SCRIPT_DIR/build:/work/build" \
        -v "$SCRIPT_DIR/buildroot/src:/work/buildroot/src" \
        -v "$SCRIPT_DIR/reports:/work/reports" \
        "$IMAGE_NAME"
}

run_shell() {
    # Check if image exists
    if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
        echo -e "${YELLOW}Docker image not found. Building...${NC}"
        echo ""
        build_image
    fi

    docker run -it --rm \
        --name "$CONTAINER_NAME" \
        -v "$SCRIPT_DIR/samples:/work/samples" \
        -v "$SCRIPT_DIR/extracted:/work/extracted" \
        -v "$SCRIPT_DIR/build:/work/build" \
        -v "$SCRIPT_DIR/buildroot/src:/work/buildroot/src" \
        -v "$SCRIPT_DIR/reports:/work/reports" \
        --entrypoint /bin/bash \
        "$IMAGE_NAME"
}

clean_image() {
    echo -e "${YELLOW}Removing EST CLI image...${NC}"
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    echo -e "${GREEN}Cleaned.${NC}"
}

# Parse command
case "${1:-run}" in
    run|"")
        run_cli
        ;;
    build)
        build_image
        ;;
    shell)
        run_shell
        ;;
    clean)
        clean_image
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
