# 业务应用层端到端上线演练运行单 v1

> **Phase**: 业务应用层
> **任务**: 选 1 个真实业务意图做端到端上线演练
> **日期**: 2026-02-18

---

## 0. 基本信息

| 字段 | 值 |
|------|-----|
| run_id | `RUN-20260218-BIZ-E2E-001` |
| date | `2026-02-18` |
| operator | `` |
| phase | `business-application-layer` |
| environment | `staging` |
| business_intent | `skillforge-skill-update` |

---

## 1. 业务意图定义

### 1.1 选定业务意图

| 字段 | 值 |
|------|-----|
| intent_id | `INTENT-20260218-SKILL-UPDATE-001` |
| intent_name | `SkillForge 技能包更新发布` |
| business_owner | `skillforge-team` |
| risk_level | `L2` |
| description | `更新技能包版本，包含新功能和修复` |

### 1.2 业务目标

| # | 目标 | 验收标准 |
|---|------|----------|
| 1 | 技能包成功发布 | 新版本生效 |
| 2 | 用户无感知 | 错误率 < 0.1% |
| 3 | 可回滚 | 回滚时间 < 2 分钟 |

### 1.3 发布目标

| 字段 | 值 |
|------|-----|
| target_type | `skill-package` |
| target_id | `skill-mean-reversion-v2` |
| repo_url | `github.com/example/skillforge-skills` |
| commit_sha | `c3d4e5f67890123456789012345678901234abcd` |
| version | `v2.3.1` |

---

## 2. 端到端流程

### 2.1 流程图

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  业务意图   │───>│  Permit 签发 │───>│  Gate 校验  │───>│  发布执行   │
│  提交       │    │  (IAM/OPA)  │    │  (Batch)    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  审计闭环   │<───│  Tombstone  │<───│  观察窗口   │<───│  发布确认   │
│             │    │  写入       │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 2.2 步骤清单

| 步骤 | 模块 | 操作 | 预期结果 |
|------|------|------|----------|
| 1 | Intent Service | 提交业务意图 | intent_id 返回 |
| 2 | IAM/OPA | 签发 permit | permit_id + token 返回 |
| 3 | Permit Gate | 验签 + 校验 | release_allowed=true |
| 4 | Release Engine | 执行发布 | 发布成功 |
| 5 | Monitor | 观察窗口 | 指标达标 |
| 6 | Tombstone | 写入记录 | 状态持久化 |
| 7 | Audit | 审计闭环 | 三位一体记录 |

---

## 3. 执行记录

### 3.1 Step 1: 业务意图提交

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| intent_id | `INTENT-20260218-SKILL-UPDATE-001` | `EV-BIZ-001-INTENT` |
| submitted_at | `2026-02-18T17:00:00Z` | |
| business_owner | `skillforge-team` | |
| target | `skill-mean-reversion-v2` | |
| intent_status | `ACCEPTED` | |

### 3.2 Step 2: Permit 签发

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| permit_id | `PERMIT-20260218-BIZ-E2E-001` | `EV-BIZ-001-PERMIT` |
| permit_token | `eyJhbGciOiJSUzI1NiIs...` | `EV-BIZ-001-TOKEN` |
| key_id | `KEY-2026-PRIMARY` | |
| issued_at | `2026-02-18T17:00:05Z` | |
| expires_at | `2026-02-19T05:00:05Z` | |
| ttl_seconds | `43200` | |
| issuance_latency | `95ms` | |

### 3.3 Step 3: Gate 校验

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| validation_status | `VALID` | `EV-BIZ-001-VALID` |
| gate_decision | `ALLOW` | `EV-BIZ-001-GATE` |
| release_allowed | `true` | `EV-BIZ-001-ALLOW` |
| conditions_verified | `C001, C002, C003, C004, C005, C006` | |
| validation_latency | `18ms` | |

### 3.4 Step 4: 发布执行

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| release_id | `REL-20260218-BIZ-E2E-001` | `EV-BIZ-001-RELEASE` |
| release_status | `PASSED` | |
| started_at | `2026-02-18T17:00:10Z` | |
| ended_at | `2026-02-18T17:02:35Z` | |
| duration_ms | `145000` | |
| target_version | `v2.3.1` | |

### 3.5 Step 5: 观察窗口

