# 外部执行与集成最小落地模块 v1 Boundary Rules

## 与 frozen 主线的边界
- 只能只读承接 frozen 对象主线
- 不得回改 Gate / Review / Release / Audit 的对象、文档、边界
- permit / Evidence / AuditPack / decision 语义只能承接，不得改写

## 与 system_execution 的边界
- `system_execution` 只承接，不裁决
- 外部执行与集成层只连接与搬运，不裁决
- 不得借本模块返修 `workflow / orchestrator / service / handler / api`

## 与 runtime 的边界
- 本模块只做最小落地，不做 runtime
- 不得实现真实执行循环、调度、外部副作用动作
- retry / compensation 只定义边界，不实现策略

## 与真实外部系统的边界
- 不接真实 webhook / queue / db / registry / slack / email / repo
- 不做真实 API 调用
- 不做真实发布、通知、同步动作

## permit / evidence 规则
- 关键动作必须以 permit 为前提
- Evidence / AuditPack 由内核生成，外部层只读承接
- 外部层不可修改 GateDecision / EvidenceRef / AuditPack / permit 语义

## change control 规则
- 允许：文档补强、命名修正、接口占位补全、导出修正
- 受控：新增子面内最小骨架文件、最小导入校验、最小连接说明
- 禁止：runtime、真实外部接入、裁决逻辑、主线对象改写

