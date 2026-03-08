# Permit Contract 字段映射

> **版本**: v1.0.0
> **更新时间**: 2026-02-18
> **契约文件**: `docs/2026-02-18/permit_contract_v1_spec.md`

---

## 1. 映射概述

本文档将 `permit_contract_v1` 契约字段映射到 Skill 的执行输入/输出。

---

## 2. 签发输入映射

### 2.1 执行上下文映射

| 契约字段 | Skill 输入字段 | 类型 | 必填 | 说明 |
|----------|----------------|------|------|------|
| `subject.repo_url` | `repo_url` | string | ✅ | 仓库URL |
| `subject.commit_sha` | `commit_sha` | string | ✅ | Git提交SHA |
| `subject.run_id` | `run_id` | string | ✅ | 运行ID |
| `subject.intent_id` | `intent_id` | string | ✅ | 意图ID |
| `subject.entry_path` | `entry_path` | string | ❌ | 入口路径 |
| `constraints.at_time` | `at_time` | string | ✅ | 时间锚点 |

### 2.2 Gate 结果映射

| 契约字段 | Skill 输入字段 | 类型 | 必填 | 说明 |
|----------|----------------|------|------|------|
| `decision_binding.final_gate_decision` | `final_gate_decision` | string | ✅ | Gate决策 |
| `decision_binding.audit_pack_ref` | `audit_pack_ref` | string | ✅ | 审计包引用 |
| `decision_binding.gate_count` | `gate_count` | int | ❌ | Gate数量 |
| `decision_binding.evidence_count` | `evidence_count` | int | ❌ | Evidence数量 |

### 2.3 签发配置映射

| 契约字段 | Skill 输入字段 | 类型 | 默认值 | 说明 |
|----------|----------------|------|--------|------|
| `constraints.time_window_seconds` | `ttl_seconds` | int | 3600 | 有效期（秒） |
| `scope.allowed_actions` | `allowed_actions` | [string] | ["release"] | 允许动作 |
| `scope.environment` | `environment` | string | development | 目标环境 |
| `scope.gate_profile` | `gate_profile` | string | batch2_8gate | Gate配置 |

---

## 3. 签发输出映射

### 3.1 Permit 结构映射

| 契约字段 | Skill 输出字段 | 类型 | 说明 |
|----------|----------------|------|------|
| `permit_id` | `permit_id` | string | Permit ID |
| `issued_at` | `issued_at` | string | 签发时间 |
| `expires_at` | `expires_at` | string | 过期时间 |
| `issuer.issuer_id` | `issuer_id` | string | 签发者ID |
| `issuer.issuer_type` | `issuer_type` | string | 签发者类型 |
| - | `permit_token` | string | JSON序列化的完整permit |
| - | `success` | bool | 签发成功标志 |

### 3.2 签名结构映射

| 契约字段 | Skill 输出字段 | 类型 | 说明 |
|----------|----------------|------|------|
| `signature.algo` | `signature.algo` | string | 签名算法 |
| `signature.value` | `signature.value` | string | 签名值 |
| `signature.key_id` | `signature.key_id` | string | 密钥ID |
| `signature.signed_at` | `signature.signed_at` | string | 签名时间 |

### 3.3 错误码映射

| 契约错误码 | Skill 错误码 | 触发条件 |
|------------|--------------|----------|
| I001 | I001 | 签发条件不满足 |
| I002 | I002 | subject 字段不完整 |
| I003 | I003 | TTL 非法 |
| I004 | I004 | 签名密钥不可用 |
| I005 | I005 | 签名失败 |

---

## 4. 验签输入映射

### 4.1 Permit Token 映射

| 契约字段 | Skill 输入字段 | 类型 | 说明 |
|----------|----------------|------|------|
| 完整 permit JSON | `permit_token` | string | JSON序列化的permit |

### 4.2 执行上下文映射

| 契约字段 | Skill 输入字段 | 类型 | 必填 | 说明 |
|----------|----------------|------|------|------|
| `subject.repo_url` | `repo_url` | string | ✅ | 仓库URL（用于匹配） |
| `subject.commit_sha` | `commit_sha` | string | ✅ | 提交SHA（用于匹配） |
| `subject.run_id` | `run_id` | string | ✅ | 运行ID（用于匹配） |
| - | `requested_action` | string | ✅ | 请求动作 |
| - | `current_time` | string | ❌ | 当前时间（用于过期检查） |

---

## 5. 验签输出映射

### 5.1 校验结果映射

| 契约字段 | Skill 输出字段 | 类型 | 说明 |
|----------|----------------|------|------|
| - | `gate_name` | string | 固定值 "permit_gate" |
| - | `gate_decision` | string | ALLOW 或 BLOCK |
| - | `permit_validation_status` | string | VALID 或 INVALID |
| - | `release_allowed` | bool | 是否允许发布 |
| - | `release_blocked_by` | string | 阻断原因 |
| `permit_id` | `permit_id` | string | Permit ID |
| - | `validation_timestamp` | string | 校验时间戳 |

### 5.2 错误码映射

