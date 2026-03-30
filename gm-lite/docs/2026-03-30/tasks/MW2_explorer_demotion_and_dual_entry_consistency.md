# MW2 Explorer Demotion And Dual Entry Consistency

你是任务 `MW2` 的执行者 Antigravity-1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 让 Explorer 中的 `Quick Start / Worksurface / Console` 降级为辅助入口
- 保证 Explorer 入口与主工作台入口行为一致，不造成双重歧义

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW2_execution_report.md`

必须包含：
1. `task_id: MW2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. explorer demotion / dual-entry consistency 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW2_review_report.md`

---

你是任务 `MW2` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW2_review_report.md`

必须包含：
1. `task_id: MW2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. explorer demotion / dual-entry consistency 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW2_compliance_attestation.md`

---

你是任务 `MW2` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_main_workbench_elevation_and_collaborative_console/MW2_compliance_attestation.md`

必须包含：
1. `task_id: MW2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
