# Buildroot 2009.05 Docker Environment

Docker image with Buildroot 2009.05 and a pre-built MIPS cross-compilation toolchain (gcc 4.3.3).

## Features

- Buildroot 2009.05 from official GitLab repository
- MIPS cross-compiler: `mips-linux-uclibc-gcc-4.3.3`
- uClibc 0.9.30.1 C library
- Based on Debian 7 (wheezy) for legacy compatibility

## Quick Start

### Build the Docker image

```bash
docker build -t buildroot-2009.05 .
```

### Compile source files

Use the provided build script:

```bash
./build.sh
```

Or manually:

```bash
docker run --rm -v $(pwd)/src:/src buildroot-2009.05 \
  mips-linux-uclibc-gcc-4.3.3 /src/rootserver.c -o /src/rootserver
```

### Interactive shell

```bash
docker run -it --rm -v $(pwd)/src:/src buildroot-2009.05
```

Inside the container:

```bash
mips-linux-uclibc-gcc-4.3.3 /src/rootserver.c -o /src/rootserver
```

## Toolchain Details

| Component | Version |
|-----------|---------|
| GCC | 4.3.3 |
| uClibc | 0.9.30.1 |
| Binutils | 2.19.1 |
| Linux Headers | 2.6.29.4 |
| Target Architecture | MIPS (big-endian) |

### Toolchain location

```
/buildroot/buildroot/build_mips/staging_dir/usr/bin/mips-linux-uclibc-gcc-4.3.3
```

The toolchain is automatically added to PATH in the container.

## Directory Structure

```
.
├── Dockerfile          # Docker build configuration
├── README.md           # This file
├── build.sh            # Build script for src/rootserver.c
└── src/
    └── rootserver.c    # Source file to compile
```

## Patches Applied

The following patches are automatically applied during the Docker build:

1. **uClibc getline fix**: Renames `getline` function in `unifdef.c` to avoid conflict with glibc
2. **xboard.mk fix**: Corrects syntax error (missing `=`)
3. **atk.mk fix**: Adds missing backslash continuation

## Troubleshooting

### SSL/TLS errors during build

The Docker image uses Debian 7 which has outdated SSL certificates. Source files are pre-downloaded using `curl -k` to bypass certificate verification.

### fakeroot download error

The build may show an error downloading `fakeroot_1.9.5.tar.gz`. This is expected and does not affect the toolchain - the cross-compiler will still be fully functional.

## License

Buildroot is licensed under the GPL-2.0. See the [Buildroot website](https://buildroot.org/) for more information.
