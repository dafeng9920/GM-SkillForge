# Gemini 架构评审｜跨插件互操作层与共享任务总线 v1

> 审查身份：世界级软件架构师 / Google Distinguished Engineer
> 核心原则：全局通读 / 区分风险等级 / 提供可执行改法
> 审查依据：《AI会议提示词｜跨插件互操作层与共享任务总线 v1》

---

## 🧠 深度推理阶段 (Thinking Process)

1. **全局系统诊断**：当前 GM 多 Agent 系统的核心痛点不是“智力不足”（Prompt/Context），而是缺乏 IPC（Inter-Process Communication，进程间通信）机制。各个 LLM 插件（Codex/Claude/Gemini）如同一个个独立运行且无法直接联网的沙盒容器，用户被迫充当了“人肉 Message Broker（消息中间件）”。
2. **架构方向选择**：要打破这种孤岛，在不共享同一内部运行环境（Session/API）的前提下，寻找“最大公约数”。对于本地安全运行的 AI 插件而言，**唯一可靠、原生支持且具备持久化特性的介质，就是“本地文件系统 (Local File System)”**。任何企图直接调 API 的方案都会因为各自生态墙和版本变动陷入适配地狱。
3. **关键缺失识别**：在现有的协议（信封、接力规则）基础上，真正缺失的是：**控制平面 (Control Plane)**。数据平面（Payload）已经有了（Task Envelope），但控制发件、收件、状态同步的机制（目录锁、Manifest快照、ACK凭证）是零。
4. **状态机优化**：将 `REQUIRES_CHANGES` 设计为状态会导致系统陷入“无限图”的死循环陷阱。在企业级系统中，任务必须是 DAG（有向无环图）。因此，打回重做的本质应该是“生成同一任务的下一个内部版本（Iteration）”。

---

## 1. 总判断

### 🔴 结论：完全同意。跨插件共享任务总线是系统跨越“玩具”到“工业级 (Core)”的生死线。

**原因**：
当前的多 Agent 协作是**伪协作 (Pseudo-collaboration)**，本质是“用户驱动的串行管道”。没有共享的系统现实 (System Reality)，LLM 永远只能是“单机版 AI”。建立共享任务总线，等同于在微服务架构中引入 Kafka/RabbitMQ，或者是 K8s 中的 etcd。这是实现自治 (Autonomy)、异步非阻塞 (Async Non-blocking)、故障恢复 (Fault Tolerance) 的绝对基石。

---

## 2. 认同的已有方向

*   ✅ **“插件不应直接互读聊天上下文”**：这是极其正确的防腐层设计。上下文包含了极其冗余、非结构化且具偏见的信息。强制用定义良好的契约（Protocol，如 JSON Envelope）交互，是 Clean Architecture 的体现。
*   ✅ **“渐进式路径 (文件 -> SQLite -> Adapter -> 自动)”**：这种 MVP 演进策略完美契合敏捷架构。它避免了提前过度设计（Over-engineering），能在极短时间内通过文件系统拿到最小验证结果。
*   ✅ **基于已有规范**：已有的 Execution / Review / final gate 分层极具实战性，符合高质量工程交付的流水线。

---

## 3. 不同意或需要修正的地方 & 最小可落地方案

我直接将这两个模块融合，通过展示“最小可落地（MVP）文件总线协议”来指出需要修正的架构点。

### 🟡 修正领域：最小中间层不仅需要这些，更缺“全局视图”

只做 Envelope、Receipt 和 Writeback 是不够的。如果我是 Claude 插件，我如何知道系统里有多少个 PENDING 的任务是给我的？难道要遍历（O(N)）解析所有的 Envelope？

**可执行改法：引入 `Manifest` (状态快照引流索)**。
必须有一个中心化的 `task_board.json`（由主控单向写入更新），里面只存轻量级的元数据，供所有节点（插件）快速读取，决定自己是否需要介入。

### 🟢 最小可落地文件总线设计 (Phase 1)

基于目录即队列（Directory-as-a-queue）的微服务设计模式：

```text
.gm_bus/
├── manifest.json          # 🔴 全局状态墙（仅包含活跃任务摘要、当前Owner和状态）
├── outbox/                # 发件箱（包含完整的 Task Envelope）
│   └── TASK-2026-001_v1.json
├── inbox/                 # 确认箱（收到任务的插件，写回 Receipt）
│   └── TASK-2026-001_v1_receipt.json
└── writeback/             # 回写箱（处理完成后的结果和审查报告）
    └── TASK-2026-001_v1_writeback.md
```

