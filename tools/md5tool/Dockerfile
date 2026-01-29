# Dockerfile for TP-Link firmware MD5 calculation
# Provides mktplinkfw tool for verifying/calculating checksums

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    cmake \
    zlib1g-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Build mktplinkfw from firmware-utils repository
WORKDIR /opt
RUN git clone https://github.com/openwrt/firmware-utils.git && \
    cd firmware-utils && \
    cmake -B build && \
    cmake --build build --target mktplinkfw && \
    cp build/mktplinkfw /usr/local/bin/ && \
    rm -rf /opt/firmware-utils

# Create working directory
WORKDIR /work

# Default command
CMD ["/bin/bash"]
