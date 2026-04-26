FROM node:22-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    build-essential \
    cmake \
    pkg-config \
    libgd-dev \
    libwebp-dev \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

# Skip registry config, use official registry for Singapore server

# Install OpenClaw globally
RUN npm install -g openclaw@2026.3.31 --no-audit --no-fund --verbose

# Set working directory
WORKDIR /app

# The entrypoint will handle plugin installation and service startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
