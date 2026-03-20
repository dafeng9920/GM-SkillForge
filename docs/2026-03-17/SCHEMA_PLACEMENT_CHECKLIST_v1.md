# 《5个生产对象 schema 落位清单 v1》

## 1. 目的

本文件用于把 5 层创建流程中的 5 个生产对象，从“文档定义”推进到“可正式落位的 schema 清单”。

本文件当前只定义：

- 对象名
- 推荐 schema 文件名
- 推荐落位目录
- 当前状态
- 与主链路的关系

本文件不进入代码实现。

---

## 2. 5 个生产对象清单

| 对象 | 推荐 schema 文件名 | 推荐落位目录 | 当前状态 | 主链位置 | 备注 |
| --- | --- | --- | --- | --- | --- |
| `IntentDraft` | `intent_draft.schema.json` | `contracts/production/intents/` | 待落位 | 需求输入 -> Intent Draft | 主入口对象 |
| `ContractBundle` | `contract_bundle.schema.json` | `contracts/production/contracts/` | 待落位 | Intent Draft -> Contract Draft | 合同集合对象 |
| `CandidateSkill` | `candidate_skill.schema.json` | `contracts/production/candidates/` | 待落位 | Contract Draft -> Candidate Skill | 候选物本体 |
| `BuildValidationReport` | `build_validation_report.schema.json` | `contracts/production/validation/` | 待落位 | Candidate Skill -> Build Validation | 创建侧最小自检 |
| `DeliveryManifest` | `delivery_manifest.schema.json` | `contracts/production/delivery/` | 待落位 | Build Validation -> Delivery Manifest | 打包层 handoff 输入物 |

---

## 3. 落位原则

### 3.1 只服务当前主链

这 5 个对象只服务于：

`需求输入 → Intent Draft → Contract Draft → Candidate Skill → Build Validation → Delivery Manifest → skill-creator / 打包层`

### 3.2 不得越权承载治理语义

- `BuildValidationReport` 不得承载最终治理通过语义
- `DeliveryManifest` 不得承载 `ReleaseDecision`
- `CandidateSkill` 不得承载正式发布状态

### 3.3 先 schema，后实现

当前优先顺序：

1. schema 文件名和目录归位先定
2. 最小样例文件再定
3. 最后才进入对象代码实现

---

## 4. 每个对象的最小落位要求

### 4.1 `IntentDraft`

最小要求：

- 明确输入需求来源
- 明确 in_scope / out_of_scope
- 明确 inputs / outputs / constraints
- 明确 `required_gates`

配套建议：

- `intent_draft.sample.json`

### 4.2 `ContractBundle`

最小要求：

- `input_schema`
- `output_schema`
- `state_schema`
- `error_schema`
- `trigger_spec`
- `evidence_spec`

配套建议：

- `contract_bundle.sample.json`

### 4.3 `CandidateSkill`

最小要求：

- 候选目录协议
- 生成文件清单
- 入口定义
- 依赖定义
- required changes 列表

配套建议：

- `candidate_skill.sample.json`

### 4.4 `BuildValidationReport`

最小要求：

- 6 个最小检查项
- `handoff_ready`
- missing artifacts
- broken references
- smoke / trace 结果

配套建议：

- `build_validation_report.sample.json`

### 4.5 `DeliveryManifest`

最小要求：

- package input root
- handoff target
- package manifest
- integrity checks
- handoff payload

配套建议：

- `delivery_manifest.sample.json`

---

## 5. 推荐目录骨架

```text
contracts/
  production/
    intents/
      intent_draft.schema.json
      intent_draft.sample.json
    contracts/
      contract_bundle.schema.json
      contract_bundle.sample.json
    candidates/
      candidate_skill.schema.json
      candidate_skill.sample.json
    validation/
      build_validation_report.schema.json
      build_validation_report.sample.json
    delivery/
      delivery_manifest.schema.json
      delivery_manifest.sample.json
```

---

## 6. 当前不做

- 不直接写对象实现代码
- 不直接改现有正式写口
- 不把治理对象混进生产对象
- 不把商用扩展对象提前塞进这 5 个对象

---

## 7. 下一步进入对象落地阶段的前置条件

进入对象落地前，应先同时满足：

1. 正式入口 `00_index.md` 已存在
2. 文档归位方案已明确
3. 冻结/半冻结标记已明确
4. 术语表已明确
5. 4 个 handoff 接口已明确

当前判定：

- 上述前置条件已在文档层成立
- 可以进入“对象落地阶段”的准备态
- 但仍应坚持：先 schema / sample，再代码实现
