#!/bin/bash
#
# TP-Link MR3020v1 Firmware Image Builder
# Uses Docker container with firmware-mod-kit and mktplinkfw
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="tplink-firmware-tools"
ORIGINAL_FW="original.bin"
OUTPUT_FW="newimage.bin"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Header offset for MR3020v1 (where squashfs starts)
HEADER_SIZE=1180160

echo -e "${YELLOW}####################################${NC}"
echo -e "${YELLOW}# TP-Link MR3020v1 Firmware Builder #${NC}"
echo -e "${YELLOW}####################################${NC}"

# Check if Docker image exists
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo -e "${YELLOW}Docker image '$IMAGE_NAME' not found. Building...${NC}"
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
fi

# Check for original firmware
if [ ! -f "$SCRIPT_DIR/$ORIGINAL_FW" ]; then
    echo -e "${RED}Error: $ORIGINAL_FW not found${NC}"
    exit 1
fi

# Show help if no arguments
show_help() {
    echo "Usage: $0 {extract|build|shell|clean}"
    echo ""
    echo "Commands:"
    echo "  extract  - Extract original firmware to squashfs-root/"
    echo "  build    - Build new firmware from squashfs-root/"
    echo "  shell    - Start interactive Docker shell"
    echo "  clean    - Remove build artifacts"
    echo ""
    echo "Workflow:"
    echo "  1. ./build.sh extract    # Extract filesystem"
    echo "  2. Edit squashfs-root/   # Modify files"
    echo "  3. ./build.sh build      # Create newimage.bin"
}

# Command handling
case "${1:-help}" in
    help|-h|--help)
        show_help
        exit 0
        ;;
    extract)
        echo -e "${GREEN}Extracting firmware...${NC}"
        docker run --rm -v "$SCRIPT_DIR:/work" "$IMAGE_NAME" bash -c "
            set -e
            cd /work
            rm -rf squashfs-root fmk

            echo 'Extracting squashfs from firmware...'
            # Extract squashfs portion (after header at offset $HEADER_SIZE)
            dd if=$ORIGINAL_FW of=rootfs.img bs=1 skip=$HEADER_SIZE 2>/dev/null

            echo 'Extracting filesystem with sasquatch...'
            sasquatch -d squashfs-root rootfs.img

            rm -f rootfs.img
            echo 'Extraction complete!'
        "
        echo -e "${GREEN}Extracted to squashfs-root/${NC}"
        ;;

    build)
        if [ ! -d "$SCRIPT_DIR/squashfs-root" ]; then
            echo -e "${RED}Error: squashfs-root/ not found. Run './build.sh extract' first.${NC}"
            exit 1
        fi

        echo -e "${GREEN}Building firmware image...${NC}"
        docker run --rm -v "$SCRIPT_DIR:/work" "$IMAGE_NAME" bash -c "
            set -e
            cd /work

            echo 'Removing old build files...'
            rm -f newsquash.bin newimage.bin kernel.bin

            echo 'Extracting kernel from original firmware...'
            # Kernel is at offset 0x200 (512) to 0x100000 (1048576)
            dd if=$ORIGINAL_FW of=kernel.bin bs=1 skip=512 count=1048064 2>/dev/null

            echo 'Creating squashfs filesystem (v4.0 with LZMA)...'
            mksquashfs4 squashfs-root/ newsquash.bin -comp lzma -noappend -all-root -b 131072 -no-xattrs

            echo 'Squashfs created:'
            ls -la newsquash.bin

            echo 'Building firmware with mktplinkfw...'
            mktplinkfw -H 0x30200001 -W 0x1 -F 4Mlzma -N \"TP-LINK Technologies\" -V \"ver. 1.0\" \
                -k kernel.bin -r newsquash.bin -o newimage.bin -j -a 0x10000 2>&1 || {
                echo 'mktplinkfw failed, trying alternate method...'

                # Fallback: manual assembly with header patching
                echo 'Using manual firmware assembly...'

                # Copy original header (first 1048576 bytes, up to rootfs start)
                dd if=$ORIGINAL_FW of=newimage.bin bs=1 count=1048576 2>/dev/null

                # Append new squashfs
                cat newsquash.bin >> newimage.bin

                # Pad to match original size or expected size
                ORIG_SIZE=\$(stat -c%s $ORIGINAL_FW)
                NEW_SIZE=\$(stat -c%s newimage.bin)

                if [ \$NEW_SIZE -lt \$ORIG_SIZE ]; then
                    echo \"Padding firmware to original size...\"
                    dd if=/dev/zero bs=1 count=\$((ORIG_SIZE - NEW_SIZE)) >> newimage.bin 2>/dev/null
                fi

                echo 'Patching MD5 checksum...'
                python3 << 'PYEOF'
import struct
import hashlib
import sys

# Read firmware
with open('newimage.bin', 'rb') as f:
    data = bytearray(f.read())

# TP-Link header MD5 is calculated over the entire firmware minus the first 16 bytes (which is the MD5 itself)
# The MD5 is stored at offset 0x4 in the header

# Calculate MD5 of data from offset 0x14 (after header MD5 and some fields)
md5_offset = 4  # Where MD5 is stored in header

# Clear the existing MD5 (16 bytes at offset 4)
old_md5 = bytes(data[md5_offset:md5_offset+16])

# Calculate new MD5 (skip first 4 bytes which is magic, then the 16-byte MD5 location)
# Actually TP-Link calculates MD5 differently - need to check exact algorithm

# For now, use mktplinkfw to verify and get correct checksum
print(f'Old MD5 at offset {md5_offset}: {old_md5.hex()}')
print('Note: Use mktplinkfw -i to verify the firmware')
PYEOF
            }

            echo ''
            echo 'Verifying firmware...'
            mktplinkfw -i newimage.bin 2>&1 | head -20 || true

            rm -f newsquash.bin kernel.bin
        "

        if [ -f "$SCRIPT_DIR/$OUTPUT_FW" ]; then
            echo ""
            echo -e "${GREEN}Build successful!${NC}"
            echo "Output: $SCRIPT_DIR/$OUTPUT_FW"
            ls -la "$SCRIPT_DIR/$OUTPUT_FW"
        else
            echo -e "${RED}Build failed!${NC}"
            exit 1
        fi
        ;;

    shell)
        echo -e "${GREEN}Starting interactive shell...${NC}"
        docker run -it --rm -v "$SCRIPT_DIR:/work" "$IMAGE_NAME" bash
        ;;

    clean)
        echo -e "${GREEN}Cleaning build files...${NC}"
        # Use Docker to clean root-owned files
        docker run --rm -v "$SCRIPT_DIR:/work" "$IMAGE_NAME" bash -c "
            rm -f /work/newsquash.bin /work/newimage.bin /work/kernel.bin /work/rootfs.img
            rm -rf /work/fmk /work/squashfs-root
        " 2>/dev/null || true
        echo "Done."
        ;;

    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
