#
# Embedded Security Testing Lab - Docker Image
# Educational environment for firmware analysis
#

FROM ubuntu:22.04

LABEL maintainer="EST Lab"
LABEL description="Embedded Security Testing Lab - Educational Environment"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install base dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
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
    && rm -rf /var/lib/apt/lists/*

# Install binwalk (legacy Python version)
RUN git clone --branch v2.3.4 --depth 1 https://github.com/ReFirmLabs/binwalk.git /tmp/binwalk && \
    cd /tmp/binwalk && \
    python3 setup.py install && \
    rm -rf /tmp/binwalk

# Build and install sasquatch (for non-standard SquashFS)
# Use CFLAGS to fix GCC 10+ multiple definition errors and disable -Werror
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

# Create application directory
WORKDIR /app

# Copy web application
COPY webapp/requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY webapp/ /app/

# Create data directory for uploads
RUN mkdir -p /data/uploads && chmod 777 /data/uploads

# Expose web port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
