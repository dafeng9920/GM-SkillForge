# SE2 Activity Bar Icon And View Container Definition

你是任务 `SE2` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 定义活动栏图标、view container、views 结构
- 明确最小图标入口如何挂接现有扩展
- 不进入真实代码实现

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE2_execution_report.md`

必须包含：
1. `task_id: SE2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. activity bar / view container 定义结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE2_review_report.md`

---

你是任务 `SE2` 的审查者 `vs--cc3`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE2_review_report.md`

必须包含：
1. `task_id: SE2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. activity bar / view container 定义审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE2_compliance_attestation.md`

---

你是任务 `SE2` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_sidebar_entry_preparation/SE2_compliance_attestation.md`

必须包含：
1. `task_id: SE2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
