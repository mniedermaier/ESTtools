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

**Note:** First run takes several minutes to download the MIPS cross-toolchain and Ghidra.

## CLI Features

The interactive terminal interface provides:

```
1) Analyze Firmware         - File info, MD5, binwalk scan, TP-Link header check
2) Extract Firmware         - Extract filesystem using binwalk
3) Browse Files             - Navigate extracted filesystem in terminal
4) Cross-Compile (MIPS)     - Compile C code for MIPS using uClibc toolchain
5) Rebuild Firmware         - Create modified firmware images
6) Reverse Engineer Binary  - Disassembly, Ghidra analysis, vulnerability scanning
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
└── buildroot/
    └── src/           # Place C source files here for cross-compilation
```

## Workflow Example

1. Place a firmware file in `tools/samples/`
2. Run `./start.sh`
3. Select **1) Analyze Firmware** to inspect the file
4. Select **2) Extract Firmware** to extract the filesystem
5. Select **3) Browse Files** to explore extracted contents
6. Select **6) Reverse Engineer Binary** to analyze binaries (e.g., `httpd`)
7. Modify files as needed
8. Select **5) Rebuild Firmware** to create a new image

## Cross-Compilation

To compile C code for MIPS:

1. Place your `.c` files in `tools/buildroot/src/`
2. Run `./start.sh`
3. Select **4) Cross-Compile (MIPS)**
4. Select the file to compile
5. Binary output appears in `tools/buildroot/src/`

## Reverse Engineering

The reverse engineering module provides three analysis tools for MIPS ELF binaries extracted from firmware:

### Objdump Disassembly

Disassemble binaries using the MIPS cross-toolchain's objdump. Available modes:

- **Disassembly (`-d`)** - Full instruction-level disassembly
- **Symbol table (`-t`)** - List all symbols (functions, variables)
- **All headers (`-x`)** - ELF headers, sections, relocations
- **Dynamic symbols (`-T`)** - Imported/exported shared library symbols

### Ghidra Headless Analysis

Runs [Ghidra](https://ghidra-sre.org/) in headless mode for automated binary analysis. This imports the binary into a Ghidra project, performs auto-analysis (function detection, cross-references, data type propagation), and reports results. The Ghidra project is saved to `ghidra_projects/` for later inspection.

### Vulnerability Pattern Search

Automated scan for common vulnerability indicators:

- **Dangerous functions** - Imported calls to `system`, `popen`, `execve`, `sprintf`, `strcpy`, `strcat`, `gets` (buffer overflows, command injection)
- **Hardcoded credentials** - Strings containing `password`, `admin`, `secret`, `backdoor`, etc.
- **Command execution patterns** - References to `/bin/sh`, `exec`, `cmd=`, shell commands
- **Network/CGI attack surface** - CGI endpoints, `ping`, `traceroute`, `userRpm` handlers

### Workflow Example

1. Extract firmware with **2) Extract Firmware**
2. Select **6) Reverse Engineer Binary**
3. Choose an analysis mode (e.g., **3) Vulnerability Pattern Search**)
4. Select a MIPS ELF binary from the extracted filesystem (e.g., `httpd`)
5. Review the results

## Requirements

- Docker
- Linux environment (tested on Ubuntu)

## Educational Topics Covered

- Firmware structure and analysis
- Filesystem formats (SquashFS)
- Cross-compilation for embedded architectures (MIPS big-endian, uClibc)
- Checksum verification mechanisms
- Firmware modification and rebuilding
- Binary reverse engineering and disassembly (objdump, Ghidra)
- Vulnerability pattern analysis

## License

Educational use only. Third-party tools (mktplinkfw, binwalk, sasquatch) retain their original licenses (GPL-2.0).
