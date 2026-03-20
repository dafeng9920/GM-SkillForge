# 最小校验阶段报告 v1

## 1. 本轮动作总结

- 校验了 5 个生产对象：
  - `IntentDraft`
  - `ContractBundle`
  - `CandidateSkill`
  - `BuildValidationReport`
  - `DeliveryManifest`
- 校验了 2 个 handoff 类型占位：
  - `candidate handoff`
  - `validation handoff`
- 严格保持在最小校验阶段：
  - 未进入业务测试
  - 未进入 handoff 执行测试
  - 未进入治理校验
  - 未进入发布校验

## 2. model / schema 一致性检查结果

### IntentDraft

- 一致项：
  - schema 中的 v1 字段均在模型中落位
  - `inputs / outputs / constraints` 的嵌套结构已由最小子模型承接
  - `status` 枚举与 schema 一致
  - `created_at / updated_at / revision` 已按兼容字段进入模型
- 不一致项：
  - 无实质不一致
- 风险等级：
  - `LOW`
- 最小修正建议：
  - 无必须修正项

### ContractBundle

- 一致项：
  - schema 中的 v1 字段均在模型中落位
  - `input_schema / output_schema / state_schema / error_schema / trigger_spec / evidence_spec` 均以宽对象形式承接，和 schema 兼容
  - `status` 枚举与 schema 一致
- 不一致项：
  - 无结构性缺口
- 风险等级：
  - `MEDIUM`
- 最小修正建议：
  - 当前只需保留现有 compat 注释，无需改字段

### CandidateSkill

- 一致项：
  - schema 中的 v1 字段均在模型中落位
  - `generated_files` 结构与 schema 内联对象一致
  - `status` 枚举与 schema 一致
  - `entrypoints / dependencies / required_changes` 与 sample 兼容
- 不一致项：
  - 无结构性缺口
- 风险等级：
  - `LOW`
- 最小修正建议：
  - 无必须修正项

### BuildValidationReport

- 一致项：
  - schema 中的 v1 字段均在模型中落位
  - `checks` 子对象与 schema 一致
  - `status` 枚举与 schema 一致
  - `summary / smoke_test_result / trace_result` 以宽对象承接，和 schema/sample 兼容
- 不一致项：
  - 无结构性缺口
- 风险等级：
  - `LOW`
- 最小修正建议：
  - 无必须修正项

### DeliveryManifest

- 一致项：
  - schema 中的 v1 字段均在模型中落位
  - `handoff_target` 枚举与 schema 一致
  - `status` 枚举与 schema 一致
  - `package_manifest / handoff_payload / integrity_checks` 与 sample 兼容
- 不一致项：
  - 无结构性缺口
- 风险等级：
  - `LOW`
- 最小修正建议：
  - 建议在后续轻量注释补强阶段继续强调 `delivered != released`

## 3. model / sample 一致性检查结果

### IntentDraft

- sample 可表达性：
  - 可完整表达
- 字段覆盖情况：
  - sample 中所有关键字段均被模型覆盖
- compat 字段处理情况：
  - `created_at / updated_at / revision` 已正确作为兼容元数据处理

### ContractBundle

- sample 可表达性：
  - 可完整表达
- 字段覆盖情况：
  - sample 中所有关键字段均被模型覆盖
- compat 字段处理情况：
  - sample 当前使用 `status=draft`
  - 模型仍保留 `validated` 兼容枚举，但未把它扩成治理语义

### CandidateSkill

- sample 可表达性：
  - 可完整表达
- 字段覆盖情况：
  - `directory_layout / generated_files / entrypoints / dependencies / required_changes` 均被覆盖
- compat 字段处理情况：
  - 无 compat 字段

### BuildValidationReport

- sample 可表达性：
  - 可完整表达
- 字段覆盖情况：
  - `checks / summary / missing_artifacts / broken_references / smoke_test_result / trace_result / handoff_ready / status` 均被覆盖
- compat 字段处理情况：
  - 无 compat 字段

### DeliveryManifest

- sample 可表达性：
  - 可完整表达
- 字段覆盖情况：
  - `package_manifest / integrity_checks / handoff_payload` 均被覆盖
- compat 字段处理情况：
  - 无 compat 字段

## 4. 主链串联性检查结果

### IntentDraft → ContractBundle

- 成立
- 对接字段：
  - `IntentDraft.intent_id`
  - `ContractBundle.intent_id`

### ContractBundle → CandidateSkill

- 成立
- 对接字段：
  - `ContractBundle.contract_id`
  - `CandidateSkill.contract_id`
  - `CandidateSkill.intent_id`

### CandidateSkill → BuildValidationReport

- 成立
- 对接字段：
  - `CandidateSkill.candidate_id`
  - `BuildValidationReport.candidate_id`

### BuildValidationReport → DeliveryManifest

- 成立
- 对接字段：
  - `BuildValidationReport.report_id`
  - `DeliveryManifest.validation_report_id`
  - `DeliveryManifest.candidate_id`

### 总体结论

- 当前主链：
  - `Requirement -> IntentDraft -> ContractBundle -> CandidateSkill -> BuildValidationReport -> DeliveryManifest`
- 仍可按最小引用字段正确串联

## 5. handoff 类型占位校验结果

### candidate handoff

- 输入对象清晰：
  - `IntentDraft`
  - `ContractBundle`
  - `CandidateSkill`
- 输出对象清晰：
  - `candidate_id`
  - `accepted`
  - `next_stage=build_validation`
- 错误对象最小闭合：
  - `code / message / retriable`
- 越界检查：
  - 未引用治理对象
  - 未引用发布对象
- 当前状态：
  - 仍然只是类型占位，不是执行层代码

### validation handoff

- 输入对象清晰：
  - `CandidateSkill`
  - `ContractBundle`
- 输出对象清晰：
  - `BuildValidationReport`
  - `accepted`
  - `next_stage=delivery_manifest`
- 错误对象最小闭合：
  - `code / message / retriable`
- 越界检查：
  - 未引用治理对象
  - 未引用发布对象
- 当前状态：
  - 仍然只是类型占位，不是执行层代码

## 6. `validated` 兼容字段专项检查

- 当前状态：
  - `ContractBundle.status.validated` 仍保留在模型中
- 风险：
  - 存在被误读为治理 `validated` 的继承性风险
- 是否仍受控：
  - **是**
  - 受控依据：
    - 类注释已明确声明 compatibility only
    - `Field(description=...)` 已明确写明 not governance validated
    - 当前 handoff 类型占位未使用该值承载治理判断
- 是否需要最小注释补强：
  - **可选**
  - 当前已足够进入下一阶段；若后续需要，可在结构固化阶段补一条模块级注释

## 7. 本轮未触碰的边界

- 冻结文档正文未改
- 主链路未改
- 正式写口未改
- 审计归属未改
- `skill-creator` 角色边界未改
- 未进入业务逻辑
- 未新增治理对象
- 未新增发布对象
- 未进入 handoff 执行实现

## 8. 当前最小校验阶段完成度

- 是否已完成 5 个生产对象的最小一致性校验：
  - **是**
- 是否具备进入“最小修正阶段”或等价下一阶段的条件：
  - **是**

## 9. 下一步建议

- 当前只有低风险继承性语义提示，没有结构阻断。
- 下一步建议进入：
  - **更轻量的结构固化 / 注释补强阶段**
