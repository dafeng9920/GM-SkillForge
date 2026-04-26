# OR3 Real Operator Relief Validation In Project Loop

你是任务 `OR3` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 在真实项目循环中验证是否出现更强连续协作、更少人工调度、更明显 operator relief
- 判断插件是否开始稳定承担实际工作

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_real_operator_relief_and_continuous_collaboration/OR3_execution_report.md`

必须包含：
1. `task_id: OR3`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. real operator relief validation 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_real_operator_relief_and_continuous_collaboration/OR3_review_report.md`

---

你是任务 `OR3` 的审查者 `Kior-A`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_real_operator_relief_and_continuous_collaboration/OR3_review_report.md`

必须包含：
1. `task_id: OR3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. real operator relief validation 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-30/verification/gm_lite_real_operator_relief_and_continuous_collaboration/OR3_compliance_attestation.md`

---

你是任务 `OR3` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-30/verification/gm_lite_real_operator_relief_and_continuous_collaboration/OR3_compliance_attestation.md`

必须包含：
1. `task_id: OR3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
