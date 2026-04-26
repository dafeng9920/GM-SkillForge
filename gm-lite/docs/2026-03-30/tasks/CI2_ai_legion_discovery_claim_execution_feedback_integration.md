# CI2 AI Legion Discovery Claim Execution Feedback Integration

你是任务 `CI2` 的执行者 Antigravity-1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 将 AI 军团的发现、认领、执行、反馈集成成连续链，而不是零散证据点
- 让 inbox 中的任务不再依赖人工再发现和再推动

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_continuous_collaboration_chain_integration_fix/CI2_execution_report.md`

必须包含：
1. `task_id: CI2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. AI legion discovery / claim / execution / feedback integration 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_continuous_collaboration_chain_integration_fix/CI2_review_report.md`

---

你是任务 `CI2` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_continuous_collaboration_chain_integration_fix/CI2_review_report.md`

必须包含：
1. `task_id: CI2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. AI legion discovery / claim / execution / feedback integration 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_continuous_collaboration_chain_integration_fix/CI2_compliance_attestation.md`

---

你是任务 `CI2` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_continuous_collaboration_chain_integration_fix/CI2_compliance_attestation.md`

必须包含：
1. `task_id: CI2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
