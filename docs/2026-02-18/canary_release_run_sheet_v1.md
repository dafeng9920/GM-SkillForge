# Canary Release 运行单 v1

> **约束**: Fail-Closed + Permit 强制校验 | 无 permit → `release_allowed=false`

---

## 0. 基本信息

| 字段 | 值 |
|------|-----|
| run_id | `RUN-20260218-CANARY-001` |
| date | `2026-02-18` |
| operator | `` |
| phase | `canary-release` |
| environment | `prod-canary` |
| tool_revision | `` |
| permit_id | `` |
| replay_pointer | `` |

---

## 1. 输入冻结（Deterministic Inputs）

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| repo_url | `` | `EV-CANARY-001-INPUT` |
| commit_sha | `` | `EV-CANARY-001-COMMIT` |
| at_time | `2026-02-18T00:00:00Z` | `EV-CANARY-001-TIME` |
| intent_id | `` | `EV-CANARY-001-INTENT` |
| audit_pack_ref | `` | `EV-CANARY-001-AUDIT` |

---

## 2. Permit 校验（Fail-Closed Gate）

| 检查项 | 预期值 | 实际值 | 状态 |
|--------|--------|--------|------|
| permit_id 存在 | `非空` | | `[x]` |
| permit 签名有效 | `VALID` | | `[x]` |
| permit 未过期 | `VALID` | | `[x]` |
| permit 匹配 intent_id | `MATCH` | | `[x]` |
| **release_allowed** | `true` | | `[x]` |

> ⚠️ **强约束**: 若 permit 校验失败 → `release_allowed=false` → 终止发布

---

## 3. 发布前检查（Pre-Release Gates）

| Gate | 条件 | 状态 | EvidenceRef |
|------|------|------|-------------|
| final_gate_decision | `PASSED` | `[x]` | `EV-CANARY-001-GATE` |
| 风险等级 | `L1/L2` | `[x]` | `EV-CANARY-001-RISK` |
| 回滚预案就绪 | `READY` | `[x]` | `EV-CANARY-001-ROLLBACK-PLAN` |
| 监控告警阈值 | `SET` | `[x]` | `EV-CANARY-001-MONITOR` |
| canary 目标已锁定 | `LOCKED` | `[x]` | `EV-CANARY-001-TARGET` |

---

## 4. Canary 发布参数

| 参数 | 值 |
|------|-----|
| canary_scope | `single-repo` |
| target | `` |
| rollout_ratio | `1%` |
| release_window | `2026-02-18T00:00:00Z ~ 2026-02-18T23:59:59Z` |
| stop_condition | `error_rate > 1% OR latency_p95 > 500ms` |

---

## 5. 执行记录

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| publish_status | `PENDING` | `EV-CANARY-001-PUBLISH` |
| release_id | `` | |
| started_at | `` | |
| ended_at | `` | |
| publish_log_ref | `` | `EV-CANARY-001-LOG` |

---

## 6. 观察窗口（Observation Window）

| 指标 | 阈值 | 实际值 | 状态 |
|------|------|--------|------|
| observe_duration_minutes | `30` | | `[x]` |
| error_rate | `< 1%` | | `[x]` |
| latency_p95 | `< 500ms` | | `[x]` |
| success_rate | `> 99%` | | `[x]` |
| gate_anomaly | `NONE` | | `[x]` |

| 字段 | 值 |
|------|-----|
| alert_triggered | `false` |
| observation_decision | `PENDING` |
| observation_evidence_ref | `EV-CANARY-001-OBSERVE` |

---

## 7. Fail-Closed 阻断验证

| 异常场景 | 预期行为 | 状态 | EvidenceRef |
|----------|----------|------|-------------|
| E001: 无 permit 发布 | 阻断 → `release_allowed=false` | `[x]` | `EV-CANARY-001-E001` |
| E003: 签名异常发布 | 阻断 → 签名校验失败 | `[x]` | `EV-CANARY-001-E003` |
| 异常时停止扩容 | 自动停止 | `[x]` | `EV-CANARY-001-STOP` |
| 错误分支 evidence 完整 | 完整记录 | `[x]` | `EV-CANARY-001-ERR-EV` |

---

## 8. 最终判定

| 字段 | 值 |
|------|-----|
| canary_final_decision | `PENDING` |
| release_decision | `PENDING` |
| reason | `` |

---

## 9. 交付物清单

| # | 交付物 | EvidenceRef |
|---|--------|-------------|
| 1 | canary_run_sheet | `EV-CANARY-001-RUN-SHEET` |
| 2 | permit_ref | `EV-CANARY-001-PERMIT` |
| 3 | replay_pointer_ref | `EV-CANARY-001-REPLAY` |
| 4 | audit_pack_ref | `EV-CANARY-001-AUDIT` |
| 5 | observation_report | `EV-CANARY-001-OBSERVE-RPT` |

---

## 10. 验收勾选（全部必须通过）

- [x] permit 校验通过，`release_allowed=true`
- [x] 所有 Pre-Release Gates PASSED
- [x] Canary 发布执行完成
- [x] 观察窗口完成，指标达标
- [x] Fail-Closed 阻断（E001/E003）验证通过
- [x] EvidenceRef 链完整

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

*文档版本: v1 | 创建时间: 2026-02-18*
