# Task Dispatcher Protocol Auto Dispatch Sender Minimal Implementation v1 Scope

## 当前模块
- task_dispatcher_protocol auto-dispatch-sender minimal implementation v1

## 当前唯一目标
- 落一个最小 sender，用于把 relay-helper 生成的下一跳 envelope / final gate input / escalation pack 转成标准 dispatch 包，供 AI 军团或主控官接收。

## 本模块允许项
- 读取 relay 输出目录
- 识别 review/compliance/final_gate/escalation 四类输入
- 生成标准 dispatch packet
- 生成可直接转发的 message 文本
- 输出发送摘要

## 本模块禁止项
- 不真正发送消息
- 不调用外部 API
- 不接入队列 / webhook / db
- 不自动修改任务卡
- 不替主控官做最终裁决

## 固定输出
- `TASK_DISPATCHER_PROTOCOL_AUTO_DISPATCH_SENDER_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `TASK_DISPATCHER_PROTOCOL_AUTO_DISPATCH_SENDER_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `TASK_DISPATCHER_PROTOCOL_AUTO_DISPATCH_SENDER_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `TASK_DISPATCHER_PROTOCOL_AUTO_DISPATCH_SENDER_MINIMAL_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `tools/task_dispatcher_auto_sender.py`

