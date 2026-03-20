#!/bin/bash

# 1. Start Xvfb (Virtual Framebuffer) in background
# This provides the "Head" for the browser without a physical monitor
Xvfb :99 -screen 0 1920x1080x24 &

# 2. Give Xvfb a moment to start
sleep 2

# 3. Launch FastAPI with Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
