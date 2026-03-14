# Quant System 基础设施设置指南

> Phase 0: 基础设施准备 (1周)
> 目标: 搭建核心基础设施，为后续Skills提供数据存储和运行环境

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Quant System 基础设施                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ TDengine    │  │ PostgreSQL  │  │   Redis     │         │
│  │ 时序数据库   │  │   元数据库   │  │  缓存+队列   │         │
│  │ (Tick数据)   │  │ (配置/权限) │  │ (会话状态)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐                                            │
│  │   MinIO     │  对象存储                                │
│  │ (Audit Pack)│  - 证据链                                  │
│  │  (回测报告) │  - 回测报告                                │
│  └─────────────┘                                            │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐                            │
│  │  Grafana    │  │ Prometheus  │  监控体系                │
│  │  (监控面板)  │  │ (指标采集)   │                            │
│  └─────────────┘  └─────────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 前置要求

1. **Docker Desktop** 已安装并运行
2. **PowerShell** (Windows) 或 **Bash** (Linux/Mac)
3. **Python 3.8+** 和 pip

### 1. 启动基础设施

#### Windows:
```powershell
# 以管理员身份运行PowerShell
cd d:\GM-SkillForge
.\scripts\start_quant_stack.ps1
```

#### Linux/Mac:
```bash
cd d:/GM-SkillForge
chmod +x scripts/start_quant_stack.sh
./scripts/start_quant_stack.sh
```

### 2. 验证服务状态

```bash
# 检查所有容器状态
docker-compose -f docker/quant-stack.yml ps

# 运行健康检查
python scripts/check_quant_stack.py
```

### 3. 访问服务

| 服务 | 地址 | 默认凭据 |
|------|------|----------|
| PostgreSQL | localhost:5432 | quant_admin / quant_secure_change_me |
| Redis | localhost:6379 | - |
| TDengine | localhost:6030 | - |
| MinIO Console | http://localhost:9000 | minioadmin / minioadmin_change_me |
| PGAdmin | http://localhost:5050 | admin@quant.local / admin_change_me |
| Redis Commander | http://localhost:8081 | - |
| Grafana | http://localhost:3000 | admin / admin_change_me |
| Prometheus | http://localhost:9090 | - |

---

## 服务详细配置

### PostgreSQL (元数据库)

**用途**: 存储策略配置、用户权限、Gate规则

**数据库**:
- `quant_meta`: 主数据库
- **Schemas**:
  - `quant_config`: 配置数据
  - `quant_data`: 市场数据元信息
  - `quant_audit`: 审计日志

**表结构**:
```
quant_config.strategies     -- 策略配置
quant_config.skills         -- Skill注册表
quant_config.gate_rules     -- Gate规则
quant_config.users          -- 用户权限

quant_data.market_info      -- 市场信息
quant_data.factors          -- 因子定义

quant_audit.trade_log       -- 交易日志
quant_audit.gate_decisions  -- Gate决策日志
quant_audit.risk_events    -- 风控事件
```

**连接示例**:
```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='quant_meta',
    user='quant_admin',
    password='quant_secure_change_me',
)
```

### TDengine (时序数据库)

**用途**: 存储实时Tick数据、交易流水、监控指标

**数据库**:
- `quant_tick`: Tick数据
- `quant_trade`: 交易流水
- `quant_metrics`: 监控指标

**连接示例**:
```python
import taos

conn = taos.connect(host='localhost', port=6030)
```

### Redis (缓存+消息队列)

**用途**: 高频缓存、消息队列、会话状态

**数据结构**:
```
# 实时持仓
position:{symbol} -> JSON

# Gate决策缓存
gate:{request_id} -> JSON

# 消息队列
queue:signals -> List
queue:orders -> List
```

**连接示例**:
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
```

### MinIO (对象存储)

**用途**: 存储Audit Pack、回测报告、策略快照

**Buckets**:
- `audit-packs`: L3合规包
- `evidence`: 证据链数据
- `backtest-reports`: 回测报告
- `strategy-snapshots`: 策略快照

**连接示例**:
```python
from minio import Minio

client = Minio(
    'localhost:9001',
    access_key='minioadmin',
    secret_key='minioadmin_change_me',
)
```

---

## 管理操作

### 查看日志

```bash
# 所有服务日志
docker-compose -f docker/quant-stack.yml logs

# 特定服务日志
docker-compose -f docker/quant-stack.yml logs postgres
docker-compose -f docker/quant-stack.yml logs redis
docker-compose -f docker/quant-stack.yml logs tdengine
docker-compose -f docker/quant-stack.yml logs minio
```

### 停止服务

```bash
# 停止并保留数据
docker-compose -f docker/quant-stack.yml stop

# 停止并删除数据卷
docker-compose -f docker/quant-stack.yml down -v
```

### 重启服务

```bash
docker-compose -f docker/quant-stack.yml restart
```

### 备份数据

```bash
# PostgreSQL备份
docker exec quant-postgres pg_dump -U quant_admin quant_meta > backup_$(date +%Y%m%d).sql

# MinIO备份
docker exec quant-minio mc mirror public/ backup/
```

---

## 故障排查

### 容器无法启动

1. 检查端口占用:
```bash
netstat -ano | findstr "5432"
netstat -ano | findstr "6379"
netstat -ano | findstr "9000"
```

2. 查看容器日志:
```bash
docker logs quant-postgres
docker logs quant-redis
```

### 连接失败

1. 确认容器运行:
```bash
docker ps | grep quant-
```

2. 测试网络连通:
```bash
docker exec quant-postgres pg_isready -U quant_admin
docker exec quant-redis redis-cli ping
```

### 性能问题

1. 查看资源使用:
```bash
docker stats
```

2. 清理未使用的数据:
```bash
docker system prune -a
```

---

## 下一步

Phase 0 完成后，开始实现 **Phase 1: 数据层 Skills**

1. [ ] openbb-fetch Skill
2. [ ] data-cleaner Skill
3. [ ] data-validator Skill
4. [ ] data-versioner Skill
5. [ ] data-enricher Skill
6. [ ] data-syncer Skill

详见: [Phase 1 实施指南](./PHASE1_DATA_LAYER.md)

---

*更新时间: 2026-03-09*
