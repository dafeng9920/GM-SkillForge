# 外部执行与集成最小落地模块 v1 Scope

## 当前模块
- 外部执行与集成最小落地模块 v1

## 当前唯一目标
- 在不破坏 frozen 主线与 `system_execution` frozen 边界的前提下，为外部执行与集成层落出最小可承接、最小可落位、最小可验收的内部骨架。

## 本模块允许项
- connector contract 最小落地
- integration gateway 最小落地
- secrets / credentials boundary 最小落地
- external action policy 最小落地
- retry / compensation boundary 最小落地
- publish / notify / sync boundary 最小落地
- permit / evidence / audit pack / decision 的只读承接规则
- 最小目录骨架
- 最小接口骨架
- 最小导入/连接检查
- 模块报告、任务板、change control rules

## 本模块禁止项
- 回改 Gate / Review / Release / Audit frozen 主线
- 回改 `system_execution` frozen 主线
- 进入 runtime
- 接入真实外部系统
- 实现 webhook / queue / db / registry / slack / email / repo 真实联调
- 实现自动重试补偿
- 实现真实发布执行
- 实现真实业务长链
- 让外部执行层成为裁决层
- 让 permit 规则失效
- 让 Evidence / AuditPack 可被改写

## 本模块最小推进范围
- 仅覆盖 6 个子面与其相互连接关系
- 仅覆盖只读承接与接口骨架
- 不进入 runtime / 外部联调 / 真实业务执行

## 固定输出
- `EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_SCOPE.md`
- `EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md`
- `EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md`
- `EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_ACCEPTANCE.md`
- `EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_REPORT.md`
- `EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_CHANGE_CONTROL_RULES.md`
- 六张任务卡

## 自动暂停条件
- 任一子任务要求修改 frozen 主线
- 任一子任务进入 runtime
- 任一子任务接入真实外部系统
- 任一子任务让外部执行层成为裁决层
- 任一子任务绕过 permit
- 任一子任务让 Evidence / AuditPack 可变
- Codex 试图绕过军团直接宣布模块完成

## 本模块未触碰项
- runtime
- 真实外部系统接入
- 自动重试补偿实现
- 真实发布执行
- 真正业务长链执行