### 🟡 修正领域：状态机设计与 `REQUIRES_CHANGES` 的定位

原有的状态机缺少异步系统最核心的**过渡态**，且 `REQUIRES_CHANGES` 定位模糊。

**判定**：`REQUIRES_CHANGES` 绝对不应该是一个独立的 State，而应该是一个 **Verdict（评审裁决结果）**。

**可执行改法：引入不可变迭代 (Immutable Iteration) 与 DISPATCHED 状态**。
1. **状态机补充**：在 `PENDING` 和 `ACCEPTED` 之间插入 `DISPATCHED`。
   `PENDING` (系统生成了任务) -> `DISPATCHED` (投递到 outbox) -> `ACCEPTED` (插件写入 receipt)。
2. **Iteration升级**：当 Review/Compliance 给出 `REQUIRES_CHANGES` verdict 时，旧的任务生命周期走向 `FAILED_ITERATION`（归档），主控根据 Writeback 意见重新生成该任务的 v2 版本（`TASK-2026-001_v2`），状态重置为 `PENDING`。这保证了状态机单向流转（DAG），避免无限死循环，且方便审计追踪每一次重做。

### 🟡 修正领域：插件 Adapter 最小职责的界定

各个插件的作用不应混淆，不能发生越权。

**可执行改法：极简职责划分**
*   **Codex (Orchestrator Adapter)**：唯一有权写 `manifest.json`。负责监听 `writeback/` 和 `inbox/`，当符合流转规则时，生成下一阶段的 Envelope 放入 `outbox/`，并处理死信/升级。
*   **Claude/Gemini (Worker Adapter)**：只读 `manifest.json` 和 `outbox/`。匹配到属于自己的任务 -> 写入 Receipt 到 `inbox/` 锁定任务 -> 开辟上下文执行 -> 输出 Markdown 报告到 `writeback/` -> 本次交互自毁。不允许它们自己修改状态或流转。

### 🟡 修正领域：Receipt 的最小字段

**可执行改法：Receipt 核心结构（兼顾防篡改与幂等）**
```json
{
  "taskId": "TASK-2026-001",
  "iteration": "v1",
  "claimedBy": "claude-code-env",  // 明确是哪个具体的沙盒接的单
  "claimedAt": "2026-03-20T10:00:00Z",
  "envelopeChecksum": "sha256-xxx...", // 防篡改：确保接到的是最新版本的心智包
  "status": "ACCEPTED" // 或 REJECTED (如果由于权限或资源原因无法接单)
}
```

---

## 4. 主要系统级风险 (Risk Assessment)

| 风险点 | 风险等级 | 场景描述 | 第一道防线 (可执行改法) |
| :--- | :--- | :--- | :--- |
| **状态不一致 (Split Brain)** | 🔴 致命 | `manifest.json` 显示 IN_PROGRESS，但实际并没有插件在执行，或已被用户手动删除。 | **单向数据流与自愈逻辑**：规定 `manifest.json` 只是从各种目录现状（outbox/inbox/writeback）推导出来的 Cached View。提供 `bus-sync` 工具，随时可以根据目录真实文件重建 manifest。 |
| **重入与幽灵任务 (Ghost Tasks)** | 🔴 致命 | 插件 B 接单后进程崩溃，没有给出 writeback，任务永远卡在 IN_PROGRESS。 | **Timeout 与死信队列**：主控板（Codex Adapter）在轮询 manifest 发现某 receipt 存活超过设定的 TTL (如 60 分钟)，自动触发 Escalation，重置任务至 PENDING。 |
| **脏读 / 并发冲突竞态** | 🟡 重要 | 未来如果两个 Claude Code 环境同时读到 outbox 的任务，并尝试写入 receipt。 | **提拔文件锁 (File Locking)** 或 **原子重命名机制 (Atomic Rename)**。目前人肉搬运时代问题不大，但只要接入自动 Adapter，必须在写 receipt 时判断文件是否存在，如果已有别人写了 receipt，立刻自动回退 (Abort)。 |
| **Writeback 凭证错位** | 🟢 建议 | 插件用旧的上下文回写了新 Iteration 的任务。 | **强制 Checksum 检验**：`writeback` 提交时必须引用原本 Envelope 的 Hash 值或者对应的 Iteration 标识。主控发现不匹配则丢弃并报警。 |

---

## 5. 推荐的下一模块

