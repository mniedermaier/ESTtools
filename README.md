# ESTtools - Embedded Systems Teaching Tools

Educational toolkit for learning about embedded systems, firmware analysis, and cross-compilation.

## Disclaimer

**This repository is intended solely for educational purposes in academic/lecture settings.**

- All materials and tools are provided for learning about embedded systems security concepts
- The selection of TP-Link devices as examples is arbitrary and does not imply any specific vulnerability, endorsement, or criticism of TP-Link products
- Do not use these tools on devices you do not own or without proper authorization
- The authors assume no responsibility for misuse of these materials

## Quick Start

```bash
cd tools

# Launch the interactive CLI (builds Docker image on first run)
./start.sh

# Or build the image first
./start.sh build
```

**Note:** First run takes several minutes to build the MIPS cross-compilation toolchain.

## CLI Features

The interactive terminal interface provides:

```
1) Analyze Firmware    - File info, MD5, binwalk scan, TP-Link header check
2) Extract Firmware    - Extract filesystem using binwalk
3) Browse Files        - Navigate extracted filesystem in terminal
4) Cross-Compile       - Compile C code for MIPS using buildroot toolchain
5) Rebuild Firmware    - Create modified firmware images
```

### Commands

```bash
./start.sh           # Launch interactive TUI
./start.sh build     # Build/rebuild Docker image
./start.sh shell     # Open shell in container
./start.sh clean     # Remove Docker image
./start.sh help      # Show help
```

## Directory Structure

```
tools/
├── start.sh           # CLI launcher
├── cli/               # CLI tool and Dockerfile
├── samples/           # Place firmware files here
├── extracted/         # Extracted firmware output
├── build/             # Built firmware output
├── buildroot/
│   └── src/           # Place C source files here for cross-compilation
├── imageManipulation/ # Firmware manipulation scripts
└── md5tool/           # MD5 verification tool
```

## Workflow Example

1. Place a firmware file in `tools/samples/`
2. Run `./start.sh`
3. Select **1) Analyze Firmware** to inspect the file
4. Select **2) Extract Firmware** to extract the filesystem
5. Select **3) Browse Files** to explore extracted contents
6. Modify files as needed
7. Select **5) Rebuild Firmware** to create a new image

## Cross-Compilation

To compile C code for MIPS:

1. Place your `.c` files in `tools/buildroot/src/`
2. Run `./start.sh`
3. Select **4) Cross-Compile (MIPS)**
4. Select the file to compile
5. Binary output appears in `tools/buildroot/src/`

## Requirements

- Docker
- Linux environment (tested on Ubuntu)

## Educational Topics Covered

- Firmware structure and analysis
- Filesystem formats (SquashFS)
- Cross-compilation for embedded architectures (MIPS)
- Checksum verification mechanisms
- Firmware modification and rebuilding

## License

Educational use only. Third-party tools (mktplinkfw, binwalk, sasquatch) retain their original licenses (GPL-2.0).
