## 1. 总判断

**结论：**
我**同意**，而且我会把表述再收紧一层：
GM 插件从 Light 走向 Core 的真正门槛，不是“让多个插件都能参与”，而是**把任务从会话里的隐性状态，升级成外部化、可审计、可恢复的共享任务现实**。
所以，**“跨插件共享任务总线”是核心难点之一，但更准确地说，核心是：共享任务总线 + 权威状态层 + 幂等运行时。**

判断标准很简单：
**如果任意一个插件会话突然消失，另一个插件仍能只靠共享层继续接力，这套系统才算真正进入 Core。**
做不到这一点，就还是“人工搬运 + 半自动脚本”的增强版。

**置信度：0.89**

**关键风险点：**

1. 把“消息传输”误当成“状态真相层”，最终出现状态漂移、重复执行、错误接力。
2. 过早做插件间直连或厂商 API mesh，导致强耦合、不可回放、不可诊断。
3. 没把 receipt / lease / task version 做严，自动接单、超时重试、升级会很快失控。

---

## 2. 你认同的已有方向

我认同你们现在的这几个判断，方向基本是对的：

### 2.1 插件不应直接互读聊天上下文

这是对的。
聊天上下文不是协议，也不是审计对象，更不是可靠状态层。
跨插件协作必须把“共享事实”放到外部，而不是寄希望于某个插件记住上文。

### 2.2 应建立共享任务仓 / 共享状态层

这是对的，而且是核心。
没有共享状态层，就没有真正意义上的“任务现实”；只有人工搬运的文本碎片。

### 2.3 应通过统一协议交互，而不是自由文本互通

这是对的。
自由文本适合解释，不适合控制。
自动投递、自动接单、自动接力、自动升级，都依赖**结构化协议对象**，而不是“让另一个 agent 自己理解”。

### 2.4 应由插件 adapter 接入统一中间层

这是对的。
adapter 的职责应该是**吸收厂商差异**，而不是承载业务真相。
业务真相必须在中间层，不在某个厂商插件里。

### 2.5 文件总线先走，再到 SQLite，再到 adapter，最后自动接力

这个方向**基本对，但要修正一句**：
**文件总线适合先验证协议和人工/半自动接力；一旦你们要做 timeout / retry / escalation runtime，SQLite 或等价的权威状态层必须提前进入核心位置。**
否则“文件总线”会很快从简单变成脆弱。

---

## 3. 你不同意或需要修正的地方

### 3.1 不要只讲“总线”，要讲“共享任务现实”

你们真正要建设的，不是一个 message bus，而是一个**任务账本**。
总线只是传输；真正重要的是：

* 任务有稳定 ID
* 派单有 dispatch_id / attempt_id
* 接单有 receipt + lease
* 写回绑定具体版本
* 状态能从 event log 重建
* 任何一步都可追溯、可重放、可恢复

### 3.2 不要把厂商名硬绑定到流程角色

“Codex 负责主控，Claude/Gemini 负责 execution/review/compliance”作为当前运营策略可以存在，
但**架构上不要固化成 vendor = role**。
应该固化的是：

* **角色**：execution / review / compliance / final gate
* **能力声明**：某 adapter 支持哪些角色、处理哪些输入、输出何种 writeback

否则以后你们一旦替换模型、增加 agent、切换供应商，协议层就会被拖着一起改。

### 3.3 现有状态机把“阶段、事件、结果”混在一起了

现在这组状态：

* PENDING
* ACCEPTED
* IN_PROGRESS
* WRITEBACK_DONE
* REVIEW_TRIGGERED
* REVIEW_DONE
* COMPLIANCE_TRIGGERED
* COMPLIANCE_DONE
* GATE_READY

能表达流程，但**不适合做自动化运行时**。
因为里面混了三种东西：

* 生命周期状态
* 编排动作事件
* 阶段性结果

这会导致状态爆炸、边界模糊、重试困难。

### 3.4 task board updater 不应是写源

task board 应该是**投影层 / 展示层**，不是权威写入层。
正确做法是：

* 共享状态层写 event
* projector 生成 task board 视图
* board 只展示，不直接定义真实状态

### 3.5 不该走的弯路

这几条我建议明确避开：

* 不要先做插件之间的直连 mesh
* 不要让多个插件直接覆盖写同一个 task.json
* 不要用自由文本当唯一交接载体
* 不要把 timeout / retry / escalation 逻辑塞进 adapter
* 不要把“收到任务了”和“真正接单了”混成一个模糊动作

---

## 4. 最小可落地方案

### 4.1 正确分层

我建议你们最终按下面 6 层看：

1. **Skill / Policy 层**
   主控官模式、三权分立、review/compliance/final gate 规则。

2. **Protocol / Schema 层**
   task envelope、dispatch、receipt、writeback、escalation 的统一结构定义。

3. **Shared Task Reality 层**
   共享任务仓、事件日志、状态快照、artifact 引用、lease。

