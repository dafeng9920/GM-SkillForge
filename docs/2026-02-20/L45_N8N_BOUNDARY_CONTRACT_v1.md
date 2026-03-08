# L4.5 n8n Boundary Contract v1

> **Job ID**: L45-D1-N8N-BOUNDARY-20260220-001
> **Skill ID**: l45_n8n_orchestration_boundary
> **Version**: v1.0
> **Date**: 2026-02-20

---

## 1. 概述

本文档定义 n8n -> SkillForge 编排边界适配层的边界合同。

**核心原则**：
1. n8n 只做编排（trigger/route/retry/notify），不做最终裁决
2. SkillForge 负责最终裁决（GateDecision / Permit / EvidenceRef / AuditPack）
3. no-permit-no-release 永不放松
4. 所有拒绝分支必须返回结构化 error envelope（fail-closed）

---

## 2. 输入边界

### 2.1 白名单字段（允许 n8n 传入）

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `repo_url` | URI | ✓ | 仓库地址 |
| `commit_sha` | string (40-hex) | ✓ | 40 字符 commit SHA |
| `at_time` | ISO-8601 timestamp | ✓ | 时间戳（必须固定，禁止 "latest"） |
| `requester_id` | string | ✓ | 请求者标识 |
| `intent_id` | string | ✓ | 意图标识（如 "cognition_10d"） |
| `n8n_execution_id` | string | ○ | n8n 工作流执行 ID（可选，用于关联追踪） |

### 2.2 禁止字段（越权拦截）

| 字段 | 原因 |
|------|------|
| `gate_decision` | n8n 不能覆盖 Gate 决策 |
| `release_allowed` | n8n 不能绕过发布控制 |
| `evidence_ref` | n8n 不能注入伪造证据 |
| `permit_id` | n8n 不能注入 permit 引用 |

### 2.3 边界规则

1. **at_time 固定原则**：
   - 必须传入固定的 ISO-8601 时间戳
   - 禁止使用 "latest"、"now"、"current"、"today" 等自动漂移值
   - 目的：确保执行可复现、可回放

2. **commit_sha 格式验证**：
   - 必须是 40 字符十六进制字符串
   - 正则：`^[0-9a-f]{40}$`

3. **白名单严格性**：
   - 仅允许上述白名单字段
   - 任何未知字段触发 `N8N-WHITELIST-VIOLATION` 错误

---

## 3. 输出边界

### 3.1 run_intent 成功响应

```json
{
  "run_id": "RUN-N8N-20260220-A1B2C3",
  "status": "ACCEPTED",
  "intent_id": "cognition_10d",
  "n8n_execution_id": "n8n-exec-xyz123",
  "boundary_validated": true,
  "forbidden_fields_detected": [],
  "created_at": "2026-02-20T10:00:00Z"
}
```

### 3.2 fetch_pack 成功响应

```json
{
  "run_id": "RUN-N8N-20260220-A1B2C3",
  "intent_id": "cognition_10d",
  "gate_decision": {
    "decision": "PASS",
    "level_min": "L3",
    "rejection_reasons": []
  },
  "evidence_ref": [
    {
      "ref_id": "EV-001",
      "type": "audit_pack",
      "path": "AuditPack/runs/RUN-N8N-20260220-A1B2C3/"
    }
  ],
  "audit_pack_ref": "AuditPack/runs/RUN-N8N-20260220-A1B2C3/",
  "replay_pointer": {
    "at_time": "2026-02-19T12:00:00Z",
    "commit_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
    "revision": "v1.0.0"
  },
  "generated_at": "2026-02-20T10:05:00Z"
}
```

### 3.3 关键输出字段说明

| 字段 | 来源 | 说明 |
|------|------|------|
| `run_id` | SkillForge | 唯一执行标识 |
| `gate_decision` | SkillForge | 最终 Gate 决策（**n8n 无法覆盖**） |
| `evidence_ref` | SkillForge | 证据引用链 |
| `audit_pack_ref` | SkillForge | AuditPack 位置（仅 PASS 时存在） |
| `replay_pointer` | SkillForge | 回放指针（用于 at-time 复现） |

---

## 4. 错误信封（Error Envelope）

### 4.1 结构化错误格式

所有拒绝分支必须返回以下结构：

```json
{
  "error_code": "N8N-FORBIDDEN-FIELD",
  "error_message": "Forbidden field detected: gate_decision. n8n cannot set gate_decision.",
  "details": {
    "forbidden_fields": ["gate_decision"],
    "allowed_fields": ["repo_url", "commit_sha", "at_time", "requester_id", "intent_id", "n8n_execution_id"]
  },
  "timestamp": "2026-02-20T10:00:00Z"
}
```

