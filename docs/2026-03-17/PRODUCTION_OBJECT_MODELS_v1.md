# PRODUCTION_OBJECT_MODELS_v1

## 1. 目的

本文件用于完成 5 个生产对象的**对象模型阶段定义**。

本阶段只定义：

- 每个对象的模型职责
- 字段分组
- 必填/可选/派生字段
- 状态字段解释
- handoff 输入/输出位置
- 明确哪些字段不得带入治理/发布语义

本阶段不做：

- 代码实现
- pydantic/dataclass/model 落地
- schema 改写
- sample 改写

---

## 2. 总模型原则

### 2.1 当前 5 个生产对象

1. `IntentDraft`
2. `ContractBundle`
3. `CandidateSkill`
4. `BuildValidationReport`
5. `DeliveryManifest`

### 2.2 统一字段分组

每个对象按以下分组理解：

- `identity`：标识字段
- `core`：对象主体字段
- `status`：状态字段
- `traceability`：追踪/修订字段
- `handoff`：用于传递到下一层的字段

### 2.3 统一禁止

在对象模型阶段，以下字段不允许被生产对象本体承载：

- `released`
- `gate_result`
- `release_decision`
- `audit_pack`
- `manual_approval`

---

## 3. IntentDraft

### 3.1 模型职责

把自然语言需求压成结构化意图草案，作为生产主链入口对象。

### 3.2 字段分组

#### identity

- `intent_id`

#### core

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

#### status

- `status`

#### traceability

- `created_at`
- `updated_at`
- `revision`

### 3.3 模型级必填字段

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

### 3.4 模型级可选字段

- `intent_name`
- `problem_statement`
- `created_at`
- `updated_at`
- `revision`

### 3.5 状态解释

- `draft`：草案态
- `reviewed`：已人工/系统初审
- `locked`：进入下游 ContractBuilder 的锁定态
- `rejected`：不进入主链

### 3.6 handoff 位置

- 输出给：`ContractBundle`

---

## 4. ContractBundle

### 4.1 模型职责

把 IntentDraft 固化为可编译、可交接的合同集合。

### 4.2 字段分组

#### identity

- `contract_id`
- `intent_id`

#### core

- `summary`
- `version`
- `input_schema`
- `output_schema`
- `state_schema`
- `error_schema`
- `trigger_spec`
- `evidence_spec`
- `required_gates`

#### status

- `status`

### 4.3 模型级必填字段

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

### 4.4 模型级可选字段

- `summary`
- `version`

### 4.5 状态解释

当前 schema 中存在：

- `draft`
- `validated`
- `rejected`
- `frozen`

模型阶段的解释是：

- `draft`：合同草案
- `frozen`：合同已锁定，可进入 CandidateSkill 编译
- `rejected`：合同不进入主链
- `validated`：**继承性状态口径，当前仅保留为 schema 兼容项，不作为生产主链的推荐状态名**

### 4.6 handoff 位置

- 输入来自：`IntentDraft`
- 输出给：`CandidateSkill`

### 4.7 重要说明

`ContractBundle` 是生产对象，不是治理通过对象。  
对象模型阶段明确：

- 不推荐把 `validated` 当成治理通过
- 后续实现层应把它视为“遗留兼容枚举”，而不是主推荐状态

---

## 5. CandidateSkill

### 5.1 模型职责

表示依据合同编译出的候选 skill 本体。

### 5.2 字段分组

#### identity

- `candidate_id`
- `intent_id`
- `contract_id`

#### core

- `candidate_name`
- `skill_root`
- `directory_layout`
- `generated_files`
- `entrypoints`
- `dependencies`
- `required_changes`

#### status

- `status`

### 5.3 模型级必填字段

- `candidate_id`
- `intent_id`
- `contract_id`
- `skill_root`
- `directory_layout`
- `generated_files`
- `status`

### 5.4 模型级可选字段

- `candidate_name`
- `entrypoints`
- `dependencies`
- `required_changes`

### 5.5 状态解释

- `draft_candidate`
- `compiled`
- `compile_failed`
- `handed_to_validation`

说明：

- `handed_to_validation` 是生产线末端 handoff 状态
- 不等于 `validated`

### 5.6 handoff 位置

- 输入来自：`ContractBundle`
- 输出给：`BuildValidationReport`

---

## 6. BuildValidationReport

### 6.1 模型职责

创建侧最小自检报告，用于判断候选物能否进入下游 handoff。

### 6.2 字段分组

#### identity

- `report_id`
- `candidate_id`

#### core

- `checks`
- `summary`
- `missing_artifacts`
- `broken_references`
- `smoke_test_result`
- `trace_result`
- `handoff_ready`

#### status

- `status`

### 6.3 模型级必填字段

- `report_id`
- `candidate_id`
- `checks`
- `summary`
- `handoff_ready`
- `status`

### 6.4 模型级可选字段

- `missing_artifacts`
- `broken_references`
- `smoke_test_result`
- `trace_result`

### 6.5 状态解释

- `verified_candidate`
- `validation_failed`
- `partially_verified`

说明：

- 这里的 `validation_failed` 是**创建侧 build validation 失败**
- 不得解释成治理线验证失败

### 6.6 handoff 位置

- 输入来自：`CandidateSkill`
- 输出给：`DeliveryManifest`

### 6.7 重要说明

`BuildValidationReport` 不得被对象模型误写成：

- `GateResult`
- `GovernanceValidation`
- `ReleaseDecision`

---

## 7. DeliveryManifest

### 7.1 模型职责

定义已通过创建侧最小自检的候选物，如何交给打包层封装。

### 7.2 字段分组

#### identity

- `delivery_id`
- `candidate_id`
- `validation_report_id`

#### core

- `delivery_name`
- `package_input_root`
- `handoff_target`
- `package_manifest`
- `integrity_checks`
- `handoff_payload`

#### status

- `status`

### 7.3 模型级必填字段

- `delivery_id`
- `candidate_id`
- `validation_report_id`
- `package_input_root`
- `handoff_target`
- `package_manifest`
- `status`

### 7.4 模型级可选字段

- `delivery_name`
- `integrity_checks`
- `handoff_payload`

### 7.5 状态解释

- `prepared`
- `handed_off`
- `package_failed`
- `delivered`

说明：

- `delivered` 表示已经交付到打包层/交付层
- 不等于正式 `released`

### 7.6 handoff 位置

- 输入来自：`BuildValidationReport`
- 输出给：`skill-creator / 打包层`

### 7.7 重要说明

`DeliveryManifest` 不得被对象模型误写成：

- `ReleasePermit`
- `ReleaseDecision`
- `AuditPack`

---

## 8. 当前模型阶段结论

### 已完成

- 5 个对象的模型职责定义
- 必填/可选字段分类
- 状态字段解释
- handoff 输入输出位置定义
- 生产对象与治理对象的语义隔离

### 仍待进入实现层处理

- 正式 model 类型实现
- schema 与 model 的一一校验
- 继承性风险字段的代码层收口
