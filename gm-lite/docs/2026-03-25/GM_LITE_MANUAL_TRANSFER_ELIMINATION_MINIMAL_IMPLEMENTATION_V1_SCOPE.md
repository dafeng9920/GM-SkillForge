# GM LITE Manual Transfer Elimination Minimal Implementation v1 Scope

## 模块目标
- 实现“手动转递开始消失”的最小落地链路
- 让插件壳内至少有一条最小 send / receive / writeback 流开始真实工作
- 目标不是全自动完全体，而是砍掉“最后一米人肉搬运”的第一刀

## 本轮唯一目标
1. 实现最小 task send 动作
2. 实现最小 writeback receive 动作
3. 实现最小状态推进闭环
4. 保持三权分立和证据链不塌

## 完成定义
- 至少一条最小自动流转链可跑
- 插件壳不再只是显示状态，而是开始承接实际发送/接收
- `MI1-MI4` 三件套齐全

## 本轮不做
- 不做完整多通道桥接
- 不做完整自动派单系统
- 不做完整重试/超时编排
- 不做完整产品发布
