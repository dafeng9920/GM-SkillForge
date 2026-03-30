# BI2_plugin_command_entry_and_bridge_trigger

你是任务 `BI2` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 在插件中补一个可见的 bridge trigger
- 让 operator 能从当前插件入口发起最小 bridge 动作

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_minimal_implementation/BI2_execution_report.md`

必须包含：
1. `task_id: BI2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. plugin command entry / bridge trigger 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_minimal_implementation/BI2_review_report.md`

---

你是任务 `BI2` 的审查者 `vs--cc3`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_minimal_implementation/BI2_review_report.md`

必须包含：
1. `task_id: BI2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. plugin command entry / bridge trigger 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_minimal_implementation/BI2_compliance_attestation.md`

---

你是任务 `BI2` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_minimal_implementation/BI2_compliance_attestation.md`

必须包含：
1. `task_id: BI2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`

