# GM Shared Task Bus Minimal Implementation v1 Scope

## 当前模块
- `gm_shared_task_bus_minimal_implementation_v1`

## 当前唯一目标
- 为 `GM-LITE` 落下 `.gm_bus` 的最小可用共享任务现实骨架，形成可被后续控制台、dispatch assist、样板链路复用的第一版实现。

## 本模块允许项
- 创建 `.gm_bus/` 最小目录结构
- 创建 `manifest / outbox / inbox / writeback / escalation / archive` 的最小文件骨架
- 创建 `TaskEnvelope / DispatchPacket / Receipt / Writeback / EscalationPack / StateLog` 的最小 schema / example / stub
- 创建最小 `validator / projector` 雏形
- 创建最小 README / usage 说明
- 创建实现级三权任务卡、任务板、回收路径

## 本模块禁止项
- 不实现真实插件直连
- 不实现网络消息总线
- 不实现 timeout / retry runtime
- 不实现自动发送
- 不实现 SQLite 状态层
- 不实现完整插件 UI
- 不复制 `D:/NEW-GM` 历史代码

## 本模块最小推进范围
- 文件系统级 `.gm_bus` 骨架
- 协议对象最小实现
- 投影视图 / 校验器雏形
- 只读 README 与示例链路

## 固定输出
- `GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_TASK_BOARD.md`
- `GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_ACCEPTANCE.md`
- `GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现插件间直连 mesh
- 开始实现自动接单确认 runtime
- 开始实现 timeout / retry / lease 运行时
- 开始引入外部队列 / webhook / 服务端
- 开始把 `task_board` 写成权威状态源

## 本模块未触碰项
- SQLite 权威状态层
- 插件 adapter
- 自动互通 runtime
- 云端 OpenClaw 持续执行
- 重型版中控 UI
