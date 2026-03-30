# GM BusManager Seed Implementation v1 Acceptance

## 通过标准

### A. 核心类
- 存在最小 `BusManager` 类
- 已定义基础读写方法
- 已定义 authority path / bus root 约定

### B. 对象模型
- 已定义 bus record 最小模型
- 已定义 `lifecycle_status`
- 已定义 `gate_levels`

### C. 元数据护栏
- 已预埋 reverse echo 槽位
- 已预埋 raw/history/noun/trace/validation 字段
- 已定义 FROZEN 只读口径

### D. 样板与说明
- 已提供 sample payload
- 已提供 `.gm_bus` 使用说明
- 已冻结 exclusions / change control

## 不通过条件
- 缺少 `BusManager` 类
- 状态模型仍混成单字段
- 缺少元数据护栏槽位
- 越界进入 watcher / auto-send / direct-connect
