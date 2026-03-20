# Task Dispatcher Protocol Minimal Validation v1 Change Control Rules

## 本阶段允许记录的变更类型
- 一致性问题记录
- 非阻断性缺口记录
- 进入 Frozen 判断前的前置条件说明

## 本阶段禁止直接执行的变更类型
- 不直接修改现有协议产物
- 不直接扩展为运行时代码
- 不直接接入外部系统
- 不直接改变既有 frozen 主线

## 非阻断性问题后续处理边界
- `next_hop` 是否升为必填项，可放到 Frozen 后或代码化前受控处理
- `REQUIRES_CHANGES` 是否显式建状态节点，可放到后续协议增强回合处理

## 已冻结层保护规则
- 不回改 Production Chain / Bridge / Governance Intake / Gate / Review / Release / Audit
- 不回改 `system_execution` frozen
- 不回改已完成的外部执行与集成准备模块结论

## 协议产物保护规则
- `task_envelope_schema.yaml`
- `state_machine.md`
- `auto_relay_rules.md`
- `writeback_contract.md`
- `escalation_protocol.md`

以上五件是当前 Frozen 判断的唯一协议输入集。

## 下一阶段前不得触碰的实现面
- dispatcher 代码
- 文件监听与状态持久化
- 自动派发器服务
- 外部队列 / webhook / db 对接

