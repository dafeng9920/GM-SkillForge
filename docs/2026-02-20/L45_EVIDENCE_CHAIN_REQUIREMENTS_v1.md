# L4.5 Evidence Chain Requirements

> **版本**: v1.0
> **日期**: 2026-02-20
> **状态**: FROZEN
> **关联 Task**: T4 (vs--cc1)
> **job_id**: L45-D1-N8N-BOUNDARY-20260220-001

---

## 1. 概述

本文档定义 n8n 编排执行的证据链字段要求，确保审计链可回放、可追溯、可验证。

### 1.1 设计原则

| 原则 | 说明 |
|------|------|
| **不可绕过** | 每次调用都经过 Gate/Permit/EvidenceRef |
| **可回放** | 支持 at-time 回放审计 |
| **完整链路** | run_id 贯穿全链路 |
| **Fail-Closed** | 失败必须返回结构化错误信封 |

---

## 2. 核心字段定义

### 2.1 必填字段（所有场景）

| 字段 | 类型 | 格式 | 说明 |
|------|------|------|------|
| `receipt_id` | string | `RCP-L45-{UUID8}` | 执行回执唯一标识 |
| `run_id` | string | `RUN-L4-{ts}-{UUID8}` | 执行运行 ID，贯穿全链路 |
| `evidence_ref` | string | `EV-{prefix}-L4-{ts}-{UUID8}` | 主证据引用 |
| `gate_decision` | enum | `PASSED \| REJECTED \| BLOCKED` | Gate 判定结果 |
| `executed_at` | datetime | ISO-8601 | 执行完成时间戳 |
| `skill_id` | string | - | 被执行的 skill 标识 |
| `workflow_id` | string | - | n8n workflow 标识 |

### 2.2 条件必填字段

| 字段 | 条件 | 说明 |
|------|------|------|
| `audit_pack_ref` | `gate_decision == PASSED` | **通过分支必须**，完整审计包引用 |
| `error_code` | `gate_decision != PASSED` | **失败分支必须**，标准化错误码 |

### 2.3 可选但结构固定字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `replay_pointer` | object | 回放指针，内容可空但结构固定 |

#### replay_pointer 子结构

```json
{
  "replay_pointer": {
    "snapshot_ref": "string | null",
    "at_time": "ISO-8601 datetime | null",
    "revision": "string | null",
    "evidence_bundle_ref": "string | null"
  }
}
```

---

## 3. Evidence Ref 前缀分类

| 前缀 | 用途 | 示例 |
|------|------|------|
| `EV-COG` | 认知生成 | `EV-COG-L4-1739980000-A1B2C3D4` |
| `EV-ADOPT` | Work Item 采纳 | `EV-ADOPT-L4-1739980000-B2C3D4E5` |
| `EV-EXEC` | 执行回执 | `EV-EXEC-L4-1739980000-C3D4E5F6` |
| `EV-PERMIT` | Permit 签发 | `EV-PERMIT-L4-1739980000-D4E5F6G7` |
| `EV-AUDIT` | 审计报告 | `EV-AUDIT-L4-1739980000-E5F6G7H8` |

---

## 4. Gate Decision 语义

| Decision | 语义 | next_action | 必须字段 |
|----------|------|-------------|----------|
| `PASSED` | 执行成功，可继续 | `continue` | `audit_pack_ref` |
| `REJECTED` | 业务规则拒绝 | `halt` | `error_code`, `error_message` |
| `BLOCKED` | 系统/安全约束阻断 | `halt` | `error_code`, `error_message` |

---

## 5. 错误码映射

| 错误码 | 语义 | gate_decision | release_allowed |
|--------|------|---------------|-----------------|
| `E001` | PERMIT_REQUIRED | REJECTED | false |
| `E003` | PERMIT_INVALID_SIGNATURE | BLOCKED | false |
| `L4_LLM_CONFIG_MISSING` | LLM 配置缺失 | BLOCKED | false |
| `L4_LLM_CALL_FAILED` | LLM 调用失败 | BLOCKED | false |

---

## 6. 最小样例

### 6.1 成功场景（PASSED）

