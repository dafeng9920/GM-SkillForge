# GM BusManager Seed Implementation v1 Scope

## 当前模块
- `gm_bus_manager_seed_implementation_v1`

## 当前唯一目标
- 为 `GM-LITE` 落下 Python 端 `.gm_bus` 核心种子实现，使后续 `dispatch assist`、`reverse echo`、`sample flow validation` 有一个最小可用的总线读写与元数据承载底座。

## 本模块允许项
- 落 `BusManager` 最小核心类
- 落总线对象最小模型
- 落 `.gm_bus` 目录读写约定
- 落 `lifecycle_status + gate_levels` 双层状态模型
- 预埋 reverse echo 所需元数据槽位
- 预埋 metadata origin / entry firewalls / history / noun anchors 的字段骨架
- 落最小 README / sample payload / usage 说明

## 本模块禁止项
- 不实现 watcher
- 不实现 auto-send
- 不实现 direct-connect
- 不实现 timeout / retry / receipt runtime
- 不实现完整插件 UI
- 不实现完整 SpecKit toolchain
- 不实现完整 Qwen 集成

## 本模块最小推进范围
- `BusManager` 核心类
- 总线记录最小 schema
- 目录骨架与样板对象
- 状态模型
- 元数据护栏字段骨架

## 固定输出
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_SCOPE.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_TASK_BOARD.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_ACCEPTANCE.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_REPORT.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现 watcher
- 开始实现 auto-send
- 开始实现 direct-connect
- 开始实现 timeout / retry runtime
- 开始实现完整插件 UI
- 开始实现完整 78B Qwen 接入

## 本模块未触碰项
- dispatch assist minimal implementation
- sample flow validation
- light release judgment
- qwen local gate integration
