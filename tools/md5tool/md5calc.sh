#!/bin/bash
#
# TP-Link MR3020 Firmware MD5 Calculator
# Uses mktplinkfw to verify/display firmware checksums
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="tplink-md5tool"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}#################################${NC}"
echo -e "${YELLOW}# TP-Link Firmware MD5 Calculator #${NC}"
echo -e "${YELLOW}#################################${NC}"

# Show help
show_help() {
    echo "Usage: $0 <firmware.bin> [options]"
    echo ""
    echo "Options:"
    echo "  -v, --verbose    Show full firmware details"
    echo "  -h, --help       Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 firmware.bin           # Check MD5 checksum"
    echo "  $0 firmware.bin -v        # Show full details"
}

# Check if Docker image exists, build if not
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo -e "${YELLOW}Docker image '$IMAGE_NAME' not found. Building...${NC}"
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
fi

# Parse arguments
VERBOSE=false
FIRMWARE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [ -z "$FIRMWARE" ]; then
                FIRMWARE="$1"
            else
                echo -e "${RED}Error: Unknown argument: $1${NC}"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Check for firmware file
if [ -z "$FIRMWARE" ]; then
    show_help
    exit 0
fi

if [ ! -f "$FIRMWARE" ]; then
    echo -e "${RED}Error: Firmware file not found: $FIRMWARE${NC}"
    exit 1
fi

# Get absolute path
FIRMWARE_PATH="$(cd "$(dirname "$FIRMWARE")" && pwd)/$(basename "$FIRMWARE")"
FIRMWARE_DIR="$(dirname "$FIRMWARE_PATH")"
FIRMWARE_NAME="$(basename "$FIRMWARE_PATH")"

echo ""
echo -e "${GREEN}Analyzing: $FIRMWARE_NAME${NC}"
echo ""

# Run mktplinkfw
if [ "$VERBOSE" = true ]; then
    docker run --rm -v "$FIRMWARE_DIR:/work" "$IMAGE_NAME" \
        mktplinkfw -i "/work/$FIRMWARE_NAME" 2>&1
else
    docker run --rm -v "$FIRMWARE_DIR:/work" "$IMAGE_NAME" \
        mktplinkfw -i "/work/$FIRMWARE_NAME" 2>&1 | grep -E "(File name|File size|MD5Sum|Hardware ID|Firmware version|valid|error)" || true
fi

echo ""
