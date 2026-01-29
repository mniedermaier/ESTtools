# ESTtools - Embedded Systems Teaching Tools

Educational toolkit for learning about embedded systems, firmware analysis, and cross-compilation.

## Disclaimer

**This repository is intended solely for educational purposes in academic/lecture settings.**

- All materials and tools are provided for learning about embedded systems security concepts
- The selection of TP-Link devices as examples is arbitrary and does not imply any specific vulnerability, endorsement, or criticism of TP-Link products
- Do not use these tools on devices you do not own or without proper authorization
- The authors assume no responsibility for misuse of these materials

## Quick Start - Web Lab

The easiest way to use this toolkit is through the web-based lab environment:

```bash
cd tools

# Start the lab
./start.sh

# Access the web interface at http://localhost:8080

# Stop the lab
./start.sh stop
```

### Lab Commands

```bash
cd tools
./start.sh start    # Start the lab (default)
./start.sh stop     # Stop the lab
./start.sh restart  # Restart the lab
./start.sh status   # Show lab status
./start.sh logs     # View container logs
./start.sh build    # Rebuild the container
./start.sh shell    # Open shell in container
./start.sh clean    # Remove all lab data
```

### Web Lab Features

The web interface provides:
- **File Info** - Basic file analysis with binwalk signature scan
- **MD5 Check** - TP-Link firmware header verification
- **Hex Dump** - View firmware header bytes
- **String Extraction** - Find readable strings in firmware
- **Filesystem Extraction** - Extract embedded filesystems

## Contents

### tools/lab/
Web-based lab environment with Docker container including all analysis tools (binwalk, mktplinkfw, sasquatch, etc.).

### tools/buildroot/
Docker-based MIPS cross-compilation environment using Buildroot 2009.05. Demonstrates how to set up a toolchain for compiling code targeting embedded Linux devices.

### tools/imageManipulation/
Tools for extracting and rebuilding firmware images. Teaches the structure of embedded firmware including:
- Firmware headers and checksums
- SquashFS filesystem extraction
- Kernel and rootfs layout

### tools/md5tool/
Utility for analyzing firmware header checksums. Demonstrates how embedded devices verify firmware integrity.

## Requirements

- Docker
- Docker Compose
- Linux environment (tested on Ubuntu)

## Educational Topics Covered

- Cross-compilation for embedded architectures (MIPS)
- Firmware structure and analysis
- Filesystem formats (SquashFS)
- Checksum verification mechanisms
- Docker-based reproducible build environments
- Web-based security analysis workflows

## License

Educational use only. Third-party tools (mktplinkfw, firmware-mod-kit, binwalk) retain their original licenses (GPL-2.0).
