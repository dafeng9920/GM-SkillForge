# Audit 最小实现准备阶段边界规则文档 v0

## Audit 与 Release 的边界
- `Release` 已冻结，当前 `Audit` 只允许承接 `Release` 输出边界。
- `Audit` 当前只允许：
  - 定义 `Release -> Audit` 的最小承接口径
  - 定义 `Audit` 侧最小承接对象边界
  - 保持 `Release` 与 `Audit` 的语义分层
- `Audit` 当前不允许：
  - 反向重写 `Release Frozen` 对象
  - 吞并 `Release` 语义
  - 借 `Audit` 准备阶段改写 `Release` compat 口径
  - 将 `Release` 的 source status 直接升级为 `Audit` 核心职责字段

## Audit 与系统执行层的边界
- `Audit` 当前只允许定义“进入系统执行层之前”的最小审计结构准备。
- `Audit` 当前不得定义：
  - `workflow routing`
  - `orchestrator action`
  - `service / handler / api behavior`
  - `runtime execution path`
  - `external execution path`
- 若某字段、对象、命名天然属于系统执行层：
  - 必须暂停
  - 不得并入 `Audit` 最小实现准备阶段
- `Audit` 输出最多只能为下游系统执行层保留边界占位，不得携带执行控制语义

## Audit 与外部执行 / 集成的边界
- `Audit` 最小实现准备不负责：
  - 外部系统调用
  - 外部审计执行
  - 发布执行
  - runtime 决策与调度
  - `API / handler / service` 落地
- 当前任何直接指向外部执行或集成的结构都视为越界。
- `Audit` 最多只能保持与外部执行 / 集成层的语义隔离，不得提前承接其职责。

## compat 风险控制

### compat 总规则
- compat 字段只能受控存在，不能主化
- compat 处理只能用于边界兼容，不得用于扩展 `Audit` 作用域
- compat 字段不得自动升格为 `Audit` 主字段或 `Audit` 主判断轴

### source-layer status 总规则
- source-layer status 字段不得直接成为 `Audit` 核心职责字段
- 不得把 `Release status / Review status / Gate status / production_status / build_validation_status / delivery_status` 直接抬升为 `Audit` 主语义
- 任何会使 source-layer status 成为 `Audit` 主判断依据的做法，视为越界

### 已登记风险项的处理口径
- `ContractBundle.status.validated`
  - 只能按已登记 compat 风险项处理
  - 不得在本阶段重新扩写其治理归属
  - 不得升格为 `Audit` 主字段
- `Release status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Audit` 主字段
- `Review status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Audit` 主字段
- `Gate status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Audit` 主字段
- `production_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Audit` 主字段
- `build_validation_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Audit` 主字段
- `delivery_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Audit` 主字段

## 禁止混入的语义类型
- 外部执行批准语义
- 最终运行时控制语义
- 非 `Audit` 职责的系统编排语义
- `audit execution result`
- `audit frozen verdict`
- 任何把 `Audit` 直接解释为最终系统执行控制层的表述

## change control 规则

### 允许变更
- `Audit` 准备文档的说明补强
- 不改变边界的表述收紧
- compat 风险登记说明增强
- `Release -> Audit` 承接口径的准备性描述增强

### 受控变更
- `Audit` 最小对象范围的轻量收敛
- `Audit payload / schema / interface` 草案边界细化
- 与系统执行层的边界占位表述细化

受控变更要求：
- 不得进入 `Audit` 实现
- 不得进入 `Audit` 校验与 Frozen
- 不得反向修改 `Release` 冻结对象
- 不得扩展到系统执行层 / 外部执行层

### 禁止变更
- 新增 `Audit handler / executor / runtime / service / api`
- 新增 `Audit workflow / orchestrator binding`
- 新增系统执行层对象与实现
- 修改已冻结 `Gate / Review / Release / Intake / Bridge / Production Chain` 边界
- 将 compat 或 source status 字段主化
- 把 `Audit` 直接导向系统执行控制、外部执行批准或运行时调度语义
