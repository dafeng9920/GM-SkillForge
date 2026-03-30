# PI1 Plugin Scaffold And Host Entry

## Execution
你是任务 `PI1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 实现第一版 `GM-LITE` 插件壳骨架
- 明确 VS Code 扩展入口与基本结构
- 不进入复杂 UI 和自动桥接

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI1_execution_report.md`

必须包含：
1. `task_id: PI1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 插件骨架与宿主入口实现结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI1_review_report.md`

## Review
你是任务 `PI1` 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI1_review_report.md`

必须包含：
1. `task_id: PI1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 插件骨架与宿主入口审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI1_compliance_attestation.md`

## Compliance
你是任务 `PI1` 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_plugin_shell_seed_implementation/PI1_compliance_attestation.md`

必须包含：
1. `task_id: PI1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
