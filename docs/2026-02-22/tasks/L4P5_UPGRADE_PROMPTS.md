# L4P5-UPGRADE 三权分立提示词（按 multi-ai-collaboration.md v3）

适用调度单：`docs/2026-02-22/task_dispatch_l4_5_upgrade.md`  
协议基线：`multi-ai-collaboration.md`、`docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`、`docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

> 执行军团口径：8 位（`vs--cc1`、`vs--cc2`、`vs--cc3`、`Kior-A`、`Kior-B`、`Kior-C`、`Antigravity-1`、`Antigravity-2`）。  
> 注：`Antigravity-3` 不存在，不参与本批次。

> 调度 Skill 统一口径：主线使用 `governance-orchestrator-skill`；  
> 兼容注释：若历史材料出现 `trinity-dispatch-orchestrator-skill`，按同一能力别名处理，不另开分支流程。

---

## RERUN-WAVE1（返工版，当前唯一执行入口）

适用前提：
- `docs/2026-02-22/verification/L4P5_final_gate_decision.json` 当前为 `REQUIRES_CHANGES`。
- 只允许执行返工链：`T90/T91/T92 -> T93复审 -> T94复审`。
- `T95+` 全部冻结，待 `T94=PASS` 后再解冻。

### 转发给 Antigravity-1（只做 T90/T92 返工）

返工目标：
1. 将 `T90/T92` 证据中的占位符 `sha256` 改为真实值（不可留 `pending_verification`）。
2. 将 `T90/T92` 实施状态从 `DESIGNED` 修正为 `COMPLETED`。
3. 补齐执行证据（命令输出、回放一致性证据）。

输出：
- `docs/2026-02-22/verification/T90_execution_report.yaml`（覆盖更新）
- `docs/2026-02-22/verification/T92_execution_report.yaml`（覆盖更新）

完成后交接：
- 通知 `Antigravity-2` 进入 `T93` 复审。

### 转发给 vs--cc3（只做 T91 返工）

返工目标：
1. 将 `T91` 证据中的占位符 `sha256` 改为真实值（不可留 `computed_on_verification`）。
2. 保持 `T91` 的 `COMPLETED` 状态，补全可复核证据链。

输出：
- `docs/2026-02-22/verification/T91_execution_report.yaml`（覆盖更新）

完成后交接：
- 通知 `Antigravity-2` 进入 `T93` 复审。

### 转发给 Antigravity-2（只做 T93 复审）

前置：
- `T90/T91/T92` 返工报告已更新完毕。

复审目标：
1. 逐项核验 `sha256` 是否真实可复算。
2. 核验 `T90/T92` 状态是否已为 `COMPLETED` 且有执行证据。
3. 满足即将 `T93` 裁决为 `ALLOW`，否则保留 `REQUIRES_CHANGES` 并列明缺项。

输出：
- `docs/2026-02-22/verification/T93_gate_decision.json`（覆盖更新）

完成后交接：
- 若 `T93=ALLOW`，通知 `Kior-C` 执行 `T94` 复审。

### 转发给 Kior-C（只做 T94 复审）

前置：
- `T93=ALLOW`。

复审目标：
1. 按 B Guard 复核 `T90/T91/T92` 证据完整性与可验证性。
2. 满足即将 `T94` 裁决为 `PASS`，否则输出 `FAIL + required_changes`。

输出：
- `docs/2026-02-22/verification/T94_compliance_attestation.json`（覆盖更新）

完成后交接：
- 若 `T94=PASS`，解冻 Wave 2（`T95/T96/T97`）。

---

## 接力顺序总表（完成后下一位）

| 当前任务 | 当前负责人 | 完成条件 | 下一任务 | 下一负责人 |
|---|---|---|---|---|
| T90 | Antigravity-1 | `T90_execution_report.yaml` | T91 / T92（并行） | vs--cc3 / Antigravity-1 |
| T91 | vs--cc3 | `T91_execution_report.yaml` | T93（等待汇总） | Antigravity-2 |
| T92 | Antigravity-1 | `T92_execution_report.yaml` | T93（等待汇总） | Antigravity-2 |
| T93 | Antigravity-2 | `T93_gate_decision.json` 且 `decision=ALLOW` | T94 | Kior-C |
| T94 | Kior-C | `T94_compliance_attestation.json` 且 `decision=PASS` | T95 / T96 / T97（并行） | Antigravity-1 / vs--cc1 / Kior-A |
| T95 | Antigravity-1 | `T95_execution_report.yaml` | T98（等待汇总） | Antigravity-2 |
| T96 | vs--cc1 | `T96_execution_report.yaml` | T98（等待汇总） | Antigravity-2 |
| T97 | Kior-A | `T97_execution_report.yaml` | T98（等待汇总） | Antigravity-2 |
| T98 | Antigravity-2 | `T98_gate_decision.json` 且 `decision=ALLOW` | T99 | Kior-C |
| T99 | Kior-C | `T99_compliance_attestation.json` 且 `decision=PASS` | T100 | Antigravity-1 |
| T100 | Antigravity-1 | `T100_execution_report.yaml` | T101 | Codex |
| T101 | Codex | `L4P5_final_gate_decision.json` | 结束 | - |

接力硬规则：
1. 前序未达到 `ALLOW/PASS`，后序不得启动。
2. 并行段（`T91/T92` 与 `T95/T96/T97`）必须全部完成后才进入下一个汇总任务。
3. 任何任务只认文件证据，不认口头完成。

---

## 给 Antigravity-1（Execution：T90/T92/T95/T100）

你是 `L4P5-UPGRADE-20260222-001` 的 Execution 角色，负责 `T90/T92/T95/T100`。  
执行前置：必须先确认对应前置任务 `gate_decision=ALLOW` 且 `compliance=PASS`。

依据文件：
- `docs/2026-02-22/task_dispatch_l4_5_upgrade.md`
- `docs/2026-02-22/L4.5.MD`
- `multi-ai-collaboration.md`
- `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

