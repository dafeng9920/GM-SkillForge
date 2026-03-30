# SC2 Automatic Writeback Followback Surface Return Patch

你是任务 `SC2` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 修复 `SR2` 暴露的工作面自动返回缺口
- 让 writeback / followback 不再依赖高摩擦手动跳转

必须写入：
- `gm-lite/docs/2026-03-29/verification/gm_lite_self_running_closure_patch/SC2_execution_report.md`

必须包含：
1. `task_id: SC2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. automatic writeback / followback surface return patch 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-29/verification/gm_lite_self_running_closure_patch/SC2_review_report.md`

---

你是任务 `SC2` 的审查者 `Kior-A`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-29/verification/gm_lite_self_running_closure_patch/SC2_review_report.md`

必须包含：
1. `task_id: SC2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. automatic writeback / followback surface return patch 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-29/verification/gm_lite_self_running_closure_patch/SC2_compliance_attestation.md`

---

你是任务 `SC2` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-29/verification/gm_lite_self_running_closure_patch/SC2_compliance_attestation.md`

必须包含：
1. `task_id: SC2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
