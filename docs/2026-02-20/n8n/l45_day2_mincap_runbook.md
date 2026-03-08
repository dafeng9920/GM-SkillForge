# L4.5 Day-2 MinCap E2E 工作流运行手册

> **Job ID**: `L45-D2-ORCH-MINCAP-20260220-002`
> **Skill ID**: `l45_orchestration_min_capabilities`
> **Wave**: Wave 2
> **Depends On**: T7, T8, T9
> **版本**: v2.0.0
> **创建日期**: 2026-02-20

---

## 1. 概述

本运行手册定义了 L4.5 Day-2 最小能力编排工作流的执行步骤和异常分支策略。

### 1.1 工作流定位

将 `run_intent` / `fetch_pack` / `query_rag` 三能力接入 n8n 实流，完成最小 E2E 演练。

### 1.2 核心目标

1. 跑通 1 条成功链路（`run_intent` → `fetch_pack` → `query_rag`）
2. 覆盖 2 条失败链路（E001 与 E003）
3. 验证业务错误禁止自动重试
4. 产出完整证据链（`run_id`/`evidence_ref`/`gate_decision`/`replay_pointer`）

---

## 2. 执行步骤

### 2.1 前置条件

1. n8n 实例已启动并可访问
2. SkillForge API 服务已启动（生产化版本）
3. T7/T8/T9 任务已完成（接口已生产化）
4. 环境变量已配置：
   - `SKILLFORGE_API_BASE`: SkillForge API 基础地址
   - `NOTIFICATION_WEBHOOK_SUCCESS`: 成功通知 webhook
   - `NOTIFICATION_WEBHOOK_FAILURE`: 失败通知 webhook
   - `NOTIFICATION_WEBHOOK_ERROR`: 错误通知 webhook

### 2.2 工作流导入

```bash
# 1. 导入工作流到 n8n
n8n import:workflow --input=docs/2026-02-20/n8n/l45_day2_mincap_workflow.json

# 2. 激活工作流
n8n activate --id=<workflow_id>
```

### 2.3 执行流程图

```
┌─────────────────┐
│ Webhook Trigger │ ◄── POST 请求
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate Input  │ ◄── 校验必填字段
└────────┬────────┘
         │
    ┌────┴────┐
    │ PASS?   │
    └────┬────┘
    YES  │  NO ──► Notify Validation Error
         │
         ▼
┌─────────────────────┐
│ Check Forbidden     │ ◄── 检测越权字段 + at_time 漂移值
│ Fields              │
└────────┬────────────┘
         │
    ┌────┴────────┐
    │ FORBIDDEN?  │
    └────┬────────┘
    NO   │  YES ──► Notify Forbidden Field
         │
         ▼
┌─────────────────┐
│ Call run_intent │ ◄── SkillForge API (T7 生产化版本)
└────────┬────────┘
         │
    ┌────┴────┐
    │ ok?     │
    └────┬────┘
    YES  │  NO ──► Notify Business Error (E001/E003)
         │
         ▼
┌─────────────────┐
│ Call fetch_pack │ ◄── SkillForge API (T8 生产化版本)
└────────┬────────┘
         │
    ┌────┴────┐
    │ ok?     │
    └────┬────┘
    YES  │  NO ──► Notify Business Error
         │
         ▼
┌─────────────────┐
│ Call query_rag  │ ◄── SkillForge API (T9 生产化版本)
└────────┬────────┘
         │
    ┌────┴────────────┐
    │gate_decision    │
    │  = ALLOW?       │
    └────┬────────────┘
    YES  │  NO ──► Notify Business Error
         │
         ▼
   Notify Success
   (含 replay_pointer)
```

### 2.4 输入参数规范

**允许字段（白名单）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo_url` | string | ✅ | 代码仓库 URL |
| `commit_sha` | string | ✅ | 提交 SHA（40字符十六进制） |
| `at_time` | string | ✅ | ISO-8601 时间戳（固定值，禁止漂移） |
| `requester_id` | string | ✅ | 请求者标识 |
| `intent_id` | string | ✅ | 意图标识 |
| `n8n_execution_id` | string | ❌ | n8n 执行 ID（自动填充） |

**禁止字段（越权拦截）：**

| 字段 | 原因 |
|------|------|
| `gate_decision` | n8n 不能覆盖 Gate 决策 |
| `release_allowed` | n8n 不能绕过发布控制 |
| `permit_token` | permit 由 SkillForge 内部签发，n8n 不可注入 |
| `evidence_ref` | n8n 不能注入伪造证据 |
| `permit_id` | n8n 不能注入 permit 引用 |
| `run_id` | run_id 由 SkillForge 内部生成 |

### 2.5 调用示例

```bash
curl -X POST https://n8n.example.com/webhook/skillforge/mincap/run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/skillforge/production-repo.git",
    "commit_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
    "at_time": "2026-02-20T14:30:00Z",
    "requester_id": "user@skillforge.dev",
    "intent_id": "cognition_10d"
  }'
