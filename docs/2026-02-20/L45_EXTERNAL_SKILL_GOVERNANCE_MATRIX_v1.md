# L4.5 外部 Skill 治理门禁矩阵 v1

> **Job ID**: `L45-D3-EXT-SKILL-GOV-20260220-003`
> **Skill ID**: `l45_external_skill_governance_batch1`
> **版本**: v1.0.0
> **创建日期**: 2026-02-20

---

## 1. 概述

本文档定义外部 Skill 治理门禁的阻断矩阵和放行矩阵，确保导入流程符合 `no-permit-no-import` 原则，并支持 `tombstone` 默认不可见、`at-time` 回放审计。

### 1.1 核心原则

1. **no-permit-no-import**: 无有效 permit 禁止导入
2. **tombstone 默认不可见**: 有害/下架条目仅 `at-time` 可回放
3. **fail-closed**: 所有阻断分支返回结构化错误信封
4. **required_changes 可执行**: 阻断必须给出明确整改建议

---

## 2. 阻断矩阵

### 2.1 全局阻断（整个导入流程终止）

| 错误码 | 触发条件 | 阻断级别 | 可重试 | required_changes |
|--------|----------|----------|--------|------------------|
| `E001` | 无 Permit | CRITICAL | ❌ 否 | "获取有效 permit 后重试" |
| `E003` | Permit 签名无效 | CRITICAL | ❌ 否 | "检查 permit 签名密钥配置" |
| `E004` | Permit 已过期 | CRITICAL | ❌ 否 | "续期 permit 后重试" |
| `E007` | Permit 已撤销 | CRITICAL | ❌ 否 | "重新申请 permit" |
| `E101` | 外部 Skill 合同缺失 | HIGH | ❌ 否 | "补充 skill.yaml 合同文件" |
| `E102` | 宪法校验失败 | HIGH | ❌ 否 | "修复宪法违规项" |
| `E103` | 安全姿态不达标 | CRITICAL | ❌ 否 | "修复安全漏洞后重新提交" |

### 2.2 目标阻断（单个 Skill 阻断，不影响其他）

| 错误码 | 触发条件 | 阻断级别 | 可重试 | required_changes |
|--------|----------|----------|--------|------------------|
| `E005` | Permit scope 不匹配 | HIGH | ❌ 否 | "申请匹配的 permit scope" |
| `E006` | Permit subject 不匹配 | HIGH | ❌ 否 | "使用正确的 subject permit" |
| `E104` | L1 合同审计失败 | MEDIUM | ❌ 否 | "修复合同 schema 错误" |
| `E105` | L2 控制审计失败 | MEDIUM | ❌ 否 | "调整控制参数至合规范围" |
| `E106` | L3 安全审计失败 | HIGH | ❌ 否 | "修复安全审计发现项" |
| `E107` | L4 证据审计失败 | MEDIUM | ❌ 否 | "补充缺失的证据字段" |
| `E108` | L5 复现审计失败 | LOW | ❌ 否 | "确保执行可复现" |

### 2.3 网络错误（允许重试）

| 错误码 | 触发条件 | 阻断级别 | 可重试 | 重试策略 |
|--------|----------|----------|--------|----------|
| `E_NETWORK` | 网络连接失败 | LOW | ✅ 是 | 最多 3 次，间隔 5 秒 |
| `E_TIMEOUT` | 请求超时 | LOW | ✅ 是 | 最多 3 次，间隔 5 秒 |

---

## 3. 放行矩阵

### 3.1 完全放行（PASS）

| 条件 | gate_decision | tombstone | registry |
|------|---------------|-----------|----------|
| L1-L5 全部 PASS + Permit 有效 | `ALLOW` | N/A | ✅ 入主仓 |
| Upgrade（同流程，只增 revision） | `ALLOW` | N/A | ✅ 新增 revision |

### 3.2 条件放行（CONDITIONAL）

| 条件 | gate_decision | tombstone | registry |
|------|---------------|-----------|----------|
| L1-L3 PASS + L4/L5 警告 | `CONDITIONAL` | N/A | ✅ 入主仓（带警告标记） |
| 已知兼容性升级 | `CONDITIONAL` | N/A | ✅ 新增 revision（需人工确认） |

### 3.3 阻断后放行路径

