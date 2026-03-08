# 2026-02-22 Task Dispatch（L4 -> L4.5 升级清单）

job_id: L4P5-UPGRADE-20260222-001
protocol: multi-ai-collaboration.md v3
owner: Codex (Orchestrator)
goal: 将“可运行 L4”升级为“可治理/可规模/可稳定运行的 L4.5”
mode: strict (default) / batch-fastlane (optional)

## 调度 Skill 口径（统一）

- 主线：`governance-orchestrator-skill`（统一编排/审查/合规入口）。
- 兼容：`trinity-dispatch-orchestrator-skill` 仅作为历史兼容别名保留。
- 注册表以 `configs/dispatch_skill_registry.json` 为准，冲突时主线优先。

## 三权分立（MUST）

- Review 总负责: Antigravity-2
- Compliance 总负责: Kior-C
- Execution 按任务实名绑定（见下表）
- 角色不可混同；任一任务缺 `execution_report + gate_decision + compliance_attestation` 即 `DENY`。

## Mode 说明（本单可切换）

当前推荐：`strict`（保持现有依赖链与门禁顺序不变）。

可选切换：`batch-fastlane`
- Wave 1: 先并行执行 `T90/T91/T92` -> 再集中 `T93` -> 再 `T94`
- Wave 2: 先并行执行 `T95/T96/T97` -> 再集中 `T98` -> 再 `T99`
- Wave 3: `T100 -> T101` 保持串行

`batch-fastlane` 前置：
1. 本波次任务均为中低风险，且模板一致。
2. 无高风险动作（Shell/File delete/DB/Network）；如检测到则自动降级回 `strict`。
3. 任一任务在汇总审查阶段未过，整波次进入修复队列，不得直接推进下波次。

## 波次编排（任务编号化 Txx）

| Wave | Task | 模块 | 主责（实名） | 审查人 | 合规人 | Depends On | 输出 |
|---|---|---|---|---|---|---|---|
| 1 | T90 | 系统级 `skillforge` 入口（全流程命令） | Antigravity-1 (Execution) | Antigravity-2 | Kior-C | - | `T90_execution_report.yaml` |
| 1 | T91 | `policy_version` 与策略配置化 | vs--cc3 (Execution) | Antigravity-2 | Kior-C | T90 | `T91_execution_report.yaml` |
| 1 | T92 | 证据链硬约束（run_id/hash/ref/replay） | Antigravity-1 (Execution) | Antigravity-2 | Kior-C | T90 | `T92_execution_report.yaml` |
| 1 | T93 | Review 验收（T90-T92） | Antigravity-2 (Review) | Codex | Kior-C | T90,T91,T92 | `T93_gate_decision.json` |
| 1 | T94 | Compliance 预审/终审（T90-T93） | Kior-C (Compliance) | Antigravity-2 | Codex | T93=ALLOW | `T94_compliance_attestation.json` |
| 2 | T95 | CI/CD 门禁自动化（PR/nightly fail-closed） | Antigravity-1 (Execution) | Antigravity-2 | Kior-C | T94=PASS | `T95_execution_report.yaml` |
| 2 | T96 | 一致性契约 + 重置语义统一（iterate/rollback/rebase） | vs--cc1 (Execution) | Antigravity-2 | Kior-C | T94=PASS | `T96_execution_report.yaml` |
| 2 | T97 | Doc-to-Skill 管线接入（ingest->parse->contract->gate->render） | Kior-A (Execution) | Antigravity-2 | Kior-C | T94=PASS | `T97_execution_report.yaml` |
| 2 | T98 | Review 验收（T95-T97） | Antigravity-2 (Review) | Codex | Kior-C | T95,T96,T97 | `T98_gate_decision.json` |
| 2 | T99 | Compliance 终审（T95-T98） | Kior-C (Compliance) | Antigravity-2 | Codex | T98=ALLOW | `T99_compliance_attestation.json` |
| 3 | T100 | 双窗口交互 + 执行拒绝权（Intent Not Buildable -> DENY） | Antigravity-1 (Execution) | Antigravity-2 | Kior-C | T99=PASS | `T100_execution_report.yaml` |
| 3 | T101 | 编排规模化压测（并发/重试/降级/队列隔离）+ Final Gate | Codex (Final Gate) | Antigravity-2 | Kior-C | T100 | `L4P5_final_gate_decision.json` |

## 任务-责任映射（用于转发与追责）

- `T90/T92/T95/T100` -> Antigravity-1
- `T91` -> vs--cc3
- `T96` -> vs--cc1
- `T97` -> Kior-A
- `T93/T98` -> Antigravity-2
- `T94/T99` -> Kior-C
- `T101` -> Codex

## 每任务统一验收口径

1. `execution_report`：包含 `PreflightChecklist / ExecutionContract / RequiredChanges`。
2. `gate_decision`：包含 `decision / reasons / evidence_refs / required_changes`。
3. `compliance_attestation`：包含 `decision / violations / evidence_refs / required_changes`。
4. 所有任务必须可追溯到 `run_id` 与 `policy_version`。

## 放行条件（L4.5）

满足以下全部条件，`T101` 才可 `ALLOW`：

1. `skillforge` 系统级命令已可跑一键全流程。
2. 证据链默认强制开启，回放可用。
3. CI/nightly 失败自动阻断发布。
4. 双窗口交互生效，执行窗口支持拒绝并输出 `required_changes`。
5. 编排层并发/重试/降级/隔离有压测证据。
6. 调度流程通过统一入口执行（`governance-orchestrator-skill` / `skillforge dispatch|gate`），不得绕过注册表。

## 验收产物（统一路径）

- `docs/2026-02-22/verification/T90_execution_report.yaml`
- `docs/2026-02-22/verification/T91_execution_report.yaml`
- `docs/2026-02-22/verification/T92_execution_report.yaml`
- `docs/2026-02-22/verification/T93_gate_decision.json`
- `docs/2026-02-22/verification/T94_compliance_attestation.json`
- `docs/2026-02-22/verification/T95_execution_report.yaml`
- `docs/2026-02-22/verification/T96_execution_report.yaml`
- `docs/2026-02-22/verification/T97_execution_report.yaml`
- `docs/2026-02-22/verification/T98_gate_decision.json`
- `docs/2026-02-22/verification/T99_compliance_attestation.json`
- `docs/2026-02-22/verification/T100_execution_report.yaml`
- `docs/2026-02-22/verification/L4P5_final_gate_decision.json`