任务目标：
1. `T90`：系统级 `skillforge` 一键全流程入口。
2. `T92`：证据链硬约束（`run_id/evidence_ref/input_hash/result_hash` + replay）。
3. `T95`：CI/CD 门禁自动化（PR/nightly fail-closed）。
4. `T100`：双窗口交互 + 执行拒绝权（Intent Not Buildable -> `DENY`）。

口径补充：
- 涉及调度/最终裁决能力时，统一按 `governance-orchestrator-skill` 主线执行；
- 若证据或旧文档出现 `trinity-dispatch-orchestrator-skill` 名称，视为兼容别名，不改变判定与交付口径。

执行输出（每任务各一份）：
- `docs/2026-02-22/verification/T90_execution_report.yaml`
- `docs/2026-02-22/verification/T92_execution_report.yaml`
- `docs/2026-02-22/verification/T95_execution_report.yaml`
- `docs/2026-02-22/verification/T100_execution_report.yaml`

报告必须包含：
- `PreflightChecklist`
- `ExecutionContract`
- `RequiredChanges`
- `gate_self_check`
- `evidence_refs`

硬约束：
1. 未通过合规不得执行。
2. 无 `EvidenceRef` 不得宣称完成。
3. 不得越权改动与任务无关文件。

完成后交接：
- `T90` 完成 -> 通知 `vs--cc3` 开 `T91`，同时你继续开 `T92`。
- `T95` 完成 -> 等待 `T96/T97`，随后由 `Antigravity-2` 开 `T98`。
- `T100` 完成 -> 交接 `Codex` 执行 `T101`。

---

## 给 vs--cc3（Execution：T91）

你是 `T91` 执行者，目标是完成 `policy_version` 与策略配置化。  
前置：`T90=ALLOW` 且合规 `PASS` 后执行。

依据文件：
- `docs/2026-02-22/task_dispatch_l4_5_upgrade.md`
- `docs/2026-02-22/L4.5.MD`
- `multi-ai-collaboration.md`

输出：
- `docs/2026-02-22/verification/T91_execution_report.yaml`

报告字段至少包含：
- `PreflightChecklist`
- `ExecutionContract`
- `RequiredChanges`
- `gate_self_check`
- `policy_version` 落地证据

完成后交接：
- `T91` 完成 -> 通知 `Antigravity-2`，等待 `T92` 一起进入 `T93`。

---

## 给 vs--cc1（Execution：T96）

你是 `T96` 执行者，目标是统一 `iterate / rollback_reset / rebase_reset` 语义，并落地一致性契约。  
前置：`T94=PASS`。

依据文件：
- `docs/2026-02-22/task_dispatch_l4_5_upgrade.md`
- `docs/2026-02-22/L4.5.MD`
- `multi-ai-collaboration.md`

