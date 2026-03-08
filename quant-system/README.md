# GM Quant System

> AI 驱动的量化交易系统 - 混合架构，对齐 SkillForge 治理框架

## 架构定位

```
┌─────────────────────────────────────────────────────────────┐
│                SkillForge (治理层)                          │
│  - 宪法定义                                                  │
│  - Gate 引擎                                                 │
│  - Evidence 标准                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ 标准接口
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                Quant System (执行层)                         │
│  - 独立部署                                                  │
│  - 遵循宪法                                                  │
│  - 输出对齐                                                  │
└─────────────────────────────────────────────────────────────┘
```

**方案 C 混合架构**：独立部署 + 治理对齐

## 快速开始

### 1. 启动基础设施

```powershell
# Windows
.\scripts\start.ps1

# Linux/Mac
./scripts/start.sh
```

### 2. 验证部署

```powershell
# Windows
.\scripts\health-check.ps1

# Linux/Mac
./scripts/health-check.sh
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 运行测试

```bash
pytest tests/ -v
```

## 目录结构

```
quant-system/
├── contracts/
│   └── INTERFACE_CONTRACTS.md    # 与 SkillForge 的接口合同
├── docker/
│   └── docker-compose.yml        # 基础设施配置
├── skills/
│   ├── base.py                   # 基础类 (符合 Evidence 规范)
│   ├── data/
│   │   ├── openbb_fetch.py       # P0-01 数据获取
│   │   └── data_validator.py     # P0-02 数据校验
│   ├── research/                 # 研发层 Skills
│   ├── risk/                     # 风控层 Skills
│   ├── execution/                # 执行层 Skills
│   └── governance/               # 治理层 Skills
├── tests/                        # 测试文件
├── docs/                         # 文档
├── CONSTITUTION_ALIGNMENT.md     # 宪法对齐声明
├── .env.example                  # 环境变量模板
└── requirements.txt              # Python 依赖
```

## 宪法对齐

Quant System 遵循 SkillForge 宪法的核心原则：

| 宪法条款 | 实现方式 |
|----------|----------|
| 终端事实优先 | 所有输出包含 `evidence_ref` + `data_hash` |
| Fail-Closed | 输入验证失败 → `REJECTED` |
| 失败不可跳过 | 所有失败记录到 `audit_logs` |
| 证据先于解释 | `evidence_ref` 先于 `result` 生成 |
| 宪法先于能力 | 先定义接口合同，后实现 Skills |

详见 [CONSTITUTION_ALIGNMENT.md](CONSTITUTION_ALIGNMENT.md)

## 接口合同

Quant System 输出符合 SkillForge Evidence 规范：

```json
{
  "envelope_version": "1.0",
  "skill_id": "kronos-predict",
  "run_id": "run-abc123",
  "trace_id": "span-quant-xyz",
  "timestamp": "2026-02-22T10:30:00Z",
  "status": "completed",
  "data": { ... },
  "evidence": {
    "evidence_ref": "evidence://quant/kronos-predict/...",
    "data_hash": "sha256:...",
    "provenance": { ... }
  },
  "gate_decision": {
    "verdict": "ALLOW",
    "checks_passed": [...],
    "violations": []
  }
}
```

详见 [contracts/INTERFACE_CONTRACTS.md](contracts/INTERFACE_CONTRACTS.md)

## 服务端口

| 服务 | 端口 | 用途 |
|------|------|------|
| TDengine | 6030, 6041 | 时序数据库 |
| PostgreSQL | 5432 | 元数据库 |
| Redis | 6379 | 缓存 |
| MinIO | 9000, 9001 | 对象存储 |

## MVP 进度

- [x] Week 1: 基础设施 + 宪法对齐
- [x] Week 1: P0 数据层 Skills
- [ ] Week 2: P0 数据层 Skills 完善
- [ ] Week 3-4: P0 研发层 Skills
- [ ] Week 5-6: P0 风控层 + 执行层 Skills
- [ ] Week 7: P0 治理层 Skills
- [ ] Week 8: P1 Skills + 验收

## 文档

- [宪法对齐声明](CONSTITUTION_ALIGNMENT.md)
- [接口合同](contracts/INTERFACE_CONTRACTS.md)
- [部署指南](docs/DEPLOYMENT.md)
- [MVP 实施计划](../docs/2026-02-22/QUANT_MVP_IMPLEMENTATION_PLAN.md)
- [完整架构设计](../docs/2026-02-22/QUANT_SYSTEM_FULL_ARCHITECTURE.md)
