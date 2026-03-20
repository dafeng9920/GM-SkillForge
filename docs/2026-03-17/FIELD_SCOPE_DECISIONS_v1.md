# FIELD_SCOPE_DECISIONS_v1

## 1. 目的

本文件用于明确 5 个生产对象在 v1 模型中的字段进入范围。

字段分为三类：

- `进入 v1 模型`
- `暂缓`
- `兼容字段`

---

## 2. IntentDraft

### 进入 v1 模型

- `intent_id`
- `intent_name`
- `summary`
- `goal`
- `problem_statement`
- `in_scope`
- `out_of_scope`
- `inputs`
- `outputs`
- `constraints`
- `required_gates`
- `status`

### 暂缓

- 无额外扩展字段

### 兼容字段

- `created_at`
- `updated_at`
- `revision`

### 风险字段

- 无明显继承性风险字段

---

## 3. ContractBundle

### 进入 v1 模型

- `contract_id`
- `intent_id`
- `summary`
- `version`
- `input_schema`
- `output_schema`
- `state_schema`
- `error_schema`
- `trigger_spec`
- `evidence_spec`
- `required_gates`
- `status`

### 暂缓

- 无额外扩展字段

### 兼容字段

- `status = validated`

### 风险字段

- `status`

说明：

- `validated` 必须保留兼容语义，不得解释为治理 validated

---

## 4. CandidateSkill

### 进入 v1 模型

- `candidate_id`
- `intent_id`
- `contract_id`
- `candidate_name`
- `skill_root`
- `directory_layout`
- `generated_files`
- `entrypoints`
- `dependencies`
- `required_changes`
- `status`

### 暂缓

- 无额外扩展字段

### 兼容字段

- 无

### 风险字段

- `status`

说明：

- `handed_to_validation` 只解释为生产态 handoff

---

## 5. BuildValidationReport

### 进入 v1 模型

- `report_id`
- `candidate_id`
- `checks`
- `summary`
- `missing_artifacts`
- `broken_references`
- `smoke_test_result`
- `trace_result`
- `handoff_ready`
- `status`

### 暂缓

- 更细颗粒度 trace 子结构

### 兼容字段

- 无

### 风险字段

- `status`

说明：

- `validation_failed` 只解释为 build validation 失败

---

## 6. DeliveryManifest

### 进入 v1 模型

- `delivery_id`
- `candidate_id`
- `validation_report_id`
- `delivery_name`
- `package_input_root`
- `handoff_target`
- `package_manifest`
- `integrity_checks`
- `handoff_payload`
- `status`

### 暂缓

- 更细颗粒度 packaging constraints

### 兼容字段

- 无

### 风险字段

- `status`

说明：

- `delivered` 只解释为交付到打包层

---

## 7. 严禁承载的语义

以下语义对 5 个对象全部禁止进入 v1 模型：

- `released`
- `gate_result`
- `release_decision`
- `audit_pack`
- `manual_approval`
- `publish_permit`
