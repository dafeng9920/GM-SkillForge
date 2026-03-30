# GM LITE Dispatch Assist Preparation v1 Scope

## 当前模块
- `gm_lite_dispatch_assist_preparation_v1`

## 当前唯一目标
- 为 `GM-LITE` 定义 dispatch assist 的最小准备边界，使主控官后续能基于 `.gm_bus`、verification 写回件与 controller console 只做半自动派发、缺件追收、next hop 生成与 gate-ready 辅助，而不是继续做人肉中继器。

## 本模块允许项
- 定义 dispatch assist 的职责边界
- 定义 dispatch packet / next hop / backfill assist 的最小输入输出
- 定义与 `.gm_bus`、`controller console`、verification 路径的关系
- 定义主控官可触发的 assist 动作
- 定义缺件追收、标准路径回填、next hop 生成的准备口径
- 定义 Light 版禁止项与 change control

## 本模块禁止项
- 不实现自动发送
- 不实现 receipt / ack runtime
- 不实现 timeout / retry runtime
- 不实现跨插件 direct-connect
- 不实现完整 watcher
- 不实现真实 agent adapter
- 不实现完整 UI

## 本模块最小推进范围
- dispatch assist 职责定义
- assist 输入输出定义
- assist 动作与状态视图定义
- exclusions / change control 定义

## 固定输出
- `GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_SCOPE.md`
- `GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_BOUNDARY_RULES.md`
- `GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_TASK_BOARD.md`
- `GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_ACCEPTANCE.md`
- `GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_REPORT.md`
- `GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现自动发送
- 开始实现跨插件 direct-connect
- 开始实现 timeout / retry / receipt runtime
- 开始实现完整 watcher
- 开始实现重 UI

## 本模块未触碰项
- 自动发送
- 自动接单确认
- timeout / retry / escalation runtime
- 插件 direct-connect
- 云端长时运行
