# L4.5 外部 Skill 治理运行手册 v1

> **Job ID**: `L45-D3-EXT-SKILL-GOV-20260220-003`
> **Skill ID**: `l45_external_skill_governance_batch1`
> **版本**: v1.0.0
> **创建日期**: 2026-02-20

---

## 1. 概述

本运行手册定义外部 Skill 治理导入工作流的执行步骤、故障排查和回滚说明。

### 1.1 核心原则

1. **no-permit-no-import**: 无有效 permit 禁止导入
2. **tombstone 默认不可见**: 有害条目仅 at-time 可回放
3. **fail-closed**: 所有阻断返回结构化错误信封
4. **n8n 不生成最终裁决**: gate_decision 由 SkillForge 返回

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
n8n import:workflow --input=docs/2026-02-20/n8n/l45_day3_external_skill_workflow.json

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
│ Check Forbidden     │ ◄── 检测越权字段 + permit 缺失
│ Fields              │
└────────┬────────────┘
         │
    ┌────┴────────┐
    │ FORBIDDEN?  │
    └────┬────────┘
    NO   │  YES ──► Notify Forbidden Field
         │
    ┌────┴────────┐
    │ PERMIT?     │
    └────┬────────┘
    YES  │  NO ──► Notify Permit Missing (E001)
         │
         ▼
┌─────────────────┐
│ Call Boundary   │ ◄── SkillForge API (E001-E007)
│ Check           │
└────────┬────────┘
         │
    ┌────┴────┐
    │ ok?     │
    └────┬────┘
    YES  │  NO ──► Notify Failure
         │
         ▼
┌─────────────────┐
│ Call Quarantine │ ◄── SkillForge API (E101-E103)
└────────┬────────┘
         │
    ┌────┴────┐
    │ ok?     │
    └────┬────┘
    YES  │  NO ──► Notify Failure
         │
         ▼
┌─────────────────┐
│ Call L1-L5      │ ◄── SkillForge API (E104-E108)
│ Audit           │
└────────┬────────┘
         │
    ┌────┴────────────┐
    │gate_decision    │
    │  = ALLOW?       │
    └────┬────────────┘
    YES  │  NO ──► Notify Failure
         │
         ▼
   Notify Success
   (入主仓)
```

### 2.4 输入参数规范

**必填字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `external_skill_ref` | string | 外部 Skill 引用 URL |
| `repo_url` | string | 代码仓库 URL |
| `commit_sha` | string | 提交 SHA（40字符十六进制） |
| `at_time` | string | ISO-8601 时间戳（固定值，禁止漂移） |

**可选字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `permit_refs` | array | Permit 引用列表（必须非空） |
| `n8n_execution_id` | string | n8n 执行 ID（自动填充） |

**禁止字段：**

| 字段 | 原因 |
|------|------|
| `gate_decision` | n8n 不能覆盖 Gate 决策 |
| `release_allowed` | n8n 不能绕过发布控制 |
| `permit_token` | permit 由 SkillForge 内部签发 |
| `evidence_ref` | n8n 不能注入伪造证据 |
| `permit_id` | n8n 不能注入 permit 引用 |
| `run_id` | run_id 由 SkillForge 内部生成 |

### 2.5 调用示例

**成功导入：**

```bash
curl -X POST https://n8n.example.com/webhook/skillforge/external-skill/import \
  -H "Content-Type: application/json" \
  -d '{
    "external_skill_ref": "https://github.com/example/valid-skill",
    "repo_url": "https://github.com/example/valid-skill.git",
    "commit_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
    "at_time": "2026-02-20T10:00:00Z",
    "permit_refs": [
      {
        "permit_id": "PERMIT-20260220-IMPORT",
        "issued_at": "2026-02-20T09:00:00Z",
        "issued_by": "admin@skillforge.dev",
        "scope": "import:external_skill"
      }
    ]
  }'
