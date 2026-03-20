# 五层主线合规整改要求 v1

## 目标
- 将当前五层主线从“结构冻结完成”提升到“合规前置条件完整”
- 不重做已冻结对象
- 不回改既有 frozen 结论
- 只补齐治理合规桥接层

## RequiredChanges

### RC-1 三权分立记录补齐
- 要求：
  - 为当前五层主线补齐 `Execution / Review / Compliance` 三权记录入口
  - 至少要能把主控、执行、验收三类角色绑定到同一条主线材料中
- 范围：
  - 仅新增治理材料，不回改 Bridge / Governance Intake / Gate / Review / Release / Audit frozen 对象
- 通过标准：
  - 能在同一主线材料中定位三权角色、职责边界和验收结论

### RC-2 permit 口径补齐
- 要求：
  - 将 `permit=VALID` 的要求显式挂接到五层主线的后续系统执行层入口条件上
- 范围：
  - 只定义系统执行层前置合规条件，不进入系统执行实现
- 通过标准：
  - 后续任何副作用操作都不能绕开 permit 条件

### RC-3 EvidenceRef / AuditPack 证据桥接补齐
- 要求：
  - 为五层主线建立正式证据引用口径
  - 至少明确：
    - evidence 产物放在哪里
    - 如何把 evidence_ref / EvidenceRef 绑定到该主线
    - 如何把 `AuditPack/evidence/` 与五层主线结论关联起来
- 范围：
  - 只补桥接与引用规则，不做外部执行
- 通过标准：
  - 五层主线后续合规报告能引用明确证据，而不是只引用叙述性结论

### RC-4 系统执行层前置门槛改写为“有条件进入”
- 要求：
  - 后续材料不得直接把当前 frozen 状态解释为“可直接进入系统执行层”
  - 必须改成：
    - `仅在三权记录 + permit + evidence bridge 补齐后，才具备进入系统执行层准备的合规前置条件`
- 范围：
  - 只收紧后续进入条件，不改当前 frozen 对象

## 禁止动作
- 不得重做 Bridge / Governance Intake / Gate / Review / Release / Audit 已冻结阶段
- 不得回改已冻结对象语义
- 不得提前进入 workflow / orchestrator / service / handler / api / runtime
- 不得把整改阶段做成系统执行实现阶段

## 后续建议阶段
- 建议新增一个窄阶段：
  - `五层主线合规整改阶段`
- 该阶段只处理：
  - 三权分立记录挂接
  - permit 条件挂接
  - AuditPack / EvidenceRef 桥接

## 关闭条件
- 只有当 RC-1 ~ RC-4 全部完成，且形成正式可引用材料后，五层主线合规检验才可由 `REQUIRES_CHANGES` 升级为 `PASS`
