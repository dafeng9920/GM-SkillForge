# HU3_machine_structure_demotion_and_debug_layer_split

你是任务 `HU3` 的执行者 `Kior-B`。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 将 `.gm_bus`、protocol、trace、raw state 等机器结构降到调试层
- 主工作面默认只保留人类可读结果
- 保持证据链与审计能力不丢失

必须写入：
- `gm-lite/docs/2026-03-31/verification/gm_lite_human_first_conversational_usability/HU3_execution_report.md`

必须包含：
1. `task_id: HU3`
2. `executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. machine structure demotion / debug split 结论
5. 最少 `EvidenceRef`

必须重点检查：
- raw `.gm_bus` / protocol / trace 是否不再占据主界面默认区域
- 调试信息是否仍可在 detail/debug 层打开
- 是否没有削弱审计追踪

写回成功后默认下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-31/verification/gm_lite_human_first_conversational_usability/HU3_review_report.md`
