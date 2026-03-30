# 任务 SH3：最小操作面与 Runtime Hooks

## Task Envelope
- `task_id`: `SH3`
- `module`: `gm_lite_shell_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `建立最小操作面与 blueprint/bus/dispatch 挂点`
- `parallel_group`: `wave_2`
- `depends_on`: `["SH1", "SH2"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-24/GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_BLUEPRINT_GATE_COEVOLUTION_MODEL_V1.md`
- `acceptance_criteria`:
  - `最小操作面成立`
  - `blueprint / bus / dispatch hooks 成立`
- `hard_constraints`:
  - `不进入 auto-send`
  - `不进入 direct-connect`
  - `不跨库搜索`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 SH3 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 建立最小操作面
- 建立 blueprint / bus / dispatch 挂点
- 让“手动转递”至少被收缩成明确动作，而不是散落在文档里
- 不进入 auto-send / direct-connect

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH3_execution_report.md`

必须包含：
1. `task_id: SH3`
2. `executor: Kior-B`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 最小操作面实现结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH3_review_report.md`

## 发给 Review 的提示词

你是任务 SH3 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH3_review_report.md`

必须包含：
1. `task_id: SH3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. action surface / hooks 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH3_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 SH3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_shell_seed_implementation/SH3_compliance_attestation.md`

必须包含：
1. `task_id: SH3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
