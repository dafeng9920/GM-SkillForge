#!/usr/bin/env bash
set -euo pipefail

# OpenClaw 自动记忆清理脚本 (带备份轮转策略)
# 路径: skills/openclaw-memory-cron-skill/scripts/auto_clean.sh

PROJECT_DIR="${1:-/root/openclaw-box}"
BACKUP_RETAIN_DAYS="${2:-7}"
BACKUP_ROOT="${PROJECT_DIR}/data/.backup"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CURRENT_BACKUP="${BACKUP_ROOT}/auto_$(date +%Y%m%d)"

echo "[$(date)] Starting Auto-Clean for OpenClaw..."

# 1. 停止服务
cd "${PROJECT_DIR}"
docker compose stop openclaw-agent || docker compose down

# 2. 备份并轮转
mkdir -p "${CURRENT_BACKUP}"
cp -a data/agents/main/sessions "${CURRENT_BACKUP}/sessions_$(date +%H%M%S)" 2>/dev/null || true
cp -a data/memory "${CURRENT_BACKUP}/memory_$(date +%H%M%S)" 2>/dev/null || true

# 删除过期备份 (Retention Policy)
echo "Cleaning backups older than ${BACKUP_RETAIN_DAYS} days..."
find "${BACKUP_ROOT}" -maxdepth 1 -name "auto_*" -type d -mtime +"${BACKUP_RETAIN_DAYS}" -exec rm -rf {} +

# 3. 彻底清理
rm -f data/agents/main/sessions/*.jsonl
rm -f data/memory/main.sqlite*

# 4. 重启
docker compose up -d
echo "[$(date)] Auto-Clean completed successfully."
