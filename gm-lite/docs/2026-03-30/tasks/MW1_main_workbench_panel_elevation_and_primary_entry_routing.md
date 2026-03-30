# MW1 Main Workbench Panel Elevation And Primary Entry Routing

你是任务 `MW1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 将 `GM-Lite Console` 从 Explorer 侧栏视图提升为独立主工作台面板
- 让默认入口和快捷键首先进入主工作台，而不是 Explorer 内嵌视图

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW1_execution_report.md`

必须包含：
1. `task_id: MW1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. main workbench elevation / primary entry routing 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW1_review_report.md`

---

你是任务 `MW1` 的审查者 `Kior-A`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW1_review_report.md`

必须包含：
1. `task_id: MW1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. main workbench elevation / primary entry routing 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW1_compliance_attestation.md`

---

你是任务 `MW1` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW1_compliance_attestation.md`

必须包含：
1. `task_id: MW1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
