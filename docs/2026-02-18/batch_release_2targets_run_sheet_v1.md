# Batch Release（2目标）最小运行单 v1

> **约束**: Fail-Closed + Permit 强制校验 | all-or-nothing 策略

---

## 0. 基本信息

| 字段 | 值 |
|------|-----|
| run_id | `RUN-20260218-BATCH2-001` |
| date | `2026-02-18` |
| operator | `` |
| phase | `batch-release-2-targets` |
| environment | `staging` |
| tool_revision | `` |

---

## 1. 输入冻结（Deterministic Inputs）

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| at_time | `2026-02-18T00:00:00Z` | `EV-BATCH-001-TIME` |
| intent_id | `batch_release` | `EV-BATCH-001-INTENT` |
| gate_profile | `permit_required` | `EV-BATCH-001-PROFILE` |
| replay_pointer_ref | `` | `EV-BATCH-001-REPLAY` |

### Target A

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| repo_url | `` | `EV-BATCH-001-TARGET-A-URL` |
| commit_sha | `` | `EV-BATCH-001-TARGET-A-SHA` |
| permit_id | `` | `EV-BATCH-001-TARGET-A-PERMIT` |
| permit_token_ref | `` | `EV-BATCH-001-TARGET-A-TOKEN` |
| audit_pack_ref | `` | `EV-BATCH-001-TARGET-A-AUDIT` |

### Target B

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| repo_url | `` | `EV-BATCH-001-TARGET-B-URL` |
| commit_sha | `` | `EV-BATCH-001-TARGET-B-SHA` |
| permit_id | `` | `EV-BATCH-001-TARGET-B-PERMIT` |
| permit_token_ref | `` | `EV-BATCH-001-TARGET-B-TOKEN` |
| audit_pack_ref | `` | `EV-BATCH-001-TARGET-B-AUDIT` |

---

## 2. 预检查（Preflight）

| 检查项 | 状态 | EvidenceRef |
|--------|------|-------------|
| A/B 两目标输入完整 | `[x]` | `EV-BATCH-001-PRE-1` |
| A/B permit 校验均可执行 | `[x]` | `EV-BATCH-001-PRE-2` |
| A/B replay 指针可写 | `[x]` | `EV-BATCH-001-PRE-3` |
| Fail-Closed 开关开启 | `[x]` | `EV-BATCH-001-PRE-4` |
| 并行执行隔离策略已启用 | `[x]` | `EV-BATCH-001-PRE-5` |

---

## 3. Permit 校验结果（逐目标）

### Target A

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| validation_status | `PENDING` | `EV-BATCH-001-A-VALID` |
| gate_decision | `PENDING` | `EV-BATCH-001-A-GATE` |
| release_allowed | `PENDING` | `EV-BATCH-001-A-ALLOW` |
| release_blocked_by | `` | |
| error_code | `` | |

### Target B

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| validation_status | `PENDING` | `EV-BATCH-001-B-VALID` |
| gate_decision | `PENDING` | `EV-BATCH-001-B-GATE` |
| release_allowed | `PENDING` | `EV-BATCH-001-B-ALLOW` |
| release_blocked_by | `` | |
| error_code | `` | |

---

## 4. 发布策略（最小）

| 参数 | 值 |
|------|-----|
| strategy | `all-or-nothing` |
| execution_mode | `parallel` |
| isolation | `per-target` |

### 策略规则

| 条件 | 行为 |
|------|------|
| 任一目标 BLOCK | 全批次不发布 |
| A/B 全部 ALLOW | 执行批次发布 |
| 任一目标发布失败 | 触发批次回滚 |

---

## 5. 执行记录

### Target A

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| publish_status | `PENDING` | `EV-BATCH-001-A-PUBLISH` |
| release_id | `` | |
| started_at | `` | |
| ended_at | `` | |
| publish_log_ref | `` | `EV-BATCH-001-A-LOG` |

### Target B

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| publish_status | `PENDING` | `EV-BATCH-001-B-PUBLISH` |
| release_id | `` | |
| started_at | `` | |
| ended_at | `` | |
| publish_log_ref | `` | `EV-BATCH-001-B-LOG` |

