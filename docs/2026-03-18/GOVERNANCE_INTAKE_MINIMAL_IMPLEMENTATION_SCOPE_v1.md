# GOVERNANCE_INTAKE_MINIMAL_IMPLEMENTATION_SCOPE_v1

## 1. 本轮范围
- 仅处理 3 个治理 intake 点的最小实现准备：
  - `Governance Candidate Intake`
  - `Governance Validation Intake`
  - `Pre-Packaging Review Intake`

## 2. 推荐最小实现形式

### Governance Candidate Intake
- 形式：
  - `typed intake object`
- 原因：
  - 上游 bridge payload 已冻结
  - 字段边界稳定
  - 适合进入最小对象实现，但不需要 service / handler / workflow

### Governance Validation Intake
- 形式：
  - `typed intake object`
- 原因：
  - 需要稳定承接 `BuildValidationReport` 派生的 bridge payload
  - 但当前只能停在治理可消费输入层，不能扩成治理验证结果

### Pre-Packaging Review Intake
- 形式：
  - `typed intake object`
- 原因：
  - 需要稳定承接 `DeliveryManifest` 派生的 bridge payload
  - 但当前只能停在预打包 review 输入层，不能扩成 release permit 或发布判断

## 3. 暂不进入最小实现的内容
- `boundary_note`
- GateDecision
- GovernanceValidation 正式对象
- ReviewDecision
- ReleaseDecision
- AuditPack
- intake service / handler / api
- workflow / orchestrator binding
- skill-creator execution binding

## 4. intake 对象的最小职责边界
- 接收 bridge payload 冻结字段
- 表达治理可消费输入结构
- 维持 compat 风险控制
- 不做任何治理裁决
- 不做任何发布裁决
- 不做任何执行动作

## 5. intake 对象当前严禁承载的语义
- approved
- governance validated
- gate pass / fail
- review decision
- release permit
- publish approved
- audit result
