# NEW-GM Intent Parity Matrix v1

Date: `2026-03-06`  
Scope: `D:\NEW-GM` → `D:\GM-SkillForge` (intent semantics, not code copy)  
Status Enum: `Implemented` | `Partial` | `Missing`

## Summary

- Total intents reviewed: `18`
- Implemented: `8`
- Partial: `6`
- Missing: `4`

判定标准：
- `Implemented`: 新仓存在合同/代码/测试/证据链闭环。
- `Partial`: 有映射或合同，但缺执行闭环或缺对齐验证。
- `Missing`: 未找到当前系统中的等价 intent 合同与执行入口。

---

## Parity Matrix

| # | 旧意图（中文） | 旧证据（NEW-GM） | 新意图（中文） | 英文ID | 当前证据 | 状态 | 缺口 / 下一步 |
|---|---|---|---|---|---|---|---|
| 1 | 宪法生存原则 | `D:\NEW-GM\docs\2026-02-16\constitution_v1.md` | 宪法生存原则 | `constitution_principle_survival` | `skillforge/src/orchestration/intent_map.yml` + `docs/2026-02-16/constitution_v1.md` | Implemented | 保持主线门禁 |
| 2 | 宪法默认拒绝原则 | 同上 | 宪法默认拒绝原则 | `constitution_principle_default_deny` | `intent_map.yml` + `core/gate_engine.py` fail-closed | Implemented | 在 M2 增加 parity 测试 |
| 3 | 宪法证据优先原则 | 同上 | 宪法证据优先原则 | `constitution_principle_evidence` | `intent_map.yml` + `core/pack_and_permit.py` | Implemented | 无 |
| 4 | 仓库审计技能 | `docs/2026-02-17/图书馆迁移/library_intent_inventory_v1.md` | 仓库审计技能 | `audit_repo_skill` | `docs/2026-02-17/图书馆迁移/contracts/intents/audit_repo.yml` | Implemented | 增加回归样例 |
| 5 | 从仓库生成技能 | 同 inventory/mapping | 从仓库生成技能 | `generate_skill_from_repo` | `docs/2026-02-17/图书馆迁移/contracts/intents/generate_skill.yml` | Implemented | 无 |
| 6 | 技能版本升级 | 同 inventory/mapping | 技能版本升级 | `upgrade_skill_revision` | `docs/2026-02-17/图书馆迁移/contracts/intents/upgrade_skill.yml` | Implemented | 无 |
| 7 | 技能墓碑化/下线 | 同 inventory/mapping | 技能墓碑化/下线 | `tombstone_skill` | `docs/2026-02-17/图书馆迁移/contracts/intents/tombstone.yml` | Implemented | 无 |
| 8 | 时间语义 | `core_time_machine` inventory 项 | 时间语义 | `time_semantics` | `docs/2026-02-17/图书馆迁移/contracts/intents/time_semantics.yml` | Implemented | 增加 at_time 回放测试 |
| 9 | 外螺旋意图摄取 | `axis_intent_ingest`（`intent_map.yml`） | 外螺旋意图摄取（计划） | `outer_intent_ingest` | `intent_map.yml` integration=`l42_planned` | Partial | 升级到 mainline + 合同测试 |
| 10 | 外螺旋负向收敛 | `axis_negative_convergence` | 外螺旋负向收敛（计划） | `outer_negative_convergence` | `intent_map.yml` integration=`l42_planned` | Partial | 增加合同与 gate 证据 |
| 11 | 外螺旋合同冻结 | `axis_contract_freeze` | 外螺旋合同冻结（计划） | `outer_contract_freeze` | `intent_map.yml` integration=`l42_planned` | Partial | 增加运行态 parity 校验 |
| 12 | 外螺旋工件构建 | `axis_artifact_build` | 外螺旋工件构建（计划） | `outer_artifact_build` | `intent_map.yml` integration=`l42_planned` | Partial | 增加端到端门禁执行 |
| 13 | 趋势跟随策略 | `strat_trend_follow` inventory 项 | 趋势跟随策略合同已存在 | `trend_following` | `docs/2026-02-17/图书馆迁移/contracts/intents/trend_following.yml` | Partial | 缺 parity 执行证据 |
| 14 | 均值回归策略 | `strat_mean_revert` inventory 项 | 均值回归策略合同已存在 | `mean_reversion` | `docs/2026-02-17/图书馆迁移/contracts/intents/mean_reversion.yml` | Partial | 缺 parity 执行证据 |
| 15 | 多因子策略 | `strat_multi_factor` inventory 项 | 多因子策略合同已存在 | `multi_factor` | `docs/2026-02-17/图书馆迁移/contracts/intents/multi_factor.yml` | Partial | 缺 parity 执行证据 |
| 16 | 外螺旋主路由语义 | `D:\NEW-GM\docs\2025-12-10\外螺旋动线.md` | 暂无直接等价新意图 | `outer_spiral_route_intent`（拟定） | `d:\GM-SkillForge\src\gateway\routers\outer_spiral_router.py` 不存在 | Missing | 定义新意图 + parity 用例 |
| 17 | 内螺旋健康/审计语义 | `D:\NEW-GM\docs\2025-11-29\内螺旋组件清单.md` | 暂无直接等价新意图 | `inner_health_audit_intent`（拟定） | `d:\GM-SkillForge\src\inner_spiral\healthcheck.py` 不存在 | Missing | 定义新意图 + parity 用例 |
| 18 | 北斗可观测灯态语义 | `D:\NEW-GM\docs\2025-12-10\Beidou-Lightup-Plan-v0.1.md` | 暂无等价主线合同 | `beidou_observability_intent`（拟定） | `d:\GM-SkillForge\src\services\beidou\beidou_store.py` 不存在 | Missing | 定义新意图 + 证据 schema |

---

## Priority Backlog (from matrix)

## P0
1. Add contracts + gate path for `outer_spiral_route_intent` (`#16`).
2. Add contracts + gate path for `inner_health_audit_intent` (`#17`).
3. Add contracts + gate path for `beidou_observability_intent` (`#18`).

## P1
1. Promote rows `#9-#12` from `l42_planned` to mainline with executable parity JSON.
2. Add parity execution evidence for strategy intents `#13-#15`.

---

## Notes

- This matrix intentionally follows the "intent-only migration" rule; it does not require copying legacy code.
- Completion criteria for each row must include machine-verifiable evidence (`GateDecision + EvidenceRef + output artifact`).
