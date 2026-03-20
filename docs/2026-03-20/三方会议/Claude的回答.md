# Claude 架构评审｜跨插件互操作层与共享任务总线 v1

> 审查日期：2026-03-20
> 审查基于：task_envelope_schema.yaml、state_machine.md、auto_relay_rules.md、task_dispatcher_relay_helper.py、relay helper scope 文档

---

## 1. 总判断

### 🔴 结论：同意——"跨插件共享任务总线"是 GM 从 Light 走向 Core 的真正核心难点。

**推理链：**

当前系统的 protocol 层设计（信封、状态机、接力规则）已经很成熟。但这些协议**全部运行在同一个文件系统、同一个人工搬运者的脑子里**。一旦你把 Codex 插件的 `build_envelope()` 生成的 JSON 拷贝到 Claude Code 的上下文窗口，然后再把 Claude Code 的 writeback 拷贝回去——你就是那条总线。

问题的本质不是 prompt 写得好不好，而是：

| 层次 | 现状 | 缺口 |
|---|---|---|
| **协议层** | ✅ 信封、状态机、接力规则已定义 | — |
| **Helper 工具** | ✅ relay_helper.py 可生成 envelope / escalation | — |
| **传输层** | 🔴 不存在 | 信封怎么从 A 到 B？ |
| **确认层** | 🔴 不存在 | B 收到后怎么回 ACK？ |
| **监控层** | 🔴 不存在 | 超时、丢件谁来发现？ |

**因此，方向完全正确。但我要修正一个认知：这不是"一个难点"，而是三个递进难点：**

1. **共享现实**（让多插件看到同一份任务数据）→ 最小可落地
2. **协议对齐**（让多插件理解同一种信封格式）→ 你们已经有了
3. **自动运行时**（让收发不再经过人手）→ 最终形态

---

## 2. 认同的已有方向

### ✅ 完全认同的判断

1. **"插件不应直接互读聊天上下文"** — 正确。聊天上下文是非结构化的、session-scoped 的、不可 merge 的。跨插件共享聊天记录是条死路。

2. **"应建立共享任务仓 / 共享状态层"** — 正确。这是唯一正确的方向。

3. **"应通过统一协议交互"** — 正确。你们的 `task_envelope_schema.yaml` 就是这个协议。它已经足够好做 v1。

4. **"共享文件总线 → SQLite → adapter → 自动接力"的渐进路径** — 正确。这是我见过的最务实的演进路线之一。

5. **relay_helper.py 的设计哲学** — scope 文档里的"禁止项"（不实现文件监听、不实现自动发送、不接 MQ/Webhook）说明你们对边界的判断非常清醒。

### ✅ 现有 task_envelope_schema 的评价

当前信封已经覆盖了 90% 的需要。`task_id`、`role`、`assignee`、`writeback`、`next_hop`、`escalation_trigger` 这些字段的设计都合理。

---

## 3. 不同意或需要修正的地方

### 🟡 修正 1：渐进路径的中间层不应跳到 SQLite，应先有 manifest

你们提出的是：`共享文件 → SQLite → adapter`

我建议修正为：`共享文件 → manifest index（JSON） → SQLite → adapter`

**原因**：直接从"一堆散落的 JSON 文件"跳到 SQLite 有一个隐藏的 gap——你需要先有一个"文件目录"。即：**哪些文件是活跃任务？哪些已关闭？当前全局状态是什么？**

一个 `task_board.json`（类似 manifest）应该是 SQLite 之前的过渡：

```json
{
  "version": 1,
  "last_updated": "2026-03-20T00:30:00+08:00",
  "active_tasks": [
    {
      "task_id": "X1",
      "state": "REVIEW_TRIGGERED",
      "envelope_path": "outbox/X1_review_envelope.json",
      "last_actor": "codex",
      "updated_at": "2026-03-20T00:25:00+08:00"
    }
  ]
}
```

这比直接上 SQLite 成本低 10 倍，而且**所有插件都能通过读文件看到它**。

### 🟡 修正 2：状态机缺少 `REQUIRES_CHANGES` 的位置