```

---

## 3. 异常分支策略

### 3.1 失败分支类型

| 分支类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| 验证错误 | 缺少必填字段 | 立即阻断，不重试 |
| 越权字段 | 检测到禁止字段 | 立即阻断，不重试 |
| at_time 漂移 | 使用 "latest"/"now" 等 | 立即阻断，不重试 |
| E001 业务错误 | PERMIT_REQUIRED | 立即阻断，不重试 |
| E003 业务错误 | PERMIT_INVALID | 立即阻断，不重试 |
| 网络错误 | 连接超时 | 允许重试（最多3次） |

### 3.2 重试策略

**允许重试的错误：**

| 错误类型 | 错误码 | 重试策略 |
|----------|--------|----------|
| 网络错误 | `E_NETWORK` | 最多 3 次，间隔 5 秒 |
| 超时错误 | `E_TIMEOUT` | 最多 3 次，间隔 5 秒 |

**禁止重试的错误：**

| 错误类型 | 错误码 | 原因 |
|----------|--------|------|
| 无 Permit | `E001` | 业务阻断，需人工介入 |
| 坏签名 | `E003` | 业务阻断，需人工介入 |
| 越权字段 | `N8N-FORBIDDEN-FIELD` | 安全违规 |
| at_time 漂移 | `N8N-AT-TIME-FIXED-REQUIRED` | 输入错误 |

### 3.3 Fail-Closed 原则

1. **越权字段命中**：立即拒绝，记录证据，不进入后续处理
2. **业务错误 (E001/E003)**：立即阻断，返回 `required_changes`，不重试
3. **网络错误**：允许重试，超过重试次数后返回错误通知
4. **任何未知错误**：默认阻断，不静默降级

---

## 4. 接口行为（生产化版本）

### 4.1 run_intent (T7)

**关键行为**：
- `run_id` 由 SkillForge 内部生成（前缀 `RUN-N8N-`）
- 禁止 n8n 注入 `gate_decision`/`release_allowed`/`evidence_ref`/`permit_id`/`run_id`
- 输出包含 `run_id`/`gate_decision`/`evidence_ref`/`release_allowed`

**成功响应**：
```json
{
  "ok": true,
  "data": { ... },
  "gate_decision": "ALLOW",
  "release_allowed": true,
  "evidence_ref": "EV-N8N-INTENT-...",
  "run_id": "RUN-N8N-..."
}
```

**失败响应 (E001)**：
```json
{
  "ok": false,
  "error_code": "E001",
  "blocked_by": "PERMIT_REQUIRED",
  "message": "Permit token is required for execution",
  "evidence_ref": "EV-N8N-INTENT-...",
  "run_id": "RUN-N8N-..."
}
```

### 4.2 fetch_pack (T8)

**关键行为**：
- 支持通过 `run_id` 和/或 `evidence_ref` 读取
- 同时提供时执行一致性校验
- 返回体包含 `replay_pointer`（可空但字段存在）

**成功响应**：
```json
{
  "ok": true,
  "data": {
    "receipt_id": "RCP-L45-...",
    "run_id": "RUN-L4-...",
    "evidence_ref": "EV-EXEC-...",
    "gate_decision": "PASSED",
    "replay_pointer": {
      "snapshot_ref": "snapshot://...",
      "at_time": "2026-02-20T10:30:00Z",
      "revision": "v1.0.0"
    }
  }
}
```

### 4.3 query_rag (T9)

**关键行为**：
- `at_time` 必须为固定 ISO-8601 时间戳
- 禁止漂移值：`latest`/`now`/`current`/`today` 等
- 返回 `replay_pointer` 用于回放

**成功响应**：
```json
{
  "ok": true,
  "query": "audit_pack_summary",
  "at_time": "2026-02-20T14:30:00Z",
  "results": [ ... ],
  "replay_pointer": {
    "at_time": "2026-02-20T14:30:00Z",
    "repo_url": "...",
    "commit_sha": "..."
  }
}
```

---

## 5. 输出规范

### 5.1 成功响应

```json
{
  "status": "SUCCESS",
  "run_id": "RUN-N8N-1739980000-A1B2C3D4",
  "gate_decision": "ALLOW",
  "release_allowed": true,
  "evidence_ref": "EV-N8N-INTENT-...",
  "replay_pointer": {
    "snapshot_ref": "snapshot://L45-D2-20260220/v1",
    "at_time": "2026-02-20T14:30:00Z",
    "revision": "v1.0.0"
  },
  "intent_id": "cognition_10d",
  "repo_url": "https://github.com/skillforge/production-repo.git",
  "commit_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
  "n8n_execution_id": "exec-456",
  "timestamp": "2026-02-20T14:35:00Z"
}
```

### 5.2 失败响应（E001 - 无 Permit）

```json
{
  "status": "BLOCKED",
  "run_id": "RUN-N8N-1739980000-DEADBEEF",
  "gate_decision": "DENY",
  "error_code": "E001",
  "blocked_by": "PERMIT_REQUIRED",
  "message": "Permit token is required for execution",
  "evidence_ref": "EV-N8N-INTENT-...",
  "auto_retry": false,
  "note": "Business errors (E001/E003) must not auto-retry",
  "timestamp": "2026-02-20T14:36:00Z"
}
```

### 5.3 失败响应（E003 - 坏签名）

```json
{
  "status": "BLOCKED",
  "run_id": "RUN-N8N-1739980000-BADF00D",
  "gate_decision": "DENY",
  "error_code": "E003",
  "blocked_by": "PERMIT_INVALID",
  "message": "Permit signature validation failed",
  "evidence_ref": "EV-N8N-INTENT-...",
  "auto_retry": false,
  "timestamp": "2026-02-20T14:37:00Z"
}
```

---

## 6. 监控与告警

### 6.1 关键指标

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| E2E 成功率 | < 95% | Warning |
| E2E 成功率 | < 80% | Critical |
| E001/E003 发生率 | > 5% | Warning |
| 网络重试次数 | > 2 次/执行 | Info |

### 6.2 证据链完整性检查

| 字段 | 必须存在 | 验证 |
|------|----------|------|
| `run_id` | ✅ | 前缀 `RUN-N8N-` |
| `evidence_ref` | ✅ | 前缀 `EV-N8N-` |
| `gate_decision` | ✅ | `ALLOW` 或 `DENY` |
| `replay_pointer` | ✅ (SUCCESS) | 包含 `at_time` |

---

## 7. 故障排查

### 7.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| E001 错误 | 无有效 permit | 确保 permit 已创建且有效 |
| E003 错误 | permit 签名无效 | 检查 permit 签名密钥配置 |
| 越权字段被拒绝 | 输入包含禁止字段 | 移除 gate_decision/release_allowed 等字段 |
| at_time 被拒绝 | 使用漂移值 | 使用固定 ISO-8601 时间戳 |
| 一致性校验失败 | run_id 与 evidence_ref 不匹配 | 使用同一次执行的标识 |

### 7.2 日志位置

- n8n 执行日志：n8n 管理界面 > Executions
- SkillForge API 日志：`/var/log/skillforge/api.log`
- AuditPack 存储：`AuditPack/runs/RUN-N8N-...`

---

## 8. 附录

### 8.1 环境变量清单

```bash
# SkillForge API
SKILLFORGE_API_BASE=https://skillforge.example.com

# 通知 Webhooks
NOTIFICATION_WEBHOOK_SUCCESS=https://hooks.example.com/success
NOTIFICATION_WEBHOOK_FAILURE=https://hooks.example.com/failure
NOTIFICATION_WEBHOOK_ERROR=https://hooks.example.com/error
```

### 8.2 相关文档

- [run_intent 生产报告](../L45_RUN_INTENT_PRODUCTION_REPORT_v1.md) - T7
- [fetch_pack 生产报告](../L45_FETCH_PACK_PRODUCTION_REPORT_v1.md) - T8
- [query_rag 生产报告](../L45_QUERY_RAG_PRODUCTION_REPORT_v1.md) - T9
- [n8n 边界合同 v1](../L45_N8N_BOUNDARY_CONTRACT_v1.md)

### 8.3 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v2.0.0 | 2026-02-20 | Day-2 MinCap E2E 版本，对接生产化接口 |
