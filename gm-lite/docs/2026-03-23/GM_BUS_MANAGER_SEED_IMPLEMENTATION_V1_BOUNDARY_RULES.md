# GM BusManager Seed Implementation v1 Boundary Rules

## 1. 唯一边界

`BusManager` 在本轮只负责：

- 管理 `.gm_bus` 最小读写
- 承载任务记录与状态记录
- 承载意图原件、补完规格、审计元数据的字段骨架

它不负责：

- 自动派发
- 自动接单
- 自动重试
- 完整运行时调度
- 跨插件通信

## 2. 唯一事实源

本轮仍以：

- `.gm_bus`

作为唯一共享任务现实层。

不得并列引入：

- `.forge_sync`

## 3. 状态模型必须双层化

`BusManager` 必须采用：

- `lifecycle_status`
- `gate_levels`

不得将生命周期与火控门禁状态混进一个字段。

## 4. 元数据必须读写分离

至少逻辑分离：

- `intent_record`
- `runtime_record`
- `audit_record`

冻结对象与执行反馈不得共写。

## 5. 必须预埋的护栏

本轮至少要给以下对象留位：

- `intent_origin_hash`
- `raw_snapshot`
- `history_log`
- `status_history`
- `explicit_nouns`
- `purified_intent_payload`
- `vote_array`
- `intent_trace_id`
- `validation_status`

## 6. FROZEN 只读

一旦对象状态推进为：

- `validation_status = FROZEN`

则原任务包必须被视为只读。

执行反馈只能进入：

- `runtime_log`
- 或独立 runtime record

## 7. 本轮成功标准

只有在以下条件同时满足时，本轮 seed implementation 才算成立：

- `BusManager` 核心类存在
- `.gm_bus` 最小目录读写存在
- 双层状态模型存在
- metadata 护栏字段骨架存在
- 无越界进入 runtime / watcher / direct-connect
