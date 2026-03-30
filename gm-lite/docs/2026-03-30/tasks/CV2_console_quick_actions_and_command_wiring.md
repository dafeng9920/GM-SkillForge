# CV2 Console Quick Actions And Command Wiring

你是任务 `CV2` 的执行者 Antigravity-1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 将高频动作接入 `GM-Lite Console`
- 减少对分散命令与 raw output 的依赖

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_conversational_worksurface_minimal_implementation/CV2_execution_report.md`

必须包含：
1. `task_id: CV2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. console quick actions / command wiring 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_conversational_worksurface_minimal_implementation/CV2_review_report.md`

---

你是任务 `CV2` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_conversational_worksurface_minimal_implementation/CV2_review_report.md`

必须包含：
1. `task_id: CV2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. console quick actions / command wiring 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_conversational_worksurface_minimal_implementation/CV2_compliance_attestation.md`

---

你是任务 `CV2` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_conversational_worksurface_minimal_implementation/CV2_compliance_attestation.md`

必须包含：
1. `task_id: CV2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
