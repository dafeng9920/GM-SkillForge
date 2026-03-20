# PRODUCTION_OBJECT_MODEL_DECISIONS_v1

## 1. 目的

本文件用于记录对象模型阶段的关键决策，避免后续进入实现层时重新漂移。

---

## 2. 决策 1：5 个生产对象的边界不变

固定对象：

1. `IntentDraft`
2. `ContractBundle`
3. `CandidateSkill`
4. `BuildValidationReport`
5. `DeliveryManifest`

结论：

- 当前不拆更多对象
- 当前不把 `RunRecord / ReleaseRecord` 并入这 5 个对象
- 当前不把治理对象并入生产对象

---

## 3. 决策 2：BuildValidationReport 保持创建侧语义

结论：

- `BuildValidationReport` 只表示创建侧最小自检
- 不得偷换成治理验证
- 不得承担 `gate_result`
- 不得承担 `release_decision`

---

## 4. 决策 3：DeliveryManifest 保持打包层 handoff 语义

结论：

- `DeliveryManifest` 只负责交给 `skill-creator / 打包层`
- 不得承担 `Release Permit`
- 不得承担最终发布判断

---

## 5. 决策 4：ContractBundle.status 的继承性风险保留但不扩散

现状：

- 当前 schema 中 `ContractBundle.status` 包含：
  - `draft`
  - `validated`
  - `rejected`
  - `frozen`

决策：

- 本轮不改 schema
- 在对象模型层明确：
  - `validated` 只保留为兼容枚举
  - 当前生产主链推荐状态是：
    - `draft`
    - `frozen`
    - `rejected`

含义：

- 不让 `validated` 在模型层继续扩散成治理语义
- 后续若进入实现层，应优先按推荐状态实现

---

## 6. 决策 5：生产对象不承载正式写口

以下字段不进入 5 个生产对象模型：

- `released`
- `gate_result`
- `release_decision`
- `audit_pack`
- `manual_approval`

这些对象继续归属于治理线。

---

## 7. 决策 6：h andoff 串联固定

生产对象模型串联固定为：

`IntentDraft -> ContractBundle -> CandidateSkill -> BuildValidationReport -> DeliveryManifest`

当前不允许：

- 跳过 `IntentDraft`
- 跳过 `ContractBundle`
- 直接从 `CandidateSkill` 进入发布语义
- 用 `DeliveryManifest` 代替审计/发布层

---

## 8. 决策 7：对象模型阶段完成标准

满足以下条件即可视为对象模型阶段完成：

1. 5 个对象的职责已明确
2. 5 个对象的字段分组已明确
3. 必填/可选字段已明确
4. 状态字段解释已明确
5. handoff 输入输出位置已明确
6. 继承性风险已显式记录
7. 未触碰冻结正文与正式写口

当前判定：

- 上述 7 条已满足
- 对象模型阶段可判定为完成