4. **Runtime / Orchestration 层**
   dispatch、自动接力、timeout、retry、escalation、主控官升级。

5. **Adapter 层**
   Codex / Claude / Gemini 各自的厂商接入与协议映射。

6. **Projection / UI 层**
   task board、归档视图、人工 override 面板。

你们现在其实已经有 1 和 2，也有半个 4。
**缺口主要在 3，随后才是 5。**

---

### 4.2 最小中间层至少要有哪些对象

我建议最小对象集就是下面这 6 个，再加 1 个强烈建议对象：

#### 必要对象

1. **TaskEnvelope**
   任务真身。
   最少字段：`task_id, root_task_id, parent_task_id, objective, constraints, priority, phase, input_refs, task_version`

2. **DispatchPacket**
   一次派单。
   最少字段：`dispatch_id, task_id, attempt_id, target_role, target_adapter_hint, input_refs, ack_deadline, due_at, idempotency_key`

3. **Receipt**
   接单确认。
   最少字段：`receipt_id, dispatch_id, task_id, actor_id, ack_type, received_at, lease_until, reason_code`

4. **Writeback**
   工作成果回写。
   最少字段：`writeback_id, task_id, dispatch_id, attempt_id, actor_id, outcome, summary, artifact_refs, based_on_task_version, submitted_at`

5. **EscalationPack**
   升级包。
   最少字段：`escalation_id, task_id, source_attempt_id, reason_code, blocker_summary, evidence_refs, requested_decision, escalate_to`

6. **StateLog**
   追加式事件日志。
   最少字段：`event_id, task_id, event_type, actor_id, causation_id, timestamp, payload_hash`

#### 强烈建议补一个

7. **ArtifactManifest**
   不然 writeback 很容易和任务错位。
   最少字段：`artifact_id/content_hash, task_id, type, path_or_uri, producer, created_at`

**一句话：**
你列的那些对象基本都该有；真正不能缺的是 **receipt、event log、artifact binding**。

---

### 4.3 文件总线 vs SQLite 状态层 vs 直接插件互调

我的建议是：

* **先做什么**：共享文件总线可以先上，用来验证协议对象和人工/半自动接力。
* **哪种最稳**：**文件承载 artifact，SQLite 承载 authoritative state** 的混合方案最稳。
* **哪种最容易失控**：**直接插件 API 对接** 最容易失控。

原因很直接：

#### 文件总线的价值

适合做：

* packet 落盘
* writeback 落盘
* artifact 交换
* 人工可见、可审计、可 debug

但它不擅长做：

* lease
* timeout 扫描
* retry 去重
* 状态查询
* 并发一致性

#### SQLite 的价值

它天然适合：

* 唯一约束
* 幂等检查
* lease / expiration
* runtime 查询
* projector 生成快照

#### 直接插件互调为什么危险

因为它会把你们绑到：

* 厂商 API 变化
* 会话语义差异
* 隐式重试
* 黑盒失败
* 不可重放

所以我的结论是：
**不要先做“插件互调”，先做“共享现实层”。**

再补一句现实边界：
如果这些插件**根本不能共享同一文件系统或同一数据库入口**，那你们下一步就不是“直连插件”，而是一个**极薄的 interop service**。
但那仍然是“共享现实层”，不是“插件 mesh”。

---

### 4.4 receipt / acknowledgment 最小设计

我建议 receipt 最小不要只表示“看见了”，而要支持“是否真正 claim 了任务”。

#### 最小字段

* `receipt_id`
* `task_id`
* `dispatch_id`
* `attempt_id`
* `actor_id`
* `ack_type`：`RECEIVED | ACCEPTED | DECLINED | DUPLICATE`
* `received_at`
* `lease_until`
* `reason_code`
* `idempotency_key`

#### 最小状态变化

建议至少支持：

* `DISPATCHED -> RECEIVED`
* `RECEIVED -> ACCEPTED -> IN_PROGRESS`
* `RECEIVED -> DECLINED`
* `DISPATCHED -> ACK_TIMEOUT`
* `ACCEPTED -> LEASE_EXPIRED -> REDISPATCH`

#### 幂等建议

* 对同一个 `dispatch_id + actor_id` 做唯一约束
* receipt 只允许**单向推进**，不允许回退
* 重复的 ACCEPT 视为 no-op
* **只有持有有效 lease 的 actor，writeback 才应被接受**
* 没有 lease 的 ACCEPTED 是不够的，它只是“口头接单”

---

### 4.5 状态机设计评估

**结论：当前状态机不够。**

缺的不是业务阶段，而是运行时关键状态。
最少还要补这些：

* `DISPATCHED`
* `DECLINED`
* `BLOCKED`
* `ACK_TIMEOUT`
* `LEASE_EXPIRED`
* `FAILED`
* `CANCELLED`
* `ESCALATED`
* `COMPLETED / ARCHIVED`

更重要的是，我建议把状态拆成三条轴，而不是继续往一个枚举里塞：

#### A. 生命周期

