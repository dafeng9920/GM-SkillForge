# GM LITE Sample Flow Validation v1 Scope

## 当前模块
- `gm_lite_sample_flow_validation_v1`

## 当前唯一目标
- 为 `GM-LITE` 运行一轮最小样板链验证，证明 `.gm_bus`、`BusManager`、controller console 与 dispatch assist 可以围绕标准任务包形成可回放、可审计、可判定的闭环。

## 本模块允许项
- 选择最小样板任务包
- 验证 `RAW -> ENRICHED -> FROZEN` 任务包链
- 验证 `next_hop / backfill / dispatch packet` 输出
- 验证 verification 三件套与 `GATE_READY`
- 验证 `lifecycle_status / gate_levels / validation_status` 的样板流
- 落最小 replay / README / validation notes

## 本模块禁止项
- 不实现新 watcher
- 不实现 auto-send
- 不实现 receipt / ack runtime
- 不实现 timeout / retry runtime
- 不实现跨插件 direct-connect
- 不扩展到完整 release judgment

## 本模块最小推进范围
- happy path 样板链
- 缺件 / backfill 样板链
- gate state / validation state 样板链
- replay / validation 说明

## 固定输出
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_SCOPE.md`
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_BOUNDARY_RULES.md`
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_TASK_BOARD.md`
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_ACCEPTANCE.md`
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_REPORT.md`
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现 watcher
- 开始实现 auto-send
- 开始实现 timeout / retry runtime
- 开始实现插件 direct-connect
- 开始扩展到 Light release judgment

## 本模块未触碰项
- qwen local gate integration
- architecture heartbeat
- light release judgment
