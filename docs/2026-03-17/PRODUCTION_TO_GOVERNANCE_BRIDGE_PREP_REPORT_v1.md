# 生成线-治理线桥接准备阶段报告 v1

## 1. 本轮动作总结

- 处理了 3 个桥接点：
  - `CandidateSkill -> Governance Candidate Intake`
  - `BuildValidationReport -> Governance Validation Intake`
  - `DeliveryManifest -> Pre-Packaging Review Intake`
- 严格保持在桥接准备阶段：
  - 只定义桥接输入、输出占位、边界与越权控制
  - 未进入治理实现
  - 未进入发布实现
  - 未进入 handoff 执行
  - 未进入 workflow / orchestrator 绑定

## 2. 3 个桥接点准备结果

### A. CandidateSkill -> Governance Candidate Intake

- 上游对象：
  - `CandidateSkill`
- 下游 intake 占位：
  - `GovernanceCandidateIntakePayload`（占位）
- 最小字段集：
  - `candidate_id`
  - `intent_id`
  - `contract_id`
  - `candidate_name`
  - `skill_root`
  - `generated_files`
  - `entrypoints`
  - `dependencies`
  - `required_changes`
  - `production_status`
- 禁止传递的语义：
  - `governance_approved`
  - `gate_passed`
  - `release_ready`
  - `published`
- 未来允许调用方：
  - `production-chain assembler`
  - `candidate intake adapter`
- 明确禁止调用方：
  - `skill-creator`
  - `release-manager`
  - `governor` 直接越过 intake 写回
  - `workflow/orchestrator` 直接构造裁决结果

### B. BuildValidationReport -> Governance Validation Intake

- 上游对象：
  - `BuildValidationReport`
- 下游 intake 占位：
  - `GovernanceValidationIntakePayload`（占位）
- 最小字段集：
  - `report_id`
  - `candidate_id`
  - `checks`
  - `summary`
  - `missing_artifacts`
  - `broken_references`
  - `smoke_test_result`
  - `trace_result`
  - `handoff_ready`
  - `build_validation_status`
- 禁止传递的语义：
  - `governance_validation_passed`
  - `audit_passed`
  - `review_passed`
  - `release_allowed`
- 未来允许调用方：
  - `build-validation adapter`
  - `governance intake adapter`
- 明确禁止调用方：
  - `release-manager`
  - `audit-pack builder`
  - `skill-creator`
  - `workflow/orchestrator` 直接解释为治理结论

### C. DeliveryManifest -> Pre-Packaging Review Intake

- 上游对象：
  - `DeliveryManifest`
- 下游 intake 占位：
  - `PrePackagingReviewIntakePayload`（占位）
- 最小字段集：
  - `delivery_id`
  - `candidate_id`
  - `validation_report_id`
  - `delivery_name`
  - `package_input_root`
  - `handoff_target`
  - `package_manifest`
  - `integrity_checks`
  - `handoff_payload`
  - `delivery_status`
- 禁止传递的语义：
  - `release_permit`
  - `publish_approved`
  - `audit_pack_complete`
  - `released`
- 未来允许调用方：
  - `delivery adapter`
  - `pre-packaging review adapter`
- 明确禁止调用方：
  - `skill-creator` 直接把自己当前输入解释为 review 结果
  - `release-manager`
  - `workflow/orchestrator` 直接下放发布结论

## 3. 桥接边界规则

- 生成线输出对象 ≠ 治理线判定对象
- `CandidateSkill` ≠ `Governance Approved Candidate`
- `BuildValidationReport` ≠ `GovernanceValidation`
- `DeliveryManifest` ≠ `Release Permit`
- `skill-creator` 只属于打包层，不前移到治理 intake
- `workflow/orchestrator` 将来最多调用桥接接口，不得获得裁决权
- 桥接层只能做：
  - 输入收拢
  - payload 映射
  - 语义隔离
- 桥接层不能做：
  - 治理裁决
  - 发布裁决
  - review 结论
  - release 结论

## 4. compat / 风险项控制

### `ContractBundle.status.validated`

- 当前状态：
  - compat / legacy-style
- 风险：
  - 易被桥接层误读为 governance validated
- 控制方式：
  - 不进入桥接推荐最小字段集
  - 若未来桥接层需要读取，只能映射为：
    - `production_contract_status`
  - 禁止映射为：
    - `governance_validated`
    - `gate_result`
    - `release_ready`

### 其他可能导致桥接误读的字段

- `CandidateSkill.status = handed_to_validation`
  - 风险：被误读为“已经通过治理 review”
  - 控制：仅保留为 `production_status`

- `BuildValidationReport.status = verified_candidate`
  - 风险：被误读为“治理验证通过”
  - 控制：仅保留为 `build_validation_status`

- `DeliveryManifest.status = delivered`
  - 风险：被误读为“已发布”
  - 控制：仅保留为 `delivery_status`

## 5. 本轮未触碰的边界

- 冻结文档正文未改
- `Production Chain v0` 未改
- 正式写口未改
- 审计归属未改
- `skill-creator` 角色边界未改
- 未进入治理逻辑
- 未进入发布逻辑
- 未进入 workflow / orchestrator
- 未进入 handoff 执行实现
- 未进入 service / handler / api

## 6. 当前完成度判断

- 是否已具备进入“桥接对象草案阶段”或等价下一阶段的条件：
  - **是**
- 若未具备，最小缺口是什么：
  - 不适用

## 7. 下一步建议

- 进入 **桥接 payload/schema 草案阶段**
