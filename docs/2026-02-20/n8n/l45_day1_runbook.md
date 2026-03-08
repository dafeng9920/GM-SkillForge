# L4.5 Day-1 n8n 工作流运行手册

> Job ID: `L45-D1-N8N-BOUNDARY-20260220-001`
> Skill ID: `l45_n8n_orchestration_boundary`
> 版本: v1.0.0
> 创建日期: 2026-02-20

---

## 1. 概述

本运行手册定义了 SkillForge n8n 编排工作流的执行步骤、重试策略和回滚说明。

### 1.1 工作流职责边界

| 允许 | 禁止 |
|------|------|
| Trigger（触发） | 生成 `release_allowed` 决策 |
| Route（路由） | 绕过 SkillForge API 直接写 registry |
| Retry（重试） | 直接写证据 |
| Notify（通知） | 修改后端 Python 业务代码 |

---

## 2. 执行步骤

### 2.1 前置条件

1. n8n 实例已启动并可访问
2. SkillForge API 服务已启动
3. 环境变量已配置：
   - `SKILLFORGE_API_BASE`: SkillForge API 基础地址
   - `NOTIFICATION_WEBHOOK_SUCCESS`: 成功通知 webhook
   - `NOTIFICATION_WEBHOOK_FAILURE`: 失败通知 webhook
   - `NOTIFICATION_WEBHOOK_ERROR`: 错误通知 webhook

### 2.2 工作流导入

```bash
# 1. 导入工作流到 n8n
n8n import:workflow --input=docs/2026-02-20/n8n/l45_day1_workflow.json

# 2. 激活工作流
n8n activate --id=<workflow_id>
```

### 2.3 执行流程

```
┌─────────────────┐
│ Webhook Trigger │ ◄── 外部 POST 请求
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
    YES  │  NO
         │   └──► Notify Validation Error
         ▼
┌─────────────────┐
│ Call run_intent │ ◄── SkillForge API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Call fetch_pack │ ◄── SkillForge API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Call query_rag   │ ◄── SkillForge API (at_time)
└────────┬────────┘
         │
    ┌────┴────────┐
    │gate_decision│
    │  = PASS?    │
    └────┬────────┘
    YES  │  NO
         │   └──► Notify Failure (BLOCKED)
         ▼
  Notify Success
```

### 2.4 输入参数规范

**允许字段（白名单）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo_url` | string | ✅ | 代码仓库 URL |
| `commit_sha` | string | ✅ | 提交 SHA（固定，禁止 latest） |
| `at_time` | string | ✅ | 时间戳（ISO 8601，固定输入） |
| `requester_id` | string | ❌ | 请求者标识 |
| `intent_id` | string | ❌ | 意图标识 |
| `n8n_execution_id` | string | ❌ | n8n 执行 ID（自动填充） |

**禁止字段（越权字段）：**

| 字段 | 说明 |
|------|------|
| `gate_decision` | 必须由 SkillForge Gate 返回 |
| `release_allowed` | 必须由 SkillForge Permit 返回 |
| `evidence_ref` | 必须由 SkillForge Evidence 返回 |
| `permit_id` | 必须由 SkillForge Permit 返回 |

### 2.5 调用示例

```bash
curl -X POST https://n8n.example.com/webhook/skillforge/run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/example/repo.git",
    "commit_sha": "abc123def456",
    "at_time": "2026-02-20T10:30:00Z",
    "requester_id": "user@example.com",
    "intent_id": "intent-001"
  }'
```

---

## 3. 重试策略

### 3.1 允许重试的错误

| 错误类型 | 错误码 | 重试策略 |
|----------|--------|----------|
| 网络错误 | `E_NETWORK` | 最多 3 次，间隔 5 秒 |
| 超时错误 | `E_TIMEOUT` | 最多 3 次，间隔 5 秒 |

### 3.2 禁止重试的错误

| 错误类型 | 错误码 | 处理方式 |
|----------|--------|----------|
| 业务错误 | `E001` | Fail-Closed，返回 `required_changes` |
| 业务错误 | `E003` | Fail-Closed，返回 `required_changes` |
| 验证错误 | `E_VALIDATION` | 直接阻断，不重试 |
| 权限错误 | `E_PERMISSION` | 直接阻断，不重试 |

### 3.3 重试配置

每个 HTTP 请求节点的重试配置：

```json
{
  "timeout": 30000,
  "retry": {
    "enabled": true,
    "maxRetries": 3,
    "retryInterval": 5000
  }
}
```

---

## 4. 回滚说明

### 4.1 工作流回滚

```bash
# 1. 停用当前工作流
n8n deactivate --id=<workflow_id>

