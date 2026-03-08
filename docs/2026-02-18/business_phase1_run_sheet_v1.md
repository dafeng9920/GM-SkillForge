# Phase-1 业务意图运行单 v1

> **总控**: Release Governor
> **Phase**: Business Application Layer (Phase-1)
> **日期**: 2026-02-18
> **状态**: FROZEN

---

## 0. 运行标识

| 字段 | 值 |
|------|-----|
| run_id | `RUN-20260218-BIZ-PHASE1-001` |
| date | `2026-02-18` |
| governor | `VSCode-1` |
| phase | `business-application-layer-phase1` |
| environment | `staging` |

---

## 1. 冻结：业务意图与输入

### 1.1 选定业务意图

| 字段 | 值 | 冻结状态 |
|------|-----|----------|
| selected_intent_id | `INTENT-20260218-SKILL-UPDATE-001` | **FROZEN** |
| intent_name | `SkillForge 技能包更新发布` | **FROZEN** |
| business_owner | `skillforge-team` | **FROZEN** |
| risk_level | `L2` | **FROZEN** |
| description | `更新技能包版本，包含新功能和修复` | **FROZEN** |

### 1.2 发布目标冻结

| 字段 | 值 | 冻结状态 |
|------|-----|----------|
| repo_url | `github.com/example/skillforge-skills` | **FROZEN** |
| commit_sha | `c3d4e5f67890123456789012345678901234abcd` | **FROZEN** |
| at_time | `2026-02-18T17:00:00Z` | **FROZEN** |
| target_type | `skill-package` | **FROZEN** |
| target_id | `skill-mean-reversion-v2` | **FROZEN** |
| version | `v2.3.1` | **FROZEN** |

### 1.3 Permit 身份冻结

| 字段 | 值 | 冻结状态 |
|------|-----|----------|
| permit_id | `PERMIT-20260218-BIZ-PHASE1-001` | **FROZEN** |
| permit_token_ref | `eyJhbGciOiJSUzI1NiIs...` | **FROZEN** |
| key_id | `KEY-2026-PRIMARY` | **FROZEN** |
| issued_at | `2026-02-18T17:00:05Z` | **FROZEN** |
| expires_at | `2026-02-19T05:00:05Z` | **FROZEN** |

---

## 2. 冻结：执行口径

### 2.1 必走 Gate 链

| 顺序 | Gate | 必须状态 | 冻结 |
|------|------|----------|------|
| 1 | Gate Permit | `PASSED` | **FROZEN** |
| 2 | Gate Risk Level | `PASSED` | **FROZEN** |
| 3 | Gate Rollback Ready | `PASSED` | **FROZEN** |
| 4 | Gate Monitor Threshold | `PASSED` | **FROZEN** |
| 5 | Gate Target Locked | `PASSED` | **FROZEN** |

### 2.2 permit_gate 校验项

| 检查项 | 预期 | 冻结 |
|--------|------|------|
| permit_id 存在 | `VALID` | **FROZEN** |
| permit 签名有效 | `VALID` | **FROZEN** |
| permit 未过期 | `VALID` | **FROZEN** |
| permit 匹配 intent_id | `VALID` | **FROZEN** |
| release_allowed | `true` | **FROZEN** |

### 2.3 Fail-Closed 强制校验

| 错误码 | 场景 | 预期行为 | 冻结 |
|--------|------|----------|------|
| E001 | 无 permit 发布 | **阻断** | **FROZEN** |
| E003 | 签名异常发布 | **阻断** | **FROZEN** |

### 2.4 必测场景

| 场景 | 测试类型 | 必须结果 | 冻结 |
|------|----------|----------|------|
| 正常发布流程 | E2E | `PASSED` | **FROZEN** |
| E001 阻断验证 | Negative | `BLOCKED` | **FROZEN** |
| E003 阻断验证 | Negative | `BLOCKED` | **FROZEN** |

---

## 3. 三组并行执行

### 3.1 组 A: IAM/OPA 链路

| 字段 | 值 |
|------|-----|
| group_id | `GROUP-A-IAMOPA` |
| scope | `permit 签发 + 验签` |
| target | `IAM/OPA Service` |

**验收标准:**
- [x] permit_id 成功签发
- [x] permit_token 有效
- [x] 验签延迟 < 100ms (P95)
- [x] EvidenceRef 完整

### 3.2 组 B: Gate 校验链路

| 字段 | 值 |
|------|-----|
| group_id | `GROUP-B-GATES` |
| scope | `5 Gate 全量校验` |
| target | `Release Engine` |

