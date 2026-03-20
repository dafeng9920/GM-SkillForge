# Gate 最小实现准备阶段边界规则文档 v0

## Gate 与 Governance Intake 的边界
- `Governance Intake` 负责：
  - 接收入治理入口侧最小 typed object
  - 保持 intake 语义清晰
  - 不承担 Gate 判定职责
- `Gate` 只承接：
  - intake 的输出边界
  - intake 到 Gate 的最小承接口径
- `Gate` 不得：
  - 反向重写 intake 冻结对象
  - 修改 intake 已冻结字段边界
  - 将 intake 对象直接解释为 Gate 判定对象

## Gate 与 Review 的边界
- Gate 只负责形成：
  - 进入 Review 之前的最小门控准备口径
- Gate 当前不得定义：
  - `review decision`
  - `review verdict`
  - `review outcome model`
- Gate 当前最多只能定义：
  - Gate 输出未来如何被 Review 承接
- `Review` 不属于本阶段范围

## Gate 与 Release 的边界
- Gate 不负责：
  - 发布
  - `release decision`
  - `release execution`
- 本阶段只能明确：
  - `Gate != Release`
  - Gate 输出不自动导向 Release
  - Release 仍属于后续阶段

## compat 风险控制

### 通用规则
- compat 风险只允许登记
- compat 风险不得借准备阶段扩范围
- compat 字段不得自动升格为 Gate 主字段
- 源层 status 语义不得直接混入 Gate 核心职责

### 已登记 compat 风险项
- `ContractBundle.status.validated`
  - 仅按已登记 compat 风险项处理
  - 不得重新解释为：
    - `governance validated`
    - `gate pass`
    - `release ready`
- `production_status`
  - 仅保留为源层上下文
  - 不得直接作为 Gate 主判定字段
- `build_validation_status`
  - 仅保留为源层上下文
  - 不得直接作为 Gate 主判定字段
- `delivery_status`
  - 仅保留为源层上下文
  - 不得直接作为 Gate 主判定字段

## 禁止混入的语义类型
- `Review` 判定语义
- `Release` 判定语义
- `Audit` 完整归属语义
- 最终发布语义
- “Gate 负责最终判定”语义
- “Gate 直接导向发布”语义

## change control 规则

### 允许变更
- 注释补强
- 文档补充
- 不改变冻结边界的范围说明增强

### 受控变更
- compat 字段去留讨论
- Gate 承接口径细化
- 非语义性结构修正

受控变更要求：
- 不得回改已冻结对象
- 不得引入 Gate 执行实现
- 必须保持在准备阶段

### 禁止变更
- 新增 Gate 执行对象
- 新增 Gate runtime / service / handler / api
- 新增 Review / Release / Audit 对象
- 引入 workflow / orchestrator 绑定
- 修改已冻结层边界
- 将 compat 字段直接主化
