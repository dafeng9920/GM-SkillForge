# LH1 Installed State Persistent Entry And Sidebar Stability

你是任务 `LH1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 补强安装态下活动栏入口与 sidebar 的持续稳定性
- 让重复进入时入口仍可见、可点、可打开

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_usability_and_stability_hardening/LH1_execution_report.md`

必须包含：
1. `task_id: LH1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. persistent entry / sidebar stability 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_usability_and_stability_hardening/LH1_review_report.md`

---

你是任务 `LH1` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_usability_and_stability_hardening/LH1_review_report.md`

必须包含：
1. `task_id: LH1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. persistent entry / sidebar stability 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_usability_and_stability_hardening/LH1_compliance_attestation.md`

---

你是任务 `LH1` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_plugin_local_usability_and_stability_hardening/LH1_compliance_attestation.md`

必须包含：
1. `task_id: LH1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
