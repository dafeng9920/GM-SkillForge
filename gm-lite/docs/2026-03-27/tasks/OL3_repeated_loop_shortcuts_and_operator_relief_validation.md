# OL3_repeated_loop_shortcuts_and_operator_relief_validation

你是任务 `OL3` 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 验证重复使用循环是否比之前更轻
- 给出实际减负证据，而不是主观描述

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_operator_load_reduction_minimal_implementation/OL3_execution_report.md`

必须包含：
1. `task_id: OL3`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. repeated loop shortcuts / operator relief 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_operator_load_reduction_minimal_implementation/OL3_review_report.md`

---

你是任务 `OL3` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_operator_load_reduction_minimal_implementation/OL3_review_report.md`

必须包含：
1. `task_id: OL3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. repeated loop shortcuts / operator relief 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_operator_load_reduction_minimal_implementation/OL3_compliance_attestation.md`

---

你是任务 `OL3` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_operator_load_reduction_minimal_implementation/OL3_compliance_attestation.md`

必须包含：
1. `task_id: OL3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`

