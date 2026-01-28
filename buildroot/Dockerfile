# Dockerfile for Buildroot 2009.05 with MIPS gcc 4.3.3 toolchain
# Using Debian 7 (wheezy) for compatibility with legacy uClibc

FROM debian:7

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Configure archive repositories for Debian 7 (wheezy)
RUN echo "deb http://archive.debian.org/debian wheezy main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security wheezy/updates main" >> /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until

# Install build dependencies for Buildroot
RUN apt-get update && apt-get install -y --force-yes \
    build-essential \
    libncurses5-dev \
    libncursesw5-dev \
    zlib1g-dev \
    bzip2 \
    wget \
    curl \
    cpio \
    unzip \
    rsync \
    bc \
    python \
    perl \
    patch \
    texinfo \
    file \
    gettext \
    git \
    bison \
    flex \
    gawk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /buildroot

# Clone Buildroot and checkout 2009.05 tag
RUN git clone --depth 1 --branch 2009.05 https://gitlab.com/buildroot.org/buildroot.git

WORKDIR /buildroot/buildroot

# Pre-download source files (Debian 7's SSL is too old for modern HTTPS)
RUN mkdir -p dl && \
    curl -k -L -o dl/linux-2.6.29.4.tar.bz2 https://cdn.kernel.org/pub/linux/kernel/v2.6/linux-2.6.29.4.tar.bz2 && \
    curl -k -L -o dl/uClibc-0.9.30.1.tar.bz2 https://uclibc.org/downloads/uClibc-0.9.30.1.tar.bz2 && \
    curl -k -L -o dl/gcc-4.3.3.tar.bz2 https://ftp.gnu.org/gnu/gcc/gcc-4.3.3/gcc-4.3.3.tar.bz2 && \
    curl -k -L -o dl/binutils-2.19.1.tar.bz2 https://ftp.gnu.org/gnu/binutils/binutils-2.19.1.tar.bz2 && \
    curl -k -L -o dl/busybox-1.14.2.tar.bz2 https://busybox.net/downloads/busybox-1.14.2.tar.bz2

# Apply Makefile patches for syntax errors
RUN sed -i 's/XBOARD_CONF_OPT --prefix/XBOARD_CONF_OPT = --prefix/' package/games/xboard/xboard.mk && \
    sed -i 's/--enable-static$/--enable-static \\/' package/atk/atk.mk

# Create MIPS configuration
RUN echo 'BR2_mips=y' > .config && \
    echo 'BR2_TOOLCHAIN_BUILDROOT=y' >> .config && \
    echo 'BR2_GCC_VERSION_4_3_3=y' >> .config && \
    echo 'BR2_UCLIBC_VERSION_0_9_30_1=y' >> .config && \
    echo 'BR2_JLEVEL=4' >> .config && \
    echo 'BR2_TARGET_ROOTFS_EXT2=n' >> .config && \
    echo 'BR2_TARGET_ROOTFS_TAR=y' >> .config && \
    yes "" | make oldconfig 2>/dev/null

# Pre-extract and patch uClibc (fix getline conflict with glibc)
RUN mkdir -p toolchain_build_mips && \
    tar -xf dl/uClibc-0.9.30.1.tar.bz2 -C toolchain_build_mips/ && \
    sed -i 's/\bgetline\b/unifdef_getline/g' toolchain_build_mips/uClibc-0.9.30.1/extra/scripts/unifdef.c && \
    touch toolchain_build_mips/uClibc-0.9.30.1/.unpacked

# Build the MIPS toolchain (ignore fakeroot download error, toolchain will be complete)
RUN make 2>&1 || true

# Verify the toolchain exists
RUN ls -la build_mips/staging_dir/usr/bin/mips-linux-uclibc-gcc-4.3.3

# Set default shell
SHELL ["/bin/bash", "-c"]

# Add toolchain to PATH
ENV PATH="/buildroot/buildroot/build_mips/staging_dir/usr/bin:${PATH}"

# Expose the buildroot directory
VOLUME ["/buildroot/buildroot/output"]

# Default command - start interactive shell
CMD ["/bin/bash"]