| 原始状态 | 修复后 | gate_decision | 行为 |
|----------|--------|---------------|------|
| `E104` (L1 失败) | 修复合同 | `ALLOW` | 重新进入审计流程 |
| `E105` (L2 失败) | 调整参数 | `ALLOW` | 重新进入审计流程 |
| `E106` (L3 失败) | 修复安全 | `ALLOW` | 重新进入审计流程 |

---

## 4. Tombstone 矩阵

### 4.1 Tombstone 触发条件

| 条件 | tombstone 原因 | 默认可见 | at-time 可回放 |
|------|----------------|----------|----------------|
| 发现有害代码 | `HARMFUL_DETECTED` | ❌ 否 | ✅ 是 |
| 许可证违规 | `LICENSE_VIOLATION` | ❌ 否 | ✅ 是 |
| 用户申请下架 | `USER_REQUEST` | ❌ 否 | ✅ 是 |
| 安全漏洞 | `SECURITY_VULNERABILITY` | ❌ 否 | ✅ 是 |
| 恶意行为 | `MALICIOUS_BEHAVIOR` | ❌ 否 | ✅ 是 |

### 4.2 Tombstone 查询口径

```yaml
# 默认查询（tombstone 不可见）
query:
  tombstone_filter: exclude  # 默认行为

# at-time 回放查询（tombstone 可见）
query:
  at_time: "2026-02-20T10:00:00Z"
  tombstone_filter: include  # 审计模式下包含
```

### 4.3 Tombstone 记录结构

```yaml
tombstone_record:
  skill_id: string
  revision: string
  tombstone_reason: string
  tombstoned_at: string
  tombstoned_by: string
  evidence_ref: string
  at_time_replay_pointer: string
  # 禁止物理删除
  deleted: false
```

---

## 5. 导入状态机

```
┌─────────────┐
│   Import    │
│   Trigger   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  Boundary   │────►│  E001-E007  │ (全局阻断)
│   Check     │     │  BLOCKED    │
└──────┬──────┘     └─────────────┘
       │ PASS
       ▼
┌─────────────┐     ┌─────────────┐
│ Quarantine  │────►│  E101-E103  │ (全局阻断)
│   Check     │     │  BLOCKED    │
└──────┬──────┘     └─────────────┘
       │ PASS
       ▼
┌─────────────┐     ┌─────────────┐
│Constitution │────►│  E102       │ (全局阻断)
│   Check     │     │  BLOCKED    │
└──────┬──────┘     └─────────────┘
       │ PASS
       ▼
┌─────────────┐     ┌─────────────┐
│  L1-L5      │────►│  E104-E108  │ (目标阻断)
│   Audit     │     │  BLOCKED    │
└──────┬──────┘     └─────────────┘
       │ PASS
       ▼
┌─────────────┐
│  Decision   │────► ALLOW / CONDITIONAL
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Permit    │────► Permit 签发
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Registry   │────► 入主仓
│  Admission  │
└─────────────┘
```

---

## 6. n8n 职责边界

### 6.1 n8n 允许操作

| 操作 | 说明 |
|------|------|
| Trigger | 接收外部 Skill 导入请求 |
| Route | 根据 SkillForge 返回的 gate_decision 路由 |
| Retry | 仅网络/超时错误重试 |
| Notify | 发送导入结果通知 |

### 6.2 n8n 禁止操作

| 操作 | 原因 |
|------|------|
| 生成 gate_decision | 最终裁决权在 SkillForge |
| 直接写 Registry | 必须经过 Permit 验证 |
| 修改 tombstone 状态 | tombstone 由治理流程控制 |
| 跳过审计链 | 必须完整执行 L1-L5 |

---

## 7. Fail-Closed 错误信封

### 7.1 标准错误格式

```json
{
  "ok": false,
  "error_code": "E104",
  "blocked_by": "L1_CONTRACT_AUDIT",
  "message": "Contract schema validation failed",
  "required_changes": [
    {
      "field": "output_schema",
      "issue": "missing",
      "fix": "Add output_schema definition"
    },
    {
      "field": "timeout",
      "issue": "exceeds_maximum",
      "current_value": 300000,
      "maximum_allowed": 60000,
      "fix": "Reduce timeout to 60000ms or less"
    }
  ],
  "evidence_ref": "EV-EXT-SKILL-...",
  "run_id": "RUN-EXT-SKILL-...",
  "timestamp": "2026-02-20T10:00:00Z"
}
```

