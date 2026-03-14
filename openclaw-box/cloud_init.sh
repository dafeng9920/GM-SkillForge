#!/bin/sh
# cloud_init.sh - Designed to be run inside the openclaw_core container

echo "🏗️ Initializing Cloud-Local Bridge..."

# 1. Setup Git Identity
git config --global user.email "commander@skillforge"
git config --global user.name "Commander"

# 2. Setup Auto-Sync Cron
# In a real container, we'd add this to crontab or a long-running process
# For now, we'll suggest adding a watchdog to entrypoint.sh or a separate service

# 3. Check for cloudflared
if ! command -v cloudflared >/dev/null 2>&1; then
    echo "📥 Downloading Cloudflare Tunnel client..."
    # Platform specific download logic
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
fi

echo "✅ Cloud side prepared. Ready to bind tunnel."
