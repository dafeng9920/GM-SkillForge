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

# Set npm mirror
RUN npm config set registry https://registry.npmmirror.com

# Install OpenClaw globally
RUN npm install -g openclaw@latest

# Set working directory
WORKDIR /app

# The entrypoint will handle plugin installation and service startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
