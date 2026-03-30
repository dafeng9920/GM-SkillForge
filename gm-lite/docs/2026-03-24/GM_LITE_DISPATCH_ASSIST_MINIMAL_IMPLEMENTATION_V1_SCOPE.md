# GM LITE Dispatch Assist Minimal Implementation v1 Scope

## 当前模块
- `gm_lite_dispatch_assist_minimal_implementation_v1`

## 当前唯一目标
- 为 `GM-LITE` 落下 dispatch assist 的最小可用实现，使主控官能够基于 `BusManager`、`.gm_bus` 与 verification 写回件，完成 next hop 计算、缺件识别、backfill 提示生成与 dispatch packet 组装，而不再依赖零散手工拼装。

## 本模块允许项
- 落 dispatch assist 核心目录骨架
- 实现 next hop assist 最小逻辑
- 实现 missing piece / backfill assist 最小逻辑
- 实现 dispatch packet build assist 最小逻辑
- 实现与 `BusManager` / `.gm_bus` / verification 的最小对接
- 落最小 sample input / output / README

## 本模块禁止项
- 不实现 auto-send
- 不实现 receipt / ack runtime
- 不实现 timeout / retry runtime
- 不实现跨插件 direct-connect
- 不实现 watcher
- 不实现完整 UI

## 本模块最小推进范围
- assist 核心逻辑
- assist 输入输出
- 与 BusManager 的最小对接
- 样板输入输出
- README / usage

## 固定输出
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_TASK_BOARD.md`
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_ACCEPTANCE.md`
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现 auto-send
- 开始实现 receipt / ack runtime
- 开始实现 timeout / retry runtime
- 开始实现 direct-connect
- 开始实现 watcher

## 本模块未触碰项
- sample flow validation
- light release judgment
- qwen local gate integration
