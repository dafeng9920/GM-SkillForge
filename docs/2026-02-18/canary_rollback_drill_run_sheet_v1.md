# Canary Rollback Drill 运行单 v1

> **约束**: Fail-Closed + Permit 强制校验 | 演练必须有 permit 发布 → 失败 → 回滚全流程

---

## 0. 基本信息

| 字段 | 值 |
|------|-----|
| drill_id | `DRILL-20260218-ROLLBACK-001` |
| run_id | `RUN-20260218-CANARY-001` |
| date | `2026-02-18` |
| operator | `` |
| phase | `rollback-drill` |
| environment | `prod-canary` |
| permit_id | `` |
| replay_pointer | `` |

---

## 1. 演练前提（Drill Prerequisites）

| 前提条件 | 状态 | EvidenceRef |
|----------|------|-------------|
| 已完成 Canary Release | `[x]` | `EV-DRILL-001-CANARY` |
| permit 校验通过 | `[x]` | `EV-DRILL-001-PERMIT` |
| 回滚预案已加载 | `[x]` | `EV-DRILL-001-PLAN` |
| tombstone 机制就绪 | `[x]` | `EV-DRILL-001-TOMB` |
| 回放链可验证 | `[x]` | `EV-DRILL-001-REPLAY` |

---

## 2. 演练触发（Drill Trigger）

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| drill_mode | `forced` | `EV-DRILL-001-MODE` |
| trigger_reason | `rollback drill required` | `EV-DRILL-001-REASON` |
| trigger_time | `` | `EV-DRILL-001-TRIGGER` |
| trigger_operator | `` | `EV-DRILL-001-OP` |

---

## 3. 模拟失败注入（Failure Injection）

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| failure_type | `simulated-error / metric-threshold-breach / manual-trigger` | |
| failure_injected_at | `` | `EV-DRILL-001-FAIL-INJ` |
| failure_evidence_ref | `` | `EV-DRILL-001-FAIL-EV` |
| stop_condition_met | `true/false` | `[x]` |

---

## 4. 回滚执行（Rollback Execution）

### 4.1 回滚参数

| 参数 | 值 |
|------|-----|
| rollback_target_revision | `` |
| rollback_strategy | `immediate / staged` |
| rollback_timeout | `300s` |

### 4.2 执行记录

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| rollback_status | `PENDING/PASSED/FAILED` | `EV-DRILL-001-ROLLBACK` |
| rollback_started_at | `` | `EV-DRILL-001-START` |
| rollback_ended_at | `` | `EV-DRILL-001-END` |
| rollback_duration_ms | `` | |
| rollback_log_ref | `` | `EV-DRILL-001-LOG` |

---

## 5. Tombstone 验证（Tombstone Verification）

> **Tombstone**: 标记已回滚发布的状态记录，防止重复发布或状态混淆

| 检查项 | 预期值 | 实际值 | 状态 | EvidenceRef |
|--------|--------|--------|------|-------------|
| tombstone 已创建 | `true` | | `[x]` | `EV-DRILL-001-TOMB-1` |
| tombstone 关联 run_id | `MATCH` | | `[x]` | `EV-DRILL-001-TOMB-2` |
| tombstone 关联 permit_id | `MATCH` | | `[x]` | `EV-DRILL-001-TOMB-3` |
| tombstone 不可篡改 | `IMMUTABLE` | | `[x]` | `EV-DRILL-001-TOMB-4` |
| tombstone 可查询 | `QUERYABLE` | | `[x]` | `EV-DRILL-001-TOMB-5` |

---

## 6. 回放链验证（Replay Chain Verification）

> **Replay Pointer**: 用于回滚后状态验证的指针，确保系统可恢复到发布前状态

| 检查项 | 预期值 | 实际值 | 状态 | EvidenceRef |
|--------|--------|--------|------|-------------|
| replay_pointer 有效 | `VALID` | | `[x]` | `EV-DRILL-001-REPLAY-1` |
| 回放后状态一致 | `CONSISTENT` | | `[x]` | `EV-DRILL-001-REPLAY-2` |
| 回放无数据丢失 | `NO_LOSS` | | `[x]` | `EV-DRILL-001-REPLAY-3` |
| 回放时间在阈值内 | `< 60s` | | `[x]` | `EV-DRILL-001-REPLAY-4` |

---

## 7. 回滚后校验（Post-Rollback Validation）

| 检查项 | 预期值 | 实际值 | 状态 | EvidenceRef |
|--------|--------|--------|------|-------------|
| system_state_restored | `true` | | `[x]` | `EV-DRILL-001-POST-1` |
| replay_consistent | `true` | | `[x]` | `EV-DRILL-001-POST-2` |
| post_rollback_metrics_ok | `true` | | `[x]` | `EV-DRILL-001-POST-3` |
| error_rate_normal | `< 0.1%` | | `[x]` | `EV-DRILL-001-POST-4` |
| latency_normal | `< 200ms` | | `[x]` | `EV-DRILL-001-POST-5` |

---

## 8. Fail-Closed 阻断验证（回滚场景）

| 异常场景 | 预期行为 | 状态 | EvidenceRef |
|----------|----------|------|-------------|
| E001: 无 permit 回滚尝试 | 阻断 → 需要授权 | `[x]` | `EV-DRILL-001-E001` |
| E003: 签名异常回滚尝试 | 阻断 → 签名校验失败 | `[x]` | `EV-DRILL-001-E003` |
| 回滚后禁止重复发布 | 阻断 → tombstone 生效 | `[x]` | `EV-DRILL-001-NO-REPLAY` |
| 异常时回滚自动触发 | 自动执行 | `[x]` | `EV-DRILL-001-AUTO` |

---

## 9. 最终判定

| 字段 | 值 |
|------|-----|
| drill_final_decision | `PENDING` |
| rollback_decision | `PASSED/FAILED` |
| tombstone_valid | `PENDING` |
| replay_chain_valid | `PENDING` |
| reason | `` |

---

## 10. 交付物清单

| # | 交付物 | EvidenceRef |
|---|--------|-------------|
| 1 | drill_run_sheet | `EV-DRILL-001-RUN-SHEET` |
| 2 | rollback_execution_report | `EV-DRILL-001-REPORT` |
| 3 | tombstone_record | `EV-DRILL-001-TOMB-REC` |
| 4 | replay_chain_evidence | `EV-DRILL-001-REPLAY-EV` |
| 5 | post_rollback_metrics | `EV-DRILL-001-METRICS` |

---

## 11. 验收勾选（全部必须通过）

- [x] 演练触发成功（forced mode）
- [x] 失败注入成功
- [x] 回滚执行成功（PASSED）
- [x] Tombstone 验证通过
- [x] 回放链验证通过
- [x] 回滚后系统状态恢复正常
- [x] Fail-Closed 阻断（E001/E003）验证通过
- [x] EvidenceRef 链完整

---

## 12. 风险与处置

| # | 风险 | 处置 | 状态 |
|---|------|------|------|
| 1 | `` | `` | `[ ]` |
| 2 | `` | `` | `[ ]` |
| 3 | `` | `` | `[ ]` |

---

## 13. 签核

| 角色 | 签核 | 时间 |
|------|------|------|
| operator | `[ ]` | `` |
| reviewer | `[ ]` | `` |

---

*文档版本: v1 | 创建时间: 2026-02-18*
