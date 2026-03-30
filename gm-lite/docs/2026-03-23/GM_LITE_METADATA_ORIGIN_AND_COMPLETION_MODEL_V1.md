# GM-LITE 元数据生成与动态补完模型 V1

## 1. 核心问题

`BusManager` 不是只负责搬运 JSON。

它承载的是：

- 用户最初意图
- 工程上下文
- 契约与规格
- 反向审计反馈
- 后续重炼依据

因此，GM-LITE 不能接受“某个 GPT-5.4 拍脑袋一次性写出元数据”这种模式。

正确原则是：

> 元数据必须经过意图固化、完整性校验和动态补完，  
> 才有资格进入总线。  

---

## 2. 初始元数据的三权分立

### 2.1 输入 A：原始灵感

这是唯一灵魂来源。

特点：

- 可以很短
- 可以很粗
- 可以只有一句大白话

但它必须被记录为：

- `raw_intent`
- `raw_intent_ref`

并且不得在后续流转中被覆盖。

### 2.2 输入 B：工程上下文 / RAG

这是系统自动注入的上下文层。

包括但不限于：

- 当前代码库事实
- `constitution / rules`
- 依赖与底座能力
- API 手册
- 冻结边界

建议记录为：

- `context_snapshot_ref`
- `context_sources`

### 2.3 输入 C：反向质询

在生成 Spec 之前，指挥层必须先完成一次最小质询。

建议字段：

- `clarification_questions`
- `clarification_answers`
- `clarification_count`

#### 准入规则

若任务复杂度达到中等及以上，但：

- `clarification_count < 3`

则这份元数据包在 BusManager 入口应视为：

- `insufficient_intent_lock`

并直接驳回。

---

## 3. 语义金字塔

总线中的任务元数据不能只有一层描述。

至少要包含三层：

### Level 0: 业务终态

回答：

- 用户最终想解决什么业务问题？

建议字段：

- `goal_statement`

示例：

- “我要在 A 股回测中不因为空值崩掉”

### Level 1: 逻辑骨架

回答：

- 这个任务的核心流程长什么样？

建议字段：

- `logic_skeleton`
- `data_flow_map`
- `error_handling_flow`

### Level 2: 物理约束

回答：

- 这个任务必须满足哪些硬约束？

建议字段：

- `constraints`
- `quality_axes`
- `allowed_side_effects`
- `forbidden_side_effects`

#### 准入规则

如果元数据只有 `Level 2`，而缺失 `Level 0` 或 `Level 1`，则说明：

- AI 已经钻进局部细节
- 丢失了业务终态

此时应判定为：

- `semantic_pyramid_incomplete`

直接打回重写。

---

## 4. 影子意图比对

在把 Spec 交给执行层之前，应允许进行一次影子意图比对。

做法：

- 将已生成的 Spec / Contract 发给异源模型
- 问它：
  - “基于这个 Spec，你认为用户最初想解决什么问题？”

#### 目的

如果影子模型反推出的业务问题，与原始灵感严重偏离，则说明：

- Spec 在生成过程中丢失了核心意图

建议字段：

- `shadow_intent_summary`
- `shadow_intent_match_score`
- `shadow_intent_verdict`

#### 规则

若 `shadow_intent_verdict = MISMATCH`，则不进入执行层，直接回到：

- `spec refinement`

---

## 5. 元数据不是一次性文件，而是活体对象

GM-LITE 中的元数据不能是一锤子买卖。

它必须支持：

- 执行中反馈回流
- 审计中漏洞回流
- 重新精炼再出发

### 5.1 执行中反馈

如果执行层发现：

- API 不可用
- 依赖已失效
- 物理约束不可满足

则不能只在代码层硬改，而必须回流元数据层。

建议字段：

- `execution_feedback`
- `runtime_feasibility_issues`
- `dependency_breakages`

### 5.2 审计中修正

如果 7B / 影子审计发现：

- reverse echo 不对齐
- 结构指纹漂移
- 约束缺失

则优先修正：

