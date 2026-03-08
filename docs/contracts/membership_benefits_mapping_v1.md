# Membership Benefits Mapping v1

> **Version**: v1
> **Updated**: 2026-02-19
> **Source**: membership_tiers.yml
> **Purpose**: M-01~M-16 权益与 YAML 配置的一一映射

---

## 统一硬规则

| 规则 | 说明 |
|------|------|
| 审计结果与会员等级无关 | GateDecision 只由 8 Gate + 证据链决定 |
| PASS 必须满足 L3 门槛 | 无任何"付费豁免" |
| 所有权益必须可审计 | 每次使用权益都写入 EvidenceRef / provenance |

---

## M-01~M-16 权益映射表

### M-01: L3 审计额度（月）

| 层级 | 额度 | YAML 字段 |
|------|------|-----------|
| FREE | 1 次 | `tiers.FREE.quotas.l3_audit_runs_per_month: 1` |
| PRO | 20 次 | `tiers.PRO.quotas.l3_audit_runs_per_month: 20` |
| STUDIO | 100 次 | `tiers.STUDIO.quotas.l3_audit_runs_per_month: 100` |
| ENTERPRISE | 500 次 | `tiers.ENTERPRISE.quotas.l3_audit_runs_per_month: 500` |

**拒绝 Error Code**: `MEMBERSHIP_QUOTA_EXCEEDED`

---

### M-02: 并发/队列优先级

| 层级 | 优先级 | YAML 字段 |
|------|--------|-----------|
| FREE | 低 | `tiers.FREE.quotas.max_concurrent_audit_jobs: 1` |
| PRO | 中 | `tiers.PRO.quotas.max_concurrent_audit_jobs: 2` |
| STUDIO | 高 | `tiers.STUDIO.quotas.max_concurrent_audit_jobs: 5` |
| ENTERPRISE | 最高 | `tiers.ENTERPRISE.quotas.max_concurrent_audit_jobs: 20` |

**拒绝 Error Code**: `MEMBERSHIP_QUOTA_EXCEEDED`

---

### M-03: 私有审计（不公开商品页）

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| 所有 | ✅ | 默认 `visibility: PRIVATE`，非公开 pack 仅账号可取 |

**拒绝 Error Code**: N/A（功能权限，不拒绝）

---

### M-04: 上架位（可售商品数量）

| 层级 | 数量 | YAML 字段 |
|------|------|-----------|
| FREE | 1 | `tiers.FREE.quotas.listing_slots: 1` |
| PRO | 20 | `tiers.PRO.quotas.listing_slots: 20` |
| STUDIO | 200 | `tiers.STUDIO.quotas.listing_slots: 200` |
| ENTERPRISE | 2000 | `tiers.ENTERPRISE.quotas.listing_slots: 2000` |

**拒绝 Error Code**: `MEMBERSHIP_QUOTA_EXCEEDED`

---

### M-05: 仅 L3 PASS 可上架

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| 所有 | ✅ | `required_checks.publish_listing.must_have` |

**拒绝 Error Code**: `MEMBERSHIP_REQUIRED_CHECK_FAILED`

---

### M-06: 自动生成商品页（SEO 页面）

| 层级 | 版本 | 说明 |
|------|------|------|
| FREE | 基础 | 基础模板 |
| PRO | 完整 | 完整模板 |
| STUDIO | 完整+品牌 | 支持品牌定制 |
| ENTERPRISE | 自定义 | 完全自定义 |

**拒绝 Error Code**: N/A（功能差异，不拒绝）

---

### M-07: 自动生成合同/模板（Scaffold Kit）

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| FREE | 基础 | `tiers.FREE.capabilities.ISSUE_API_TOKEN: true` |
| PRO+ | ✅ | 同上 |

**拒绝 Error Code**: N/A（功能权限，不拒绝）

---

### M-08: 失败整改助手（required_changes 结构化）

| 层级 | 支持 | 说明 |
|------|------|------|
| 所有 | ✅ | FAIL 必须包含 `required_changes`（会员不影响） |

**拒绝 Error Code**: N/A（平台基础能力）

---

### M-09: 一键升级重审（upgrade→re-audit）

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| FREE | ❌ | `tiers.FREE.capabilities.UPGRADE_AND_REAUDIT: false` |
| PRO+ | ✅ | `tiers.PRO.capabilities.UPGRADE_AND_REAUDIT: true` |