### 4.2 错误代码表

| 错误代码 | HTTP 状态 | 说明 |
|----------|-----------|------|
| `N8N-FORBIDDEN-FIELD` | 400 | 检测到禁止字段（越权尝试） |
| `N8N-WHITELIST-VIOLATION` | 400 | 检测到未知字段 |
| `N8N-AT-TIME-FIXED-REQUIRED` | 400 | at_time 使用了禁止的自动漂移值 |
| `N8N-MISSING-REQUIRED-FIELD` | 400 | 缺少必需字段 |
| `MEMBERSHIP-CAPABILITY-DENIED` | 403 | 会员层级不具备 n8n 执行能力 |
| `MEMBERSHIP-QUOTA-EXCEEDED` | 403 | 会员配额已用尽 |
| `MEMBERSHIP-RATE-LIMITED` | 429 | 请求频率超限 |
| `INTERNAL-ERROR` | 500 | 内部错误 |

### 4.3 Fail-Closed 原则

1. **禁止字段命中**：立即拒绝，不进入后续处理
2. **白名单违规**：立即拒绝，不进入后续处理
3. **会员能力不足**：立即拒绝，不创建 run_id
4. **格式错误**：立即拒绝，返回具体错误信息

---

## 5. API 端点定义

### 5.1 POST /n8n/run_intent

**用途**：n8n 触发意图执行

**请求**：
```json
{
  "repo_url": "https://github.com/skillforge/workflow-orchestration",
  "commit_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
  "at_time": "2026-02-19T12:00:00Z",
  "requester_id": "user-kior-b",
  "intent_id": "cognition_10d",
  "n8n_execution_id": "n8n-exec-xyz123"
}
```

**响应**：见 [3.1 run_intent 成功响应](#31-run_intent-成功响应)

### 5.2 GET /n8n/fetch_pack

**用途**：获取执行包（证据、决策、审计）

**参数**：
- `run_id` (必需)：执行标识
- `n8n_execution_id` (可选)：n8n 执行 ID

**响应**：见 [3.2 fetch_pack 成功响应](#32-fetch_pack-成功响应)

### 5.3 GET /n8n/query_rag

**用途**：带 at_time 的 RAG 查询

**参数**：
- `query` (必需)：查询字符串
- `at_time` (必需，固定时间戳)：时间旅行查询
- `n8n_execution_id` (可选)：n8n 执行 ID

**响应**：
```json
{
  "query": "cognition results",
  "at_time": "2026-02-19T12:00:00Z",
  "results": [
    {
      "content": "...",
      "source_ref": "...",
      "relevance_score": 0.95
    }
  ],
  "replay_pointer": {
    "at_time": "2026-02-19T12:00:00Z"
  },
  "generated_at": "2026-02-20T10:00:00Z"
}
```

---

## 6. 会员策略集成

### 6.1 n8n 执行前置检查

在 `run_intent` 执行前，调用 `check_execute_via_n8n` 中间件：

```python
from contracts.policy.membership_middleware import check_execute_via_n8n

result = check_execute_via_n8n(
    tier=user.tier,
    permit_status=permit.status,
    execution_contract_present=True,
    tombstone_state=None,
    enabled_addons=user.enabled_addons,
    current_concurrent_jobs=current_jobs,
)

if not result.allowed:
    # 返回结构化错误信封
    return error_response(result)
```

### 6.2 检查项

| 检查类型 | 说明 |
|----------|------|
| capability | `EXECUTE_VIA_N8N` 能力 |
| required_checks | permit 状态、执行合同、tombstone 状态 |
| quota | `max_concurrent_exec_jobs` 并发限制 |

---

## 7. 实现文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `skillforge/src/contracts/api/n8n_boundary_v1.yaml` | 合同 | OpenAPI 3.0.3 定义 |
| `skillforge/src/api/routes/n8n_boundary_adapter.py` | 代码 | 边界适配器实现 |
| `docs/2026-02-20/L45_N8N_BOUNDARY_CONTRACT_v1.md` | 文档 | 本文档 |

---

## 8. 验收检查

### 8.1 自动检查

```bash
# 会员策略回归测试
pytest -q skillforge/tests/test_membership_regression.py
# 预期：passed

# 会员策略单元测试
pytest -q skillforge/tests/test_membership_policy.py
# 预期：passed
```

### 8.2 手动检查

- [ ] 边界合同文档与 machine contract 字段一致
- [ ] 禁止字段命中时返回 fail-closed
- [ ] at_time "latest" 被正确拦截
- [ ] 白名单外的未知字段被正确拦截

---

## 9. 变更历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-02-20 | 初始版本，定义 n8n 边界合同 |
