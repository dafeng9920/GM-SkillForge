# TC3_quick_actions_for_latest_send_and_read

你是任务 `TC3` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 给 outbox / writeback 增加“最新一条 / 快速发送 / 快速读取”短路径
- 保留确认机制，不把安全边界打穿

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC3_execution_report.md`

必须包含：
1. `task_id: TC3`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. quick actions 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC3_review_report.md`

---

你是任务 `TC3` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC3_review_report.md`

必须包含：
1. `task_id: TC3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. quick actions 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC3_compliance_attestation.md`

---

你是任务 `TC3` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_task_context_and_quick_actions_third_cut/TC3_compliance_attestation.md`

必须包含：
1. `task_id: TC3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`