你们在问题 5 中问了这个问题。我的回答是：

**`REQUIRES_CHANGES` 既不是状态也不是结果标签——它是一个"回退触发器"。**

它应该触发以下状态变迁：

```
REVIEW_DONE (verdict=REQUIRES_CHANGES)
  → state 回到 PENDING
  → 生成新 envelope，iteration + 1
  → 绑定原始 task_id + iteration 号
```

如果你把 `REQUIRES_CHANGES` 做成一个状态节点，你的状态图就变成有环图（可以无限回退），这会让状态机的 invariant 检查变得极其复杂。

**具体建议**：在 task_envelope 中增加一个字段：

```yaml
iteration:
  type: integer
  default: 1
  description: "当前任务的迭代轮次，REQUIRES_CHANGES 时 +1"
```

状态机不加新节点。`REQUIRES_CHANGES` verdict 触发的是"重新投递同一个 task_id 的 iteration N+1"。

### 🟡 修正 3：信封缺少 `timestamp` 和 `origin_plugin` 字段

当前信封缺少两个关键的跨插件字段：

```yaml
origin_plugin:
  type: string
  enum: [codex, claude, gemini, human]
  description: "该信封由哪个插件生成"

created_at:
  type: string
  format: date-time
  description: "信封创建时间戳"
```

没有这两个字段，你在多插件场景下无法做：
- 超时检测（不知道什么时候发出的）
- 来源审计（不知道谁发出的）
- 冲突仲裁（两个插件同时写同一个 task_id 时）

---

## 4. 最小可落地方案

### Phase 0：共享文件总线（建议立即启动）

```
workspace/
├── .gm-bus/                          ← 共享任务总线根目录
│   ├── task_board.json               ← manifest：所有活跃任务的索引
│   ├── outbox/                       ← 投递箱：待接收的 envelope
│   │   ├── X1_review_envelope.json
│   │   └── X2_execution_envelope.json
│   ├── inbox/                        ← 收件箱：已接收的 envelope + receipt
│   │   ├── X1_receipt.json
│   │   └── X2_receipt.json
│   ├── writeback/                    ← 回写区：标准 writeback 路径
│   │   ├── X1_execution_report.md
│   │   ├── X1_review_report.md
│   │   └── X1_compliance_attestation.md
│   ├── escalation/                   ← 升级区
│   │   └── X1_escalation_pack.json
│   └── archive/                      ← 归档区：GATE_READY 后移入
│       └── X1/
```

**工作流**：

```
1. Codex 拆分任务 → 写 envelope 到 outbox/
2. Codex 更新 task_board.json
3. 用户把 outbox/ 中的 envelope 复制到 Claude Code 的对话中
   （这一步现在是人工的，将来由 adapter 自动化）
4. Claude Code 执行完毕 → 写 writeback 到 writeback/
5. Claude Code 写 receipt 到 inbox/
6. 用户运行 relay_helper.py → 生成下一跳 envelope 到 outbox/
7. 循环直到 GATE_READY
```

**关键约束**：
- 所有插件只通过 `.gm-bus/` 目录交互
- 任何直接的聊天上下文引用都是协议违规
- `task_board.json` 是唯一的全局状态视图

### Phase 1：receipt 机制（在 Phase 0 稳定后启动）

### Phase 2：SQLite 状态层（在 Phase 1 稳定后启动）

### Phase 3：插件 adapter + 自动收发（在 Phase 2 稳定后启动）

---

## 5. 逐题回答

### Q1. 架构判断
- **同意**。
- 原因见上方第 1 节。补充一点：你们当前的 relay_helper.py 的 `infer_state()` 函数其实已经是一个"极简状态总线"——它通过文件存在性推断状态。这个思路是对的，只是它目前只能被一个人跑，不能被多个插件并发感知。

### Q2. 最小中间层对象

至少需要 **6 个对象 + 1 个索引**：

