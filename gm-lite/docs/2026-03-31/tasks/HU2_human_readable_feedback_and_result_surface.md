# HU2_human_readable_feedback_and_result_surface

你是任务 `HU2` 的执行者 `Antigravity-2`。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 把 Console 默认反馈改成面向人的执行反馈
- 默认告诉用户：正在做什么、做完了什么、卡在哪、下一步是什么
- 输出/文件去向可见，但默认不抛 raw machine structure

必须写入：
- `gm-lite/docs/2026-03-31/verification/gm_lite_human_first_conversational_usability/HU2_execution_report.md`

必须包含：
1. `task_id: HU2`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. human-readable feedback / result surface 结论
5. 最少 `EvidenceRef`

必须重点检查：
- 默认英文技术提示是否已降级
- 默认反馈是否改成人类可读文本
- 文件/结果/下一步是否清楚可见

写回成功后默认下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-31/verification/gm_lite_human_first_conversational_usability/HU2_review_report.md`
