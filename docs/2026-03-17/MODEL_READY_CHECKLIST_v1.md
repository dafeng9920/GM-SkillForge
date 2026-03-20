# MODEL_READY_CHECKLIST_v1

## 1. 目的

本清单用于判断 5 个生产对象是否具备进入“最小实现阶段”的条件。

本清单只服务于：

- `IntentDraft`
- `ContractBundle`
- `CandidateSkill`
- `BuildValidationReport`
- `DeliveryManifest`

本清单不适用于治理对象、发布对象、运行态对象。

---

## 2. 通用检查项

进入最小实现阶段前，每个对象必须同时满足：

1. 已有正式 schema
2. 已有正式 sample
3. 已完成对象模型阶段定义
4. 已明确对象职责
5. 已明确最小必需字段
6. 已明确暂缓字段
7. 已明确兼容字段
8. 已明确风险字段
9. 已明确状态字段是否进入模型
10. 已明确不得承载的治理/发布语义
11. 已明确上游最小引用方式
12. 已明确下游最小引用方式

---

## 3. 5 个对象检查清单

### IntentDraft

- [x] schema 已落位
- [x] sample 已落位
- [x] 主职责明确
- [x] 最小字段范围明确
- [x] 不承载治理语义

### ContractBundle

- [x] schema 已落位
- [x] sample 已落位
- [x] 主职责明确
- [x] 最小字段范围明确
- [x] `validated` 继承性风险已单独标记

### CandidateSkill

- [x] schema 已落位
- [x] sample 已落位
- [x] 主职责明确
- [x] 最小字段范围明确
- [x] 不承载 release 语义

### BuildValidationReport

- [x] schema 已落位
- [x] sample 已落位
- [x] 主职责明确
- [x] 最小字段范围明确
- [x] 已明确不是治理验证

### DeliveryManifest

- [x] schema 已落位
- [x] sample 已落位
- [x] 主职责明确
- [x] 最小字段范围明确
- [x] 已明确不是 Release Permit

---

## 4. handoff 准备检查项

4 个 handoff 在进入最小实现阶段前至少要满足：

1. 输入对象边界明确
2. 输出对象边界明确
3. 触发条件明确
4. 允许写者明确
5. 禁止写者明确
6. 失败返回结构明确
7. 当前是否只做类型占位已明确

---

## 5. 当前结论

当前 5 个生产对象已经满足进入“最小实现阶段”的准备条件。  
但进入实现时，仍需坚持：

- 先最小对象
- 先类型边界
- 先兼容风险收口
- 不引入治理/发布对象
