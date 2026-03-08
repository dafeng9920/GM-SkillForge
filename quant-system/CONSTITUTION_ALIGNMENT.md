# Quant System 宪法对齐声明

> 版本: v1.0
> 日期: 2026-02-22
> 状态: 生效

---

## 1. 架构定位

Quant System 采用**混合架构**：
- **独立部署**：作为独立子系统运行
- **治理对齐**：遵循 SkillForge 宪法约束
- **接口统一**：输出符合 SkillForge Evidence 规范

```
┌─────────────────────────────────────────────────────────────┐
│                    架构关系                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SkillForge (治理层)                     │   │
│  │                                                      │   │
│  │  - 宪法定义 (constitution_v1)                        │   │
│  │  - Gate 引擎                                         │   │
│  │  - Evidence 标准                                     │   │
│  │  - Replay 能力                                       │   │
│  │                                                      │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│                         │ 标准接口                          │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Quant System (执行层)                   │   │
│  │                                                      │   │
│  │  - 独立部署                                          │   │
│  │  - 遵循宪法                                          │   │
│  │  - 输出对齐                                          │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 宪法条款对齐

### 2.1 最高信条对齐

| 宪法条款 | Quant System 实现 | 状态 |
|----------|------------------|------|
| **终端事实优先** | 所有输出包含 `evidence_ref` + `data_hash` | ✅ 对齐 |
| **Fail-Closed** | 输入验证失败 → `REJECTED`，无默认放行 | ✅ 对齐 |
| **失败不可跳过** | 所有失败记录到 `audit_logs`，包含 `error_code` | ✅ 对齐 |
| **证据先于解释** | `evidence_ref` 先于 `result` 生成 | ✅ 对齐 |
| **宪法先于能力** | 本文档先于 Skill 实现定义约束 | ✅ 对齐 |

### 2.2 不可回退红线对齐

| 红线 | Quant System 实现 | 状态 |
|------|------------------|------|
| 不允许以叙事替代证据 | 代码级 `evidence_ref`，非文字描述 | ✅ 对齐 |
| 不允许把失败标记为"部分成功" | 严格的 `status` 枚举：`completed/failed/rejected` | ✅ 对齐 |
| 不允许在无证据链的情况下执行关键动作 | 交易执行前必须通过 Gate 检查 | ✅ 对齐 |
| 不允许通过人工口径绕过 Gate | 所有调用通过 API，Gate 检查强制 | ✅ 对齐 |
| 不允许旧代码复制进入新实现 | 新建代码，无复制 | ✅ 对齐 |

---

## 3. 独立性声明

### 3.1 独立原因

```yaml
independence_reasons:
  license_isolation:
    - OpenBB 使用 AGPLv3
    - 隔离避免污染主系统

  iteration_velocity:
    - 量化策略需要快速迭代
    - 独立发布周期

  domain_boundary:
    - 量化领域有特定专业需求
    - 独立的错误码和问题目录
```

### 3.2 独立范围

```
quant-system/
├── skills/           # 独立的 Skill 实现
├── docker/           # 独立的基础设施
├── tests/            # 独立的测试
├── config/           # 独立的配置
└── docs/             # 独立的文档
```

---

## 4. 接口对齐

### 4.1 Evidence 格式对齐

Quant System 输出符合 SkillForge Evidence 规范：

```json
{
  "evidence_ref": "evidence://quant/{skill_id}/{hash}",
  "trace_id": "trace-quant-{uuid}",
  "timestamp": "2026-02-22T10:30:00Z",
  "skill_id": "kronos-predict",
  "status": "completed",
  "gate_decision": {
    "verdict": "ALLOW",
    "checks_passed": ["confidence_threshold", "context_valid"],
    "violations": []
  },
  "data": { ... },
  "data_hash": "sha256:abc123..."
}
```

### 4.2 Gate 决策格式对齐

```json
{
  "gate_name": "risk-guard",
  "gate_decision": "ALLOW",
  "next_action": "continue",
  "error_code": null,
  "evidence_refs": [
    {
      "issue_key": "TRADE-20260222001",
      "source_locator": "evidence://quant/risk-guard/...",
      "content_hash": "sha256:...",
      "tool_revision": "v1.0.0",
      "timestamp": "2026-02-22T10:30:00Z"
    }
  ]
}
```

### 4.3 审计日志格式对齐

```json
{
  "event_type": "skill_run",
  "event_data": {
    "skill_id": "veighna-execute",
    "run_id": "run-20260222001",
    "status": "completed"
  },
  "correlation_id": "corr-20260222001",
  "trace_context": {
    "parent_span": "span-skillforge-xxx",
    "span_id": "span-quant-yyy"
  },
  "timestamp": "2026-02-22T10:30:00Z"
}
```

---

## 5. Gate 规则对齐

Quant System Gate 规则语义与 SkillForge 一致：

| Gate 规则 | 语义 | 触发条件 |
|-----------|------|----------|
| `POSITION_LIMIT` | DENY | 仓位 > 阈值 |
| `DAILY_LOSS_LIMIT` | DENY | 日亏损 > 阈值 |
| `DRAWDOWN_LIMIT` | DENY | 回撤 > 阈值 |
| `CONFIDENCE_THRESHOLD` | WARN | 预测置信度 < 阈值 |
| `LIQUIDITY_CHECK` | WARN | 流动性不足 |

**裁决优先级**：
```
DENY > WARN > ALLOW
```

**Fail-Closed 规则**：
- Gate 检查超时 → DENY
- Gate 检查异常 → DENY
- Gate 配置缺失 → DENY

---

## 6. 调用边界

### 6.1 SkillForge → Quant System

```yaml
# SkillForge 通过标准接口调用 Quant System

endpoint: /api/v1/quant/skill/run
method: POST
request:
  skill_id: string
  input: object
  trace_context: object
  controls: object
response:
  status: enum [completed, failed, rejected]
  data: object
  evidence_ref: string
  gate_decision: object
  trace_id: string
```

### 6.2 Quant System → SkillForge

```yaml
# Quant System 回调 SkillForge (可选)

endpoint: /api/v1/evidence/register
method: POST
request:
  evidence_ref: string
  evidence_data: object
  provenance: object
```

---

## 7. 合规验证

### 7.1 自检清单

- [x] 所有 Skill 输出包含 `evidence_ref`
- [x] Gate 检查失败时 `gate_decision = DENY`
- [x] 无"部分成功"状态
- [x] 错误码定义完整
- [x] 审计日志可追溯
- [x] 输出格式符合 Evidence 规范

### 7.2 对齐测试

```bash
# 验证输出格式对齐
pytest tests/test_constitution_alignment.py -v

# 验证 Gate 规则语义
pytest tests/test_gate_semantics.py -v
```

---

## 8. 变更原则

1. **宪法变更**：跟随 SkillForge 宪法版本更新
2. **接口变更**：需双方协商，保持向后兼容
3. **Gate 规则变更**：只能增强约束，不能放宽

---

## 9. 生效声明

本文档定义 Quant System 与 SkillForge 宪法的对齐关系。

Quant System 作为独立子系统，承诺遵循 SkillForge 宪法的核心原则，同时保持部署独立性。

---

*签署: GM Team*
*日期: 2026-02-22*
