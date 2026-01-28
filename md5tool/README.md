# TP-Link Firmware MD5 Calculator

Docker-based tool for verifying and displaying MD5 checksums of TP-Link firmware images (MR3020 and compatible devices).

## Features

- Verify TP-Link firmware header MD5 checksums
- Display firmware metadata (hardware ID, version, offsets)
- Supports V1/V2 TP-Link firmware headers

## Requirements

- Docker

## Quick Start

```bash
cd md5tool

# Check firmware MD5 (builds Docker image on first run)
./md5calc.sh /path/to/firmware.bin

# Show full firmware details
./md5calc.sh /path/to/firmware.bin -v
```

## Usage

```
Usage: ./md5calc.sh <firmware.bin> [options]

Options:
  -v, --verbose    Show full firmware details
  -h, --help       Show this help

Examples:
  ./md5calc.sh firmware.bin           # Check MD5 checksum
  ./md5calc.sh firmware.bin -v        # Show full details
```

## Example Output

```
Analyzing: original.bin

File name              : original.bin
File size              : 0x003e0200 /  4063744 bytes
Header MD5Sum1         : 22 7d 93 97 42 73 fa 95 79 b4 a8 65 a7 71 dd 6b (ok)
Hardware ID            : 0x30200001
Firmware version       : ver. 1.0
```

## Supported Devices

- TP-Link TL-MR3020 v1
- Other TP-Link devices using V1/V2 firmware headers

## License

Uses mktplinkfw from OpenWrt firmware-utils (GPL-2.0).