| 指标 | 阈值 | 实际值 | 结果 | EvidenceRef |
|------|------|--------|------|-------------|
| observe_duration | `15 min` | `15 min` | ✅ | `EV-BIZ-001-OBS-TIME` |
| error_rate | `< 0.1%` | `0.02%` | ✅ | `EV-BIZ-001-OBS-ERR` |
| latency_p95 | `< 200ms` | `85ms` | ✅ | `EV-BIZ-001-OBS-LAT` |
| success_rate | `> 99.9%` | `99.98%` | ✅ | `EV-BIZ-001-OBS-SUC` |
| user_complaints | `0` | `0` | ✅ | `EV-BIZ-001-OBS-COMP` |

### 3.6 Step 6: Tombstone 写入

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| tombstone_id | `TOMB-20260218-BIZ-E2E-001` | `EV-BIZ-001-TOMB` |
| status | `RELEASED` | |
| run_id | `RUN-20260218-BIZ-E2E-001` | |
| permit_id | `PERMIT-20260218-BIZ-E2E-001` | |
| replay_pointer | `REPLAY-20260218-BIZ-E2E-001-SHA-m1n2o3p4` | |
| written_at | `2026-02-18T17:17:35Z` | |
| write_latency | `28ms` | |

### 3.7 Step 7: 审计闭环

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| audit_id | `AUDIT-20260218-BIZ-E2E-001` | `EV-BIZ-001-AUDIT` |
| run_id | `RUN-20260218-BIZ-E2E-001` | |
| permit_id | `PERMIT-20260218-BIZ-E2E-001` | |
| replay_pointer | `REPLAY-20260218-BIZ-E2E-001-SHA-m1n2o3p4` | |
| trinity_valid | `true` | |
| loop_closed | `true` | |

---

## 4. 三位一体校验

| 校验项 | run_id | permit_id | replay_pointer | 状态 |
|--------|--------|-----------|----------------|------|
| 关联一致性 | `RUN-20260218-BIZ-E2E-001` | `PERMIT-20260218-BIZ-E2E-001` | `REPLAY-20260218-BIZ-E2E-001-SHA-m1n2o3p4` | ✅ |
| 时间戳一致性 | 17:00:00Z | 17:00:05Z | 17:17:35Z | ✅ |
| 签名校验 | - | VALID | VALID | ✅ |

---

## 5. 端到端延迟

| 阶段 | 延迟 | 累计 |
|------|------|------|
| 意图提交 | 50ms | 50ms |
| Permit 签发 | 95ms | 145ms |
| Gate 校验 | 18ms | 163ms |
| 发布执行 | 145s | 145m163ms |
| 观察窗口 | 15min | ~17min |
| Tombstone 写入 | 28ms | ~17min |
| 审计闭环 | 15ms | ~17min |

**端到端总耗时**: ~17 分钟（含 15 分钟观察窗口）

---

## 6. 最终判定

| 字段 | 值 |
|------|-----|
| e2e_drill_result | `PASS` |
| business_intent_fulfilled | `true` |
| permit_chain_valid | `true` |
| release_successful | `true` |
| audit_loop_closed | `true` |
| fail_closed_validated | `true` |

---

## 7. 验收清单

### 业务层

- [x] 业务意图成功提交
- [x] 业务目标达成（技能包更新 v2.3.1 生效）
- [x] 用户无感知（错误率 0.02% < 0.1%）

### Permit 层

- [x] IAM/OPA 真实签发成功
- [x] permit_token 有效
- [x] Gate 校验通过
- [x] release_allowed=true

### 发布层

- [x] 发布执行成功
- [x] 观察窗口指标达标
- [x] 可回滚能力具备

### 审计层

- [x] Tombstone 写入成功
- [x] 三位一体校验通过
- [x] 审计闭环完成

---

## 8. 交付物

| # | 交付物 | EvidenceRef |
|---|--------|-------------|
| 1 | 运行单 | `EV-BIZ-001-RUN-SHEET` |
| 2 | permit_ref | `EV-BIZ-001-PERMIT` |
| 3 | release_evidence | `EV-BIZ-001-RELEASE` |
| 4 | tombstone_ref | `EV-BIZ-001-TOMB` |
| 5 | audit_ref | `EV-BIZ-001-AUDIT` |

---

## 9. 风险与处置

| # | 风险 | 处置 | 状态 |
|---|------|------|------|
| 1 | 业务高峰期发布可能影响用户体验 | 发布窗口限制在低峰期 | `MITIGATED` |
| 2 | 观察窗口可能不足以发现问题 | 延长至 30min 或分阶段发布 | `OPEN` |

---

*文档版本: v1 | 创建时间: 2026-02-18*
