# GM-LITE 元数据入口防火墙 V1

## 1. 核心目的

本文件定义 `BusManager` 在接收“网页版构思 -> 生产级元数据”转换结果时，必须执行的三道逻辑防火墙。

目标是：

> 防止全局感丢失、关键语义蒸发、异常处理缺位、上下游耦合被忽略。  

这三道防火墙属于：

- 代码生成前拦截
- 昂贵执行前拦截
- `GLM` 齐射前最后一道元数据准入门

---

## 2. 第一防火墙：元数据指纹完整性审计

### 2.1 原则

不要只看描述长短，要看关键信息是否还活着。

当用户原始构思进入系统后，某些核心名词、关键约束、业务实体不能在 Spec 中凭空蒸发。

### 2.2 最小实现思路

进行一次极简的：

- `keyword resonance check`

对比对象：

- `raw_intent`
- `goal_statement`
- `generated_spec_summary`

### 2.3 规则

若原始构思中的核心名词在 Spec 中缺失，则判定为：

- `critical_semantic_loss`

示例：

- 原始构思提到：
  - `A股`
  - `NaN`
  - `涨停`
- 但 Spec 中完全没有：
  - 缺失值处理
  - 市场边界
  - 关键异常场景

则总线入口必须拦截。

### 2.4 建议字段

- `semantic_resonance_keywords`
- `semantic_resonance_score`
- `semantic_loss_alerts`

---

## 3. 第二防火墙：反向约束质询

### 3.1 原则

在任务正式进入执行队列前，应让一个“不知道原始构思全文”的影子角色，仅凭 Spec 判断：

- 遇到异常场景时系统是否知道如何自保

这是一种：

- `blindfold test`

### 3.2 质询问题样例

影子审计员只看 Spec，然后回答：

- 如果运行环境断网怎么办？
- 如果数据全是空值怎么办？
- 如果字段对不上怎么办？
- 如果依赖接口失效怎么办？

### 3.3 判定规则

如果影子审计员指出：

- Spec 未覆盖这些异常与防御性边界

则应判定为：

- `defensive_global_missing`

并打回重写，而不是交给执行层“边写边补”。

### 3.4 建议字段

- `blindfold_questions`
- `blindfold_answers`
- `blindfold_gap_findings`
- `blindfold_verdict`

---

## 4. 第三防火墙：全局上下文锚点

### 4.1 原则

AI 容易陷入局部最优，因此总线必须强迫它声明：

- 这个任务影响谁
- 依赖谁
- 会改变哪些全局链路

### 4.2 必填字段

BusManager 元数据中必须预留：

- `upstream_dependencies`
- `global_impact`

### 4.3 作用

即便当前任务只是一个局部组件，例如“均线计算”，它也必须说明：

- 会不会影响后续策略回测
- 会不会影响数据清洗层
- 会不会影响信号计算层

### 4.4 判定规则

如果任务具有明显上下游关系，但：

- `upstream_dependencies` 为空
- `global_impact` 为空

则应判定为：

- `global_anchor_missing`

并在入口处直接退回。

---

## 5. Validation Status：元数据成熟度状态

为了避免残缺元数据过早进入昂贵执行层，任务包必须具备一个显式状态字段：

- `validation_status`

建议最小候选值：

- `RAW`
- `ENRICHED`
- `FROZEN`

### 5.1 `RAW`

表示：

- 仅有网页端 / 对话端搬来的原始输入
- 还未经过意图固化与防火墙检查

### 5.2 `ENRICHED`

表示：

- 已经注入上下文
- 已完成质询
- 已过入口防火墙初检
- 但还未冻结为可执行法典

### 5.3 `FROZEN`

表示：

- 关键信息未丢失
- 异常与边界已补全
- 上下游影响已声明
- 准备交给执行层

### 5.4 准入门槛

只有：

- `validation_status = FROZEN`

的任务包，才允许触发昂贵的执行齐射。

---

## 6. RAW 历史镜像与不可删名词规则

### 6.1 不得覆盖 RAW 原件

`RAW -> ENRICHED -> FROZEN` 的推进，不得以覆盖 RAW 原件为代价。

BusManager 入口应至少保留：

- 一份当前任务包的主记录
- 一份 `RAW` 历史镜像

建议逻辑层命名：

- `raw_snapshot`
- `history_log`

若未来落到文件系统层，可再映射到：

- `.history/`
- `archive/`
- `raw/`

但当前制度层先冻结原则：

> RAW 原件必须可追溯、可回看、不可被补完流程静默覆盖。  

### 6.2 禁止删除 RAW 中的显式名词

在 `RAW -> ENRICHED` 的补全过程中，系统必须防止 AI 把“非标但关键”的用户表达抹掉。

因此入口防火墙必须包含一条规则：

- `no_explicit_noun_deletion`

也就是说：

- 原始构思中的显式业务名词
- 关键实体
- 特定市场术语
- 用户自己点明的异常场景

不得在补全过程中无痕消失。

若发生这种情况，应判定为：

- `raw_signal_erased`

并打回重写。

### 6.3 最小校验建议

可在入口层进行：

