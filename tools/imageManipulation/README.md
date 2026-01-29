# TP-Link MR3020v1 Firmware Image Manipulation

Docker environment for extracting, modifying, and rebuilding TP-Link MR3020v1 firmware images.

## Features

- Extract squashfs filesystem from original firmware
- Modify filesystem contents
- Rebuild firmware with correct TP-Link checksums
- Based on firmware-mod-kit and OpenWrt mktplinkfw

## Requirements

- Docker
- Original TP-Link MR3020v1 firmware (`original.bin`)

## Quick Start

### 1. Build the Docker image

```bash
./build.sh shell   # First run will build the image
exit
```

Or explicitly:

```bash
docker build -t tplink-firmware-tools .
```

### 2. Extract the firmware

```bash
./build.sh extract
```

This creates `squashfs-root/` with the extracted filesystem.

### 3. Modify the filesystem

Edit files in `squashfs-root/` as needed:

```bash
ls squashfs-root/
# bin  dev  etc  lib  mnt  overlay  proc  rom  root  sbin  sys  tmp  usr  var  www
```

### 4. Build the new firmware

```bash
./build.sh build
```

Output: `newimage.bin`

## Commands

| Command | Description |
|---------|-------------|
| `./build.sh extract` | Extract original firmware to `squashfs-root/` |
| `./build.sh build` | Build new firmware from `squashfs-root/` |
| `./build.sh shell` | Start interactive Docker shell |
| `./build.sh clean` | Remove build artifacts |

## Directory Structure

```
imageManipulation/
├── Dockerfile          # Docker build configuration
├── README.md           # This file
├── build.sh            # Build script
├── original.bin        # Original TP-Link firmware
├── squashfs-root/      # Extracted filesystem (after extract)
└── newimage.bin        # Built firmware (after build)
```

## Technical Details

### Firmware Structure

The MR3020v1 firmware consists of:
- **Header** (0x00 - 0x120000): TP-Link header with checksums
- **Kernel** (0x200 - ~0x100000): Linux kernel
- **SquashFS** (0x120000 - end): Root filesystem

### Tools Used

- **firmware-mod-kit**: Squashfs extraction/creation with LZMA support
- **mktplinkfw**: TP-Link firmware checksum calculation (from OpenWrt)

### Checksum Process

1. Extract header from original firmware
2. Create new squashfs from modified filesystem
3. Concatenate header + new squashfs
4. Calculate correct MD5 checksum
5. Patch checksum in firmware header

## Flashing

**Warning**: Flashing modified firmware can brick your device!

To flash via web interface:
1. Access router at http://192.168.0.254 (default)
2. Go to System Tools > Firmware Upgrade
3. Select `newimage.bin`
4. Click Upgrade

To flash via TFTP (recovery):
1. Set PC IP to 192.168.0.66
2. Start TFTP server with `newimage.bin` as `mr3020v1_tp_recovery.bin`
3. Power on router while holding reset button

## License

firmware-mod-kit and mktplinkfw are GPL-licensed tools.
