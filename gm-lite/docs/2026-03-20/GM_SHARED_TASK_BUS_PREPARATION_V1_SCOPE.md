# GM Shared Task Bus Preparation v1 Scope

## 当前模块
- `gm_shared_task_bus_preparation_v1`

## 当前唯一目标
- 为 `GM-LITE` 建立共享任务总线 `.gm_bus` 的最小准备定义，明确目录结构、协议对象、权威状态层边界、禁止项、固定输出和验收标准。

## 本模块允许项
- 定义 `.gm_bus` 目录结构
- 定义 `TaskEnvelope / DispatchPacket / Receipt / Writeback / EscalationPack / StateLog` 的最小对象边界
- 定义 `manifest / task_board` 的投影关系
- 定义共享文件总线与后续 SQLite 状态层的边界
- 定义 Light 版当前不做什么
- 定义 AI 军团在本模块中的执行 / 审查 / 合规分工

## 本模块禁止项
- 不实现自动发送
- 不实现真实插件互调
- 不实现 timeout / retry runtime
- 不实现完整插件 UI
- 不直接迁移 `D:/NEW-GM` 历史代码
- 不引入外部服务、队列、Webhook
- 不把 `task board` 定义成权威状态写源

## 本模块最小推进范围
- 文档冻结
- 对象定义
- 总线目录定义
- 权威状态边界定义
- 任务板与投影关系定义

## 固定输出
- `GM_SHARED_TASK_BUS_PREPARATION_V1_SCOPE.md`
- `GM_SHARED_TASK_BUS_PREPARATION_V1_BOUNDARY_RULES.md`
- `GM_SHARED_TASK_BUS_PREPARATION_V1_TASK_BOARD.md`
- `GM_SHARED_TASK_BUS_PREPARATION_V1_ACCEPTANCE.md`
- `GM_SHARED_TASK_BUS_PREPARATION_V1_REPORT.md`
- `GM_SHARED_TASK_BUS_PREPARATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_SHARED_TASK_BUS_PREPARATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现 `.gm_bus` 运行时代码
- 开始实现 SQLite 状态层
- 开始实现自动发送 / 自动接单确认
- 开始设计插件直连 mesh
- 开始接入 `D:/NEW-GM` 旧代码而非抽取意图

## 本模块未触碰项
- `.gm_bus` 最小实现
- 共享状态层 SQLite
- plugin adapter
- 自动接力 runtime
- 超时 / 重试 / 升级执行器
