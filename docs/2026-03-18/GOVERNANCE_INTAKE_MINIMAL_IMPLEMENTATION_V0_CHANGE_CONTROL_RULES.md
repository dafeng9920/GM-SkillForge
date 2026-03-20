# Governance Intake Minimal Implementation v0 变更控制规则

## 1. 适用范围
- `GovernanceCandidateIntake`
- `GovernanceValidationIntake`
- `PrePackagingReviewIntake`
- 对应 bridge `payload/schema/interface` 草案
- 对应 governance intake 字段映射与 compat 风险控制文档

## 2. 允许变更
- 注释补强
- 非语义性路径修正
- 文档补充
- 不改变字段意义的说明增强

## 3. 受控变更
- compat 字段是否继续保留为背景风险项
- intake 字段映射规则细化
- 非语义性结构修正

受控变更要求：
- 必须重新做 governance intake minimal validation
- 必须重新做 governance intake minimal implementation freeze judgment
- 必须确认未引入 Gate / Review / Release 语义

## 4. 禁止变更
- 将 governance intake object 解释为治理判定对象
- 将 governance intake object 解释为发布判定对象
- 将 `production_status` / `build_validation_status` / `delivery_status` 扩散成治理态或发布态状态
- 将 `ContractBundle.status.validated` 抬升为 governance intake 主字段或治理语义
- 引入 GateDecision / ReviewDecision / ReleaseDecision / AuditPack
- 引入 intake service / handler / api / workflow binding / orchestrator binding

## 5. compat 风险专项
### ContractBundle.status.validated
- 必须继续保持：
  - compat / legacy-style
  - not governance validated
  - not gate pass
  - not release ready
- 禁止通过别名、映射或注释漂移重新包装为治理语义

## 6. 边界重申
- 不修改 `Production Chain v0 Frozen`
- 不修改 `Bridge Draft v0 Frozen`
- 不修改 `Bridge Minimal Implementation v0 Frozen`
- 不修改正式写口
- 不修改审计归属
- 不前移 `skill-creator` 角色边界
- 不进入 Gate / Review / Release / Audit 实现
