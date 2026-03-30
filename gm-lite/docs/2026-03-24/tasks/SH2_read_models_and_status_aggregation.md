# 任务 SH2：Read Model / View Model / Status Aggregation

## Task Envelope
- `task_id`: `SH2`
- `module`: `gm_lite_shell_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `建立 read model / view model 与状态聚合`
- `parallel_group`: `wave_1`
- `depends_on`: `[]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-24/GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_EXECUTOR_INSPECTOR_ARBITER_ALLOCATION_V1.md`
- `acceptance_criteria`:
  - `状态聚合成立`
  - `可看到当前任务、卡点、下一步`
- `hard_constraints`:
  - `不进入重型 UI`
  - `不进入 auto-send`
  - `不跨库搜索`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 SH2 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 建立 read model / view model 与状态聚合
- 让 shell 能看到当前状态、卡点、下一步
- 不进入重型 UI / auto-send

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH2_execution_report.md`

必须包含：
1. `task_id: SH2`
2. `executor: Antigravity-2`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 状态聚合实现结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH2_review_report.md`

## 发给 Review 的提示词

你是任务 SH2 的审查者 vs--cc1。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH2_review_report.md`

必须包含：
1. `task_id: SH2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. read model / status aggregation 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH2_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 SH2 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH2_compliance_attestation.md`

必须包含：
1. `task_id: SH2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
