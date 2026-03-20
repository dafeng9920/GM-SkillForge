# GOVERNANCE_INTAKE_FIELD_SCOPE_DECISIONS_v1

## 1. Governance Candidate Intake

### 进入 v1 最小实现的字段
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

### 暂缓字段
- `boundary_note`

### compat 字段
- 无直接 compat 字段进入

### 禁止字段
- `approved`
- `gate_passed`
- `release_ready`
- `published`

## 2. Governance Validation Intake

### 进入 v1 最小实现的字段
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

### 暂缓字段
- `boundary_note`

### compat 字段
- 无直接 compat 字段进入

### 禁止字段
- `governance_validation_passed`
- `audit_passed`
- `review_passed`
- `release_allowed`

## 3. Pre-Packaging Review Intake

### 进入 v1 最小实现的字段
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

### 暂缓字段
- `boundary_note`

### compat 字段
- 无直接 compat 字段进入

### 禁止字段
- `release_permit`
- `publish_approved`
- `released`