`CREATED -> DISPATCHED -> CLAIMED -> RUNNING -> SUBMITTED -> DECIDED -> COMPLETED`

#### B. 阶段

`EXECUTION | REVIEW | COMPLIANCE | FINAL_GATE`

#### C. 结果

`PASS | REQUIRES_CHANGES | BLOCKED | FAIL | TIMEOUT`

所以：

* `REQUIRES_CHANGES` **不该是主状态**
* 它应该是**结果标签 / decision outcome**
* 全局状态可以变成 `NEEDS_REWORK` 或直接触发 `REDISPATCH_TO_EXECUTION`

另外：

* `WRITEBACK_DONE` 更像事件
* `REVIEW_TRIGGERED` / `COMPLIANCE_TRIGGERED` 更像编排动作
* `GATE_READY` 更像派生条件

它们不太适合做权威主状态。

---

### 4.6 插件 adapter 最小职责

#### Codex adapter 的最小职责

它是 **control-plane adapter**：

* 创建 TaskEnvelope / child task
* 发 DispatchPacket
* 读 Receipt / Writeback / Escalation
* 依据规则推进状态
* 触发 review / compliance / final gate
* 做 retry / escalation 决策
* 产出最终裁决

它**不应该**自己持有一套私有真相层。

#### Claude adapter 的最小职责

它是 **worker-plane adapter**：

* 暴露 capability manifest
* 读取可分派任务
* 写 Receipt 并 claim lease
* 执行 execution / review / compliance 中被分配的角色
* 产出标准化 Writeback
* 必要时写 blocker / escalation

#### Gemini adapter 的最小职责

从架构上说，它和 Claude adapter **几乎同构**。
区别不该在协议，而该在**能力声明与默认路由策略**上。

也就是说：

* Claude/Gemini adapter 的协议职责应尽量一致
* 真正不同的是 supported roles、输入类型、默认优先级、输出质量特征

这点很重要：
**worker adapter 应该统一，vendor 差异要被包在 adapter 内部。**

---

## 5. 主要风险

### 5.1 共享存储根本不成立

如果这些插件不能共同访问同一个目录、同一个 DB、或同一个状态服务，你们整个“文件总线 / SQLite”方案都会受限。
**第一道防线：** 先验证“共享可达性”，再设计 runtime。

### 5.2 状态不一致 / 分裂真相

文件、task board、插件内记忆、helper 逻辑各写一份，很快就会漂。
**第一道防线：** 单一权威写源 = event log + projector；其他都只是视图。

### 5.3 重复投递 / 重复执行

自动 retry、人工重发、多个 adapter 同时 claim，都可能造成重复工作。
**第一道防线：** `dispatch_id + attempt_id + lease + idempotency key`。

### 5.4 receipt 丢失 / ghost acceptance

看起来有人接单了，实际上没有真正执行；或者执行了但系统没确认。
**第一道防线：** ACK deadline、lease expiry、heartbeat、可重投递。

### 5.5 writeback 与任务错位

最常见的灾难之一：把旧结果写到新任务，或者把 review 写到 execution attempt。
**第一道防线：** writeback 必带 `dispatch_id + attempt_id + based_on_task_version + artifact hash`。

### 5.6 escalation 误触发或循环升级

尤其在 timeout/retry 一起启用后，最容易出现“不断升级主控官”。
**第一道防线：** escalation reason code、最大 hop 数、冷却时间、初期保留人工 override。

---

## 6. 推荐的下一模块

我推荐你们下一步正式立项的是：

## **`共享任务总线最小实现模块`**

不是 adapter 准备模块，也不是继续做纯准备文档模块。

### 原因

因为你们现在最缺的不是“谁来接插件”，而是：

* 统一对象是否够用
* 状态能否成为唯一真相
* receipt / lease 是否成立
* writeback 能否绑定正确任务版本
* timeout / retry / escalation 能否在共享层跑通

这些不成立，adapter 做得再漂亮也只是空壳。

### 这个模块最小应交付什么

1. **协议对象 v0.1 冻结**
   至少冻结：TaskEnvelope / DispatchPacket / Receipt / Writeback / EscalationPack / StateLog

2. **共享现实层最小落地**

   * artifact 用共享文件
   * state 用 SQLite
   * event log 追加写
   * projector 生成任务快照

3. **lease / timeout / retry / escalation 的最小 runtime**
   先别做复杂自动化，只做规则可跑通。

4. **三个标准闭环用例**

   * happy path：execution -> review -> compliance -> gate
   * review `REQUIRES_CHANGES` -> 回 execution
   * ACK timeout / lease expired -> retry / escalate

5. **保留人工 override**
   在 adapter 自动化稳定前，不要去掉人工接力。

### 下一步之后再做什么

这个模块跑通之后，再做 **adapter 准备与接入模块**。
顺序不要反。

---

最后一句压缩成一句话就是：

**你们现在最该建设的，不是“让多个插件互相说话”，而是“让多个插件对同一个任务事实负责”。**
前者只是通信，后者才是系统。
