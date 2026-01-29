# Dockerfile for TP-Link MR3020v1 firmware manipulation
# Includes firmware-mod-kit and mktplinkfw tools

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    zlib1g-dev \
    liblzma-dev \
    liblzo2-dev \
    python3 \
    python3-pip \
    wget \
    unzip \
    xz-utils \
    cmake \
    libssl-dev \
    bsdmainutils \
    squashfs-tools \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Install firmware-mod-kit
WORKDIR /opt
RUN git clone https://github.com/rampageX/firmware-mod-kit.git

# Build squashfs tools
WORKDIR /opt/firmware-mod-kit/src
RUN cd squashfs-3.0 && make

# Build squashfs4.2 with LZMA support for v4.0 filesystem
RUN git clone https://github.com/devttys0/sasquatch.git /opt/sasquatch && \
    cd /opt/sasquatch && \
    ./build.sh 2>&1 || true

# Build squashfs-tools 4.6.1 with LZMA for creating v4.0 squashfs
WORKDIR /opt
RUN wget -O squashfs-tools.tar.gz "https://github.com/plougher/squashfs-tools/archive/refs/tags/squashfs-tools-4.6.1.tar.gz" && \
    tar -xzf squashfs-tools.tar.gz && \
    cd squashfs-tools-squashfs-tools-4.6.1/squashfs-tools && \
    make LZMA_XZ_SUPPORT=1 XZ_SUPPORT=1 && \
    cp mksquashfs /usr/local/bin/mksquashfs4 && \
    cp unsquashfs /usr/local/bin/unsquashfs4 && \
    rm -rf /opt/squashfs-tools.tar.gz

# Build other tools
RUN cd crcalc && make || true

# Build mktplinkfw from firmware-utils repository
WORKDIR /opt
RUN git clone https://github.com/openwrt/firmware-utils.git && \
    cd firmware-utils && \
    cmake -B build && \
    cmake --build build --target mktplinkfw && \
    cp build/mktplinkfw /usr/local/bin/

# Create working directory
WORKDIR /work

# Add tools to PATH
ENV PATH="/opt/firmware-mod-kit/src/squashfs-3.0:/opt/firmware-mod-kit:${PATH}"
ENV FMK_DIR="/opt/firmware-mod-kit"

# Default command
CMD ["/bin/bash"]