| 对象 | 用途 | 你们已有？ |
|---|---|---|
| `task_envelope` | 任务投递信封 | ✅ 已有 schema |
| `dispatch_packet` | 投递动作的元数据（谁、何时、投给谁） | ❌ 缺少，建议合并到 envelope 的 `origin_plugin` + `created_at` |
| `receipt` | 接单确认 | ❌ 完全缺失 |
| `writeback` | 执行结果回写 | ✅ 已有路径约定 |
| `escalation_pack` | 升级包 | ✅ 已有 |
| `state_log` | 状态变更日志 | ❌ 缺失 |
| `task_board` | 全局任务索引 | ❌ 缺失（我在修正1中提出） |

**我的建议是：先做 receipt + task_board，因为这两个是打通"人工搬运"到"半自动搬运"的关键。**

`dispatch_packet` 可以不单独建对象，合并到 envelope 里加 2 个字段即可。`state_log` 在 Phase 0 可以用 append-only 的 JSON Lines 文件替代。

### Q3. 文件总线 vs 直接插件互调

| 方式 | 稳定性 | 落地成本 | 失控风险 |
|---|---|---|---|
| **共享文件总线** | 🟢 最稳 | 🟢 最低 | 🟢 最低 |
| **SQLite 状态层** | 🟢 稳 | 🟡 中等 | 🟡 并发写需要锁 |
| **直接插件 API 对接** | 🔴 极不稳 | 🔴 极高 | 🔴 最容易失控 |
| **消息队列 / Webhook** | 🟡 稳但重 | 🔴 极高 | 🟡 运维负担 |

**推荐**：共享文件总线。

**原因**：
1. 所有 IDE 插件都能读写本地文件——这是**唯一一个所有插件都保证支持的 I/O 通道**
2. 文件是持久化的、可审计的、可 git 追踪的
3. 不需要任何外部服务
4. 你们的 relay_helper.py 已经在做基于文件存在性的状态推断——这就是文件总线的雏形

**最容易失控的是直接插件 API 对接**——因为每个插件的 API 拓扑不同、认证方式不同、版本迭代不同。你做一个 Codex→Claude 的直连，然后 Claude API 改版，整条链路立刻断裂。

### Q4. Receipt / Acknowledgment 最小设计

```json
{
  "receipt": {
    "task_id": "X1",
    "iteration": 1,
    "received_by": "claude",
    "received_at": "2026-03-20T00:30:00+08:00",
    "envelope_hash": "sha256:abc123...",
    "status": "ACCEPTED",
    "reject_reason": null
  }
}
```

**最小字段**：
- `task_id` — 对应哪个任务
- `iteration` — 对应哪一轮
- `received_by` — 谁接的
- `received_at` — 何时接的
- `envelope_hash` — 接的是哪一份信封（防篡改、防错位）
- `status` — `ACCEPTED` | `REJECTED`
- `reject_reason` — 拒绝时的原因

**状态变化**：
```
PENDING → (envelope 投入 outbox) → DISPATCHED
DISPATCHED → (receipt.status=ACCEPTED) → ACCEPTED
DISPATCHED → (receipt.status=REJECTED) → BLOCKED (+ escalation)
```

注意：这里多了一个 `DISPATCHED` 状态。你们现有状态机缺这个。`PENDING` 和 `ACCEPTED` 之间不应该是原子的——因为在多插件场景下，"已发出但对方还没确认"是一个真实存在的中间态。

**幂等建议**：
- 同一 `task_id` + `iteration` 的 receipt 只允许写入一次
- 重复写入应返回已有 receipt 而非覆盖
- relay_helper 在检测到 receipt 已存在时跳过

### Q5. 状态机评估

当前状态集合评估：

```
✅ PENDING          — 保留
🟡 → 建议插入 DISPATCHED（信封已投递但未确认）
✅ ACCEPTED         — 保留
✅ IN_PROGRESS      — 保留
✅ WRITEBACK_DONE   — 保留
✅ REVIEW_TRIGGERED — 保留
✅ REVIEW_DONE      — 保留
✅ COMPLIANCE_TRIGGERED — 保留
✅ COMPLIANCE_DONE  — 保留
✅ GATE_READY       — 保留
✅ BLOCKED          — 保留
✅ DENY             — 保留
```

