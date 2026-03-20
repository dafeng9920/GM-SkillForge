# Task Dispatcher Protocol Preparation v1 Scope

## 当前模块
- task_dispatcher_protocol preparation v1

## 当前唯一目标
- 为 AI 军团的任务投递、状态流转、标准写回、自动接力、主控升级建立最小协议准备定义。

## 本模块允许项
- 定义 task envelope 最小字段
- 定义 state machine 最小状态集
- 定义 writeback contract
- 定义 auto-relay 规则
- 定义 escalation protocol
- 定义与主控官 skill 的承接关系
- 定义固定输出与 change control 规则

## 本模块禁止项
- 不实现 dispatcher 代码
- 不实现自动监听程序
- 不接入数据库、消息队列、Webhook
- 不回改既有 frozen 主线
- 不改写既有模块结论
- 不把 dispatcher 写成新的裁决层

## 本模块最小推进范围
- 协议定义
- 状态定义
- 写回定义
- 升级定义
- 边界与禁止项

## 固定输出
- `TASK_DISPATCHER_PROTOCOL_PREPARATION_V1_SCOPE.md`
- `TASK_DISPATCHER_PROTOCOL_PREPARATION_V1_BOUNDARY_RULES.md`
- `TASK_DISPATCHER_PROTOCOL_PREPARATION_V1_REPORT.md`

## 自动暂停条件
- 开始实现 runtime
- 开始实现真实自动派发器代码
- 开始引入外部系统
- 开始改写 frozen 主线
- 开始把 dispatcher 写成裁决者

## 本模块未触碰项
- dispatcher 代码实现
- 任务自动派发服务
- writeback 校验器代码
- 最终 gate 聚合器代码