- `Spec`
- `Contract`
- `Checklist`

而不是直接靠代码补丁遮掩。

建议字段：

- `audit_feedback`
- `spec_revision_required`
- `revision_reason`

---

## 5.3 物理嵌套而非覆盖写入

`RAW -> ENRICHED -> FROZEN` 不应通过“覆盖旧对象”实现。

更稳的方式是：

> 让后态包裹前态，而不是让后态抹掉前态。  

建议最小结构：

```json
{
  "intent_trace_id": "uuid_xxx",
  "validation_status": "ENRICHED",
  "payload": {
    "raw_origin": {},
    "enriched_spec": {},
    "diff_analysis": []
  }
}
```

其中：

- `raw_origin` = 原始构思原件
- `enriched_spec` = 补完后的工程规格
- `diff_analysis` = 本轮补全过程新增了什么、修正了什么

#### 作用

这样后续任意阶段都可以把：

- `raw_origin`
- `enriched_spec`
- 最终执行产物

拿出来做跨代对照，而不是只剩最后一层结果。

---

## 6. 元数据完整性校验器

在 `BusManager` 入口前，应存在一个只看元数据不看代码的校验器：

- `spec_validator`

它至少要检查：

1. 是否有明确输入输出定义
2. 是否存在业务终态
3. 是否存在逻辑骨架
4. 是否存在物理约束
5. 是否引用了不存在的依赖
6. 质询是否足够
7. 描述复杂度是否足以支撑任务复杂度

### 复杂度校验建议

若任务被标记为复杂任务，但：

- 描述极短
- 缺失关键字段
- 逻辑骨架过于空泛

则应判定为：

- `metadata_under_specified`

并直接打回重写。

---

## 6.1 显式名词提取与名词共振校验

为了防止 AI 在补全过程中把“非标但关键”的业务灵魂磨掉，BusManager 入口前应支持：

- `explicit_noun_extractor`

最小目标：

- 从 `raw_intent` 中提取显式专有名词、关键指标名、策略术语、业务实体名

建议字段：

- `explicit_nouns`

示例：

- `MA5_Cross_MA20`
- `Limit_Up_Probe`
- `A股`
- `NaN`

### 准入规则

在 `RAW -> ENRICHED` 转换时，执行一次：

- `noun_anchor_intersection_check`

如果 `raw_origin` 中的核心显式名词在 `enriched_spec` 中消失，则判定为：

- `core_noun_lost`

并拒绝将状态推进到 `ENRICHED`。

---

## 7. 对 BusManager 的直接约束

后续 `gm_bus_manager_seed_implementation_v1` 至少必须支持以下元数据字段：

- `raw_intent`
- `raw_intent_ref`
- `context_snapshot_ref`
- `context_sources`
- `clarification_questions`
- `clarification_answers`
- `clarification_count`
- `goal_statement`
- `logic_skeleton`
- `data_flow_map`
- `error_handling_flow`
- `constraints`
- `quality_axes`
- `execution_feedback`
- `runtime_feasibility_issues`
- `audit_feedback`
- `spec_revision_required`
- `revision_reason`
- `shadow_intent_summary`
- `shadow_intent_match_score`
- `shadow_intent_verdict`
- `payload.raw_origin`
- `payload.enriched_spec`
- `payload.diff_analysis`
- `explicit_nouns`

---

## 8. 当前结论

本文件正式冻结以下判断：

1. 元数据生成必须经过原始灵感、工程上下文、反向质询三层固化
2. 任务元数据必须满足语义金字塔三层结构
3. 影子意图比对适合作为执行前的偏题预警器
4. 元数据必须支持执行反馈与审计反馈的动态补完
5. `spec_validator` 应作为 BusManager 入口前置校验器
6. GM-LITE 必须通过准入门槛，逼模型把“全局 3/4”吐进不可篡改元数据包
7. `RAW -> ENRICHED` 应采用物理嵌套而非覆盖写入
8. `explicit_nouns` 与名词共振校验是保住业务灵魂的必要机制
