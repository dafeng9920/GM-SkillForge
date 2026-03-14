#!/usr/bin/env bash
set -euo pipefail

# 服务器瘦身一键维护脚本
# 路径: skills/server-maintenance-slimming-skill/scripts/slim_server.sh

echo "=========================================="
echo "🚀 开始服务器瘦身与运维维护..."
echo "=========================================="
BEFORE_FREE=$(df -h / | awk 'NR==2 {print $4}')
echo "清理前可用空间: ${BEFORE_FREE}"

# 1. Docker 深度清理
echo -e "\n[1/4] 清理 Docker 冗余对象..."
docker system prune -f
# 可选: 清理未使用的镜像
# docker image prune -a -f

# 2. 系统日志截断
echo -e "\n[2/4] 截断系统日志至 100MB..."
journalctl --vacuum-size=100M
journalctl --vacuum-time=1s

# 3. 软件包管理清理
echo -e "\n[3/4] 清理 YUM/DNF 与包管理器缓存..."
dnf clean all || yum clean all || true
if command -v pnpm &> /dev/null; then
    pnpm store prune
fi

# 4. 可选的应用层清理
echo -e "\n[4/4] 检查是否有已知大头应用需要清理..."
OPENCLAW_EXT="/root/.openclaw/extensions"
if [ -d "${OPENCLAW_EXT}" ]; then
    echo "检测到 OpenClaw 扩展，建议手动清理无用适配器 (qqbot, wecom)..."
    # rm -rf ${OPENCLAW_EXT}/qqbot ${OPENCLAW_EXT}/wecom
fi

echo -e "\n=========================================="
AFTER_FREE=$(df -h / | awk 'NR==2 {print $4}')
echo "✅ 清理完成！"
echo "清理后可用空间: ${AFTER_FREE}"
echo "=========================================="
