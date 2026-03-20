# Review 最小校验准备阶段范围文档 v0

## 当前阶段
- 当前阶段：
  - `Review 最小校验准备阶段`
- 当前阶段性质：
  - 仅做 `Review` 最小校验准备定义
  - 不进入 `Review` 最小校验执行
  - 不进入 `Review Frozen` 判断
  - 不进入 `Release / Audit`

## 当前唯一目标
- 为 `Review 最小校验阶段` 定义：
  - 最小校验范围
  - 最小校验对象
  - 最小校验口径
  - 与 `Review 最小实现 / Review Frozen / Release / Audit` 的边界
  - 允许项 / 禁止项
  - 固定输出
  - 自动暂停条件
  - compat / 风险控制规则
  - change control 约束

## 本阶段校验准备范围
- 仅限以下对象与关系：
  - `Review typed object`
  - `Review payload`
  - `Review schema`
  - `Review interface`
  - 四层之间的一致性
  - 与 `Gate` 输出承接口径的一致性
  - compat / source status 风险是否受控
  - 是否混入 `Review` 不应承担的 `Release / Audit` 语义
- 明确排除：
  - 行为校验
  - 执行校验
  - runtime 校验
  - workflow / orchestrator 校验
  - service / handler / api 校验
  - integration 校验
  - `Release / Audit` 层校验
  - Frozen 成立性判断

## 本阶段允许项

### 允许项 A：Review 最小校验范围定义
- 可以明确：
  - `Review` 最小校验阶段校验什么
  - `Review` 最小校验阶段不校验什么
  - 校验对象范围
  - 校验层级范围
  - 校验边界
  - 校验收敛条件
  - 校验排除项

### 允许项 B：Review 最小校验对象定义
- 可以明确未来要校验的最小对象集合：
  - `Review typed object`
  - `Review payload`
  - `Review schema`
  - `Review interface`
  - 四层之间的一致性关系
  - 与 `Gate` 输出承接口径的一致性关系

### 允许项 C：Review 最小校验口径定义
- 可以定义下一阶段校验时应使用的最小口径：
  - 字段一致性
  - 职责边界一致性
  - 层间口径一致性
  - compat 风险是否受控
  - 是否混入越界语义
  - 是否把 `Release / Audit` 语义提前写入 `Review`

### 允许项 D：边界规则固化
- 可以明确：
  - `Review` 最小校验与 `Review` 最小实现的边界
  - `Review` 最小校验与 `Review` 最小校验执行的边界
  - `Review` 最小校验与 `Review Frozen` 的边界
  - `Review` 最小校验与 `Release` 的边界
  - `Review` 最小校验与 `Audit` 的边界

### 允许项 E：风险控制与暂停规则
- 可以固化：
  - compat 风险控制
  - source status 风险控制
  - 越界暂停规则
  - change control 规则

### 允许项 F：固定输出文档准备
- 只允许围绕本阶段所需正式文档进行组织与固化

## 本阶段禁止项

### 禁止项 A：Review 最小校验执行
- 不得进入：
  - 实际校验动作
  - 校验结果产出
  - 通过 / 不通过结论
  - 校验报告正文
  - 校验通过性判断

### 禁止项 B：Review Frozen 判断
- 不得进入：
  - `Frozen = true / false` 判断
  - 冻结成立结论
  - 冻结报告
  - 冻结变更控制文档正文

### 禁止项 C：回改 Review 最小实现
- 不得修改：
  - 已落位的 `Review typed object`
  - 已落位的 `Review payload`
  - 已落位的 `Review schema`
  - 已落位的 `Review interface`
  - `REVIEW_MINIMAL_IMPLEMENTATION_V0_REPORT.md`
  - `REVIEW_MINIMAL_IMPLEMENTATION_V0_CHANGE_CONTROL_RULES.md`

### 禁止项 D：进入后续阶段
- 不得进入：
  - `Release` 实现
  - `Audit` 实现
  - `Release / Audit decision` 设计
  - `publish / release semantics`

### 禁止项 E：扩大到系统层
- 不得进入：
  - `workflow`
  - `orchestrator`
  - `service`
  - `handler`
  - `api`
  - `runtime`
  - `external integration`
  - `handoff / intake execution`

### 禁止项 F：偷渡最终判定语义
- 不得混入：
  - `final review verdict`
  - `final release verdict`
  - `publish approval`
  - `audit ownership verdict`
  - `final delivery approval`

### 禁止项 G：反向改写已冻结上游
- 不得修改：
  - `Gate Minimal Implementation Frozen` 对应冻结文档正文
  - `Governance Intake Minimal Implementation Frozen` 对应冻结文档正文
  - `Bridge / Production Chain` 已冻结文档正文
  - 已冻结对象边界

## 本阶段固定输出
- 固定输出文档：
  - `REVIEW_MINIMAL_VALIDATION_PREPARATION_V0_SCOPE.md`
  - `REVIEW_MINIMAL_VALIDATION_PREPARATION_V0_BOUNDARY_RULES.md`

## 本阶段自动暂停条件
- 出现以下任一情况必须自动暂停：
  - 开始进入实际校验执行
  - 开始给出“通过 / 不通过 / 基本通过”之类校验结论
  - 开始进入 `Review Frozen` 判断
  - 开始回改 `Review` 最小实现产物
  - 开始进入 `Release / Audit` 实现或判定语义
  - 开始扩大到 `workflow / orchestrator / service / handler / api / runtime`
  - 开始将 compat 或 source status 字段主化
  - 开始为了便于校验而扩大 `Review` 职责
  - 开始输出无法沉淀为正式文档的聊天式解释

## 本阶段未触碰项
- `Production Chain v0` 未改
- `Bridge Draft v0` 未改
- `Bridge Minimal Implementation v0` 未改
- `Governance Intake Minimal Implementation v0` 未改
- `Gate Minimal Implementation Frozen` 未改
- 已冻结文档正文未改
- 主链路顺序未改
- 正式写口未改
- 审计归属未改
- `skill-creator` 角色边界未改
- 未进入 `Review` 最小校验执行
- 未进入 `Review Frozen`
- 未进入 `Release / Audit`
- 未进入 `workflow / orchestrator / service / handler / api`