```

---

## 3. 阻断矩阵参考

### 3.1 全局阻断（E001-E007, E101-E103）

| 错误码 | 触发条件 | 重试 | required_changes |
|--------|----------|------|------------------|
| E001 | 无 Permit | ❌ | "获取有效 permit 后重试" |
| E003 | Permit 签名无效 | ❌ | "检查 permit 签名密钥配置" |
| E004 | Permit 已过期 | ❌ | "续期 permit 后重试" |
| E007 | Permit 已撤销 | ❌ | "重新申请 permit" |
| E101 | 合同缺失 | ❌ | "补充 skill.yaml 合同文件" |
| E102 | 宪法校验失败 | ❌ | "修复宪法违规项" |
| E103 | 安全姿态不达标 | ❌ | "修复安全漏洞后重新提交" |

### 3.2 目标阻断（E104-E108）

| 错误码 | 触发条件 | 重试 | required_changes |
|--------|----------|------|------------------|
| E104 | L1 合同审计失败 | ❌ | "修复合同 schema 错误" |
| E105 | L2 控制审计失败 | ❌ | "调整控制参数至合规范围" |
| E106 | L3 安全审计失败 | ❌ | "修复安全审计发现项" |
| E107 | L4 证据审计失败 | ❌ | "补充缺失的证据字段" |
| E108 | L5 复现审计失败 | ❌ | "确保执行可复现" |

### 3.3 允许重试的错误

| 错误码 | 触发条件 | 重试策略 |
|--------|----------|----------|
| E_NETWORK | 网络连接失败 | 最多 3 次，间隔 5 秒 |
| E_TIMEOUT | 请求超时 | 最多 3 次，间隔 5 秒 |

---

## 4. Tombstone 操作

### 4.1 Tombstone 触发条件

- 发现有害代码
- 许可证违规
- 用户申请下架
- 安全漏洞
- 恶意行为

### 4.2 Tombstone 查询

**默认查询（tombstone 不可见）：**

```bash
curl -X GET "https://skillforge.example.com/api/v1/skills/harmful-skill"
# 返回 404 Not Found
```

**at-time 回放查询（tombstone 可见）：**

```bash
curl -X GET "https://skillforge.example.com/api/v1/skills/harmful-skill?at_time=2026-02-20T10:00:00Z&include_tombstone=true"
# 返回 tombstone 记录
```

### 4.3 Tombstone 记录结构

```json
{
  "skill_id": "harmful-skill",
  "revision": "v1.0.0",
  "tombstone_reason": "HARMFUL_DETECTED",
  "tombstoned_at": "2026-02-20T10:05:00Z",
  "tombstoned_by": "security-audit",
  "evidence_ref": "EV-TOMBSTONE-...",
  "at_time_replay_pointer": "rp-20260220T100000Z",
  "deleted": false
}
```

**重要**: Tombstone 禁止物理删除，仅标记 `deleted=false`。

---

## 5. 输出规范

### 5.1 成功响应

```json
{
  "status": "SUCCESS",
  "run_id": "RUN-EXT-SKILL-1739980000-A1B2C3D4",
  "gate_decision": "ALLOW",
  "release_allowed": true,
  "evidence_ref": "EV-EXT-SKILL-...",
  "replay_pointer": {
    "at_time": "2026-02-20T10:00:00Z",
    "snapshot_ref": "snapshot://L45-D3-20260220/v1"
  },
  "external_skill_ref": "https://github.com/example/valid-skill",
  "registry_admission": true,
  "revision": "v1.0.0",
  "timestamp": "2026-02-20T10:05:00Z"
}
```

### 5.2 失败响应（E001 - 无 Permit）

```json
{
  "status": "BLOCKED",
  "run_id": "RUN-EXT-SKILL-...",
  "gate_decision": "DENY",
  "error_code": "E001",
  "blocked_by": "PERMIT_REQUIRED",
  "message": "Permit is required for external skill import",
  "required_changes": [
    {
      "field": "permit_refs",
      "issue": "empty",
      "fix": "Obtain a valid import permit before retrying"
    }
  ],
  "auto_retry": false,
  "timestamp": "2026-02-20T10:00:00Z"
}
```

### 5.3 失败响应（Tombstone）

```json
{
  "status": "BLOCKED",
  "run_id": "RUN-EXT-SKILL-...",
  "gate_decision": "DENY",
  "error_code": "E103",
  "blocked_by": "SECURITY_AUDIT",
  "message": "Harmful code detected: backdoor found in main.py",
  "tombstone": {
    "reason": "HARMFUL_DETECTED",
    "visible_by_default": false,
    "at_time_replayable": true
  },
  "required_changes": [
    {
      "field": "main.py",
      "issue": "backdoor_detected",
      "fix": "Remove malicious code and resubmit"
    }
  ],
  "auto_retry": false,
  "timestamp": "2026-02-20T10:05:00Z"
}
```

---

## 6. 故障排查

### 6.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| E001 错误 | 无 permit_refs | 添加有效的 permit_refs |
| E003 错误 | permit 签名无效 | 检查签名密钥配置 |
| E101 错误 | skill.yaml 缺失 | 补充合同文件 |
| E102 错误 | 宪法违规 | 修复违规项 |
| E103 错误 | 安全漏洞 | 修复安全漏洞 |
| 越权字段被拒绝 | 输入包含禁止字段 | 移除 gate_decision/release_allowed 等字段 |
| at_time 被拒绝 | 使用漂移值 | 使用固定 ISO-8601 时间戳 |

### 6.2 日志位置

- n8n 执行日志：n8n 管理界面 > Executions
- SkillForge API 日志：`/var/log/skillforge/api.log`
- 外部 Skill 审计日志：`AuditPack/external_skills/`

### 6.3 回滚操作

**工作流回滚：**

```bash
# 1. 停用当前工作流
n8n deactivate --id=<workflow_id>

