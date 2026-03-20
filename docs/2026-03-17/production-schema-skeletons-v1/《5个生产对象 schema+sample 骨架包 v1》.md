# 《5个生产对象 schema+sample 骨架包 v1》

## 1. 目的

本骨架包用于把当前 5 层创建流程中的 5 个生产对象，先落成：

- 最小 `schema`
- 最小 `sample`

当前阶段只做对象骨架，不做：

- 代码实现
- 正式目录迁移
- 正式写口改动
- 治理对象混入

---

## 2. 当前包含对象

1. `IntentDraft`
2. `ContractBundle`
3. `CandidateSkill`
4. `BuildValidationReport`
5. `DeliveryManifest`

---

## 3. 文件清单

### Intent

- `intent_draft.schema.json`
- `intent_draft.sample.json`

### Contract

- `contract_bundle.schema.json`
- `contract_bundle.sample.json`

### Candidate

- `candidate_skill.schema.json`
- `candidate_skill.sample.json`

### Build Validation

- `build_validation_report.schema.json`
- `build_validation_report.sample.json`

### Delivery

- `delivery_manifest.schema.json`
- `delivery_manifest.sample.json`

---

## 4. 使用纪律

- 这些文件当前属于“对象落地前半步”
- 可作为后续 `contracts/production/` 的正式迁移输入
- 不等于已经进入代码层
- 不等于已经进入治理线

---

## 5. 主链位置

这些对象只服务于当前主链：

`需求输入 → Intent Draft → Contract Draft → Candidate Skill → Build Validation → Delivery Manifest → skill-creator / 打包层`

不得借本骨架包：

- 扩治理范围
- 改主链顺序
- 给 `skill-creator` 增权
- 让 `BuildValidationReport` 冒充治理通过
