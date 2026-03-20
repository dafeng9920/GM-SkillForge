# Base on NVIDIA CUDA for 5070 Ti Passthrough
FROM nvidia/cuda:12.4.1-base-ubuntu22.04

# Avoid interaction prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    xvfb \
    libgbm1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libasound2 \
    libxshmfence1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcups2 \
    drm-info \
    && rm -rf /var/lib/apt/lists/*

# Set Working Directory
WORKDIR /app

# Install Python Dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Playwright and its specific browser binaries
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy Application Code
COPY . .

# Set Execution Permissions
RUN chmod +x entrypoint.sh

# Environment Variable for Xvfb
ENV DISPLAY=:99

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
