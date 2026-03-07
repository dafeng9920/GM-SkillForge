#!/usr/bin/env bash
set -euo pipefail

# OpenClaw 记忆库一键清理脚本
# 用于清理远端服务器的 sessions 和 memory

PROJECT_DIR="${1:-/root/openclaw-box}"
BACKUP_DIR="${PROJECT_DIR}/data/.backup/before_clear_$(date +%Y%m%d-%H%M%S)"

echo "=========================================="
echo "OpenClaw 记忆库清理脚本"
echo "=========================================="
echo "项目目录: ${PROJECT_DIR}"
echo "备份目录: ${BACKUP_DIR}"
echo ""

# 检查目录是否存在
if [ ! -d "${PROJECT_DIR}" ]; then
    echo "❌ 错误: 项目目录不存在: ${PROJECT_DIR}"
    exit 1
fi

cd "${PROJECT_DIR}"

# Step 1: 显示当前状态
echo "[1/6] 检查当前记忆库占用..."
du -sh data/agents/main/sessions data/memory 2>/dev/null || true
echo ""

# Step 2: 停止服务
echo "[2/6] 停止 OpenClaw 服务..."
docker compose stop openclaw-agent || docker compose down
echo ""

# Step 3: 创建备份
echo "[3/6] 备份当前记忆库..."
mkdir -p "${BACKUP_DIR}"
cp -a data/agents/main/sessions "${BACKUP_DIR}/sessions_backup" 2>/dev/null || true
cp -a data/memory "${BACKUP_DIR}/memory_backup" 2>/dev/null || true
echo "✅ 备份完成: ${BACKUP_DIR}"
echo ""

# Step 4: 清理 sessions
echo "[4/6] 清理 sessions..."
rm -f data/agents/main/sessions/*.jsonl
echo "✅ sessions 已清理"
echo ""

# Step 5: 清理 memory
echo "[5/6] 清理 memory..."
rm -f data/memory/main.sqlite*
echo "✅ memory 已清理"
echo ""

# Step 6: 重启服务
echo "[6/6] 重启 OpenClaw 服务..."
docker compose up -d
sleep 3
docker compose ps
echo ""

# 验收检查
echo "=========================================="
echo "验收检查"
echo "=========================================="

# 检查 sessions
echo "Sessions 目录:"
ls -lh data/agents/main/sessions/ 2>/dev/null || echo "  (空目录)"

# 检查 memory
echo "Memory 目录:"
ls -lh data/memory/ 2>/dev/null || echo "  (空目录)"

# 检查服务状态
echo "服务状态:"
docker compose ps

# 检查日志
echo "最近日志:"
docker compose logs --since 30s openclaw-agent | tail -20

echo ""
echo "=========================================="
echo "✅ 清理完成！"
echo "=========================================="
echo "备份位置: ${BACKUP_DIR}"
echo "如需恢复: cp -a ${BACKUP_DIR}/sessions_backup/* data/agents/main/sessions/"
