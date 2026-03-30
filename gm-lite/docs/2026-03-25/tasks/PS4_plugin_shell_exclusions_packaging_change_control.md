# PS4 Plugin Shell Exclusions Packaging Change Control

## Execution
你是任务 `PS4` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 定义当前插件壳准备阶段的 exclusions
- 定义 packaging 边界
- 定义 change control
- 不进入市场发布实现

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_preparation/PS4_execution_report.md`

必须包含：
1. `task_id: PS4`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. exclusions / packaging / change control 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_preparation/PS4_review_report.md`

## Review
你是任务 `PS4` 的审查者 vs--cc1。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_preparation/PS4_review_report.md`

必须包含：
1. `task_id: PS4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. exclusions / packaging / change control 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_preparation/PS4_compliance_attestation.md`

## Compliance
你是任务 `PS4` 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_preparation/PS4_compliance_attestation.md`

必须包含：
1. `task_id: PS4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
