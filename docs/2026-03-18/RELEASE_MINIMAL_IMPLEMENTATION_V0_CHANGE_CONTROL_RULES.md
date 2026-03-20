# Release Minimal Implementation v0 Frozen 变更控制规则

## Frozen 后允许变更类型
- 注释补强
- 文档补充
- 非语义性路径修正
- 不改变字段意义的说明增强
- 不改变职责边界的轻量结构整理

## Frozen 后受控变更类型
- compat 字段去留调整提案
- 非语义性字段顺序整理
- Release 四层对象的结构性 fix 提案
- 与 `Review` 承接口径的非语义性整理

受控变更要求：
- 不得直接在 Frozen 后当前阶段执行
- 必须进入单独修正阶段
- 必须重新经过最小校验
- 不得扩大到 `Audit / 系统执行层`

## Frozen 后禁止变更类型
- 新增 `release decision` 或 final release 判定语义
- 新增 `Audit` 对象或语义
- 新增 `Release runtime / service / handler / api`
- 新增 `workflow / orchestrator` 绑定
- 修改已冻结上游对象边界
- 将 compat 字段直接主化
- 将 source status 字段抬升为 `Release` 核心职责字段
- 将 `Release` 直接导向 `Audit ownership`、`final audit verdict` 或外部发布执行语义

## 已冻结层保护规则
- 不修改 `Production Chain v0 Frozen`
- 不修改 `Bridge Draft v0 Frozen`
- 不修改 `Bridge Minimal Implementation v0 Frozen`
- 不修改 `Governance Intake Minimal Implementation v0 Frozen`
- 不修改 `Gate Minimal Implementation Frozen` 对应冻结文档正文
- 不修改 `Review Minimal Implementation Frozen` 对应冻结文档正文
- 不修改已冻结对象边界

## Release 四层对象保护规则

### typed object
- 允许：
  - 注释补强
  - 非语义性路径修正
- 受控：
  - 非语义性结构整理
- 禁止：
  - 引入 `release decision`
  - 引入 `Audit` 语义
  - 扩大为执行态对象

### payload
- 允许：
  - 说明性增强
- 受控：
  - 非语义性字段顺序整理
- 禁止：
  - 引入执行态 payload
  - 引入工作流编排 payload
  - 引入外部发布执行 payload

### schema
- 允许：
  - 说明性增强
- 受控：
  - 非语义性约束整理
- 禁止：
  - 引入审计规则
  - 引入运行时分支规则
  - 引入外部发布执行规则
  - 引入系统层审批路由规则

### interface
- 允许：
  - 注释补强
- 受控：
  - 非语义性表述整理
- 禁止：
  - 引入 `service interface`
  - 引入 `handler interface`
  - 引入 `api / orchestrator contract`
  - 引入 runtime contract

## compat / source status 字段保护规则
- `ContractBundle.status.validated`
  - 继续只作为 compat 风险关注点
  - 不得升级为 `Release Frozen` 主判断轴
  - 不得重新解释为 `release decision / publish approval / audit ownership result`
- `Review status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Release Frozen` 主判断轴
- `Gate status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Release Frozen` 主判断轴
- `production_status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Release Frozen` 主判断轴
- `build_validation_status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Release Frozen` 主判断轴
- `delivery_status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Release Frozen` 主判断轴

## 禁止混入 Audit / 系统执行语义规则
- 禁止出现：
  - `audit_result`
  - `audit_owner`
  - `final_audit_verdict`
  - `external_publish_execution`
  - `release_runtime_action`
  - `final_release_verdict`
  - `external_delivery_execution_approval`
- 禁止将 `Release Frozen` 解释为：
  - Audit 已具备实现结论
  - Publish 已具备执行结论
  - External delivery 已具备授权结论

## 下一阶段前不得触碰的实现面
- `Release` 执行态实现
- `Audit` 最小实现准备之外的任何实现
- `workflow / orchestrator`
- `service / handler / api`
- 任何运行时执行逻辑
- 外部发布执行逻辑
