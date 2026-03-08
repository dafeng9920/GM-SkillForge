# GM-SkillForge TODO（2026-02-24）

目标：在 `L4.5_ACHIEVED` 基线上，启动 `L5` 首轮推进（并发/重试降级/压测回放/nightly gate）。
状态枚举：`已完成` | `进行中` | `待完成` | `阻塞`

## 今日状态总览

| 项目 | 负责人 | 状态 | 证据 |
|---|---|---|---|
| L4.5 Final Gate 收口（T101） | Codex | 已完成 | `docs/2026-02-22/verification/L4P5_final_gate_decision.json` |
| Wave 1/2 三权闭环（T90-T99） | Execution/Review/Compliance 军团 | 已完成 | `docs/2026-02-22/verification/T9*_*.{yaml,json}` |
| 调度口径统一（governance 主线） | Codex | 已完成 | `docs/2026-02-22/task_dispatch_l4_5_upgrade.md` |
| 提示词口径统一（含兼容注释） | Codex | 已完成 | `docs/2026-02-22/tasks/L4P5_UPGRADE_PROMPTS.md` |
| L5-L6 计划更新到新基线 | Codex | 已完成 | `docs/2026-02-22/L5-L6_EXECUTION_PLAN.md` |

## 今日推进任务（L5 Day-1）

| 编号 | 任务 | 负责人 | 状态 | 当日完成标准 | 输出/证据 |
|---|---|---|---|---|---|
| D1 | 并发能力基线脚本（M1-M3） | Antigravity-1 | 待完成 | 能跑 100+ 任务并产出成功率/P95/积压恢复时间 | `reports/l5-load/baseline_2026-02-24.json` |
| D2 | 自动重试与降级策略基线（M4-M6） | vs--cc1 | 待完成 | 明确瞬态/非瞬态重试和降级触发矩阵，含 fail-closed 证明 | `reports/l5-reliability/retry_degrade_2026-02-24.md` |
| D3 | 回放一致性校验（M8） | Kior-A | 待完成 | 对固定样本回放一致性 >= 99%（若不足给 required_changes） | `reports/l5-replay/baseline_2026-02-24.json` |
| D4 | Nightly Gate 草案接入（M10） | Antigravity-1 | 待完成 | nightly job 可触发并输出 gate 结果（失败阻断） | CI run link + `docs/2026-02-24/nightly_gate_note.md` |
| D5 | 统一发现器核验（S2） | Codex | 待完成 | `skills/ + .agents/skills` 扫描输出一致，冲突策略可解释 | `configs/dispatch_skill_registry.json` 校验记录 |
| D6 | 当日 Gate 小结 | Codex | 待完成 | 汇总 D1-D5，给出 `ALLOW/REQUIRES_CHANGES` | `docs/2026-02-24/verification/L5_day1_gate_decision.json` |

## 分段推进看板（L4.6 -> L5.0）

| 阶段 | 目标 | 当前状态 | 关键未完成项 |
|---|---|---|---|
| L4.6 | 命令与证据基础层 | 进行中 | 原生命令闭环基础版、证据链强制化全覆盖 |
| L4.7 | 策略与门禁层 | 待完成 | policy_version 全链路、PR/nightly fail-closed |
| L4.8 | 编排可靠性层 | 待完成 | n8n production endpoints、并发/重试/降级/隔离证据 |
| L4.9 | 交互执行层 | 待完成 | 双窗口前端联调、执行拒绝权 |
| L5.0 | 能力闭环达标 | 待完成 | 原有6缺口完成证据、主线新增能力最小集落地 |

## 依赖与顺序（今天）

1. 先做 `D1+D2+D3`（可并行）。
2. `D4` 依赖 `D1+D2` 输出的指标与策略口径。
3. `D6` 依赖 `D1-D5` 全部产出。

## 风险与拦截

1. 任一任务无 EvidenceRef：不计完成。
2. 任一指标脚本只给描述不落盘：`REQUIRES_CHANGES`。
3. 任一出现 fail-open 路径：直接 `DENY` 当日放行。

## 明日入口（2026-02-25）

1. 若 `D6=ALLOW`：进入 L5 Day-2（扩大并发规模 + 注入故障演练）。
2. 若 `D6=REQUIRES_CHANGES`：仅修复阻断项，不扩任务面。
