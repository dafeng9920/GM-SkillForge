# Task Dispatcher Protocol Relay Helper Minimal Validation v1 Change Control Rules

## 本阶段允许记录的变更类型
- 行为校验结论
- 非阻断性缺口记录
- Frozen 前置条件确认

## 本阶段禁止直接执行的变更类型
- 不直接扩展 helper 能力
- 不直接接入自动发送
- 不直接加入文件监听
- 不直接改变 dispatcher protocol frozen 结论

## 非阻断性问题后续处理边界
- writeback 内容最小字段校验，可放到后续增强回合
- 直接读取原始 envelope，可放到后续增强回合

## 下一阶段前不得触碰的实现面
- 自动发送
- 消息队列 / webhook / db
- 任务板自动改写
- 主控官自动裁决

