#
# Embedded Security Testing - CLI Tool
# Educational environment for firmware analysis
#

FROM ubuntu:22.04

LABEL maintainer="EST Lab"
LABEL description="Embedded Security Testing CLI - Educational Environment"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV TERM=xterm-256color

# Install base dependencies including MIPS cross-compiler
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    build-essential \
    cmake \
    pkg-config \
    wget \
    curl \
    file \
    xxd \
    binutils \
    zlib1g-dev \
    liblzma-dev \
    liblzo2-dev \
    libmagic-dev \
    mtd-utils \
    gzip \
    bzip2 \
    p7zip-full \
    unzip \
    cpio \
    squashfs-tools \
    libssl-dev \
    gcc-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install rich

# Install binwalk (legacy Python version)
RUN git clone --branch v2.3.4 --depth 1 https://github.com/ReFirmLabs/binwalk.git /tmp/binwalk && \
    cd /tmp/binwalk && \
    python3 setup.py install && \
    rm -rf /tmp/binwalk

# Build and install sasquatch (for non-standard SquashFS)
RUN git clone https://github.com/devttys0/sasquatch.git /tmp/sasquatch && \
    cd /tmp/sasquatch && \
    sed -i 's/-Werror//g' patches/patch0.txt && \
    CFLAGS="-fcommon" ./build.sh && \
    rm -rf /tmp/sasquatch

# Build mktplinkfw from OpenWrt firmware-utils
RUN git clone --depth 1 https://github.com/openwrt/firmware-utils.git /tmp/firmware-utils && \
    cd /tmp/firmware-utils && \
    cmake -B build && \
    cmake --build build --target mktplinkfw && \
    cp build/mktplinkfw /usr/local/bin/ && \
    chmod +x /usr/local/bin/mktplinkfw && \
    rm -rf /tmp/firmware-utils

# Create work directory
WORKDIR /work

# Copy CLI tool
COPY est.py /usr/local/bin/est
RUN chmod +x /usr/local/bin/est

# Create directories
RUN mkdir -p /work/samples /work/extracted /work/build /work/buildroot/src

ENTRYPOINT ["python3", "/usr/local/bin/est"]
