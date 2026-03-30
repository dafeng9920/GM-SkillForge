# RJ1 Local Use Release Criteria And Threshold Judgment

你是任务 `RJ1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 判断当前插件是否达到“仅自己本地长期使用”的最低 release 条件
- 输出 criteria / threshold judgment
- 不进入插件市场判断

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_release_judgment/RJ1_execution_report.md`

必须包含：
1. `task_id: RJ1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. local-use release criteria / threshold judgment 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_release_judgment/RJ1_review_report.md`

---

你是任务 `RJ1` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_release_judgment/RJ1_review_report.md`

必须包含：
1. `task_id: RJ1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. local-use release criteria / threshold judgment 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_release_judgment/RJ1_compliance_attestation.md`

---

你是任务 `RJ1` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_release_judgment/RJ1_compliance_attestation.md`

必须包含：
1. `task_id: RJ1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
