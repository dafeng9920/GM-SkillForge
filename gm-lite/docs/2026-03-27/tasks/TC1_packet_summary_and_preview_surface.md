# TC1_packet_summary_and_preview_surface

你是任务 `TC1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 给 packet 增加最小 JSON 摘要 / 内容预览能力
- 让操作人不必先打开完整文件才能理解 packet 基本内容

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC1_execution_report.md`

必须包含：
1. `task_id: TC1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. packet summary / preview 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC1_review_report.md`

---

你是任务 `TC1` 的审查者 `vs--cc3`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC1_review_report.md`

必须包含：
1. `task_id: TC1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. packet summary / preview 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC1_compliance_attestation.md`

---

你是任务 `TC1` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC1_compliance_attestation.md`

必须包含：
1. `task_id: TC1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`

