# 《contracts/production/ 迁移与对齐包 v1》

## 1. 目的

本文件用于把当前 `production-schema-skeletons-v1/` 中的 5 组对象骨架，
进一步压成一份可执行的 `contracts/production/` 正式迁移与对齐包。

本文件只包含：

1. 5 组 schema 正式落位路径
2. 5 组 sample 正式落位路径
3. 命名一致性检查
4. sample/schema 对齐检查
5. 5 对象 handoff 串联检查结果

本文件不进入：

- 代码实现
- 冻结文档正文修改
- 正式写口改动
- 主链路顺序调整

---

## 2. 5 组 schema 正式落位路径

| 对象 | 当前骨架文件 | 正式落位路径 |
| --- | --- | --- |
| `IntentDraft` | `production-schema-skeletons-v1/intent_draft.schema.json` | `contracts/production/intents/intent_draft.schema.json` |
| `ContractBundle` | `production-schema-skeletons-v1/contract_bundle.schema.json` | `contracts/production/contracts/contract_bundle.schema.json` |
| `CandidateSkill` | `production-schema-skeletons-v1/candidate_skill.schema.json` | `contracts/production/candidates/candidate_skill.schema.json` |
| `BuildValidationReport` | `production-schema-skeletons-v1/build_validation_report.schema.json` | `contracts/production/validation/build_validation_report.schema.json` |
| `DeliveryManifest` | `production-schema-skeletons-v1/delivery_manifest.schema.json` | `contracts/production/delivery/delivery_manifest.schema.json` |

---

## 3. 5 组 sample 正式落位路径

| 对象 | 当前骨架文件 | 正式落位路径 |
| --- | --- | --- |
| `IntentDraft` | `production-schema-skeletons-v1/intent_draft.sample.json` | `contracts/production/intents/intent_draft.sample.json` |
| `ContractBundle` | `production-schema-skeletons-v1/contract_bundle.sample.json` | `contracts/production/contracts/contract_bundle.sample.json` |
| `CandidateSkill` | `production-schema-skeletons-v1/candidate_skill.sample.json` | `contracts/production/candidates/candidate_skill.sample.json` |
| `BuildValidationReport` | `production-schema-skeletons-v1/build_validation_report.sample.json` | `contracts/production/validation/build_validation_report.sample.json` |
| `DeliveryManifest` | `production-schema-skeletons-v1/delivery_manifest.sample.json` | `contracts/production/delivery/delivery_manifest.sample.json` |

---

## 4. 命名一致性检查

### 4.1 文件命名口径

统一口径：

- schema 文件：`snake_case.schema.json`
- sample 文件：`snake_case.sample.json`

### 4.2 5 组对象检查结果

| 对象 | schema 文件名 | sample 文件名 | 是否一致 | 备注 |
| --- | --- | --- | --- | --- |
| `IntentDraft` | `intent_draft.schema.json` | `intent_draft.sample.json` | ✅ | 一致 |
| `ContractBundle` | `contract_bundle.schema.json` | `contract_bundle.sample.json` | ✅ | 一致 |
| `CandidateSkill` | `candidate_skill.schema.json` | `candidate_skill.sample.json` | ✅ | 一致 |
| `BuildValidationReport` | `build_validation_report.schema.json` | `build_validation_report.sample.json` | ✅ | 一致 |
| `DeliveryManifest` | `delivery_manifest.schema.json` | `delivery_manifest.sample.json` | ✅ | 一致 |

### 4.3 对象名与文件名映射检查

| 对象名 | 文件前缀 | 检查结果 |
| --- | --- | --- |
| `IntentDraft` | `intent_draft` | ✅ |
| `ContractBundle` | `contract_bundle` | ✅ |
| `CandidateSkill` | `candidate_skill` | ✅ |
| `BuildValidationReport` | `build_validation_report` | ✅ |
| `DeliveryManifest` | `delivery_manifest` | ✅ |

结论：

