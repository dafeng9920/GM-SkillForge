# TP2_writeback_navigation_precondition_validation

你是任务 `TP2` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 验证 writeback 导航前置条件是否成立
- 明确缺 writeback 时的处理是否清楚、可见、不可伪造

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_navigation_precondition_patch/TP2_execution_report.md`

必须包含：
1. `task_id: TP2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. writeback navigation precondition validation 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_navigation_precondition_patch/TP2_review_report.md`

---

你是任务 `TP2` 的审查者 `vs--cc3`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_navigation_precondition_patch/TP2_review_report.md`

必须包含：
1. `task_id: TP2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. writeback navigation precondition validation 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_navigation_precondition_patch/TP2_compliance_attestation.md`

---

你是任务 `TP2` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_navigation_precondition_patch/TP2_compliance_attestation.md`

必须包含：
1. `task_id: TP2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`

