# 桥接 payload/schema 草案阶段报告 v1

## 1. 本轮动作总结

- 处理了 3 个桥接点：
  - Governance Candidate Intake
  - Governance Validation Intake
  - Pre-Packaging Review Intake
- 产出了对应的：
  - payload 草案
  - schema 草案
  - interface 草案
- 严格保持草案阶段、未进入实现：
  - 未实现 intake service
  - 未实现治理对象
  - 未实现发布对象
  - 未实现 workflow / orchestrator 绑定

## 2. 3 个桥接点草案结果

### Governance Candidate Intake

- 上游对象：
  - `CandidateSkill`
- payload 草案：
  - `contracts/governance_bridge/candidate_intake.payload.json`
- schema 草案：
  - `contracts/governance_bridge/candidate_intake.schema.json`
- interface 草案：
  - `contracts/governance_bridge/candidate_intake.interface.md`
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
  - approved
  - gate-pass
  - release-ready

### Governance Validation Intake

- 上游对象：
  - `BuildValidationReport`
- payload 草案：
  - `contracts/governance_bridge/validation_intake.payload.json`
- schema 草案：
  - `contracts/governance_bridge/validation_intake.schema.json`
- interface 草案：
  - `contracts/governance_bridge/validation_intake.interface.md`
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
  - governance-pass
  - audit-pass
  - release-allowed

### Pre-Packaging Review Intake

- 上游对象：
  - `DeliveryManifest`
- payload 草案：
  - `contracts/governance_bridge/pre_packaging_review.payload.json`
- schema 草案：
  - `contracts/governance_bridge/pre_packaging_review.schema.json`
- interface 草案：
  - `contracts/governance_bridge/pre_packaging_review.interface.md`
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
  - release-permit
  - publish-approved
  - released

## 3. 字段映射规则

逐桥接点映射规则详见：

- [GOVERNANCE_BRIDGE_FIELD_MAPPING_v1.md](/d:/GM-SkillForge/docs/2026-03-17/GOVERNANCE_BRIDGE_FIELD_MAPPING_v1.md)

## 4. 桥接边界与禁止语义

- `CandidateSkill` 不是 `Governance Approved Candidate`
- `BuildValidationReport` 不是 `GovernanceValidation`
- `DeliveryManifest` 不是 `Release Permit`
- `skill-creator` 不前移成治理 intake
- `workflow/orchestrator` 不获得裁决权

## 5. compat 风险控制

- `ContractBundle.status.validated`
  - 当前仍未进入桥接推荐字段集
  - 不得通过别名包装成治理语义
  - 仅允许保留在生产链内部 compat 语义中

## 6. 本轮未触碰的边界

- `Production Chain v0` 未改
- 冻结文档正文未改
- 主链路顺序未改
- 正式写口未改
- 审计归属未改
- `skill-creator` 角色边界未改
- 未进入治理逻辑
- 未进入发布逻辑
- 未进入 workflow / orchestrator
- 未进入 handoff 执行实现
- 未进入 service / handler / api

## 7. 当前完成度判断

- 是否已具备进入“桥接对象草案冻结判断阶段”或等价下一阶段的条件：
  - **是**
- 若未具备，最小缺口是什么：
  - 不适用

## 8. 下一步建议

- 进入 **桥接对象草案冻结判断阶段**
