#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-/root/openclaw-box}"
DATA_DIR="${PROJECT_DIR}/data"

echo "[1/7] enter project: ${PROJECT_DIR}"
cd "${PROJECT_DIR}"

echo "[2/7] stop stray host processes that can occupy 18789"
pkill -f openclaw-gateway || true
pkill -f "docker-proxy.*127.0.0.1:18789" || true

echo "[3/7] show current 18789 listeners"
ss -lntp | grep 18789 || true

echo "[4/7] cleanup stuck containers"
docker rm -f openclaw_core 2>/dev/null || true
docker compose down --remove-orphans || true

echo "[5/7] normalize data ownership"
chown -R 1000:1000 "${DATA_DIR}"

echo "[6/7] build and start stack"
docker compose up -d --build

echo "[7/7] post-check"
docker compose ps
docker compose logs --since 3m openclaw-agent | grep -E "logged in|EACCES|Unknown model|No API key|Embedded agent failed|lane task error" || true

echo "Done. If container is still stuck with no exit event, run: systemctl restart docker"

