#!/bin/sh

# Repair permissions for plugins
echo "Repairing plugin permissions..."
chmod -R 755 /root/.openclaw/extensions

# Ensure OpenClaw config is repaired
echo "Repairing OpenClaw config..."
openclaw doctor --fix

# Install Feishu plugin
echo "Ensuring Feishu plugin is installed..."
openclaw plugins install @xzq-xu/feishu

# Start OpenClaw
echo "Starting OpenClaw..."
OPENCLAW_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18793}"
openclaw gateway run --port "${OPENCLAW_GATEWAY_PORT}" --allow-unconfigured --bind lan
