# GM LITE Dispatch Assist Minimal Implementation v1 Change Control Rules

## 允许变更
- 可细化 assist 函数名与对象名
- 可细化 packet 字段
- 可细化 sample flow 与 README
- 可细化与 BusManager 的最小接口

## 禁止变更
- 不得引入 auto-send
- 不得引入 receipt / ack runtime
- 不得引入 timeout / retry runtime
- 不得引入 direct-connect
- 不得把 sample flow validation 提前并入本轮

## 升级条件
- assist 与 BusManager 接口冲突
- verification 路径权威冲突
- 尝试把 assist 写成完整运行时系统