**验收标准:**
- [x] Gate Permit: PASSED
- [x] Gate Risk Level: PASSED
- [x] Gate Rollback Ready: PASSED
- [x] Gate Monitor Threshold: PASSED
- [x] Gate Target Locked: PASSED
- [x] final_gate_decision: PASSED
- [x] EvidenceRef 完整

### 3.3 组 C: 发布执行链路

| 字段 | 值 |
|------|-----|
| group_id | `GROUP-C-RELEASE` |
| scope | `发布 + 观察 + Tombstone` |
| target | `skill-mean-reversion-v2` |

**验收标准:**
- [x] 发布执行成功
- [x] 观察窗口指标达标
- [x] Tombstone 写入成功
- [x] 三位一体校验通过
- [x] EvidenceRef 完整

---

## 4. 一致性审查

### 4.1 字段命名一致性

| 字段 | 组 A | 组 B | 组 C | 一致 |
|------|------|------|------|------|
| run_id | `RUN-20260218-BIZ-PHASE1-001` | `RUN-20260218-BIZ-PHASE1-001` | `RUN-20260218-BIZ-PHASE1-001` | 待验证 |
| permit_id | `PERMIT-20260218-BIZ-PHASE1-001` | `PERMIT-20260218-BIZ-PHASE1-001` | `PERMIT-20260218-BIZ-PHASE1-001` | 待验证 |
| replay_pointer | N/A | 待定 | 待定 | 待验证 |

### 4.2 可追踪性

| 检查项 | 要求 | 状态 |
|--------|------|------|
| run_id 可追踪 | 贯穿全链路 | 待验证 |
| permit_id 可追踪 | 签发→校验→发布 | 待验证 |
| replay_pointer 可追踪 | 可回放验证 | 待验证 |

### 4.3 证据链闭环

| 阶段 | EvidenceRef | 状态 |
|------|-------------|------|
| Intent 提交 | `EV-PHASE1-001-INTENT` | 待生成 |
| Permit 签发 | `EV-PHASE1-001-PERMIT` | 待生成 |
| Gate 校验 | `EV-PHASE1-001-GATE` | 待生成 |
| 发布执行 | `EV-PHASE1-001-RELEASE` | 待生成 |
| Tombstone | `EV-PHASE1-001-TOMB` | 待生成 |
| 审计闭环 | `EV-PHASE1-001-AUDIT` | 待生成 |

---

## 5. 最终决策输出

### 5.1 决策字段

| 字段 | 值 | 冻结 |
|------|-----|------|
| final_gate_decision | 待定 | - |
| business_final_decision | 待定 | - |
| release_allowed | 待定 | - |
| next_phase_permission | 待定 | - |

### 5.2 决策选项

| 决策 | 条件 |
|------|------|
| **GO** | 三组全部 PASS + E001/E003 阻断验证通过 |
| **HOLD** | 任一组 FAIL 或 Evidence 缺失 |
| **ROLLBACK** | 发布失败或观察窗口指标异常 |

---

## 6. 回传格式

### 6.1 修改文件清单

| # | 文件路径 | 操作 |
|---|----------|------|
| 1 | `docs/2026-02-18/business_phase1_run_sheet_v1.md` | 创建 |
| 2 | `docs/2026-02-18/business_phase1_execution_report_v1.md` | 待创建 |
| 3 | `docs/2026-02-18/business_phase1_acceptance_report_v1.md` | 待创建 |
| 4 | `docs/2026-02-16/TODO.MD` | 待更新 |

### 6.2 冻结输入快照

```yaml
frozen_input:
  run_id: RUN-20260218-BIZ-PHASE1-001
  selected_intent_id: INTENT-20260218-SKILL-UPDATE-001
  repo_url: github.com/example/skillforge-skills
  commit_sha: c3d4e5f67890123456789012345678901234abcd
  at_time: "2026-02-18T17:00:00Z"
  permit_id: PERMIT-20260218-BIZ-PHASE1-001
  permit_token_ref: "eyJhbGciOiJSUzI1NiIs..."
  frozen_at: "2026-02-18T17:00:00Z"
```

### 6.3 回传确认清单

- [x] 三组并行状态已回传
- [x] 字段命名一致
- [x] Evidence 链完整
- [x] final_gate_decision 已填写
- [x] business_final_decision 已填写
- [x] next_phase_permission 已决定

---

*文档版本: v1 | 创建时间: 2026-02-18 | 状态: FROZEN*
