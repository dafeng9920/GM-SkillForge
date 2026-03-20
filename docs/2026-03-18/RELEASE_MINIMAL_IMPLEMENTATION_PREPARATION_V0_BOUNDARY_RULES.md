# Release 最小实现准备阶段边界规则文档 v0

## Release 与 Review 的边界
- `Review` 已冻结，当前 `Release` 只允许承接 `Review` 输出边界。
- `Release` 当前只允许：
  - 定义 `Review -> Release` 的最小承接口径
  - 定义 `Release` 侧最小承接对象边界
  - 保持 `Review` 与 `Release` 的语义分层
- `Release` 当前不允许：
  - 反向重写 `Review Frozen` 对象
  - 吞并 `Review` 语义
  - 借 `Release` 准备阶段改写 `Review` compat 口径
  - 将 `Review` 的 source status 直接升级为 `Release` 核心职责字段

## Release 与 Audit 的边界
- `Release` 当前只允许定义“进入 `Audit` 之前”的最小发布结构准备。
- `Release` 当前不得定义：
  - `audit outcome`
  - `audit decision`
  - `audit ownership`
  - `audit execution path`
  - `audit runtime / service / api`
- 若某字段、对象、命名天然属于 `Audit`：
  - 必须暂停
  - 不得并入 `Release` 最小实现准备阶段
- `Release` 输出最多只能为下游 `Audit` 保留边界占位，不得携带审计归责语义

## Release 与系统执行层的边界
- `Release` 最小实现准备不负责：
  - `workflow / orchestrator`
  - `handler / service / api`
  - `runtime execution`
  - 外部发布执行
  - 外部集成
- 当前任何直接指向系统执行层的结构都视为越界。
- `Release` 最多只能保持与系统执行层的语义隔离，不得提前承接执行职责。

## compat 风险控制

### compat 总规则
- compat 字段只能受控存在，不能主化
- compat 处理只能用于边界兼容，不得用于扩展 `Release` 作用域
- compat 字段不得自动升格为 `Release` 主字段或 `Release` 主判断轴

### source-layer status 总规则
- source-layer status 字段不得直接成为 `Release` 核心职责字段
- 不得把 `Review status / Gate status / production_status / build_validation_status / delivery_status` 直接抬升为 `Release` 主语义
- 任何会使 source-layer status 成为 `Release` 主判断依据的做法，视为越界

### 已登记风险项的处理口径
- `ContractBundle.status.validated`
  - 只能按已登记 compat 风险项处理
  - 不得在本阶段重新扩写其治理归属
  - 不得升格为 `Release` 主字段
- `Gate status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Release` 主字段
- `production_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Release` 主字段
- `build_validation_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Release` 主字段
- `delivery_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Release` 主字段

## 禁止混入的语义类型
- `audit ownership verdict`
- `final audit verdict`
- `audit execution semantics`
- 审计归责语义
- `release execution result`
- `release frozen verdict`
- 任何把 `Release` 直接解释为最终审计归责层的表述

## change control 规则

### 允许变更
- `Release` 准备文档的说明补强
- 不改变边界的表述收紧
- compat 风险登记说明增强
- `Review -> Release` 承接口径的准备性描述增强

### 受控变更
- `Release` 最小对象范围的轻量收敛
- `Release payload / schema / interface` 草案边界细化
- 与 `Audit` 的边界占位表述细化

受控变更要求：
- 不得进入 `Release` 实现
- 不得进入 `Release` 校验与 Frozen
- 不得反向修改 `Review` 冻结对象
- 不得扩展到 `Audit / 系统层`

### 禁止变更
- 新增 `Release handler / executor / runtime / service / api`
- 新增 `Release workflow / orchestrator binding`
- 新增 `Audit` 对象与实现
- 修改已冻结 `Gate / Review / Intake / Bridge / Production Chain` 边界
- 将 compat 或 source status 字段主化
- 把 `Release` 直接导向 `audit ownership / final audit verdict / execution runtime` 语义