**缺少的关键状态**：

| 缺失状态 | 理由 |
|---|---|
| `DISPATCHED` | 已发出、待接收确认。没有这个状态你无法区分"还没发"和"发了但没人接" |
| `TIMEOUT` | 可选。建议作为 `BLOCKED` 的子类型而非独立状态，用 `blocked_reason: "timeout"` 区分 |

**关于 `REQUIRES_CHANGES`**：
- 🔴 **不应作为状态节点**
- ✅ **应作为 review/compliance 的 verdict 标签**
- 触发效果：task 的 `iteration` +1，状态回到 `PENDING`，新一轮流转开始
- 旧 iteration 的所有 writeback 保留在 archive 中，不删除

### Q6. 插件 Adapter 设计

#### Codex Adapter（主控角色）

| 职责 | 说明 |
|---|---|
| 生成 envelope | 调用 `build_envelope()` 生成标准信封 |
| 写入 outbox/ | 将 envelope JSON 写入共享目录 |
| 更新 task_board.json | 维护全局任务索引 |
| 读取 inbox/ receipt | 检查接单确认 |
| 读取 writeback/ | 检查回写件完整性 |
| 触发 relay_helper | 执行自动接力判断 |
| 终验裁决 | GATE_READY 后做最终 gate decision |

**不做**：不执行任务本身、不替代 review/compliance 角色

#### Claude Adapter（执行 / 审查角色）

| 职责 | 说明 |
|---|---|
| 读取 outbox/ envelope | 从共享目录读取分配给自己的信封 |
| 写入 inbox/ receipt | 确认接单 |
| 执行任务 | 根据 role 执行 execution / review / compliance |
| 写入 writeback/ | 将结果写入标准路径 |
| 更新 task_board.json | 更新自己负责的任务状态 |

**不做**：不生成下一跳 envelope（这是 Codex / relay_helper 的事）、不做终验裁决

#### Gemini Adapter（执行 / 审查角色）

与 Claude Adapter 职责**完全一致**。差异仅在：
- 读写文件的 API 调用方式不同（Gemini CLI vs Claude Code CLI）
- 上下文窗口大小和格式偏好不同

**关键设计原则**：Adapter 不是"为每个 AI 写一套不同的逻辑"。Adapter 的唯一职责是**把标准协议翻译成该插件能理解的格式，以及把该插件的输出翻译回标准协议格式**。内核逻辑是完全共享的。

### Q7. 最大风险点

| # | 风险 | 严重性 | 第一道防线 |
|---|---|---|---|
| 1 | **状态不一致**：task_board.json 与实际文件不同步 | 🔴 致命 | **每次状态变更前先校验文件存在性**。relay_helper 已经在做 `infer_state()`，这个思路正确。task_board 应该是 derived state（可重建），而非 source of truth |
| 2 | **重复投递**：同一个 envelope 被投递两次 | 🟡 重要 | **envelope 写入前检查 outbox/ 是否已存在同 task_id + iteration 的文件**。relay_helper 的幂等规则4已经覆盖了这个，但需要扩展到全链路 |
| 3 | **receipt 丢失**：执行完成但没写 receipt | 🟡 重要 | **writeback 存在但 receipt 不存在时，relay_helper 应自动补 receipt**（因为 writeback 本身就是"我做完了"的证据） |
| 4 | **writeback 与任务错位**：X1 的 writeback 文件内容其实是 X2 的 | 🔴 致命 | **writeback 文件内部必须包含 task_id 字段**。relay_helper 在读取 writeback 时应校验内部 task_id 与文件名 task_id 的一致性 |
| 5 | **并发冲突**：Codex 和 Claude 同时写 task_board.json | 🟡 重要 | **Phase 0 不需要解决**——因为 Phase 0 是人工搬运，不存在真正的并发。Phase 2 上 SQLite 后自然解决。Phase 0 只需要约定"task_board 只由 relay_helper 写" |

### Q8. 下一阶段建议

**推荐：`共享任务总线最小实现模块`**

理由：

