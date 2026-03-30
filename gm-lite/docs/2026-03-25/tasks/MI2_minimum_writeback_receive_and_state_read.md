# MI2 Minimum Writeback Receive And State Read

## Execution
你是任务 `MI2` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 实现最小 writeback receive
- 实现最小状态回读
- 不进入完整自动回收系统

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_minimal_implementation/MI2_execution_report.md`

必须包含：
1. `task_id: MI2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. writeback receive / state read 实现结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_minimal_implementation/MI2_review_report.md`

## Review
你是任务 `MI2` 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_minimal_implementation/MI2_review_report.md`

必须包含：
1. `task_id: MI2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. writeback receive / state read 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_minimal_implementation/MI2_compliance_attestation.md`

## Compliance
你是任务 `MI2` 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_minimal_implementation/MI2_compliance_attestation.md`

必须包含：
1. `task_id: MI2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
