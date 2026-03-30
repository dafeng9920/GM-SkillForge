# 任务 SH1：Shell 统一入口与目录骨架

## Task Envelope
- `task_id`: `SH1`
- `module`: `gm_lite_shell_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `建立 shell 的统一入口与目录骨架`
- `parallel_group`: `wave_1`
- `depends_on`: `[]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-24/GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_REPORT.md`
- `acceptance_criteria`:
  - `统一入口存在`
  - `目录骨架清晰`
- `hard_constraints`:
  - `不进入重型 UI`
  - `不进入 auto-send`
  - `不跨库搜索`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 SH1 的执行者 Antigravity-1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 建立 shell 的统一入口与目录骨架
- 让系统不再只是散落代码，而有最小外壳入口
- 不进入重型 UI / auto-send

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH1_execution_report.md`

必须包含：
1. `task_id: SH1`
2. `executor: Antigravity-1`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. shell 统一入口与目录骨架实现结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH1_review_report.md`

## 发给 Review 的提示词

你是任务 SH1 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH1_review_report.md`

必须包含：
1. `task_id: SH1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. shell 入口与结构审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH1_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 SH1 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH1_compliance_attestation.md`

必须包含：
1. `task_id: SH1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
