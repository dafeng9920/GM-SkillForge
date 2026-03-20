# GM LITE Controller Console Minimal Implementation v1 Scope

## 当前模块
- `gm_lite_controller_console_minimal_implementation_v1`

## 当前唯一目标
- 为 `GM-LITE` 落下主控官控制台的最小可用骨架，使主控官能够基于 `.gm_bus` 与 verification 结果查看状态、缺件、next hop、gate ready 与阻断项。

## 本模块允许项
- 落控制台最小目录骨架
- 落控制台只读 read model / view model 骨架
- 落最小状态视图对象
- 落最小告警 / gate-ready 视图对象
- 落最小 README / usage 说明
- 落最小样板输入输出

## 本模块禁止项
- 不实现完整插件 UI
- 不实现自动 watcher
- 不实现 dispatch runtime
- 不实现 adapter
- 不实现自动发送
- 不实现权限系统

## 本模块最小推进范围
- 控制台骨架
- 只读视图对象
- 样板状态输入输出
- 主控动作占位定义

## 固定输出
- `GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_TASK_BOARD.md`
- `GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_ACCEPTANCE.md`
- `GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现 UI/面板
- 开始实现自动刷新 watcher
- 开始实现 adapter
- 开始实现 dispatch / relay runtime
- 开始引入外部服务

## 本模块未触碰项
- 完整插件 UI
- 自动 watcher
- dispatch assist runtime
- adapter
- timeout / retry / receipt runtime
