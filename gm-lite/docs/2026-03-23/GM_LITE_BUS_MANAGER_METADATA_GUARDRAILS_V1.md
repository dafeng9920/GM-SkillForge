# GM-LITE BusManager 元数据护栏 V1

## 1. 核心目的

本文件用于冻结 `BusManager` 在总线元数据层必须遵守的深层逻辑约束。

目标不是“先把总线跑起来”，而是：

> 让总线在承载意图、执行产物、反向语义回声与多模型审计时，  
> 不丢失逻辑精度，不允许中途漂移，不允许被执行层篡改。  

---

## 2. 总线元数据的五个必须项

### 2.1 意图原件不可变

总线必须保留一份**不可变的意图原件**。

至少应包含：

- `raw_requirement_ref`
- `spec_id`
- `contract_ref`
- `checklist_ref`
- `intent_origin_hash`

#### 规则

- `intent_origin_hash` 只能由指挥层生成
- 执行层、审查层、合规层、影子审计层都不得改写
- 任何中途修改描述、标签、约束、边界的行为，都必须视为：
  - `intent_tampering`

#### 作用

保证 7B / 影子审计 / reverse echo 比对的，永远是最初始、最原汁原味的意图。

---

### 2.2 读写分离

BusManager 必须在物理存储上分离：

- `intent original`
- `execution artifacts`
- `audit artifacts`

#### 最小分离原则

意图原件和执行产物不能共享同一份可写对象。

建议至少逻辑分层为：

- `intent_record`
- `runtime_record`
- `audit_record`

并建议在文件系统层进一步隔离：

- `inbox/raw/`
- `inbox/enriched/`
- `inbox/frozen/`

#### 作用

防止执行层通过“顺手改任务包”来掩盖漂移或 Bug。

#### FROZEN 只读规则

一旦进入 `FROZEN`：

- 原任务包只读
- 执行层不得修改
- 执行反馈写入独立 `runtime_record / runtime_log`

---

### 2.3 投票阵列必须预留

总线必须能承载多个异源审计意见，而不是只接受单一回声结论。

至少应预留：

- `vote_array`

每个投票对象建议包含：

- `auditor_id`
- `auditor_type`
- `model_family`
- `tag_match_score`
- `io_assertion_result`
- `side_effect_assertion_result`
- `reverse_inference_score`
- `structural_alignment_score`
- `verdict`
- `created_at`

#### 作用

未来如果同时存在：

- 审计员 A：`MATCH`
- 审计员 B：`MISMATCH`

总线必须能承载这种碰撞，而不是粗暴覆盖。

---

### 2.4 意图纯化

发给影子审计员 / reverse echo 的对比基准，必须做一次**意图纯化**。

也就是说，审计输入不得夹带：

- 具体实现提示
- 执行层自我解释
- 过程性修补描述
- 带有引导意味的代码注释

应该尽量只保留：

- 目标
- 输入输出边界
- 副作用约束
- 关键标签

建议字段：

- `purified_intent_payload`

#### 作用

防止审计模型顺着执行逻辑去“圆谎”，而不是真正从结果逆推出目标。

---

### 2.5 幽灵追踪位

总线应支持一个只用于完整性追踪的隐形探针字段：

- `ghost_trace`

它不参与业务逻辑，也不参与用户可见功能。

#### 作用

当任务包在总线上流转一圈后，如果 `ghost_trace` 丢失、变形或被覆盖，说明存在：

- 逻辑损耗
- 非法重写
- 中间层对象覆盖问题

这是高并发工业总线的大忌。

---

## 3. 状态模型必须双层化

BusManager 不得把所有状态塞进一个字符串字段。

### 3.1 生命周期状态

建议字段：

- `lifecycle_status`

最小候选值：

- `PENDING`
- `IN_PROGRESS`
- `WRITEBACK_DONE`
- `GATE_READY`
- `BLOCKED`
- `FAILED`

### 3.2 分级门禁状态

建议字段：

- `gate_levels`

最小结构：

```json
{
  "L1_STATIC": "PENDING",
  "L2_ECHO": "PENDING",
  "L3_STRESS": "PENDING"
}
```

最小候选值：

- `PENDING`
- `PASSED`
- `FAILED`
- `SKIPPED`

#### 作用

- 生命周期用于描述任务在哪个阶段
- 门禁状态用于描述各层火控是否通过

两者混用会导致后续 console、dispatch assist、sample flow 全部变乱。

---

## 4. 反向语义回声的最小元数据槽位

BusManager 至少应预留以下字段：

- `task_id`
- `spec_id`
- `dispatch_id`
- `attempt_id`
- `origin_model`
- `raw_requirement_ref`
- `contract_ref`
- `checklist_ref`
- `intent_origin_hash`
- `tag_cloud`
- `io_assertions`
- `allowed_side_effects`
- `forbidden_side_effects`
- `pseudocode_flow_ref`
- `logic_tree_ref`
- `purified_intent_payload`
- `vote_array`
- `reverse_inference_summary`
- `reverse_inference_score`
- `disagreement_score`
- `structural_alignment_score`
- `verdict`
- `ghost_trace`

---

## 5. 当前实现前置约束

在 `gm_bus_manager_seed_implementation_v1` 中，至少必须做到：

1. 定义上述元数据字段的最小模型
2. 明确哪些字段只读
3. 明确哪些字段只能由审计层写入
4. 明确意图原件与执行产物的分层存储
5. 明确双层状态模型

本轮仍不要求：

- 完整 watcher
- 自动发送
- direct-connect
- timeout / retry runtime

---

## 6. 当前结论

本文件正式冻结以下判断：

1. `intent_origin_hash` 必须存在，且不可被执行层篡改
2. BusManager 必须读写分离意图原件与执行产物
3. `vote_array` 是异源审计的必要预留位
4. `purified_intent_payload` 是 reverse echo 成立的前提
5. `ghost_trace` 是完整性探针，适合高并发总线自检
6. 状态模型必须采用 `lifecycle_status + gate_levels` 的双层设计
