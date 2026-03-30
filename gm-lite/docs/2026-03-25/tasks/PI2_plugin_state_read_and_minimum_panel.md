# PI2 Plugin State Read And Minimum Panel

## Execution
你是任务 `PI2` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 实现插件壳对当前 `GM-LITE` 状态的读取
- 实现最小显示面或最小面板
- 不进入重型交互

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI2_execution_report.md`

必须包含：
1. `task_id: PI2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 状态读取与最小面板实现结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI2_review_report.md`

## Review
你是任务 `PI2` 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI2_review_report.md`

必须包含：
1. `task_id: PI2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 状态读取与最小面板审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI2_compliance_attestation.md`

## Compliance
你是任务 `PI2` 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI2_compliance_attestation.md`

必须包含：
1. `task_id: PI2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
