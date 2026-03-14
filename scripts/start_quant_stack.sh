#!/bin/bash
# Quant System 基础设施启动脚本
# Phase 0: 基础设施准备

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

echo "=========================================="
echo "Quant System 基础设施启动"
echo "=========================================="
echo ""
echo "项目根目录: $PROJECT_ROOT"
echo "Docker配置: $DOCKER_DIR"
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

echo "✓ Docker运行正常"

# 切换到Docker目录
cd "$DOCKER_DIR"

# 创建必要的目录
echo ""
echo "创建数据目录..."
mkdir -p sql
mkdir -p redis
mkdir -p prometheus
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p data/tdengine
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/minio

echo "✓ 数据目录创建完成"

# 停止并删除旧容器（如果存在）
echo ""
echo "清理旧容器..."
docker-compose -f quant-stack.yml down -v 2>/dev/null || true

# 启动基础设施
echo ""
echo "启动基础设施容器..."
docker-compose -f quant-stack.yml up -d

# 等待容器启动
echo ""
echo "等待容器启动..."
sleep 10

# 检查容器状态
echo ""
echo "检查容器状态..."
docker-compose -f quant-stack.yml ps

# 等待服务就绪
echo ""
echo "等待服务就绪..."
echo "  PostgreSQL..."
until docker exec quant-postgres pg_isready -U quant_admin > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " ✓"

echo "  Redis..."
until docker exec quant-redis redis-cli ping > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " ✓"

echo "  MinIO..."
until curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " ✓"

echo "  TDengine..."
until docker exec quant-tdengine taos -s tdengine > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " ✓"

# 显示访问信息
echo ""
echo "=========================================="
echo "✓ 基础设施启动完成！"
echo "=========================================="
echo ""
echo "服务访问地址："
echo "  PostgreSQL:     localhost:5432"
echo "  Redis:          localhost:6379"
echo "  TDengine:       localhost:6030"
echo "  MinIO Console:  http://localhost:9000"
echo "  MinIO API:       http://localhost:9001"
echo "  PGAdmin:        http://localhost:5050"
echo "  Redis Commander: http://localhost:8081"
echo "  Grafana:        http://localhost:3000"
echo "  Prometheus:     http://localhost:9090"
echo ""
echo "默认凭据："
echo "  PostgreSQL:     quant_admin / quant_secure_change_me"
echo "  MinIO:          minioadmin / minioadmin_change_me"
echo "  PGAdmin:        admin@quant.local / admin_change_me"
echo "  Grafana:        admin / admin_change_me"
echo ""
echo "下一步："
echo "  1. 运行健康检查: python scripts/check_quant_stack.py"
echo "  2. 开始Phase 1: 数据层实现"
echo ""