- 当前 5 组对象的文件命名可以直接迁移到 `contracts/production/`
- 不需要额外命名纠偏

---

## 5. sample/schema 对齐检查

### 5.1 检查维度

本轮只检查最小一致性：

1. sample 是否覆盖 schema 的必填字段
2. sample 顶层对象名与 schema 标题是否一致
3. sample 是否误带治理线正式语义
4. sample 是否仍停留在当前主链范围内

### 5.2 检查结果

| 对象 | 必填字段覆盖 | 标题/对象对齐 | 无越权语义 | 主链范围正确 | 结果 |
| --- | --- | --- | --- | --- | --- |
| `IntentDraft` | ✅ | ✅ | ✅ | ✅ | 通过 |
| `ContractBundle` | ✅ | ✅ | ✅ | ✅ | 通过 |
| `CandidateSkill` | ✅ | ✅ | ✅ | ✅ | 通过 |
| `BuildValidationReport` | ✅ | ✅ | ✅ | ✅ | 通过 |
| `DeliveryManifest` | ✅ | ✅ | ✅ | ✅ | 通过 |

### 5.3 特别检查

#### `BuildValidationReport`

- 当前 sample 未把 `BuildValidationReport` 写成治理通过对象
- 未出现 `released / validated / gate_result`
- 结论：✅ 通过

#### `DeliveryManifest`

- 当前 sample 未承载 `ReleaseDecision`
- 仍停在打包层 handoff 输入物语义
- 结论：✅ 通过

---

## 6. 5 对象 handoff 串联检查结果

### 6.1 当前串联链

`IntentDraft -> ContractBundle -> CandidateSkill -> BuildValidationReport -> DeliveryManifest`

### 6.2 串联检查表

| 上游对象 | 下游对象 | 串联依据 | 是否成立 | 风险 |
| --- | --- | --- | --- | --- |
| `IntentDraft` | `ContractBundle` | `intent_id` 驱动合同生成 | ✅ | 无 |
| `ContractBundle` | `CandidateSkill` | `contract_id` 驱动候选物编译 | ✅ | 无 |
| `CandidateSkill` | `BuildValidationReport` | `candidate_id` 驱动最小自检 | ✅ | 无 |
| `BuildValidationReport` | `DeliveryManifest` | `validation_report_id + handoff_ready` 驱动交付准备 | ✅ | 无 |

### 6.3 handoff 角色边界检查

| handoff | 生成线结束点 | 下游接管点 | 当前是否与正式 handoff 文档一致 |
| --- | --- | --- | --- |
| `candidate handoff` | `CandidateSkill + BuildValidationReport` | 治理线 candidate 接收 | ✅ |
| `validation handoff` | candidate 已交付 | `validator` | ✅ |
| `review handoff` | validation/gate 结束后 | `admin-review-console` | ✅ |
| `release/audit handoff` | review 结束或无需 review | `release-manager / evidence-collector` | ✅ |

### 6.4 串联结论

- 5 对象自身链路已经能形成稳定的生产侧对象序列
- 当前 handoff 串联与 [HANDOFF_INTERFACES_v1.md](/d:/GM-SkillForge/docs/2026-03-17/HANDOFF_INTERFACES_v1.md) 一致
- 目前没有发现：
  - 主链跳步
  - 治理语义提前混入
  - 打包层越权

---

## 7. 最终迁移判定

### 当前可直接推进的内容

- 5 组 schema 的正式目录落位
- 5 组 sample 的正式目录落位
- 后续 schema/sample 校验脚本编写

### 当前仍不进入的内容

- 对象代码实现
- 正式写口收口到代码层
- 治理对象实现
- 目录实体迁移以外的架构重构

### 最终结论

`contracts/production/` 的 5 组对象迁移条件已成立。

下一步若继续推进，最小动作应是：

1. 实体创建 `contracts/production/...` 目录骨架
2. 将这 5 组 schema/sample 从 `docs` 骨架包迁入正式 contracts 草案区
3. 补最小 schema/sample 校验说明
