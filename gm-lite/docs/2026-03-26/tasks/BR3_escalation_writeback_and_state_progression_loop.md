# BR3 Escalation Writeback And State Progression Loop

你是任务 `BR3` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 把 escalation、writeback、state progression 串成最小闭环
- 确保 blockage / recovery 不只是局部脚本，而是能推进总线状态
- 保持 tri-split 不塌

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_blockage_recovery_runtime_minimal_implementation/BR3_execution_report.md`

必须包含：
1. `task_id: BR3`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. escalation / writeback / state progression 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_blockage_recovery_runtime_minimal_implementation/BR3_review_report.md`

---

你是任务 `BR3` 的审查者 `vs--cc3`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_blockage_recovery_runtime_minimal_implementation/BR3_review_report.md`

必须包含：
1. `task_id: BR3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. escalation / writeback / state progression 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-26/verification/gm_lite_blockage_recovery_runtime_minimal_implementation/BR3_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

---

你是任务 `BR3` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-26/verification/gm_lite_blockage_recovery_runtime_minimal_implementation/BR3_compliance_attestation.md`

必须包含：
1. `task_id: BR3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
