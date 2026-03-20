# contracts/production/ 对象落位报告 v1

## 1. 本轮动作总结

本轮已完成：

- 创建 `contracts/production/` 最小正式目录骨架
- 在正式草案区建立 5 组对象的正式落位路径
- 将 5 组 schema 文件从 `docs/2026-03-17/production-schema-skeletons-v1/` 复制到正式草案区
- 将 5 组 sample 文件从 `docs/2026-03-17/production-schema-skeletons-v1/` 复制到正式草案区
- 完成迁移后的一致性检查

本轮严格保持为**非实现阶段**：

- 未进入代码实现
- 未创建 model / dataclass / pydantic
- 未编写 sample 校验脚本
- 未实现 handoff 代码
- 未落 `RunRecord / ReleaseRecord`

说明：

- 本轮采用“复制落位”而不是“删除源骨架包”，以保留 docs 骨架包作为来源归档
- 因此当前存在：
  - `docs` 中的骨架包
  - `contracts/production/` 中的正式草案区

---

## 2. 正式落位路径

### IntentDraft

- [intent_draft.schema.json](/d:/GM-SkillForge/contracts/production/intent/intent_draft.schema.json)
- [intent_draft.sample.json](/d:/GM-SkillForge/contracts/production/intent/intent_draft.sample.json)

### ContractBundle

- [contract_bundle.schema.json](/d:/GM-SkillForge/contracts/production/contract/contract_bundle.schema.json)
- [contract_bundle.sample.json](/d:/GM-SkillForge/contracts/production/contract/contract_bundle.sample.json)

### CandidateSkill

- [candidate_skill.schema.json](/d:/GM-SkillForge/contracts/production/candidate/candidate_skill.schema.json)
- [candidate_skill.sample.json](/d:/GM-SkillForge/contracts/production/candidate/candidate_skill.sample.json)

### BuildValidationReport

- [build_validation_report.schema.json](/d:/GM-SkillForge/contracts/production/validation/build_validation_report.schema.json)
- [build_validation_report.sample.json](/d:/GM-SkillForge/contracts/production/validation/build_validation_report.sample.json)

### DeliveryManifest

- [delivery_manifest.schema.json](/d:/GM-SkillForge/contracts/production/delivery/delivery_manifest.schema.json)
- [delivery_manifest.sample.json](/d:/GM-SkillForge/contracts/production/delivery/delivery_manifest.sample.json)

---

## 3. 迁移一致性检查

### 3.1 命名一致性

检查结果：

- `IntentDraft` -> `intent_draft.schema.json / intent_draft.sample.json` ✅
- `ContractBundle` -> `contract_bundle.schema.json / contract_bundle.sample.json` ✅
- `CandidateSkill` -> `candidate_skill.schema.json / candidate_skill.sample.json` ✅
- `BuildValidationReport` -> `build_validation_report.schema.json / build_validation_report.sample.json` ✅
- `DeliveryManifest` -> `delivery_manifest.schema.json / delivery_manifest.sample.json` ✅

结论：

- 文件命名口径统一为 `snake_case.schema.json` / `snake_case.sample.json`
- 未出现迁移中改名或语义漂移

### 3.2 sample/schema 对齐

检查结果：

- 5 组对象均存在 schema + sample 成对文件 ✅
- 5 组 schema 标题与对象名一致 ✅
- 5 组 sample 均覆盖当前 schema 的最小必填字段 ✅

结论：

- sample/schema 对齐成立

### 3.3 主链串联性

当前 5 对象仍可按以下顺序串联：

`Requirement -> IntentDraft -> ContractBundle -> CandidateSkill -> BuildValidationReport -> DeliveryManifest`

检查结果：

- `IntentDraft` 保持主入口对象语义 ✅
- `ContractBundle` 保持合同集合对象语义 ✅
- `CandidateSkill` 保持候选物本体语义 ✅
- `BuildValidationReport` 保持创建侧最小自检语义 ✅
- `DeliveryManifest` 保持打包层 handoff 输入物语义 ✅

结论：

- 主链串联未断裂
- 未出现跳步或替换关系

### 3.4 路径引用完整性

检查结果：

- 10 个正式文件全部已落位 ✅
- 5 组对象路径清晰，无缺文件 ✅
- 当前 schema/sample 内部无外部路径引用断裂问题 ✅

结论：

- 本轮路径落位完整

### 3.5 是否混入治理/发布语义

检查结果：

- 未新增 `released` ✅
- 未新增 `gate_result` ✅
- 未新增 `ReleaseDecision` ✅
- 未新增 `AuditPack` ✅
- `BuildValidationReport` 未被改写成治理审计对象 ✅
- `DeliveryManifest` 未被改写成 `Release Permit` ✅

继承性风险记录：

- [contract_bundle.schema.json](/d:/GM-SkillForge/contracts/production/contract/contract_bundle.schema.json) 当前仍包含 `status.enum = ["draft", "validated", "rejected", "frozen"]`
- 这不是本轮迁移新增字段，而是源骨架自带语义
- 本轮未改该语义
- 该项应在后续“对象模型阶段”单独复核其是否与当前主链完全一致

结论：

- 本轮未新增治理/发布语义
- 但 `ContractBundle.status` 的 `validated` 口径应作为后续复核项保留

---

## 4. 本轮未触碰的边界

本轮明确未触碰：

- 冻结文档正文未改
- 主链路未改
- 正式写口未改
- 审计归属未改
- `skill-creator` 角色边界未改
- 未进入 model / 实现层

本轮也未做：

- handoff 代码实现
- schema 语义扩展
- sample 语义扩展
- 商用扩展层并入当前主线

---

## 5. 当前对象落位阶段完成度

### 是否已完成 5 个生产对象的正式草案落位

结论：**是。**

当前已完成：

- 正式目录骨架
- 10 个文件正式落位
- 命名一致性检查
- sample/schema 对齐检查
- 主链串联检查

### 是否具备进入“对象模型阶段”的前提

结论：**是。**

前提已满足：

- 正式入口存在
- 归位方案存在
- 冻结/只读说明存在
- 术语表存在
- handoff 接口定义存在
- 5 对象 schema/sample 已正式落位

---

## 6. 下一步建议

下一步只建议进入**对象模型阶段**，最小动作是：

1. 对这 5 个对象逐个补“字段级模型约束复核”
2. 明确哪些字段将进入正式 model
3. 先定义对象模型草案，再决定是否进入实现层

当前不建议直接跳到：

- 代码实现
- handoff 逻辑实现
- 运行记录对象实现
- 治理对象实现