基于敏捷原则与最小可行性测试，我强烈建议**直接立项并推进**：

### 🎯 `共享任务总线最小实现模块 (Shared Bus MVP)`

**理由：**
1. **不要做“准备模块”**：“准备模块”通常意味着写大量的口水文档。真正的架构是在真实文件读写和解析碰撞中跑出来的。
2. **隔离依赖**：不需要先完成 Adapter 的自动化对接。你可以立刻定义出 `.gm_bus` 的目录树和那三个核心 JSON (manifest, envelope_v2, receipt) 的结构 schema。
3. **低成本验证**：你可以用极其简单的 CLI 脚本或者甚至靠人在这个目录结构下继续当一段时间的“手动总线路由器”，去跑通一次端到端验证。只要这套文件格式经受住了考验，外围接自动化的 Adapter 只是写几行文件监听代码的事情。

**你的下一步行动建议 (Action Items):**
1. 创建一个 Git repo 或分支专门定义 `.gm_bus/` 及其 schema。
2. 将你现有的 Envelope 加入 iteration 和哈希字段。
3. 编写一个无脑的 python 脚本 `bus-sync.py`（相当于最早的 master controller），只根据存在的 envelope/receipt/writeback 文件，自动生成/刷新 `manifest.json`。这就是你的 MVP。
---------------
花絮：

用户提出的是一个经典的架构级 ROI (投资回报率) 和战略决断问题。作为一名 Distinguished Engineer，我不能只说“好”或者“不好”，必须从“业务顶层价值”、“人力机会成本”、“系统演进生命周期”三个维度给出判定，并给出止损点 (Stop-loss point)。
以架构大师的身份，我的回答是：绝对值得搞，而且这是你当前系统唯一的“破局点”。

但“怎么搞”决定了你会成为神，还是陷入泥潭。以下是我的深度判定：

1. 为什么“不得不搞”？（解除算力封印）
你现在的状态叫作 "Human-as-a-Service" (人类即服务) —— 架构图上画着牛逼的 Codex、Claude、Gemini，但它们之间连接的网线，是你自己的手和脑子。

现状瓶颈：如果不搞总线，系统算力的天花板就是你复制粘贴的手速和你的睡眠时间。
搞定后的跨越：搞定总线后，系统将跨入真正的 Agentic 原生时代。你可以睡前下发一个包含 10 个子模块架构重构的超级任务，Codex 在深夜自动拆解，Claude 和 Gemini 并发执行并在清晨完成 Review 和合规检查。这带来的生产力提升不是 10%，而是 10 倍 (10x) 的代际压制。
2. ROI 层面的残酷真相：真正的壁垒在工程，不在 Prompt
很多人以为写出了极好的 Prompt 就是掌握了 AI，这是错觉。Prompt 会随着模型能力的迭代迅速贬值。
真正有护城河的，是这套“让多个智能体共享现实并相互纠错执行的运行时协议（Runtime Protocol）”。一旦你把当前的 SOP 从“约束你自己的心智”变成了“约束机器的文件总线代码”，这套系统就成了你的数字资产，也就是你在造一家“没有物理工位的超级外包公司”。这个价值无可估量。
3. 给你的“控本避坑”建议（怎么搞才不亏）
值得搞的前提，是你严格遵守“极简架构”的红线，千万别搞高大上的过度设计：

🔴 不要搞的服务：什么中间件、消息队列 (Kafka/RabbitMQ)、Webhook、跨网络通信 API。一旦引入，你就会从一个 AI 指挥官变成一个苦逼的底层运维工程师。
🟡 必须忍受的阵痛：初期的错误流转、状态死锁、各个插件还没把 Adapter 跑顺畅时可能出现的混乱。这时候不要急着加复杂的容错逻辑，就是用最简单的脚本清理目录重启。
🟢 最小可计算的投入（MVP）：
这周（2天）：建好 .gm_bus 文件夹，把信封和收据的 JSON 格式定死。你继续当人肉搬运工，但严格按照文件夹契约搬运，看看这套文件协议有没有信息缺失。
下周（3天）：写一个不超过 200 行的 Python 轮询脚本 (bus-daemon.py)，代替你的手，只要看到 outbox 有文件，就塞给对应的 CLI / 插件终端。
最终判定： 这趟水值得蹚。你现在卡在“半自动突击步枪”的阶段，只要越过了这道“全自动换弹总线”的坎，你就掌握了“加特林机枪”。立刻新建 .gm_bus 文件夹，跑起来！