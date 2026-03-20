# Review 最小实现准备阶段边界规则文档 v0

## Review 与 Gate 的边界
- `Gate` 已冻结，当前 `Review` 只允许承接 `Gate` 输出边界。
- `Review` 当前只允许：
  - 定义 `Gate -> Review` 的最小承接口径
  - 定义 `Review` 侧最小承接对象边界
  - 保持 `Gate` 与 `Review` 的语义分层
- `Review` 当前不允许：
  - 反向重写 `Gate Frozen` 对象
  - 吞并 `Gate` 语义
  - 借 `Review` 准备阶段改写 `Gate` compat 口径
  - 将 `Gate` 的 source status 直接升级为 `Review` 核心职责字段

## Review 与 Release 的边界
- `Review` 当前只允许定义“进入 `Release` 之前”的最小审查结构准备。
- `Review` 当前不得定义：
  - `release outcome`
  - `release decision`
  - `publish permit`
  - `release execution path`
- 若某字段、对象、命名天然属于 `Release`：
  - 必须暂停
  - 不得并入 `Review` 最小实现准备阶段
- `Review` 输出最多只能为下游 `Release` 保留边界占位，不得携带发布判定语义

## Review 与 Audit 的边界
- `Review` 不负责：
  - `audit execution`
  - `audit ownership verdict`
  - `audit runtime`
  - `audit service / api`
- 当前任何直接指向 `Audit` 执行的结构都视为越界。
- `Review` 最多只能保持与 `Audit` 的语义隔离，不得提前承接 `Audit` 职责。

## compat 风险控制

### compat 总规则
- compat 字段只能受控存在，不能主化
- compat 处理只能用于边界兼容，不得用于扩展 `Review` 作用域
- compat 字段不得自动升格为 `Review` 主字段或 `Review` 主判断轴

### source-layer status 总规则
- source-layer status 字段不得直接成为 `Review` 核心职责字段
- 不得把 `Gate status / build status / delivery status` 直接抬升为 `Review` 主语义
- 任何会使 source-layer status 成为 `Review` 主判断依据的做法，视为越界

### 已登记风险项的处理口径
- `ContractBundle.status.validated`
  - 只能按已登记 compat 风险项处理
  - 不得在本阶段重新扩写其治理归属
  - 不得升格为 `Review` 主字段
- `production_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Review` 主字段
- `build_validation_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Review` 主字段
- `delivery_status`
  - 只能作为 source-layer 风险关注点
  - 不得升格为 `Review` 主字段

## 禁止混入的语义类型
- `release permit`
- `publish approval`
- `audit ownership verdict`
- `final release verdict`
- `final publish semantics`
- `review execution result`
- `review frozen verdict`
- 任何把 `Review` 直接解释为最终发布判定层的表述

## change control 规则

### 允许变更
- `Review` 准备文档的说明补强
- 不改变边界的表述收紧
- compat 风险登记说明增强
- `Gate -> Review` 承接口径的准备性描述增强

### 受控变更
- `Review` 最小对象范围的轻量收敛
- `Review payload / schema / interface` 草案边界细化
- 与 `Release` 的边界占位表述细化

受控变更要求：
- 不得进入 `Review` 实现
- 不得进入 `Review` 校验与 Frozen
- 不得反向修改 `Gate` 冻结对象
- 不得扩展到 `Release / Audit / 系统层`

### 禁止变更
- 新增 `Review handler / executor / runtime / service / api`
- 新增 `Review workflow / orchestrator binding`
- 新增 `Release / Audit` 对象与实现
- 修改已冻结 `Gate / Intake / Bridge / Production Chain` 边界
- 将 compat 或 source status 字段主化
- 把 `Review` 直接导向 `Release permit / publish approval / audit ownership` 语义