### 7.2 错误信封必填字段

| 字段 | 说明 |
|------|------|
| `ok` | 固定为 `false` |
| `error_code` | 错误码（E001-E108） |
| `blocked_by` | 阻断模块标识 |
| `message` | 人类可读错误描述 |
| `required_changes` | 可执行的整改建议（数组） |
| `evidence_ref` | 证据引用 |
| `run_id` | 运行标识 |
| `timestamp` | 时间戳 |

---

## 8. 验收场景

### 8.1 成功场景（PASS）

```yaml
input:
  external_skill_ref: "https://github.com/example/valid-skill"
  repo_url: "https://github.com/example/valid-skill.git"
  commit_sha: "a1b2c3d4e5f6789012345678901234567890abcd"
  at_time: "2026-02-20T10:00:00Z"
  permit_refs:
    - permit_id: "PERMIT-20260220-IMPORT"

expected:
  gate_decision: ALLOW
  tombstone: null
  registry_admission: true
  run_id: "RUN-EXT-SKILL-..."
  evidence_ref: "EV-EXT-SKILL-..."
```

### 8.2 阻断场景（E001 - 无 Permit）

```yaml
input:
  external_skill_ref: "https://github.com/example/skill-no-permit"
  repo_url: "https://github.com/example/skill-no-permit.git"
  commit_sha: "deadbeef12345678901234567890123456789012"
  at_time: "2026-02-20T10:00:00Z"
  permit_refs: []

expected:
  ok: false
  error_code: E001
  blocked_by: PERMIT_REQUIRED
  message: "Permit is required for external skill import"
  required_changes:
    - field: "permit_refs"
      issue: "empty"
      fix: "Obtain a valid import permit before retrying"
  auto_retry: false
```

### 8.3 Tombstone 场景（有害检测）

```yaml
input:
  external_skill_ref: "https://github.com/example/harmful-skill"
  repo_url: "https://github.com/example/harmful-skill.git"
  commit_sha: "badf00d123456789012345678901234567890123"
  at_time: "2026-02-20T10:00:00Z"
  permit_refs:
    - permit_id: "PERMIT-20260220-IMPORT"

expected:
  ok: false
  error_code: E103
  blocked_by: SECURITY_AUDIT
  message: "Harmful code detected: backdoor found in main.py"
  tombstone:
    reason: HARMFUL_DETECTED
    visible_by_default: false
    at_time_replayable: true
  required_changes:
    - field: "main.py"
      issue: "backdoor_detected"
      fix: "Remove malicious code and resubmit"
  auto_retry: false
```

### 8.4 回放场景（at-time 查询）

```yaml
query:
  at_time: "2026-02-20T10:00:00Z"
  skill_id: "harmful-skill"
  include_tombstone: true

expected:
  ok: true
  data:
    skill_id: "harmful-skill"
    revision: "v1.0.0"
    tombstone:
      reason: HARMFUL_DETECTED
      tombstoned_at: "2026-02-20T10:05:00Z"
    replay_pointer:
      at_time: "2026-02-20T10:00:00Z"
      snapshot_ref: "snapshot://..."
```

---

## 9. 关键约束验证

| 约束 | 状态 | 说明 |
|------|------|------|
| no-permit-no-import | ✅ | E001-E007 全局阻断 |
| tombstone 默认不可见 | ✅ | visible_by_default=false |
| at-time 可回放 | ✅ | replay_pointer 记录 |
| 业务错误不重试 | ✅ | auto_retry=false |
| required_changes 可执行 | ✅ | 结构化整改建议 |
| n8n 不生成裁决 | ✅ | gate_decision 来自 SkillForge |
| E001/E003 语义不变 | ✅ | 与 release-gate-skill 一致 |

---

## 10. 实现引用

| 文件 | 说明 |
|------|------|
| `skillforge/src/skills/gates/gate_permit.py` | Permit 校验 |
| `skillforge/src/skills/gates/gate_constitution.py` | 宪法校验 |
| `skillforge/src/skills/external_skill_import.py` | 外部 Skill 导入流程 |
| `docs/2026-02-20/n8n/l45_day3_external_skill_workflow.json` | n8n 工作流定义 |

---

## 11. 变更历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2026-02-20 | 初始版本，定义治理门禁矩阵 |
