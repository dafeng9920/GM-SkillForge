# Review 最小校验准备阶段边界规则文档 v0

## Review 最小校验准备与 Review 最小实现的边界
- `Review` 最小实现阶段已完成。
- 当前阶段只允许：
  - 读取与整理 `Review` 最小实现产物的校验准备口径
  - 定义下阶段如何校验
  - 明确校验对象与校验边界
- 当前阶段不允许：
  - 反向修改最小实现
  - 因为准备校验而重做实现
  - 借“校验准备”名义补实现缺口

## Review 最小校验准备与 Review 最小校验执行的边界
- 当前阶段只是为后续 `Review 最小校验执行阶段` 做准备。
- 当前阶段不得：
  - 真正执行校验
  - 给出通过 / 不通过
  - 给出阻断性问题清单的最终判定版本
  - 给出完成反馈结论
- 当前阶段最多只能定义：
  - 下一阶段校验对象
  - 下一阶段校验口径
  - 下一阶段排除项与暂停项

## Review 最小校验准备与 Review Frozen 的边界
- `Review Frozen` 属于后续阶段，不属于当前阶段。
- 当前阶段只能明确：
  - Frozen 判断不能提前发生
  - Frozen 需要以最小校验执行结果为前提
  - 当前阶段不具备给出 Frozen 结论的资格

## Review 最小校验准备与 Release 的边界
- 当前阶段不得定义：
  - `release object`
  - `release decision`
  - `publish permit`
  - `release execution path`
  - `release runtime`
- 若某个校验口径天然属于 `Release`：
  - 必须暂停
  - 不得并入 `Review` 最小校验准备阶段

## Review 最小校验准备与 Audit 的边界
- 当前阶段不得定义：
  - `audit object`
  - `audit execution`
  - `audit ownership verdict`
  - `audit runtime / service / api`
- 若某个校验口径天然属于 `Audit`：
  - 必须暂停
  - 不得并入 `Review` 最小校验准备阶段

## compat / source status 风险控制规则

### compat 风险总规则
- compat 字段只能被纳入“校验关注点”
- compat 字段不得被提升为核心校验主轴
- compat 风险准备只能用于界定“边界是否受控”
- 不得借 compat 扩展 `Review` 作用域

### source status 风险总规则
- source status 字段只能作为受控风险项
- 不得被抬升为 `Review` 核心职责依据
- 不得被直接解释为：
  - `Review` 主判断依据
  - `Release` 主判断依据
  - `Audit` 主判断依据

### 已登记风险项
- `ContractBundle.status.validated`
  - 只能作为 compat 风险关注点
  - 不得升级为 `Review` 核心校验主轴
- `Gate status`
  - 只能作为 source-layer 风险关注点
  - 不得升级为 `Review` 核心校验主轴
- `production_status`
  - 只能作为 source-layer 风险关注点
  - 不得升级为 `Review` 核心校验主轴
- `build_validation_status`
  - 只能作为 source-layer 风险关注点
  - 不得升级为 `Review` 核心校验主轴
- `delivery_status`
  - 只能作为 source-layer 风险关注点
  - 不得升级为 `Review` 核心校验主轴

## change control 规则

### 允许变更
- 注释补强
- 文档补充
- 不改变冻结边界的范围说明增强

### 受控变更
- compat 字段去留讨论
- `Review` 校验口径细化
- 非语义性结构修正

受控变更要求：
- 不得回改已冻结对象
- 不得进入 `Review` 校验执行
- 必须保持在准备阶段

### 禁止变更
- 新增 `Review` 校验执行内容
- 新增 `Review Frozen` 结论内容
- 新增 `Release / Audit` 对象或判定语义
- 引入 `workflow / orchestrator / service / handler / api / runtime`
- 修改已冻结层边界
- 将 compat 或 source status 字段直接主化

## 禁止混入的语义类型
- `final review verdict`
- `final release verdict`
- `publish approval`
- `audit ownership verdict`
- `final delivery approval`
- 任何使 `Review` 最小校验准备看起来像通过性判断的表述
