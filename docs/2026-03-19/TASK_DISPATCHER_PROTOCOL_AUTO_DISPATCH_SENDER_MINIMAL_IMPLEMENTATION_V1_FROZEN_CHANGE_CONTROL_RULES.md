# Task Dispatcher Protocol Auto Dispatch Sender Minimal Implementation v1 Frozen Change Control Rules

## Frozen 后允许变更类型
- 文本模板补强
- 输出字段补强
- 样例覆盖补强

## Frozen 后受控变更类型
- 增加 compliance / final_gate / escalation 封包样例
- 增加更丰富的消息模板

## Frozen 后禁止变更类型
- 直接扩成真实发送器
- 直接接入网络 / webhook / queue / db
- 直接加入自动确认送达
- 直接加入自动重试
- 直接替代主控官裁决

## 下一阶段前不得触碰的实现面
- 真实对外发送
- 送达确认
- 自动重试
- 外部消息基础设施