输出：
- `docs/2026-02-22/verification/T96_execution_report.yaml`

报告必须说明：
1. 统一语义定义。
2. 兼容/不兼容边界。
3. fail-closed 策略。

完成后交接：
- `T96` 完成 -> 通知 `Antigravity-2`，等待 `T95/T97` 一起进入 `T98`。

---

## 给 Kior-A（Execution：T97）

你是 `T97` 执行者，目标是接入 Doc-to-Skill 管线（`ingest -> parse -> contract -> gate -> render`）。  
前置：`T94=PASS`。

依据文件：
- `docs/2026-02-22/task_dispatch_l4_5_upgrade.md`
- `docs/2026-02-22/L4.5.MD`
- `multi-ai-collaboration.md`

输出：
- `docs/2026-02-22/verification/T97_execution_report.yaml`

报告必须包含：
- 端到端链路证据
- 输入输出契约样例
- 失败样例与 `required_changes`

完成后交接：
- `T97` 完成 -> 通知 `Antigravity-2`，等待 `T95/T96` 一起进入 `T98`。

---

## 给 Antigravity-2（Review：T93/T98）

你是本批次 Review 角色，负责：
- `T93`：验收 `T90/T91/T92`
- `T98`：验收 `T95/T96/T97`

依据文件：
- `docs/2026-02-22/task_dispatch_l4_5_upgrade.md`
- `multi-ai-collaboration.md`
- `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`

输出：
- `docs/2026-02-22/verification/T93_gate_decision.json`
- `docs/2026-02-22/verification/T98_gate_decision.json`

每个结论必须包含：
- `decision` (`ALLOW | REQUIRES_CHANGES | DENY`)
- `reasons`
- `evidence_refs`
- `required_changes`（如有）

必查项：
1. 是否存在无证据宣称完成。
2. 是否满足任务依赖与波次顺序。
3. 是否保持 fail-closed。

完成后交接：
- `T93` 且 `ALLOW` -> 通知 `Kior-C` 执行 `T94`。
- `T98` 且 `ALLOW` -> 通知 `Kior-C` 执行 `T99`。

---

## 给 Kior-C（Compliance：T94/T99）

你是本批次 Compliance 角色，按 B Guard 做硬拦截。  
职责：
- `T94`：对 `T90-T93` 出具合规裁决
- `T99`：对 `T95-T98` 出具合规终审

依据文件：
- `docs/2026-02-22/task_dispatch_l4_5_upgrade.md`
- `multi-ai-collaboration.md`
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

输出：
- `docs/2026-02-22/verification/T94_compliance_attestation.json`
- `docs/2026-02-22/verification/T99_compliance_attestation.json`

硬规则：
1. 无 `EvidenceRef` => `FAIL`
2. 需要 permit 但无 `permit=VALID` => `FAIL`
3. 任一关键前置未满足 => `FAIL`

结论字段：
- `decision` (`PASS | FAIL`)
- `violations`
- `evidence_refs`
- `required_changes`（如有）
- `reviewed_at`

完成后交接：
- `T94` 且 `PASS` -> 通知 `Antigravity-1 / vs--cc1 / Kior-A` 并行执行 `T95/T96/T97`。
- `T99` 且 `PASS` -> 通知 `Antigravity-1` 执行 `T100`。

---

## 给 Codex（Final Gate：T101）

你是主控官，执行 `T101`：编排规模化压测收口 + Final Gate。  
前置：`T100` 完成且上游三权记录齐全。

口径补充：
- Final Gate 默认使用统一治理主线（`governance-orchestrator-skill` + `skillforge dispatch|gate`）；
- 允许读取历史别名证据（`trinity-dispatch-orchestrator-skill`），但最终结论以统一注册表口径为准。

汇总输入：
- `T90/T91/T92/T95/T96/T97/T100` 的 execution reports
- `T93/T98` gate decisions
- `T94/T99` compliance attestations

输出：
- `docs/2026-02-22/verification/L4P5_final_gate_decision.json`

裁决规则：
1. 缺任一三权记录 => `DENY`
2. 任一 `compliance != PASS` => `REQUIRES_CHANGES`
3. 全部满足且压测证据达标 => `ALLOW`

完成后收口：
- `T101` 产出后，同步写回 `task_dispatch_l4_5_upgrade.md` 状态列与最终结论。
