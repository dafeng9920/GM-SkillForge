# MT2 First Cut Send Receive Hook Definition

## Execution
你是任务 `MT2` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 冻结手动转递消失第一刀的切点
- 冻结插件壳中的 send / receive hook 位置
- 不进入完整桥接实现

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_preparation/MT2_execution_report.md`

必须包含：
1. `task_id: MT2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 第一刀切点与 hook 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_preparation/MT2_review_report.md`

## Review
你是任务 `MT2` 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_preparation/MT2_review_report.md`

必须包含：
1. `task_id: MT2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 第一刀切点与 hook 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_preparation/MT2_compliance_attestation.md`

## Compliance
你是任务 `MT2` 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-25/verification/gm_lite_manual_transfer_elimination_preparation/MT2_compliance_attestation.md`

必须包含：
1. `task_id: MT2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
