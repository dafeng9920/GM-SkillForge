# Task Dispatcher Protocol Auto Dispatch Sender Minimal Validation v1 Change Control Rules

## 本阶段允许记录的变更类型
- 封包行为校验结论
- message 模板校验结论
- 非阻断性样例覆盖缺口记录

## 本阶段禁止直接执行的变更类型
- 不直接扩成真实发送器
- 不直接接入外部消息系统
- 不直接加入接单确认逻辑

## 非阻断性问题后续处理边界
- compliance / final_gate / escalation 样例覆盖，可在后续增强回合补足
- message 文本增强，可在后续增强回合补足

## 下一阶段前不得触碰的实现面
- 网络发送
- 队列 / webhook / db
- 自动确认送达
- 自动重试

