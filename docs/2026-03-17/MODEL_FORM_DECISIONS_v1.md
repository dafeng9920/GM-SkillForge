# MODEL_FORM_DECISIONS_v1

## 1. 目的

本文件用于决定 5 个生产对象在“最小实现阶段”推荐采用的表示形式。

本文件只做形式决策，不创建任何代码文件。

---

## 2. 形式选择原则

### 优先级

1. 先选最轻、最稳、最不易越权的表示形式
2. 先满足字段边界和类型清晰
3. 不为未来商用扩展提前引入复杂实现

### 当前推荐

- 生产对象优先使用 `pydantic` 进入最小实现阶段
- handoff 优先使用“接口类型占位/typed payload 定义”，不直接落执行逻辑

原因：

- 5 个生产对象本身就是 schema-first 定义
- 进入实现时需要最小字段校验能力
- 需要清晰区分必填、可选、兼容字段
- `pydantic` 更适合承接当前 schema-first 产物

---

## 3. 5 个对象的形式决策

| 对象 | 是否进入最小实现 | 推荐实现形式 | 原因 |
| --- | --- | --- | --- |
| `IntentDraft` | 是 | `pydantic` | 入口对象，字段边界需要明确约束 |
| `ContractBundle` | 是 | `pydantic` | 合同对象字段多、兼容风险高，需要显式约束 |
| `CandidateSkill` | 是 | `pydantic` | 候选物本体，目录与文件清单字段较多 |
| `BuildValidationReport` | 是 | `pydantic` | 自检结果对象，需防止误入治理语义 |
| `DeliveryManifest` | 是 | `pydantic` | handoff 输入物，需要结构稳定 |

---

## 4. handoff 形式决策

| handoff | 当前是否进入最小实现 | 当前形式 |
| --- | --- | --- |
| `candidate handoff` | 是 | 类型占位 + payload 结构定义 |
| `validation handoff` | 是 | 类型占位 + payload 结构定义 |
| `review handoff` | 否（只做准备） | 文档接口定义，不进代码 |
| `release/audit handoff` | 否（只做准备） | 文档接口定义，不进代码 |

---

## 5. 当前不选的形式

### dataclass

当前不优先使用，原因：

- 必填/可选/兼容字段表达不如 `pydantic` 直接
- 当前阶段重点是 schema-first 对齐，不是极简内存对象

### 纯 typed model 占位

当前不作为 5 个主对象的首选，原因：

- 只做 typed 占位会弱化字段约束
- 容易把继承性风险字段带进实现层而不显式处理

---

## 6. 当前结论

当前 5 个生产对象进入最小实现阶段时，推荐统一采用：

- `pydantic` 作为对象表示形式
- handoff 先做类型占位，不做执行逻辑
