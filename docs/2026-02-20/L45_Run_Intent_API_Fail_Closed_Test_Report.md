# L4.5 run_intent API Fail-Closed 测试报告

> **测试时间**: 2026-02-20
> **测试环境**: 本地开发环境
> **API 端点**: `http://127.0.0.1:8000/api/v1/n8n/run_intent`

---

## 1. 测试概述

验证 `run_intent` API 的 Fail-Closed 机制，确保在各种边界条件下正确阻断非法请求。

---

## 2. 测试场景与结果

### 场景 1: FREE 层访问（会员能力不足）

**请求**:
```json
{
  "repo_url": "https://github.com/genesismind-bot/GM-SkillForge.git",
  "commit_sha": "0000000000000000000000000000000000000001",
  "at_time": "2026-02-20T15:00:00Z",
  "requester_id": "ops-l45",
  "intent_id": "cognition_10d",
  "tier": "FREE"
}
```

**响应**:
```json
{
  "ok": false,
  "error_code": "N8N_MEMBERSHIP_DENIED",
  "blocked_by": "MEMBERSHIP_CAPABILITY_DENIED",
  "message": "Tier FREE does not have capability: EXECUTE_VIA_N8N",
  "run_id": "RUN-N8N-1771569325-F4F3754F",
  "evidence_ref": "EV-N8N-INTENT-1771569325-C2455CF7"
}
```

**验证点**:
- ✅ 错误码正确: `N8N_MEMBERSHIP_DENIED`
- ✅ 阻断原因明确: `MEMBERSHIP_CAPABILITY_DENIED`
- ✅ run_id 生成: `RUN-N8N-...`
- ✅ evidence_ref 生成: `EV-N8N-...`

---

### 场景 2: STUDIO 层无 Permit（需要有效 permit）

**请求**:
```json
{
  "repo_url": "https://github.com/genesismind-bot/GM-SkillForge.git",
  "commit_sha": "0000000000000000000000000000000000000001",
  "at_time": "2026-02-20T15:00:00Z",
  "requester_id": "ops-l45",
  "intent_id": "cognition_10d",
  "tier": "STUDIO"
}
```

**响应**:
```json
{
  "ok": false,
  "error_code": "N8N_MEMBERSHIP_DENIED",
  "blocked_by": "MEMBERSHIP_REQUIRED_CHECK_FAILED",
  "message": "Required condition not met: permit.status: VALID",
  "run_id": "RUN-N8N-1771572851-5840D4B8",
  "evidence_ref": "EV-N8N-INTENT-1771572851-032CF866"
}
```

**验证点**:
- ✅ 会员能力通过（tier: STUDIO 生效）
- ✅ Permit 校验触发: `permit.status: VALID`
- ✅ 证据链完整

---

### 场景 3: Permit Token 注入攻击（禁止字段）

**请求**:
```json
{
  "repo_url": "https://github.com/genesismind-bot/GM-SkillForge.git",
  "commit_sha": "0000000000000000000000000000000000000001",
  "at_time": "2026-02-20T15:00:00Z",
  "requester_id": "ops-l45",
  "intent_id": "cognition_10d",
  "tier": "STUDIO",
  "permit_token": "{...伪造 permit...}"
}
```

**响应**:
```json
{
  "ok": false,
  "error_code": "N8N_FORBIDDEN_FIELD_INJECTION",
  "blocked_by": "N8N_POLICY_VIOLATION",
  "message": "n8n attempted to inject forbidden fields: ['permit_token']. These fields are computed by SkillForge only.",
  "run_id": "RUN-N8N-1771573486-81FB19B7",
  "evidence_ref": "EV-N8N-INTENT-1771573486-A5648034",
  "forbidden_field_evidence": {
    "issue_key": "N8N-FORBIDDEN-RUN-N8N-1771573486-81FB19B7",
    "forbidden_fields": ["permit_token"],
    "action_taken": "REJECTED_AND_IGNORED"
  }
}
```

**验证点**:
- ✅ 禁止字段检测: `permit_token`
- ✅ 阻断动作: `REJECTED_AND_IGNORED`
- ✅ 安全审计记录: `forbidden_field_evidence`

---

## 3. Fail-Closed 验证总结

| 检查点 | 状态 | 说明 |
|--------|------|------|
| 会员策略阻断 | ✅ 通过 | FREE 层无法执行 n8n |
| Permit 校验 | ✅ 通过 | 无有效 permit 被阻断 |
| 禁止字段注入 | ✅ 通过 | permit_token 不可外部注入 |
| run_id 生成 | ✅ 通过 | 每次请求生成唯一 run_id |
| evidence_ref 生成 | ✅ 通过 | 证据链完整 |
| 错误码语义 | ✅ 通过 | 错误码与 SKILL.md 一致 |

---

## 4. 最终结论（已闭环）

### 状态更新

| 状态 | 说明 |
|------|------|
| ✅ Fail-Closed 正常 | 外部注入 `permit_token` 会被阻断（`N8N_FORBIDDEN_FIELD_INJECTION`） |
| ✅ 成功链路可达 | `run_intent` 已接入内部 `PermitIssuer`，可走到 `ALLOW` |
| ✅ 设计矛盾已消除 | "禁止外部 permit" 与 "内部签发+校验 permit" 已统一 |

### 运行前提

| 前提 | 说明 |
|------|------|
| `PERMIT_HS256_KEY` | 运行时需配置签名密钥 |
| 会员层级 | 需有 `EXECUTE_VIA_N8N` 能力（如 `STUDIO`） |

### 验证结果

- `skillforge/tests/test_n8n_run_intent_internal_permit.py`: **19 passed** ✅

### 设计统一

```
n8n 请求 → 禁止外部 permit_token → SkillForge 内部 PermitIssuer 签发 → GatePermit 校验 → ALLOW
```

**API 设计已闭环，可进入生产验证阶段。**

---

## 5. 证据清单

| 文件 | 说明 |
|------|------|
| [n8n_orchestration.py](../../skillforge/src/api/routes/n8n_orchestration.py) | API 实现 |
| [membership_tiers.yml](../../skillforge/src/contracts/policy/membership_tiers.yml) | 会员策略配置 |
| [l45_day2_mincap_runbook.md](./n8n/l45_day2_mincap_runbook.md) | 运行手册 |

---

**报告生成时间**: 2026-02-20
**报告状态**: ✅ FAIL-CLOSED 验证通过
