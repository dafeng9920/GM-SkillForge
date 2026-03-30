# EB4_examples_notes_and_skillforge_handoff_boundary

你是任务 `EB4` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 明确 example 包、边界说明
- 冻结 SkillForge 只消费标准化对象的 handoff 原则

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_and_contract_preparation/EB4_execution_report.md`

必须包含：
1. `task_id: EB4`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. examples / notes / SkillForge handoff boundary 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_and_contract_preparation/EB4_review_report.md`

---

你是任务 `EB4` 的审查者 `Kior-A`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_and_contract_preparation/EB4_review_report.md`

必须包含：
1. `task_id: EB4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. examples / notes / SkillForge handoff boundary 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_and_contract_preparation/EB4_compliance_attestation.md`

---

你是任务 `EB4` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-27/verification/gm_lite_execution_bridge_and_contract_preparation/EB4_compliance_attestation.md`

必须包含：
1. `task_id: EB4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`