# 2. 导入上一版本
n8n import:workflow --input=docs/2026-02-20/n8n/l45_day3_external_skill_workflow_v0.json

# 3. 激活回滚版本
n8n activate --id=<old_workflow_id>
```

**Skill 回滚（at-time 回放）：**

```bash
# 回放特定时间点的状态
curl -X GET "https://skillforge.example.com/api/v1/skills/example-skill?at_time=2026-02-20T09:00:00Z"
```

---

## 7. 验收演练

### 7.1 场景 1：成功导入

1. 准备有效的外部 Skill 和 permit
2. 发送导入请求
3. 验证 gate_decision=ALLOW
4. 验证 registry_admission=true

### 7.2 场景 2：E001 阻断

1. 准备无 permit 的请求
2. 发送导入请求
3. 验证 error_code=E001
4. 验证 required_changes 非空
5. 验证 auto_retry=false

### 7.3 场景 3：Tombstone 回放

1. 准备有害 Skill（触发 E103）
2. 发送导入请求
3. 验证 tombstone 记录
4. 使用 at-time 查询
5. 验证可回放

---

## 8. 附录

### 8.1 环境变量

```bash
# SkillForge API
SKILLFORGE_API_BASE=https://skillforge.example.com

# 通知 Webhooks
NOTIFICATION_WEBHOOK_SUCCESS=https://hooks.example.com/success
NOTIFICATION_WEBHOOK_FAILURE=https://hooks.example.com/failure
NOTIFICATION_WEBHOOK_ERROR=https://hooks.example.com/error
```

### 8.2 相关文档

- [外部 Skill 治理矩阵](../L45_EXTERNAL_SKILL_GOVERNANCE_MATRIX_v1.md)
- [release-gate-skill SKILL.md](../../skills/release-gate-skill/SKILL.md)
- [L4.5 启动清单 v2](../L4.5%20启动清单%20v2（2026-02-20）.md)

### 8.3 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2026-02-20 | 初始版本 |
