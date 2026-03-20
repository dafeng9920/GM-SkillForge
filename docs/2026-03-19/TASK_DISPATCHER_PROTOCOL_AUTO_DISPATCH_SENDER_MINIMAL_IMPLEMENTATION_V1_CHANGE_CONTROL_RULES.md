# Task Dispatcher Protocol Auto Dispatch Sender Minimal Implementation v1 Change Control Rules

## 允许变更
- 输出字段补充
- message 模板补强
- 识别更多 relay 文件类型

## 受控变更
- 增加 dispatch packet 元字段
- 增加更多目标角色

## 禁止变更
- 直接扩展为真实发送器
- 直接接入队列 / webhook / db / 外部 API
- 直接替代主控官做决策

