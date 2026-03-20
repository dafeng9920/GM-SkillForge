# Review 最小校验执行阶段变更控制规则 v0

## 本阶段允许记录的变更类型
- 注释补强建议
- 文档补充建议
- 非语义性路径修正建议
- 不改变职责边界的字段说明增强建议

## 本阶段禁止直接执行的变更类型
- 直接修改 `Review typed object`
- 直接修改 `Review payload`
- 直接修改 `Review schema`
- 直接修改 `Review interface`
- 直接修改已冻结层
- 直接引入 `Release / Audit` 语义
- 直接引入 `workflow / orchestrator / service / handler / api`

## 阻断性问题的后续处理边界
- 若后续出现阻断性问题：
  - 只能进入专门修复阶段
  - 不得在校验执行阶段顺手修复
  - 修复范围必须重新收窄并单独定义

## 非阻断性问题的后续处理边界
- 若后续出现非阻断性问题：
  - 只能进入轻量修正阶段
  - 不得借机扩大到更高层级对象或执行链

## 已冻结层保护规则
- 不修改 `Production Chain v0 Frozen`
- 不修改 `Bridge Draft v0 Frozen`
- 不修改 `Bridge Minimal Implementation v0 Frozen`
- 不修改 `Governance Intake Minimal Implementation v0 Frozen`
- 不修改 `Gate Minimal Implementation Frozen` 对应冻结文档正文
- 不修改已冻结对象边界

## Review 四层对象的变更控制规则

### typed object
- 允许：
  - 问题记录
  - 变更建议
- 禁止：
  - 在本阶段直接修改对象字段或职责

### payload
- 允许：
  - 问题记录
  - 变更建议
- 禁止：
  - 在本阶段直接修改 payload 内容

### schema
- 允许：
  - 问题记录
  - 变更建议
- 禁止：
  - 在本阶段直接修改 schema 约束

### interface
- 允许：
  - 问题记录
  - 变更建议
- 禁止：
  - 在本阶段直接修改 interface 语义

## compat / source status 字段的变更控制规则
- `ContractBundle.status.validated`
  - 继续只作为 compat 风险关注点
  - 不得升级为 `Review` 主判断轴
- `Gate status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Review` 主判断轴
- `production_status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Review` 主判断轴
- `build_validation_status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Review` 主判断轴
- `delivery_status`
  - 继续只作为 source-layer 风险关注点
  - 不得升级为 `Review` 主判断轴

## 禁止混入 Release / Audit 语义规则
- 禁止出现：
  - `release_decision`
  - `publish_approved`
  - `release_permit`
  - `audit_result`
  - `audit_owner`
  - `final_review_verdict`
  - `final_delivery_approval`
- 禁止将 `Review` 校验结论升级为：
  - Frozen 结论
  - Release 准入结论
  - Audit 准入结论

## 下一阶段前不得触碰的实现面
- `Review Frozen` 判断
- `Release / Audit` 实现
- `workflow / orchestrator`
- `service / handler / api`
- 任何运行时执行逻辑
