# GM LITE Controller Console Preparation v1 Scope

## 当前模块
- `gm_lite_controller_console_preparation_v1`

## 当前唯一目标
- 为 `GM-LITE` 建立主控官控制台的最小准备定义，明确控制台职责、只读/可控边界、输入输出对象、与 `.gm_bus` 的承接关系，以及当前 Light 版不做什么。

## 本模块允许项
- 定义 controller console 的职责边界
- 定义 controller console 与 `.gm_bus` 的读取关系
- 定义 controller console 与 task board / verification / bridge 的关系
- 定义主控官在控制台中需要看到的最小视图
- 定义最小交互动作边界
- 定义 Light 版控制台禁止项与 change control

## 本模块禁止项
- 不实现 UI
- 不实现插件面板
- 不实现自动刷新 watcher
- 不实现自动发送
- 不实现跨插件 adapter
- 不实现权限/登录系统

## 本模块最小推进范围
- 视图定义
- 输入输出定义
- 交互动作边界
- 与 `.gm_bus`、verification、task board 的承接关系

## 固定输出
- `GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_SCOPE.md`
- `GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_BOUNDARY_RULES.md`
- `GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_TASK_BOARD.md`
- `GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_ACCEPTANCE.md`
- `GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_REPORT.md`
- `GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现 UI / 面板
- 开始实现自动刷新或文件监听
- 开始实现 dispatch runtime
- 开始实现插件直连
- 开始把控制台写成权威状态层

## 本模块未触碰项
- controller console 最小实现
- 插件 UI
- 自动 watcher
- dispatch assist 运行时
- adapter
