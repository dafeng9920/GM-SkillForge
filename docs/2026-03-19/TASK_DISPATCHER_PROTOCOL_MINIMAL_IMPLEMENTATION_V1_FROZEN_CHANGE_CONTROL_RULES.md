# Task Dispatcher Protocol Minimal Implementation v1 Frozen Change Control Rules

## Frozen 后允许变更类型
- 文档补强
- 说明性注释补强
- 示例补充
- 非语义性命名收紧

## Frozen 后受控变更类型
- `next_hop` 从可选升级为受控必填
- `REQUIRES_CHANGES` 是否显式建模为状态节点
- writeback 最小字段的受控补充
- escalation trigger 的受控补充

## Frozen 后禁止变更类型
- 直接改写五件协议产物的核心职责定义
- 直接扩展为 runtime 代码
- 直接接入外部系统或基础设施
- 直接改变主控官 / AI 军团的职责分工
- 让 dispatcher 取得最终裁决权

## 已冻结层保护规则
- 不回改 Production Chain / Bridge / Governance Intake / Gate / Review / Release / Audit
- 不回改 `system_execution` frozen
- 不回改外部执行与集成准备模块已完成结论

## 协议输入集保护规则
以下五件为当前 Frozen 协议输入集，不得无审计地变更：
- [task_envelope_schema.yaml](/d:/GM-SkillForge/docs/2026-03-19/task_envelope_schema.yaml)
- [state_machine.md](/d:/GM-SkillForge/docs/2026-03-19/state_machine.md)
- [auto_relay_rules.md](/d:/GM-SkillForge/docs/2026-03-19/auto_relay_rules.md)
- [writeback_contract.md](/d:/GM-SkillForge/docs/2026-03-19/writeback_contract.md)
- [escalation_protocol.md](/d:/GM-SkillForge/docs/2026-03-19/escalation_protocol.md)

## 主控官 / 军团边界保护规则
- 主控官负责最终终验与模块裁决
- AI 军团负责 execution / review / compliance
- dispatcher protocol 只负责投递、写回、状态流转、升级条件

## 下一阶段前不得触碰的实现面
- dispatcher runtime
- 文件系统监听
- 队列 / webhook / db
- 自动派发服务
- 外部系统接入

