# GOVERNANCE_BRIDGE_FIELD_MAPPING_v1

## 1. CandidateSkill -> Governance Candidate Intake

### 透传字段

- `candidate_id`
- `intent_id`
- `contract_id`
- `candidate_name`
- `skill_root`
- `generated_files`
- `entrypoints`
- `dependencies`
- `required_changes`

### 重命名字段

- `status` -> `production_status`

### 降级说明字段

- `boundary_note`

### 排除字段

- 无新增排除字段；仅排除所有治理/发布语义别名

### compat 禁入字段

- `ContractBundle.status.validated` 不在该桥接点字段集中

## 2. BuildValidationReport -> Governance Validation Intake

### 透传字段

- `report_id`
- `candidate_id`
- `checks`
- `summary`
- `missing_artifacts`
- `broken_references`
- `smoke_test_result`
- `trace_result`
- `handoff_ready`

### 重命名字段

- `status` -> `build_validation_status`

### 降级说明字段

- `boundary_note`

### 排除字段

- 所有治理通过/失败语义别名

### compat 禁入字段

- `ContractBundle.status.validated` 不在该桥接点字段集中

## 3. DeliveryManifest -> Pre-Packaging Review Intake

### 透传字段

- `delivery_id`
- `candidate_id`
- `validation_report_id`
- `delivery_name`
- `package_input_root`
- `handoff_target`
- `package_manifest`
- `integrity_checks`
- `handoff_payload`

### 重命名字段

- `status` -> `delivery_status`

### 降级说明字段

- `boundary_note`

### 排除字段

- 所有发布许可/发布通过语义别名

### compat 禁入字段

- `ContractBundle.status.validated` 不在该桥接点字段集中