```json
{
  "receipt_id": "RCP-L45-A1B2C3D4",
  "run_id": "RUN-L4-1739980000-A1B2C3D4",
  "evidence_ref": "EV-EXEC-L4-1739980000-A1B2C3D4",
  "gate_decision": "PASSED",
  "executed_at": "2026-02-20T10:30:00Z",
  "skill_id": "l45_n8n_orchestration_boundary",
  "workflow_id": "wf_12345",
  "job_id": "L45-D1-N8N-BOUNDARY-20260220-001",
  "permit_token": "PERMIT-L4-1739980000-XYZ123",
  "audit_pack_ref": "audit://packs/L45-D1-20260220-001",
  "replay_pointer": {
    "snapshot_ref": "snapshot://L45-D1-20260220-001/v1",
    "at_time": "2026-02-20T10:30:00Z",
    "revision": "v1.0.0",
    "evidence_bundle_ref": "evidence://bundles/L45-D1-20260220-001"
  },
  "evidence_chain": {
    "evidence_refs": [
      {
        "ref_id": "EV-COG-L4-1739980000-A1B2C3D4",
        "type": "cognition",
        "source_locator": "cognition://dims/1739980000-A1B2C3D4",
        "content_hash": "sha256:abc123...",
        "timestamp": "2026-02-20T10:29:30Z",
        "tool_revision": "v1.0.0"
      },
      {
        "ref_id": "EV-PERMIT-L4-1739980000-XYZ123",
        "type": "permit",
        "source_locator": "permit://tokens/XYZ123",
        "content_hash": "sha256:def456...",
        "timestamp": "2026-02-20T10:29:45Z",
        "tool_revision": "v1.0.0"
      }
    ]
  },
  "output": {
    "status": "success",
    "data": {
      "dimensions": 10,
      "processed": true
    },
    "metrics": {
      "duration_ms": 1500,
      "tokens_used": 500
    }
  }
}
```

### 6.2 失败场景（E001 - 无 Permit）

```json
{
  "receipt_id": "RCP-L45-E5F6G7H8",
  "run_id": "RUN-L4-1739980500-E5F6G7H8",
  "evidence_ref": "EV-EXEC-L4-1739980500-E5F6G7H8",
  "gate_decision": "REJECTED",
  "error_code": "E001",
  "error_message": "Permit required but not provided",
  "executed_at": "2026-02-20T10:35:00Z",
  "skill_id": "l45_n8n_orchestration_boundary",
  "workflow_id": "wf_12345",
  "job_id": "L45-D1-N8N-BOUNDARY-20260220-002",
  "replay_pointer": {
    "snapshot_ref": null,
    "at_time": "2026-02-20T10:35:00Z",
    "revision": null,
    "evidence_bundle_ref": null
  },
  "output": {
    "status": "failure"
  }
}
```

### 6.3 阻断场景（E003 - 坏签名）

```json
{
  "receipt_id": "RCP-L45-I9J0K1L2",
  "run_id": "RUN-L4-1739981000-I9J0K1L2",
  "evidence_ref": "EV-EXEC-L4-1739981000-I9J0K1L2",
  "gate_decision": "BLOCKED",
  "error_code": "E003",
  "error_message": "Permit signature validation failed",
  "executed_at": "2026-02-20T10:40:00Z",
  "skill_id": "l45_n8n_orchestration_boundary",
  "workflow_id": "wf_12345",
  "job_id": "L45-D1-N8N-BOUNDARY-20260220-003",
  "permit_token": "INVALID_TOKEN",
  "replay_pointer": {
    "snapshot_ref": null,
    "at_time": "2026-02-20T10:40:00Z",
    "revision": null,
    "evidence_bundle_ref": null
  },
  "output": {
    "status": "failure"
  }
}
```

---

## 7. 与现有 Schema 的关系

### 7.1 引用关系

```
work_item_schema.json
    └── 引用 execution_receipt (新增)
            ├── run_id (贯穿全链路)
            ├── evidence_ref (主证据)
            ├── gate_decision (Gate 判定)
            └── replay_pointer (回放指针)
```

### 7.2 不破坏的已有字段

以下 work_item_schema 必填字段保持不变：
- `work_item_id`
- `intent`
- `inputs`
- `constraints`
- `acceptance`
- `evidence`
- `adopted_from`

---

## 8. 验收标准

| # | 标准 | 验证方式 |
|---|------|----------|
| 1 | `run_id`、`evidence_ref`、`gate_decision` 为必填 | schema required 检查 |
| 2 | 通过分支必须有 `audit_pack_ref` | schema allOf 条件检查 |
| 3 | `replay_pointer` 可空但结构固定 | schema nullable + properties 检查 |
| 4 | 不破坏已有 work_item schema 必填字段 | 兼容性测试 |
| 5 | 与 T1/T2 输出字段名称一致 | 字段对齐检查 |

---

## 9. 关联文档

- [external_skill_governance_contract_v1.yaml](../2026-02-19/contracts/external_skill_governance_contract_v1.yaml)
- [gate_interface_v1.yaml](../../skillforge/src/contracts/gates/gate_interface_v1.yaml)
- [work_item_schema.json](../../skillforge/src/contracts/governance/work_item_schema.json)
- [n8n_execution_receipt.schema.json](../../skillforge/src/contracts/governance/n8n_execution_receipt.schema.json)

---

## 10. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0 | 2026-02-20 | 初始版本 | vs--cc1 |
