# Task Dispatcher Protocol Relay Helper Minimal Implementation v1 Change Control Rules

## 允许变更
- 参数补充
- 输出文件命名收紧
- 状态摘要格式补强
- envelope 字段补齐

## 受控变更
- 新增下一跳类型
- 新增升级触发类型
- 新增最小字段校验

## 禁止变更
- 直接扩成自动发送服务
- 直接接入数据库 / 队列 / webhook
- 直接替代主控官终验
- 直接改动既有 frozen 协议语义

