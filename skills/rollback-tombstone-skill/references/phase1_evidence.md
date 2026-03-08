# Phase-1 验收证据引用

## 运行记录

| 字段 | 值 |
|------|-----|
| drill_id | `DRILL-20260218-BIZ-PHASE1-001` |
| run_id | `RUN-20260218-BIZ-PHASE1-001` |
| permit_id | `PERMIT-20260218-BIZ-PHASE1-001` |
| replay_pointer | `REPLAY-20260218-BIZ-PHASE1-001-SHA-m1n2o3p4` |

## 回滚执行结果

| 字段 | 值 |
|------|-----|
| rollback_status | PASSED |
| rollback_duration | 90s (1.5 min) |
| rollback_strategy | immediate |

## Tombstone 记录

| 字段 | 值 |
|------|-----|
| tombstone_id | `TOMB-20260218-BIZ-PHASE1-ROLLBACK-001` |
| status | ROLLED_BACK |
| write_latency | 35ms |

## 回放一致性

| 检查项 | 结果 |
|--------|------|
| replay_pointer 有效 | VALID |
| 回放后状态一致 | CONSISTENT |
| 回放无数据丢失 | NO_LOSS |
| 回放时间 | 45s < 60s |

**replay_consistency**: true

## 关联报告

- 演练报告: `docs/2026-02-18/business_phase1_rollback_drill_report_v1.md`
- 运行单: `docs/2026-02-18/canary_rollback_drill_run_sheet_v1.md`
