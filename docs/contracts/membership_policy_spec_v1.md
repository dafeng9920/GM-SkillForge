# Membership Policy Specification v1

> **Version**: v1
> **Updated**: 2026-02-19
> **Status**: ACTIVE
> **Config Source**: `src/contracts/policy/membership_tiers.yml`

---

## 1. 概述

本文档定义 GM-SkillForge 的会员层级策略，由 `membership_policy_enforcer.py` 在运行时加载和执行。

### 1.1 核心原则

**硬规则：会员层级 NEVER 改变 GateDecision**

会员策略仅控制：
- 访问权限 (capabilities)
- 配额限制 (quotas)
- 速率限制 (rate limits)
- 数据保留 (retention)

会员策略**不**影响：
- Gate 校验结果
- Permit 签发决策
- AuditPack 内容

---

## 2. 层级定义

| 层级 | 定位 | L3 配额/月 | L4 配额/月 | L5 配额/月 | 托管执行 |
|------|------|------------|------------|------------|----------|
| FREE | 试用 | 1 | 0 | 0 | 否 |
| PRO | 创作者 | 20 | 0 | 0 | 可选插件 |
| STUDIO | 团队 | 100 | 10 | 0 | 是 |
| ENTERPRISE | 企业 | 500 | 50 | 10 | 是 |

---

## 3. 能力矩阵

| 能力 | FREE | PRO | STUDIO | ENTERPRISE |
|------|------|-----|--------|------------|
| AUDIT_L3 | ✓ | ✓ | ✓ | ✓ |
| AUDIT_L4 | ✗ | ✗ | ✓ | ✓ |
| AUDIT_L5 | ✗ | ✗ | ✗ | ✓ |
| PUBLISH_LISTING | ✓ | ✓ | ✓ | ✓ |
| UPGRADE_AND_REAUDIT | ✗ | ✓ | ✓ | ✓ |
| EXECUTE_VIA_N8N | ✗ | 插件 | ✓ | ✓ |
| CREATE_ORG | ✗ | ✗ | ✓ | ✓ |
| EXPORT_WHITELIST | ✗ | ✗ | ✓ | ✓ |

---

## 4. 必要检查 (Required Checks)

### 4.1 发布检查 (publish_listing)

所有层级发布前必须满足：

```yaml
must_have:
  - gate_decision.decision: "PASS"
  - gate_decision.level_min: "L3"
  - permit.status: "VALID"
  - audit_pack.present: true
  - audit_pack.hash_present: true
  - provenance.present: true
must_not_have:
  - tombstone.state: "TOMBSTONED"
```

### 4.2 执行检查 (execute_via_n8n)

所有层级执行前必须满足：

```yaml
must_have:
  - permit.status: "VALID"
  - execution_contract.present: true
must_not_have:
  - tombstone.state: "TOMBSTONED"
```

---

## 5. 错误码

| 错误码 | 含义 | 场景 |
|--------|------|------|
| `MEMBERSHIP_QUOTA_EXCEEDED` | 配额超限 | 月度审计次数用尽 |
| `MEMBERSHIP_RATE_LIMITED` | 速率限制 | API 请求过快 |
| `MEMBERSHIP_CAPABILITY_DENIED` | 能力缺失 | 无权执行某操作 |
| `MEMBERSHIP_REQUIRED_CHECK_FAILED` | 检查失败 | 必要条件不满足 |

---

## 6. 插件 (Add-ons)

### 6.1 hosted_execution

适用于 PRO 层级，启用托管 n8n 执行：

```yaml
applies_to_tiers: [PRO]
toggles:
  capabilities:
    EXECUTE_VIA_N8N: true
  quotas:
    max_concurrent_exec_jobs: 2
```

**插件不绕过 required_checks**，仅增加能力。

---

## 7. 执行挂点

### 7.1 审计入队前
```python
enforcer.check_capability(user_tier, "AUDIT_L3")
enforcer.check_quota(user_tier, "l3_audit_runs_per_month", current_usage)
enforcer.check_rate_limit(user_tier, "audit_jobs_per_hour")
```

### 7.2 发布前
```python
enforcer.check_required_checks("publish_listing", context)
```

### 7.3 n8n 执行前
```python
enforcer.check_required_checks("execute_via_n8n", context)
```

---

## 8. 文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| 运行时配置 | `src/contracts/policy/membership_tiers.yml` | 策略定义 |
| 策略执行器 | `src/contracts/policy/membership_policy_enforcer.py` | 校验逻辑 |
| 规格文档 | `docs/contracts/membership_policy_spec_v1.md` | 本文档 |

---

## 9. 上线前检查清单

- [ ] 能正确返回 4 个 membership 错误码
- [ ] 会员层级不会改写 GateDecision
- [ ] addons 只增能力，不绕过 required_checks
- [ ] schema 校验通过（缺字段即 fail-fast）

---

*文档版本: v1*
*最后更新: 2026-02-19*
