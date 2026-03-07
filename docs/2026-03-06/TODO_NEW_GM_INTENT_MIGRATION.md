# TODO - NEW-GM 意图迁移（2026-03-06）

状态枚举：`待完成` | `进行中` | `已完成` | `阻塞`

## P0（阻断放行）

| 编号 | 任务 | 状态 | DoD | 输出 |
|---|---|---|---|---|
| M1 | 建立 NEW-GM 意图对齐矩阵 | 已完成 | 覆盖外螺旋/内螺旋/北斗/gmhub/编排；每项含新 `intent_id` + gate_path + evidence | `docs/2026-03-06/NEW_GM_INTENT_PARITY_MATRIX_v1.md` |
| M2 | 外螺旋语义迁移回归（最小 1 条） | 待完成 | 旧动线在新链路可跑通并有 GateDecision + EvidenceRef | `docs/2026-03-06/verification/NEW_GM_OUTER_SPIRAL_PARITY.json` |
| M3 | 内螺旋健康/审计语义迁移回归（最小 1 条） | 待完成 | 新链路可表达旧健康/审计语义并通过 fail-closed 校验 | `docs/2026-03-06/verification/NEW_GM_INNER_SPIRAL_PARITY.json` |
| M4 | 北斗可观测语义迁移回归（最小 1 条） | 待完成 | 事件/状态语义以新 Evidence/AuditPack 结构固定并可复验 | `docs/2026-03-06/verification/NEW_GM_BEIDOU_PARITY.json` |
| M5 | 更新总账本专节 | 待完成 | `VERIFICATION_MAP.md` 增加 NEW-GM Intent Migration 专节，引用 M1-M4 证据 | `docs/VERIFICATION_MAP.md` |

## P1（收敛与维护）

| 编号 | 任务 | 状态 | DoD | 输出 |
|---|---|---|---|---|
| M6 | 旧术语到新 intent 的别名表 | 待完成 | 统一 outer_spiral/beidou 等旧词到新 `intent_id`，禁止口径漂移 | `docs/2026-03-06/NEW_GM_TERM_ALIAS_MAP.md` |
| M7 | 反向追溯表 | 待完成 | 每个新 `intent_id` 可追溯到 NEW-GM 来源文档与验收证据 | `docs/2026-03-06/NEW_GM_INTENT_TRACEBACK.md` |

## 风险规则（Fail-Closed）

1. 任一迁移项无 `EvidenceRef`：不计完成。  
2. 任一 parity 回归只有文档、无 JSON 结果：`REQUIRES_CHANGES`。  
3. 任一意图对齐无法给出 gate_path：`BLOCKED`。  

## 关联文档

- `docs/2026-03-06/NEW_GM_INTENT_MIGRATION_GAP_REPORT.md`
