#!/bin/bash
#
# Build script for rootserver.c using Buildroot 2009.05 MIPS toolchain
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="buildroot-2009.05"
SOURCE_FILE="rootserver.c"
OUTPUT_FILE="rootserver"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Buildroot 2009.05 MIPS Build ===${NC}"

# Check if Docker image exists
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo -e "${YELLOW}Docker image '$IMAGE_NAME' not found. Building...${NC}"
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
fi

# Check if source file exists
if [ ! -f "$SCRIPT_DIR/src/$SOURCE_FILE" ]; then
    echo -e "${RED}Error: $SCRIPT_DIR/src/$SOURCE_FILE not found${NC}"
    exit 1
fi

echo -e "${GREEN}Compiling $SOURCE_FILE...${NC}"

# Run the compiler in Docker
docker run --rm \
    -v "$SCRIPT_DIR/src:/src" \
    "$IMAGE_NAME" \
    mips-linux-uclibc-gcc-4.3.3 "/src/$SOURCE_FILE" -o "/src/$OUTPUT_FILE"

# Verify output
if [ -f "$SCRIPT_DIR/src/$OUTPUT_FILE" ]; then
    echo -e "${GREEN}Build successful!${NC}"
    echo ""
    echo "Output file:"
    ls -la "$SCRIPT_DIR/src/$OUTPUT_FILE"
    echo ""
    echo "File type:"
    file "$SCRIPT_DIR/src/$OUTPUT_FILE"
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
