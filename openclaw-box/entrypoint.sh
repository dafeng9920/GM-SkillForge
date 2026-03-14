#!/bin/sh

# Ensure OpenClaw config is repaired
echo "Repairing OpenClaw config..."
openclaw doctor --fix

# Install Feishu plugin
echo "Ensuring Feishu plugin is installed..."
openclaw plugins install @xzq-xu/feishu

# Start OpenClaw
echo "Starting OpenClaw..."
openclaw gateway run --port 18789 --allow-unconfigured --bind lan
