# GM Shared Task Bus Frozen Judgment v1 Scope

## 当前模块
- `gm_shared_task_bus_frozen_judgment_v1`

## 当前唯一目标
- 基于已完成的 preparation / minimal implementation / minimal validation 结果，判断 `.gm_bus` 共享任务总线是否满足 Frozen 成立条件，并固化冻结范围、冻结依据、变更控制规则。

## 本模块允许项
- 核对 `.gm_bus` 最小目录骨架
- 核对协议对象最小定义
- 核对 `manifest / task_board / projector / validator` 边界
- 核对 verification 结果一致性
- 固化 Frozen 范围
- 固化 Frozen 后 change control
- 输出 Frozen 报告

## 本模块禁止项
- 不新增实现
- 不重写最小实现
- 不进入 SQLite 状态层
- 不进入 adapter
- 不进入自动互通 runtime
- 不进入插件 UI

## Frozen 成立条件
1. `.gm_bus` 最小目录骨架齐全
2. 六个协议对象最小定义齐全
3. `manifest / task_board` 边界清晰
4. `task_board` 未成为权威写源
5. `validator / projector` 雏形存在
6. 无 runtime 混入
7. 无 SQLite / adapter / 插件直连混入
8. verification 结果一致
9. Frozen 范围可列举
10. Frozen 后变更控制规则可执行

## 固定输出
- `GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_SCOPE.md`
- `GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_BOUNDARY_RULES.md`
- `GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_TASK_BOARD.md`
- `GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_ACCEPTANCE.md`
- `GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md`
- `GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_CHANGE_CONTROL_RULES.md`
- `GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_PROMPTS.md`

## 自动暂停条件
- 任何一方开始补实现
- 任何一方开始扩到 SQLite / adapter / runtime
- 任何一方开始修改 frozen 前提事实

## 本模块未触碰项
- SQLite 状态层
- 插件 adapter
- 自动互通 runtime
- timeout / retry runtime
- 插件 UI
