# GM Shared Task Bus Minimal Validation v1 Scope

## 当前模块
- `gm_shared_task_bus_minimal_validation_v1`

## 当前唯一目标
- 对 `.gm_bus` 的最小实现进行结构级、协议级、样板链路级验证，确认其已具备作为 `GM-LITE` 共享任务现实层的最小可用性。

## 本模块允许项
- 验证 `.gm_bus` 目录结构是否与实现文档一致
- 验证 `TaskEnvelope / DispatchPacket / Receipt / Writeback / EscalationPack / StateLog` 的最小对象是否齐备
- 验证 `manifest / task_board` 权威/投影边界未混淆
- 验证最小 `validator / projector` 雏形是否能支撑样板链路
- 验证 `chat-output-to-bus bridge` 当前边界是否被正确保留为未实现项
- 输出阻断性 / 非阻断性问题清单

## 本模块禁止项
- 不修改架构目标
- 不新增 runtime
- 不新增插件直连
- 不新增 SQLite 状态层
- 不直接补做 Light 控制台
- 不借验证名义重写整个最小实现

## 本模块最小推进范围
- 结构核对
- 协议核对
- 样板链路核对
- 边界与合规核对

## 固定输出
- `GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_SCOPE.md`
- `GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_BOUNDARY_RULES.md`
- `GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_TASK_BOARD.md`
- `GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_ACCEPTANCE.md`
- `GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_REPORT.md`
- `GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始补自动发送
- 开始补 receipt runtime
- 开始补 timeout / retry
- 开始补插件 adapter
- 开始把 `task_board` 改成权威状态源

## 本模块未触碰项
- SQLite 状态层
- 插件 adapter
- 自动互通 runtime
- timeout / retry runtime
- 插件 UI
