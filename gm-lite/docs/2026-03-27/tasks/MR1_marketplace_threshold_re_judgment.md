# MR1 Marketplace Threshold Re Judgment

你是任务 `MR1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 基于 `MH1-MH4` 结果，重审当前插件是否已达到 marketplace judgment threshold
- 不进入真正发布动作

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_marketplace_re_judgment/MR1_execution_report.md`

必须包含：
1. `task_id: MR1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. marketplace threshold re-judgment 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_marketplace_re_judgment/MR1_review_report.md`

---

你是任务 `MR1` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_marketplace_re_judgment/MR1_review_report.md`

必须包含：
1. `task_id: MR1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. marketplace threshold re-judgment 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_marketplace_re_judgment/MR1_compliance_attestation.md`

---

你是任务 `MR1` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_plugin_marketplace_re_judgment/MR1_compliance_attestation.md`

必须包含：
1. `task_id: MR1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
