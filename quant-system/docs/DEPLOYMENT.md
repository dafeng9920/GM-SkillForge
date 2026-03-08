# GM Quant System - 基础设施部署指南

> 版本: v1.0
> 更新日期: 2026-02-22

---

## 1. 系统要求

### 1.1 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8+ 核 |
| 内存 | 16 GB | 32+ GB |
| 存储 | 200 GB SSD | 500+ GB NVMe |
| GPU | - | NVIDIA RTX 3060+ (用于 Kronos 推理) |

### 1.2 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Docker Desktop | 4.20+ | Windows/Mac |
| Docker Engine | 24.0+ | Linux |
| Docker Compose | 2.20+ | 随 Docker Desktop 安装 |
| Python | 3.11+ | 本地开发 |
| Git | 2.40+ | 版本控制 |

---

## 2. 快速开始

### 2.1 克隆项目

```bash
git clone https://github.com/your-org/gm-quant-system.git
cd gm-quant-system
```

### 2.2 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env  # 或使用你喜欢的编辑器
```

### 2.3 启动服务

**Windows (PowerShell):**
```powershell
.\scripts\start.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

### 2.4 验证部署

```bash
# 运行健康检查
./scripts/health-check.sh   # Linux/Mac
.\scripts\health-check.ps1  # Windows
```

---

## 3. 服务说明

### 3.1 核心服务

| 服务 | 端口 | 用途 |
|------|------|------|
| TDengine | 6030, 6041 | 时序数据存储 (行情、交易、日志) |
| PostgreSQL | 5432 | 元数据存储 (策略、配置、规则) |
| Redis | 6379 | 缓存 + 消息队列 |
| MinIO | 9000, 9001 | 对象存储 (证据、报告) |

### 3.2 可选服务

| 服务 | 端口 | 启动方式 | 用途 |
|------|------|----------|------|
| OpenBB Adapter | 6900 | `--profile full` | 数据获取 (AGPL 隔离) |
| Prometheus | 9090 | `--profile monitoring` | 指标采集 |
| Grafana | 3000 | `--profile monitoring` | 可视化面板 |

启动可选服务:
```bash
docker compose --profile full up -d
docker compose --profile monitoring up -d
```

---

## 4. 详细配置

### 4.1 TDengine

**创建数据库:**
```sql
-- 连接 TDengine
taos -h localhost -P 6030

-- 创建量化数据库
CREATE DATABASE quant KEEP 365 DAYS 10 BLOCKS 6;

-- 使用数据库
USE quant;

-- 创建行情表
CREATE STABLE market_data (
    ts TIMESTAMP,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    amount DOUBLE
) TAGS (symbol BINARY(20), exchange BINARY(20), interval BINARY(10));

-- 创建交易流水表
CREATE STABLE trade_flow (
    ts TIMESTAMP,
    trade_id BINARY(50),
    strategy_id BINARY(50),
    symbol BINARY(20),
    action BINARY(10),
    quantity INT,
    price DOUBLE,
    status BINARY(20)
) TAGS (gateway BINARY(20));

-- 创建审计日志表
CREATE STABLE audit_logs (
    ts TIMESTAMP,
    record_id BINARY(50),
    event_type BINARY(30),
    event_data NCHAR(4096),
    correlation_id BINARY(50)
) TAGS (skill_id BINARY(50));
```

### 4.2 PostgreSQL

数据库会在首次启动时自动初始化，包括:
- 10+ 数据表
- 5 条默认 Gate 规则
- 18 个 Skills 注册

**手动连接:**
```bash
docker exec -it quant-postgres psql -U quant -d quant_system
```

**查看 Skills:**
```sql
SELECT skill_id, layer, priority, enabled FROM skills ORDER BY priority, layer;
```

### 4.3 Redis

**连接测试:**
```bash
docker exec -it quant-redis redis-cli
> PING
PONG
> INFO
```

**配置说明:**
- 最大内存: 2GB
- 淘汰策略: allkeys-lru
- 持久化: AOF

### 4.4 MinIO

**访问控制台:**
- URL: http://localhost:9001
- 用户: quantadmin
- 密码: quant123456 (请修改!)

**创建存储桶:**
```bash
# 安装 mc 客户端
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# 配置别名
./mc alias set quant http://localhost:9000 quantadmin quant123456

# 创建存储桶
./mc mb quant/evidence
./mc mb quant/audit-packs
./mc mb quant/backtest-reports
./mc mb quant/strategy-snapshots

# 设置保留策略
./mc ilm rule add quant/evidence --expire-days 365
```

---

## 5. 常用命令

### 5.1 服务管理

```bash
# 启动所有服务
docker compose up -d

# 停止所有服务
docker compose down

# 重启单个服务
docker compose restart tdengine

# 查看日志
docker compose logs -f postgres

# 查看资源使用
docker stats
```

### 5.2 数据备份

```bash
# PostgreSQL 备份
docker exec quant-postgres pg_dump -U quant quant_system > backup_$(date +%Y%m%d).sql

# TDengine 备份
docker exec quant-tdengine taosdump -o /backup -D quant

# MinIO 备份
./mc mirror quant/evidence ./backup/evidence
```

### 5.3 数据恢复

```bash
# PostgreSQL 恢复
cat backup.sql | docker exec -i quant-postgres psql -U quant quant_system

# TDengine 恢复
docker exec quant-tdengine taosdump -i /backup
```

---

## 6. 故障排查

### 6.1 常见问题

**Q: 容器无法启动**
```bash
# 检查端口占用
netstat -tlnp | grep -E "5432|6379|6030|9000"

# 检查 Docker 日志
docker compose logs tdengine
```

**Q: 数据库连接失败**
```bash
# 检查容器状态
docker compose ps

# 检查网络
docker network ls
docker network inspect quant-system_quant-network
```

**Q: 内存不足**
```bash
# 调整 Docker 内存限制
# 编辑 docker-compose.yml，添加:
# deploy:
#   resources:
#     limits:
#       memory: 4G
```

### 6.2 日志位置

| 服务 | 容器内路径 |
|------|-----------|
| TDengine | /var/log/taos |
| PostgreSQL | /var/log/postgresql |
| Redis | 无 (输出到 stdout) |
| MinIO | 无 (输出到 stdout) |

---

## 7. 安全建议

1. **修改默认密码**: 修改 `.env` 中的所有密码
2. **限制网络访问**: 仅暴露必要端口
3. **启用 TLS**: 生产环境配置 HTTPS
4. **定期备份**: 设置自动备份任务
5. **日志审计**: 定期检查审计日志

---

## 8. 下一步

- [ ] 运行健康检查确认部署成功
- [ ] 配置 VeighNa CTP Gateway (SimNow)
- [ ] 下载 Kronos 模型
- [ ] 开始开发 P0 Skills

---

*文档结束*
