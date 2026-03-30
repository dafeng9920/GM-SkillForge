# SI1 Writeback Identity Propagation Patch

你是任务 `SI1` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 修复 `SR2` 暴露的 writeback 身份标识链断裂
- 让 `intent_trace_id` 从 writeback JSON 一路传到 summary 和 receive operator

必须写入：
- `gm-lite/docs/2026-03-29/verification/gm_lite_surface_return_identity_patch/SI1_execution_report.md`

必须包含：
1. `task_id: SI1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. writeback identity propagation patch 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-29/verification/gm_lite_surface_return_identity_patch/SI1_review_report.md`

---

你是任务 `SI1` 的审查者 `Kior-A`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-29/verification/gm_lite_surface_return_identity_patch/SI1_review_report.md`

必须包含：
1. `task_id: SI1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. writeback identity propagation patch 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-29/verification/gm_lite_surface_return_identity_patch/SI1_compliance_attestation.md`

---

你是任务 `SI1` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-29/verification/gm_lite_surface_return_identity_patch/SI1_compliance_attestation.md`

必须包含：
1. `task_id: SI1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
