# WS4 Validation Remaining Gaps And Next-Cut Direction

你是任务 `WS4` 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 汇总 `gm_lite_plugin_real_usable_worksurface_v1` 结果
- 判断插件是否已经开始承担真实日常工作面角色
- 识别剩余高频体力劳动缺口

必须写入：
- `gm-lite/docs/2026-03-28/verification/gm_lite_plugin_real_usable_worksurface/WS4_execution_report.md`

必须包含：
1. `task_id: WS4`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. validation / remaining gaps / next-cut direction 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-28/verification/gm_lite_plugin_real_usable_worksurface/WS4_review_report.md`

---

你是任务 `WS4` 的审查者 `vs--cc1`。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-28/verification/gm_lite_plugin_real_usable_worksurface/WS4_review_report.md`

必须包含：
1. `task_id: WS4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. validation / remaining gaps / next-cut direction 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-28/verification/gm_lite_plugin_real_usable_worksurface/WS4_compliance_attestation.md`

---

你是任务 `WS4` 的合规官 `Kior-C`。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-28/verification/gm_lite_plugin_real_usable_worksurface/WS4_compliance_attestation.md`

必须包含：
1. `task_id: WS4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
