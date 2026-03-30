# FT4 Field Notes Gaps And Release Direction

## Execution
你是任务 `FT4` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 汇总现场结论、缺口和下一步 release direction
- 不进入新实现

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_field_test_validation/FT4_execution_report.md`

必须包含：
1. `task_id: FT4`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. field notes / gaps / release direction 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_field_test_validation/FT4_review_report.md`

## Review
你是任务 `FT4` 的审查者 vs--cc1。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_field_test_validation/FT4_review_report.md`

必须包含：
1. `task_id: FT4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. field notes / gaps / release direction 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_field_test_validation/FT4_compliance_attestation.md`

## Compliance
你是任务 `FT4` 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_field_test_validation/FT4_compliance_attestation.md`

必须包含：
1. `task_id: FT4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