- `explicit_noun_set(raw_intent)` 提取
- 与 `ENRICHED/FROZEN` 中的保留情况进行比对

如果核心显式名词集合显著缩水，则不允许放行。

---

## 6.4 状态日志存证

元数据状态推进必须附带不可逆的日志存证。

建议字段：

- `status_history`

最小结构：

```json
[
  {"status": "RAW", "ts": 1711234567, "by": "User_Input"},
  {"status": "ENRICHED", "ts": 1711234580, "by": "Model_GPT54_Enricher"},
  {"status": "FROZEN", "ts": 1711234600, "by": "Gatekeeper_Validator"}
]
```

#### 作用

- 追踪每次状态跃迁是谁做的
- 观察复杂任务是否被“秒回”粗暴补全
- 为后续漂移审计与回放提供时间轴

---

## 7. 意图追溯 ID

总线必须允许追踪：

- 到底是哪一步把原始构思带偏了

因此建议增加：

- `intent_trace_id`

它的作用不是业务字段，而是：

- 审计定位
- 漂移追责
- 追踪从原始灵感到最终 Contract 的整个链路

### 6.1 追溯链建议

同一条任务链中，至少要能通过 `intent_trace_id` 关联：

- `raw_intent`
- `context_enrichment`
- `clarification_round`
- `spec_generation`
- `shadow_check`
- `freeze_decision`

---

## 8. 状态存储方式约束

BusManager 的状态推进，不应主要依赖文件名后缀来表达。

不推荐把核心状态设计成：

- `task_001.raw.json`
- `task_001.enriched.json`
- `task_001.frozen.json`

这样的外部命名链作为唯一真相。

更稳的方式是：

- 在 JSON 内部维护统一状态字段
- 让 `intent_trace_id`、`validation_status`、`history_log` 持续贯穿

建议最小方式：

- 主记录内部维护：
  - `intent_trace_id`
  - `validation_status`
  - `history_log`
  - `raw_snapshot_ref`
  - `status_history`

文件系统可以做镜像与归档，但不应让“文件名变化”承担主要状态语义。

---

## 8.1 物理隔离建议

即使状态语义主要存于 JSON 内部字段，文件系统层仍建议做物理隔离，至少区分：

- `inbox/raw/`
- `inbox/enriched/`
- `inbox/frozen/`

其作用不是承担唯一真相，而是：

- 权限分层
- 运行时组织
- 降低误写风险

### FROZEN 只读规则

一旦任务包进入：

- `validation_status = FROZEN`

则该任务包必须在逻辑层或文件系统层被视为只读。

执行层：

- 只能读取 `FROZEN` 任务包
- 不得回写或修改其中任何意图/规格字段

执行反馈应单独写入：

- `runtime_log`
- 或独立 execution artifacts

而不是回写到原始冻结任务包中。

---

## 8.2 Global Scan 建议步骤

在 `RAW -> ENRICHED` 之前，建议增加一个：

- `global_scan`

目标：

- 扫描现有 `.gm-lite/skills/`、Spec、接口合同、现有代码资产
- 发现当前任务的可能邻居与隐藏依赖

若发现高相关对象，应将其作为：

- `shadow_context_refs`

注入后续补全过程。

这一步在 Light 版可以先做成：

- 建议性步骤
- 或预留字段

但在后续增强版中，应提升为正式准入辅助机制。

---

## 9. 对 BusManager 的直接约束

后续 `gm_bus_manager_seed_implementation_v1` 至少必须预留以下字段：

- `validation_status`
- `intent_trace_id`
- `semantic_resonance_keywords`
- `semantic_resonance_score`
- `semantic_loss_alerts`
- `blindfold_questions`
- `blindfold_answers`
- `blindfold_gap_findings`
- `blindfold_verdict`
- `upstream_dependencies`
- `global_impact`
- `raw_snapshot`
- `history_log`
- `explicit_noun_set`
- `status_history`
- `runtime_log`

并支持以下规则：

1. `RAW -> ENRICHED -> FROZEN` 的单向推进
2. 未达 `FROZEN` 不得进入执行队列
3. 检测到语义丢失、全局锚点缺失、防御性缺失时必须打回
4. 不得覆盖 RAW 原件
5. 不得静默删除 RAW 中的显式名词
6. `FROZEN` 任务包必须只读
7. 执行反馈不得覆盖冻结任务包

---

## 10. 当前结论

本文件正式冻结以下判断：

1. BusManager 入口必须具备三道元数据逻辑防火墙
2. 关键语义丢失必须在执行前被拦截
3. 影子反向质询适合作为执行前的防御性缺失检查
4. `upstream_dependencies` 与 `global_impact` 是强制全局注意力字段
5. `validation_status` 必须成为昂贵执行前的总线准入闸
6. `intent_trace_id` 是后续漂移审计与链路回溯的必要字段
7. RAW 原件必须保留历史镜像，不得被 ENRICHED/FROZEN 静默覆盖
8. 核心状态应优先存储于 JSON 内部字段，而不是文件名后缀
9. `status_history` 应成为元数据状态推进的默认存证链
10. `FROZEN` 任务包必须只读，执行反馈走独立通道
