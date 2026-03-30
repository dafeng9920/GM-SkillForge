# SE1 Sidebar Entry Product Boundary

你是任务 `SE1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 定义 `GM-LITE` 侧边栏入口的产品边界
- 明确从命令面板入口到产品入口的切换口径
- 不进入实际 UI 实现

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE1_execution_report.md`

必须包含：
1. `task_id: SE1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. sidebar entry product boundary 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE1_review_report.md`

---

你是任务 `SE1` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE1_review_report.md`

必须包含：
1. `task_id: SE1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. sidebar entry product boundary 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE1_compliance_attestation.md`

---

你是任务 `SE1` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE1_compliance_attestation.md`

必须包含：
1. `task_id: SE1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
