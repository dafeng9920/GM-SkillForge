# MW4 Validation Remaining Gaps And Main Workbench Judgment

你是任务 `MW4` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 汇总 main workbench elevation 与 collaborative console 结果
- 判断 `GM-Lite` 是否已经脱离“Explorer 里的一堆视图”，成为真正主工作台
- 识别剩余缺口和下一刀方向

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW4_execution_report.md`

必须包含：
1. `task_id: MW4`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. validation / remaining gaps / main workbench judgment 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW4_review_report.md`

---

你是任务 `MW4` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW4_review_report.md`

必须包含：
1. `task_id: MW4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. validation / remaining gaps / main workbench judgment 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW4_compliance_attestation.md`

---

你是任务 `MW4` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW4_compliance_attestation.md`

必须包含：
1. `task_id: MW4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
