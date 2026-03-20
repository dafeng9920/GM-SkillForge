# 最小实现阶段报告 v1

## 1. 本轮动作总结

- 创建了 5 个生产对象的最小 `pydantic` 模型草案
- 创建了 2 个 handoff 类型占位：
  - `candidate handoff`
  - `validation handoff`
- 严格保持在最小实现阶段：
  - 未进入业务逻辑
  - 未进入治理实现
  - 未进入发布实现
  - 未进入 handoff 执行实现

## 2. 5 个对象模型落地结果

### IntentDraft

- 文件路径：`contracts/production/intent/intent_draft.model.py`
- 类名：`IntentDraft`
- 最小字段集：
  - `intent_id`
  - `summary`
  - `goal`
  - `in_scope`
  - `out_of_scope`
  - `inputs`
  - `outputs`
  - `constraints`
  - `required_gates`
  - `status`
- compat 字段：
  - `created_at`
  - `updated_at`
  - `revision`
- 风险点：
  - 无明显继承性风险

### ContractBundle

- 文件路径：`contracts/production/contract/contract_bundle.model.py`
- 类名：`ContractBundle`
- 最小字段集：
  - `contract_id`
  - `intent_id`
  - `input_schema`
  - `output_schema`
  - `state_schema`
  - `error_schema`
  - `trigger_spec`
  - `evidence_spec`
  - `required_gates`
  - `status`
- compat 字段：
  - `status="validated"`
- 风险点：
  - `validated` 容易被误读为治理 validated

### CandidateSkill

- 文件路径：`contracts/production/candidate/candidate_skill.model.py`
- 类名：`CandidateSkill`
- 最小字段集：
  - `candidate_id`
  - `intent_id`
  - `contract_id`
  - `skill_root`
  - `directory_layout`
  - `generated_files`
  - `status`
- compat 字段：无
- 风险点：
  - `handed_to_validation` 只允许作为生产态 handoff 语义

### BuildValidationReport

- 文件路径：`contracts/production/validation/build_validation_report.model.py`
- 类名：`BuildValidationReport`
- 最小字段集：
  - `report_id`
  - `candidate_id`
  - `checks`
  - `summary`
  - `handoff_ready`
  - `status`
- compat 字段：无
- 风险点：
  - `validation_failed` 不得扩为治理验证失败

### DeliveryManifest

- 文件路径：`contracts/production/delivery/delivery_manifest.model.py`
- 类名：`DeliveryManifest`
- 最小字段集：
  - `delivery_id`
  - `candidate_id`
  - `validation_report_id`
  - `package_input_root`
  - `handoff_target`
  - `package_manifest`
  - `status`
- compat 字段：无
- 风险点：
  - `delivered` 不得扩为 `released`

## 3. handoff 类型占位结果

### candidate handoff

- 文件路径：`contracts/production/handoff/candidate_handoff.types.py`
- 输入 payload：
  - `intent`
  - `contract`
  - `candidate`
- 输出 payload：
  - `candidate_id`
  - `accepted`
  - `next_stage=build_validation`
- 最小错误对象：
  - `CandidateHandoffError`

### validation handoff

- 文件路径：`contracts/production/handoff/validation_handoff.types.py`
- 输入 payload：
  - `candidate`
  - `contract`
- 输出 payload：
  - `report`
  - `accepted`
  - `next_stage=delivery_manifest`
- 最小错误对象：
  - `ValidationHandoffError`

## 4. `validated` 兼容字段处理结果

- 是否进入模型：**是**
- 进入位置：
  - `ContractBundle.status`
- compat 标注方式：
  - 类注释明确说明：
    - compatibility-only
    - not governance validated
- 防止治理语义扩散方式：
  - 不新增任何 gate/release 字段
  - 不让该字段进入 handoff 决策语义
  - 不把它映射成 `GateDecision / ReleasePermit / GovernanceValidation`

## 5. 本轮未触碰的边界

- 冻结文档正文未改
- 主链路未改
- 正式写口未改
- 审计归属未改
- `skill-creator` 角色边界未改
- 未进入业务逻辑
- 未新增治理对象
- 未新增发布对象
- 未进入 handoff 执行实现

## 6. 当前最小实现阶段完成度

- 是否已完成 5 个生产对象的最小模型实现：**是**
- 是否已具备进入“最小校验阶段”或等价下一阶段的条件：**是**

## 7. 下一步建议

下一步只建议进入：

- **model/schema 一致性检查**
