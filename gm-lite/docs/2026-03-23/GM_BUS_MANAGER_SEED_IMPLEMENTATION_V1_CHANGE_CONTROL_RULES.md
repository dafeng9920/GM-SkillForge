# GM BusManager Seed Implementation v1 Change Control Rules

## 允许变更
- 可以细化 `BusManager` 核心方法名
- 可以细化对象字段名
- 可以细化 `.gm_bus` 目录骨架
- 可以细化 sample payload / README

## 禁止变更
- 不得引入 watcher
- 不得引入 auto-send
- 不得引入 direct-connect
- 不得引入完整 timeout / retry / receipt runtime
- 不得把 Qwen 集成插进本轮
- 不得改写 `.gm_bus` frozen 主线定义

## 升级条件
- 出现状态模型冲突
- 出现 authority path 冲突
- 出现 `.gm_bus` vs 其他总线命名分裂
- 出现将 seed implementation 膨胀为完整 runtime 的行为