1. **跨插件互操作层准备模块** — 太抽象，没有可验收的产出
2. **共享任务总线最小实现模块** — ✅ **推荐** — 有明确的产出（`.gm-bus/` 目录结构 + task_board.json + receipt schema + 更新后的 relay_helper）
3. **插件 adapter 准备模块** — 太早，总线还没有，adapter 没有东西可以 adapt

**具体产出定义**：

```
共享任务总线最小实现模块 v1 的验收条件：
├── .gm-bus/ 目录结构已创建
├── task_board.json schema 已定义
├── receipt.json schema 已定义
├── task_envelope_schema.yaml 已补充 origin_plugin / created_at / iteration 字段
├── relay_helper.py 已支持：
│   ├── 读写 .gm-bus/ 目录
│   ├── 生成 + 校验 receipt
│   ├── 更新 task_board.json
│   └── writeback 内部 task_id 校验
├── 人工搬运 SOP 文档已写（临时方案）
└── 端到端 dry-run 验证通过（一个 task 走完 PENDING → GATE_READY）
```

---

## 6. 推荐的下一模块

### 🟢 立项建议：`gm-shared-task-bus-v1`

**优先级排序**：

| 序号 | 子任务 | 优先级 | 预期耗时 |
|---|---|---|---|
| 1 | 定义 `.gm-bus/` 目录结构 | P0 | 30 min |
| 2 | 定义 `task_board.json` schema | P0 | 30 min |
| 3 | 定义 `receipt.json` schema | P0 | 30 min |
| 4 | 补充 envelope schema（+3 字段） | P0 | 15 min |
| 5 | 升级 relay_helper.py | P1 | 2 hr |
| 6 | 写人工搬运 SOP | P1 | 1 hr |
| 7 | 端到端 dry-run | P1 | 1 hr |

**不该走的弯路**：

1. 🔴 **不要现在做自动发送** — 人工搬运是可以工作的，而且在 Phase 0 人工搬运本身就是最好的调试手段
2. 🔴 **不要现在上数据库** — JSON 文件在 Phase 0 完全够用，过早引入 SQLite 会让所有插件都需要 SQLite 驱动
3. 🔴 **不要现在做 Webhook / 消息队列** — 引入外部服务会让整个系统从"本地可控"变成"分布式不可控"
4. 🔴 **不要试图让插件互相调用 API** — 这是最大的坑。每个插件的 API 都在快速迭代，直连等于把稳定性绑定在最不稳定的一层

---

## 附录：修正后的状态机建议

```
PENDING
  → DISPATCHED        (envelope 写入 outbox)
  → ACCEPTED          (receipt.status = ACCEPTED)
  → IN_PROGRESS       (执行单元开始工作)
  → WRITEBACK_DONE    (writeback 文件写入)
  → REVIEW_TRIGGERED  (review envelope 生成)
  → REVIEW_DONE       (review_report 写入)
    ├── verdict=PASS → COMPLIANCE_TRIGGERED
    └── verdict=REQUIRES_CHANGES → PENDING (iteration+1)
  → COMPLIANCE_TRIGGERED
  → COMPLIANCE_DONE
    ├── verdict=PASS → GATE_READY
    └── verdict=REQUIRES_CHANGES → PENDING (iteration+1)
  → GATE_READY        (进入主控终验池)

任意状态 → BLOCKED  (依赖未满足 / 超时 / 缺件)
任意状态 → DENY     (scope violation / 不可恢复失败)
```
花絮：
架构评审已写入 Claude的回答.md。核心观点速览：

总判断：同意——共享任务总线是从 Light 到 Core 的真正核心难点
3 个修正：渐进路径中增加 manifest 层、REQUIRES_CHANGES 应为回退触发器而非状态节点、envelope 补 3 个跨插件字段
最小落地：.gm-bus/ 共享文件总线（outbox/inbox/writeback 目录结构）
推荐立项：gm-shared-task-bus-v1，而非 adapter 或互操作层准备模块
最大风险：状态不一致 > writeback 错位 > 并发冲突，给了每条的第一道防线