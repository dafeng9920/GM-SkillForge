# TODO（Unfinished Snapshot from 2026-03-05）

来源文档：`docs/2026-03-05/TODO_UPGRADE_2026-03-05.md`  
生成时间：2026-03-06（append-only，不回写历史）

---

## 筛选规则

仅保留原文中状态为以下值的任务：
- `证据缺失`
- `待完成`
- `进行中`
- `阻塞`
- `REQUIRES_CHANGES`

---

## P0 - 证据补齐（阻断性）

| 编号 | 任务 | 原状态（2026-03-05） | 输出文件路径 | 截止时间 |
|---|---|---|---|---|
| D1 | 并发能力基线脚本（M1-M3） | 证据缺失 | `reports/l5-load/baseline_2026-03-05.json` | 2026-03-06 23:59 UTC |
| D2 | 自动重试与降级策略基线（M4-M6） | 证据缺失 | `reports/l5-reliability/retry_degrade_2026-03-05.md` | 2026-03-06 23:59 UTC |
| D3 | 回放一致性校验（M8） | 证据缺失 | `reports/l5-replay/baseline_2026-03-05.json` | 2026-03-06 23:59 UTC |
| D6 | 当日 Gate 小结 | 证据缺失 | `docs/2026-03-05/verification/L5_day1_gate_decision.json` | 2026-03-07 00:30 UTC |

---

## P1 - 已有证据核验（非阻断但必须核验）

| 编号 | 任务 | 原状态（2026-03-05） | 输出文件路径 | 截止时间 |
|---|---|---|---|---|
| V1 | L3 Gap Closure 证据核验 | 待完成 | `reports/l3_gap_closure/2026-03-05/verification_report.json` | 2026-03-06 18:00 UTC |

---

## P2 - 配置与文档更新（低优先级）

| 编号 | 任务 | 原状态（2026-03-05） | 输出文件路径 | 截止时间 |
|---|---|---|---|---|
| U1 | 技能注册表配置核验 | 待完成 | `configs/dispatch_skill_registry.json` + `reports/config/registry_verification_2026-03-05.json` | 2026-03-07 23:59 UTC |
| U2 | 文档时间戳更新 | 待完成 | `docs/2026-03-05/CHANGELOG.md` | 2026-03-07 23:59 UTC |

---

## 今日执行建议（2026-03-06）

1. 先做 P0：D6 汇总与签发（若 D1/D2/D3 已有实证则先做状态回填）。  
2. 再做 P1：V1 核验落盘并补证据链。  
3. 最后做 P2：U1/U2 文档与配置一致性收口。  

---

## 备注

- 本文档是“未完成项快照”，不替代原始计划文档。  
- 原始文档保持 `COMPLETED_LOCKED`，仅通过新日期文档继续推进。  

---

## 执行结果回填（2026-03-06）

回填时间：2026-03-06T05:50:06Z（UTC）

| 编号 | 回填状态（2026-03-06） | 证据/结果 |
|---|---|---|
| D1 | COMPLETED | `reports/l5-load/baseline_2026-03-05.json` |
| D2 | COMPLETED | `reports/l5-reliability/retry_degrade_2026-03-05.md` |
| D3 | COMPLETED | `reports/l5-replay/baseline_2026-03-05.json` |
| D6 | COMPLETED | `docs/2026-03-05/verification/L5_day1_gate_decision.json` |
| V1 | COMPLETED | `reports/l3_gap_closure/2026-03-05/verification_report.json` |
| U1 | COMPLETED | `configs/dispatch_skill_registry.json` + `reports/config/registry_verification_2026-03-05.json`（`overall_status=PASS`） |
| U2 | COMPLETED | `docs/2026-03-05/CHANGELOG.md` |

### 回填说明

- 本次为 append-only 回填，不修改原“未完成快照”内容。
- 全部清单目标路径已存在并完成核验。