# 2. 导入上一版本
n8n import:workflow --input=docs/2026-02-20/n8n/l45_day1_workflow_v0.json

# 3. 激活回滚版本
n8n activate --id=<old_workflow_id>
```

### 4.2 执行回滚（at-time 回放）

由于所有执行都使用固定的 `at_time`，可以通过 `query_rag(at_time)` 重新查询历史状态：

```bash
# 回放特定时间点的执行
curl -X POST https://skillforge.example.com/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run-20260220-001",
    "at_time": "2026-02-20T10:30:00Z",
    "query_type": "audit_pack"
  }'
```

### 4.3 紧急阻断

如果发现工作流行为异常：

1. **立即停用工作流**：
   ```bash
   n8n deactivate --id=<workflow_id>
   ```

2. **通知相关方**：
   - 通过 `NOTIFICATION_WEBHOOK_ERROR` 发送阻断通知

3. **审计追踪**：
   - 所有执行记录保留在 n8n execution history
   - SkillForge 端保留完整证据链

---

## 5. 输出规范

### 5.1 成功响应

```json
{
  "status": "SUCCESS",
  "run_id": "run-20260220-001",
  "gate_decision": "PASS",
  "evidence_ref": "ev-abc123",
  "release_allowed": true,
  "replay_pointer": "rp-20260220T103000Z",
  "audit_pack_ref": "audit-pack-001",
  "timestamp": "2026-02-20T10:35:00Z"
}
```

### 5.2 失败响应（业务阻断）

```json
{
  "status": "BLOCKED",
  "run_id": "run-20260220-002",
  "gate_decision": "FAIL",
  "error_code": "E001",
  "error_message": "Contract validation failed",
  "required_changes": [
    "Add missing field: output_schema",
    "Fix timeout value exceeds maximum"
  ],
  "timestamp": "2026-02-20T10:36:00Z"
}
```

### 5.3 错误响应（系统错误）

```json
{
  "status": "API_ERROR",
  "error_code": "E_NETWORK",
  "error_message": "Connection timeout after 30s",
  "retry_count": 3,
  "run_id": "run-20260220-003",
  "n8n_execution_id": "exec-456",
  "timestamp": "2026-02-20T10:40:00Z"
}
```

---

## 6. 监控与告警

### 6.1 关键指标

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 工作流执行成功率 | < 95% | Warning |
| 工作流执行成功率 | < 80% | Critical |
| API 响应时间 P99 | > 10s | Warning |
| 重试次数 | > 2 次/执行 | Info |

### 6.2 告警渠道

- 成功/失败通知：`NOTIFICATION_WEBHOOK_SUCCESS` / `NOTIFICATION_WEBHOOK_FAILURE`
- 系统错误通知：`NOTIFICATION_WEBHOOK_ERROR`

---

## 7. 故障排查

### 7.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 验证失败 | 缺少必填字段 | 检查输入是否包含 repo_url/commit_sha/at_time |
| API 超时 | SkillForge 服务不可用 | 检查服务健康状态，触发重试 |
| gate_decision 为空 | SkillForge 未返回决策 | 检查 SkillForge 日志，确认请求到达 |
| 禁止字段被拒绝 | 输入包含越权字段 | 移除 gate_decision/release_allowed 等字段 |

### 7.2 日志位置

- n8n 执行日志：n8n 管理界面 > Executions
- SkillForge API 日志：`/var/log/skillforge/api.log`
- 证据链日志：SkillForge Evidence Store

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

- [L4.5 启动清单 v2](../L4.5%20启动清单%20v2（2026-02-20）.md)
- [n8n 边界合同 v1](../L45_N8N_BOUNDARY_CONTRACT_v1.md) - 待 T2 完成
- [工作流运行报告 v1](../L45_N8N_WORKFLOW_RUN_REPORT_v1.md)

### 8.3 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2026-02-20 | 初始版本，实现最小闭环 |
