# HU1_dialog_first_start_and_dispatch_entry

你是任务 `HU1` 的执行者 `Antigravity-1`。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 将 `GM-Lite Console` 推进为对话优先的启动/派发入口
- 让用户通过自然输入直接触发启动/继续/派发，而不是先理解动作按钮体系
- 保持与现有 `.gm_bus` 中转链兼容

必须写入：
- `gm-lite/docs/2026-03-31/verification/gm_lite_human_first_conversational_usability/HU1_execution_report.md`

必须包含：
1. `task_id: HU1`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. dialog-first start / dispatch entry 结论
5. 最少 `EvidenceRef`

必须重点检查：
- Console 输入是否可直接触发启动/继续/派发
- 是否减少“先点按钮再补动作”的流程
- 是否没有破坏现有 `.gm_bus` 路径与 quick actions

写回成功后默认下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-31/verification/gm_lite_human_first_conversational_usability/HU1_review_report.md`
