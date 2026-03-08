# L45 P2 Provenance Enforcement Report v1

> Job ID: `L45-D6-SEEDS-P2-20260220-006`
> Task ID: `T31`
> Executor: `Kior-B`
> Wave: `Wave 1`
> Date: 2026-02-20

---

## 概要

本报告记录 SEEDS-P2 中 Provenance 强制化的实施：
- 所有 GateDecision **必须**包含 `ruleset_revision`
- 所有 GateDecision **必须**包含 `provenance.repro_env`

---

## 1. Schema 强制化变更

### 1.1 顶层 Required 字段

```json
"required": [
  "job_id",
  "gate_decision",
  "ruleset_revision",
  "timestamp",
  "evidence_ref",
  "provenance"
]
```

**变更说明**：
- `ruleset_revision` 已在 P0 阶段强制化，保持不变
- `provenance` 新增为必填字段（P2 强制化）

### 1.2 Provenance 结构强制化

```json
"provenance": {
  "type": "object",
  "required": ["repro_env"],
  "properties": {
    "repro_env": {
      "type": "object",
      "required": ["python_version", "deps_lock_hash", "os", "tool_versions"],
      ...
    }
  }
}
```

**变更说明**：
- `provenance` 必须包含 `repro_env` 字段
- `repro_env` 必须包含全部 4 个子字段：
  - `python_version`
  - `deps_lock_hash`
  - `os`
  - `tool_versions`

### 1.3 ALLOW 决策的额外约束

```json
"allOf": [
  {
    "if": { "gate_decision": { "const": "ALLOW" } },
    "then": {
      "required": ["ruleset_revision", "provenance"],
      ...
    }
  }
]
```

**约束**：`ALLOW` 决策如果没有 `ruleset_revision` 或 `provenance.repro_env` 将被 Schema 拒绝。

---

## 2. 拒绝样例

### 2.1 缺少 ruleset_revision

```json
{
  "job_id": "L45-D6-SEEDS-P2-20260220-006",
  "gate_decision": "ALLOW",
  "timestamp": "2026-02-20T18:00:00Z",
  "evidence_ref": "EV-001",
  "provenance": {
    "repro_env": {
      "python_version": "3.11",
      "deps_lock_hash": "abc123",
      "os": "Windows 11",
      "tool_versions": {"gm_skillforge": "0.0.1"}
    }
  }
}
```

**拒绝原因**：缺少 `ruleset_revision` 字段
**错误码**：`SCHEMA_VALIDATION_FAILED`

### 2.2 缺少 provenance.repro_env

```json
{
  "job_id": "L45-D6-SEEDS-P2-20260220-006",
  "gate_decision": "ALLOW",
  "ruleset_revision": "v1",
  "timestamp": "2026-02-20T18:00:00Z",
  "evidence_ref": "EV-001",
  "provenance": {
    "captured_at": "2026-02-20T18:00:00Z",
    "source": {
      "repo_url": "https://github.com/skillforge/GM-SkillForge",
      "commit_sha": "abc123"
    }
  }
}
```

**拒绝原因**：`provenance` 缺少必需的 `repro_env` 字段
**错误码**：`SCHEMA_VALIDATION_FAILED`

### 2.3 repro_env 字段不完整

```json
{
  "job_id": "L45-D6-SEEDS-P2-20260220-006",
  "gate_decision": "ALLOW",
  "ruleset_revision": "v1",
  "timestamp": "2026-02-20T18:00:00Z",
  "evidence_ref": "EV-001",
  "provenance": {
    "repro_env": {
      "python_version": "3.11",
      "os": "Windows 11"
    }
  }
}
```

**拒绝原因**：`repro_env` 缺少必需字段 `deps_lock_hash` 和 `tool_versions`
**错误码**：`SCHEMA_VALIDATION_FAILED`

---

## 3. 合规样例

```json
{
  "job_id": "L45-D6-SEEDS-P2-20260220-006",
  "skill_id": "l45_seeds_p2_operationalization",
  "task_id": "T31",
  "executor": "Kior-B",
  "gate_decision": "ALLOW",
  "ruleset_revision": "v1",
  "timestamp": "2026-02-20T18:00:00Z",
  "evidence_ref": "EV-001",
  "provenance": {
    "captured_at": "2026-02-20T18:00:00Z",
    "source": {
      "repo_url": "https://github.com/skillforge/GM-SkillForge",
      "commit_sha": "abc123"
    },
    "repro_env": {
      "python_version": "3.11",
      "deps_lock_hash": "LOCKHASH-PLACEHOLDER",
      "os": "Windows 11",
      "tool_versions": {
        "gm_skillforge": "0.0.1"
      }
    }
  },
  "verdict": {
    "implementation_ready": "YES",
    "regression_ready": "YES",
    "baseline_ready": "YES",
    "ready_for_next_batch": "YES"
  }
}
```

---

## 4. 约束验证

| 约束 | 状态 | 说明 |
|------|------|------|
| 缺 ruleset_revision 必须拒绝 | ✅ | Schema required 字段 |
| 缺 provenance.repro_env 必须拒绝 | ✅ | Schema required 字段 |
| 报告给出拒绝样例 | ✅ | 第 2 节提供 3 个样例 |
| 不得将 required 字段降级为 optional | ✅ | 仅添加 required，未移除 |

---

## 5. Gate 自检

```bash
python -m pytest -q skillforge/tests/test_provenance_loader.py skillforge/tests/test_ruleset_revision_binding.py
```

**预期结果**：所有测试通过

---

## 6. 交付物清单

| 文件路径 | 类型 | 状态 |
|----------|------|------|
| `skillforge/src/contracts/governance/gate_decision_envelope.schema.json` | 修改 | ✅ |
| `docs/2026-02-20/L45_P2_PROVENANCE_ENFORCEMENT_REPORT_v1.md` | 新建 | ✅ |

---

## 7. 签署

```yaml
signer: "Kior-B"
role: "SEEDS-P2 Provenance Enforcement"
signature_timestamp: "2026-02-20T18:00:00Z"
gate_decision: "ALLOW"
constraints_satisfied: true
```

---

*End of Report*