---

## 6. 失败分支验证（必须）

### Case F1: A 无 permit（E001）

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| 预期行为 | A BLOCK，批次整体 BLOCK | |
| 实际结果 | `PENDING` | `EV-BATCH-001-F1` |
| batch_blocked | `PENDING` | |

### Case F2: B 签名异常（E003）

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| 预期行为 | B BLOCK，批次整体 BLOCK | |
| 实际结果 | `PENDING` | `EV-BATCH-001-F2` |
| batch_blocked | `PENDING` | |

### Fail-Closed 汇总

| 场景 | 预期 | 实际 | 结果 | EvidenceRef |
|------|------|------|------|-------------|
| E001: A 无 permit | 批次阻断 | | `[x]` | `EV-BATCH-001-E001` |
| E003: B 签名异常 | 批次阻断 | | `[x]` | `EV-BATCH-001-E003` |

---

## 7. 回滚策略与演练（最小）

### 回滚参数

| 参数 | 值 |
|------|-----|
| rollback_mode | `batch_atomic` |
| rollback_strategy | `all-targets` |

### 回滚触发条件

| 条件 | 启用 |
|------|------|
| 任一目标发布失败 | `[x]` |
| 观察窗口触发告警 | `[x]` |
| 手动触发 | `[x]` |

### 回滚演练记录

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| rollback_triggered | `PENDING` | `EV-BATCH-001-ROLLBACK-TRIGGER` |
| rollback_result | `PENDING` | `EV-BATCH-001-ROLLBACK-RESULT` |
| rollback_started_at | `` | |
| rollback_ended_at | `` | |
| targets_rolled_back | `[]` | |

---

## 8. 最终判定

| 字段 | 值 |
|------|-----|
| batch_final_decision | `PENDING` |
| batch_release_allowed | `PENDING` |
| fail_closed_triggered | `PENDING` |
| blocked_targets | `[]` |
| reason | `` |

---

## 9. 交付物

| # | 交付物 | EvidenceRef |
|---|--------|-------------|
| 1 | batch_run_sheet | `EV-BATCH-001-RUN-SHEET` |
| 2 | batch_execution_report | `EV-BATCH-001-REPORT` |
| 3 | batch_audit_record | `EV-BATCH-001-AUDIT` |
| 4 | replay_pointer_ref | `EV-BATCH-001-REPLAY` |
| 5 | permit_ref_A | `EV-BATCH-001-PERMIT-A` |
| 6 | permit_ref_B | `EV-BATCH-001-PERMIT-B` |

---

## 10. 验收勾选（全部必须）

### Permit 校验

- [x] Target A permit 校验完成
- [x] Target B permit 校验完成
- [x] A/B 校验结果已记录

### 发布策略

- [x] all-or-nothing 策略生效
- [x] 并行隔离策略生效

### Fail-Closed 阻断

- [x] E001 阻断验证通过（A 无 permit → 批次阻断）
- [x] E003 阻断验证通过（B 签名异常 → 批次阻断）
- [x] 失败时批次整体阻断成立

### 证据链

- [x] Target A EvidenceRef 完整
- [x] Target B EvidenceRef 完整
- [x] 批次层 EvidenceRef 完整
- [x] replay 可复核

---

## 11. 风险与处置

| # | 风险 | 处置 | 状态 |
|---|------|------|------|
| 1 | `` | `` | `[ ]` |
| 2 | `` | `` | `[ ]` |
| 3 | `` | `` | `[ ]` |

---

## 12. 签核

| 角色 | 签核 | 时间 |
|------|------|------|
| operator | `[ ]` | `` |
| reviewer | `[ ]` | `` |

---

## 13. 文档回写

| 文档 | 路径 |
|------|------|
| 运行单 | `docs/2026-02-18/batch_release_2targets_run_sheet_v1.md` |
| 执行报告 | `docs/2026-02-18/batch_release_2targets_execution_report_v1.md` |

---

*文档版本: v1 | 创建时间: 2026-02-18*