**拒绝 Error Code**: `MEMBERSHIP_CAPABILITY_DENIED`

---

### M-10: Tombstone 下架与回溯

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| 所有 | ✅ | `tiers.*.capabilities.TOMBSTONE: true` |

**拒绝 Error Code**: N/A（平台基础能力）

---

### M-11: Experience Capture（成长机制固化）

| 层级 | 支持 | 说明 |
|------|------|------|
| 所有 | ✅ | 每次审计/修复后追加 `evolution.json` |

**拒绝 Error Code**: N/A（平台基础能力）

---

### M-12: 托管执行臂（n8n 执行）

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| FREE | ❌ | `tiers.FREE.capabilities.EXECUTE_VIA_N8N: false` |
| PRO | 可选加购 | `addons.hosted_execution.applies_to_tiers: [PRO]` |
| STUDIO+ | ✅ | `tiers.STUDIO.capabilities.EXECUTE_VIA_N8N: true` |

**拒绝 Error Code**: `MEMBERSHIP_CAPABILITY_DENIED`

---

### M-13: 争议仲裁材料（审计包留档）

| 层级 | 天数 | YAML 字段 |
|------|------|-----------|
| FREE | 7 天 | `tiers.FREE.retention.audit_packs_days: 7` |
| PRO | 90 天 | `tiers.PRO.retention.audit_packs_days: 90` |
| STUDIO | 365 天 | `tiers.STUDIO.retention.audit_packs_days: 365` |
| ENTERPRISE | 5 年 | `tiers.ENTERPRISE.retention.audit_packs_days: 1825` |

**拒绝 Error Code**: N/A（retention 不拒绝，仅控制保留时间）

---

### M-14: 团队协作/RBAC

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| FREE | ❌ | `tiers.FREE.capabilities.CREATE_ORG: false` |
| PRO | ❌ | `tiers.PRO.capabilities.CREATE_ORG: false` |
| STUDIO+ | ✅ | `tiers.STUDIO.capabilities.CREATE_ORG: true` |

**拒绝 Error Code**: `MEMBERSHIP_CAPABILITY_DENIED`

---

### M-15: 私有市场/企业白名单导出

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| FREE | ❌ | `tiers.FREE.capabilities.EXPORT_WHITELIST: false` |
| PRO | ❌ | `tiers.PRO.capabilities.EXPORT_WHITELIST: false` |
| STUDIO+ | ✅ | `tiers.STUDIO.capabilities.EXPORT_WHITELIST: true` |

**拒绝 Error Code**: `MEMBERSHIP_CAPABILITY_DENIED`

---

### M-16: API/CI 集成（自动审计流水线）

| 层级 | 支持 | YAML 字段 |
|------|------|-----------|
| FREE | 基础 | `tiers.FREE.capabilities.ISSUE_API_TOKEN: true` |
| PRO+ | ✅ | `tiers.PRO.rate_limit.api_requests_per_minute: 60` |

**拒绝 Error Code**: `MEMBERSHIP_RATE_LIMITED`

---

## Error Code 汇总

| Error Code | 触发场景 | 对应权益 |
|------------|----------|----------|
| `MEMBERSHIP_QUOTA_EXCEEDED` | 配额用尽 | M-01, M-02, M-04 |
| `MEMBERSHIP_CAPABILITY_DENIED` | 能力缺失 | M-09, M-12, M-14, M-15 |
| `MEMBERSHIP_RATE_LIMITED` | 速率超限 | M-16 |
| `MEMBERSHIP_REQUIRED_CHECK_FAILED` | 检查失败 | M-05 |

---

## 审计证据路径

| 权益 | 证据文件 |
|------|----------|
| M-01 | `billing/usage.jsonl` + `GateDecision` |
| M-02 | `provenance/run_meta.json` |
| M-04 | `market/listings.json` |
| M-05 | `permit.json` + `audit_pack_hash` |
| M-12 | `execution_trace.jsonl` |
| M-14 | `org_audit_log.jsonl` |
| M-15 | `whitelist.json` |
| M-16 | `api_access_log.jsonl` |

---

*文档版本: v1*
*最后更新: 2026-02-19*
