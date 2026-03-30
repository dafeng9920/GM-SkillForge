# GM-LITE 反向推导核准模型 V1

## 1. 核心问题

当不同模型对同一段代码给出不同“反向推导”时，不能继续依赖自然语言互评。

例如：

- 模型 A 说它是支付回调
- 模型 B 说它是订单状态更新
- 模型 C 说它是外部 API 通信

如果核准仍建立在自由描述上，最终就会退化成玄学。

因此，GM-LITE 的基本原则是：

> 将反向推导从“自然语言描述”升级为“结构化比对与向量化风险信号”。

---

## 2. 四层核准链

### Layer 1: Tag Cloud Matching

不让模型写作文，而让模型从预设标签库中做选择。

标签建议至少分四类：

- `Domain`
- `Action`
- `Risk`
- `Artifact`

示例：

- `#Payment`
- `#Database_Write`
- `#User_Auth`
- `#External_HTTP`
- `#Data_Format`

#### 判定规则

如果上游 Spec 关键标签不出现在反向推导的高优先级标签中，则触发偏题预警。

#### 作用

- 低成本粗筛
- 发现明显语义跑偏

---

### Layer 2: I/O + Side Effect Assertions

这是反向推导核准的主判据。

不问“代码像什么”，而问：

- 输入 A 会得到什么输出？
- 允许哪些副作用？
- 会不会触发禁止副作用？

#### 判定规则

若 Spec 要求：

- 输入 `A` 得到输出 `B`
- 且不得写文件 / 不得访问外部网络

而代码行为被独立判定为：

- 输出 `C`
- 或出现非法副作用

则直接视为逻辑漂移。

#### 作用

- 作为主裁决层
- 优先级高于自然语言解释

---

### Layer 3: Consensus / Disagreement Scoring

通过多个异源模型的反向推导结果形成风险信号。

推荐构成：

- 2 个本地模型
- 1 个云端模型

将其推导结果做 embedding 后，与原始需求向量或 Spec 意图向量比对。

#### 不只看平均值

必须同时看：

- 平均相似度
- 最低分
- 方差
- 是否存在离群模型

#### 判定规则

若出现以下任一情况，触发升级核验：

- 平均值低于阈值
- 任一模型给出极低相似度
- 方差过大，表明分歧严重

#### 作用

- 风险预警
- 分歧检测

不作为唯一真理。

---

### Layer 4: Structural Fingerprint Alignment

最终看代码逻辑骨架是否与上游预期一致。

上游输出：

- `PseudocodeFlow`
- `LogicTree`

下游提取：

- AST
- CFG（可选）
- 关键结构指纹

#### 不要求整棵树完全同形

重点比对：

- 关键条件分支是否存在
- 关键循环 / 重试 / 回滚位置是否正确
- 副作用节点位置是否匹配
- 状态变更顺序是否匹配
- 禁止结构是否出现

#### 作用

- 结构审计
- 发现“功能看似对了但写法已偏离法典”的问题

---

## 3. 总判定原则

GM-LITE 对反向推导的最终判定采用以下优先级：

1. `I/O + Side Effect Assertions`
2. `Structural Fingerprint Alignment`
3. `Tag Cloud Matching`
4. `Consensus / Disagreement Scoring`

这意味着：

- 语义标签用于粗筛
- 分歧评分用于预警
- 行为断言与结构对齐用于主裁决

---

## 4. 反向推导不是自由辩论

反向推导模型在 GM-LITE 中的角色不是法官，而是：

- 偏题探测器
- 风险信号源
- 异源监察哨

因此：

> 监督 GPT-5.4 的，不是另一个模型的情绪或文采，  
> 而是标签、边界、结构与分歧信号。

---

## 5. 与其他制度件的关系

本文件与以下制度件强耦合：

- [GM_LITE_TRUST_ARCHITECTURE_NOT_AI_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_TRUST_ARCHITECTURE_NOT_AI_V1.md)
- [GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md)
- [GM_LITE_11_AXES_OS_STANDARD_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_11_AXES_OS_STANDARD_V1.md)

---

## 6. 当前结论

本文件正式冻结以下共识：

1. 反向推导核准不能建立在自由语言互评上
2. Tag Cloud 适合粗筛，不适合最终裁决
3. I/O 与副作用断言是主判据
4. 共识评分用于预警，不是唯一真理
5. 结构指纹对齐是防止逻辑漂移的关键硬手段