| 契约错误码 | Skill 错误码 | release_blocked_by | 触发条件 |
|------------|--------------|-------------------|----------|
| E001 | E001 | PERMIT_REQUIRED | permit_token 缺失 |
| E002 | E002 | PERMIT_INVALID | 格式无效/字段缺失 |
| E003 | E003 | PERMIT_INVALID | 签名校验失败 |
| E004 | E004 | PERMIT_EXPIRED | 已过期 |
| E005 | E005 | PERMIT_SCOPE_MISMATCH | 作用域不匹配 |
| E006 | E006 | PERMIT_SUBJECT_MISMATCH | 主体不匹配 |
| E007 | E007 | PERMIT_REVOKED | 已撤销 |

---

## 6. Evidence 字段映射

### 6.1 签发 Evidence

| 契约要求 | Skill Evidence 字段 | 说明 |
|----------|---------------------|------|
| gate_decision_evidence | `issue_key` | Evidence ID |
| audit_pack_evidence | `source_locator` | 来源定位 |
| subject_verification_evidence | `decision_snapshot.subject_match` | 主体验证 |
| - | `content_hash` | 内容哈希 |
| - | `tool_revision` | 工具版本 |
| - | `timestamp` | 时间戳 |

### 6.2 验签 Evidence

| 契约要求 | Skill Evidence 字段 | 说明 |
|----------|---------------------|------|
| permit_token_evidence | `source_locator` | permit://{permit_id} |
| signature_verification_evidence | `decision_snapshot.signature_valid` | 签名校验结果 |
| subject_match_evidence | `decision_snapshot.subject_match` | 主体匹配结果 |
| - | `issue_key` | Evidence ID |
| - | `content_hash` | 内容哈希 |

---

## 7. 完整 Permit JSON 示例

### 7.1 签发后 permit_token 结构

```json
{
  "permit_id": "PERMIT-20260218-BIZ-PHASE1-001",
  "issuer": {
    "issuer_id": "skillforge-permit-service",
    "issuer_type": "AUTOMATED_GATE"
  },
  "issued_at": "2026-02-18T17:00:05Z",
  "expires_at": "2026-02-19T05:00:05Z",
  "subject": {
    "repo_url": "github.com/example/skillforge-skills",
    "commit_sha": "c3d4e5f67890123456789012345678901234abcd",
    "run_id": "RUN-20260218-BIZ-PHASE1-001",
    "intent_id": "INTENT-20260218-SKILL-UPDATE-001",
    "entry_path": null
  },
  "scope": {
    "allowed_actions": ["release"],
    "environment": "staging",
    "gate_profile": "batch2_8gate"
  },
  "constraints": {
    "at_time": "2026-02-18T17:00:00Z",
    "max_release_count": 1,
    "time_window_seconds": 43200
  },
  "decision_binding": {
    "final_gate_decision": "PASSED",
    "gate_count": 8,
    "audit_pack_ref": "audit-10465f76",
    "evidence_count": 8
  },
  "signature": {
    "algo": "HS256",
    "value": "base64_encoded_signature...",
    "key_id": "skillforge-permit-key-2026",
    "signed_at": "2026-02-18T17:00:05Z"
  },
  "revocation": {
    "revoked": false,
    "revoked_at": null,
    "revoked_by": null,
    "reason": null
  }
}
```

### 7.2 验签输出示例（成功）

```json
{
  "gate_name": "permit_gate",
  "gate_decision": "ALLOW",
  "permit_validation_status": "VALID",
  "release_allowed": true,
  "release_blocked_by": null,
  "error_code": null,
  "permit_id": "PERMIT-20260218-BIZ-PHASE1-001",
  "evidence_refs": [
    {
      "issue_key": "PERMIT-VAL-PERMIT-20260218-BIZ-PHASE1-001-1708280405",
      "source_locator": "permit://PERMIT-20260218-BIZ-PHASE1-001",
      "content_hash": "sha256:abc123...",
      "tool_revision": "1.0.0",
      "timestamp": "2026-02-18T17:00:05Z",
      "decision_snapshot": {
        "check": "all_passed",
        "permit_id": "PERMIT-20260218-BIZ-PHASE1-001",
        "subject_match": true,
        "scope_match": true
      }
    }
  ],
  "validation_timestamp": "2026-02-18T17:00:05Z"
}
```

### 7.3 验签输出示例（E001 阻断）

```json
{
  "gate_name": "permit_gate",
  "gate_decision": "BLOCK",
  "permit_validation_status": "INVALID",
  "release_allowed": false,
  "release_blocked_by": "PERMIT_REQUIRED",
  "error_code": "E001",
  "permit_id": null,
  "evidence_refs": [
    {
      "issue_key": "PERMIT-BLOCK-E001-1708280405",
      "source_locator": "permit://none",
      "content_hash": "sha256:def456...",
      "tool_revision": "1.0.0",
      "timestamp": "2026-02-18T17:00:05Z",
      "decision_snapshot": {
        "check": "existence",
        "permit_token_present": false
      }
    }
  ],
  "validation_timestamp": "2026-02-18T17:00:05Z",
  "reason": "Permit token is missing"
}
```

---

## 8. 实现文件引用

| 能力 | 实现文件 | 契约校验 |
|------|----------|----------|
| 签发 | `skillforge/src/skills/gates/permit_issuer.py` | `PermitIssuer.issue_permit()` |
| 验签 | `skillforge/src/skills/gates/gate_permit.py` | `GatePermit.execute()` |
| 契约定义 | `docs/2026-02-18/permit_contract_v1_spec.md` | - |

---

*文档版本: v1.0.0 | 创建时间: 2026-02-18*
