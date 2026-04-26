# GM-Lite Handoff / TODO

日期: 2026-04-05

## 当前结论

- Webview 运行时问题已修复，GM-Lite 页面可正常启动、接收 snapshot、恢复显示。
- `Continue Current Chain / 继续当前链` 的主交互已经基本可用。
- `Resume Current Task / 继续执行当前任务` 之前是本地伪闭环；今天已切到真实 `execution_request` 派发路径。
- 当前最新有效证据表明，`Resume Current Task` 现在会生成真实 dispatch packet 写入 `.gm_bus/outbox/`，并指向真实执行者 `antigravity-1`。
- 但完整实战链尚未闭环验证完：还缺执行消费、review、compliance 三段真实推进证据。

## 今天已完成

### 1. Webview / UI / 控制台侧

- 修复 webview boot/snapshot/render 主路径。
- 外部化主脚本，保留 `WV0/WV2` 运行时证据点。
- 修复 `Only GM-Lite` 过滤和部分 transcript 噪音。
- `Continue Current Chain` 现在能：
  - 锁定当前链 writeback
  - 恢复上下文
  - 给出 `Next` 提示
- `Clear / 清空` 已修复。

### 2. 主链可用性

- `Continue Current Chain` -> `Resume Current Task` 的 UI 路已经通。
- 原先 `Codex Output Ingested` 的多类自噪音已压掉。
- 但“后续按钮偶尔需要再点一下才出现”仍有轻微残留，当前不阻塞。

### 3. 真实链路修复

重点文件:
- `D:\gm-lite\vscode-extension\src\core\AutoProgressionService.ts`

今天对该文件做了净化：

- 移除了旧的本地伪闭环核心：
  - 本地直接 success/writeback 直写
  - 本地伪造 execution `codex_output`
  - 本地 execution run 记录伪完成
- 保留 claim/session 基础设施。
- `Resume Current Task` 改为派发真实 `execution_request` 到 `.gm_bus/outbox/`。
- `to_participant` 改为真实执行者 `antigravity-1`。
- `payload.data.context` 从旧的 `original_payload` 清理为 `original_payload_summary`，不再夹带 UI 对话文本、messages、raw_text。

## 最新关键证据

### 1. 新 packet 已符合真实 execution_request 基本要求

最新确认的 packet:
- `D:\gm-lite\.gm_bus\outbox\4c0f9893-1a54-45a4-bd83-7bb686aab319.json`

关键字段:
- `payload.type.name = "execution_request"`
- `task_id = "bo1-task-001"`
- `to_participant = "antigravity-1"`
- `review_required = true`
- `context.original_payload_summary` 已存在

这说明：
- `Resume Current Task` 已不再把 UI 提示语直接换壳塞进 bus
- dispatch 层从伪闭环切到了真实派发

### 2. 旧问题证据仍需记住

之前被合规抓到的旧问题：
- payload 是控制台说明文本
- `to_participant = gm-lite-bus`
- 本地 0ms success writeback
- review evidence 缺失

这些旧证据不能丢，但今天的新 packet 已证明其中前两项正在被修正。

## 当前未完成断点

接下来不要再围绕 UI 小问题打转，重点盯真实链推进：

1. `antigravity-1` 是否真实消费 `execution_request`
2. outbox -> inbox 是否发生真实推进
3. 是否出现新的真实 execution 产物
4. 是否出现 review 证据
5. 是否出现 compliance 证据
6. 是否仍会冒出本地 0ms success writeback

## 明天优先 TODO

### P0

- 以 `4c0f9893-1a54-45a4-bd83-7bb686aab319.json` 之后的新链为基线，追踪：
  - outbox
  - inbox
  - claims
  - writeback
  - continuations
  - feedback_events
- 目标是确认这条 `execution_request` 是否真的被 `antigravity-1` 接单并推进。

### P1

- 若 execution 能推进，继续确认：
  - review 是否真实出现
  - compliance 是否真实出现
- 不接受仅有 execution success 的半链。

### P2

- 若又出现本地立即 success/writeback：
  - 优先检查是否还有别的旧路径绕过 `AutoProgressionService.ts` 新主路
  - 优先查 command wiring，而不是先怀疑 packet 结构

## 不要再犯的坑

- 不要把三权审计 prompt 写成“先修改代码”。
- 审计轮和修复轮必须分开。
- 不要再把 UI 提示文本写入真实 execution payload。
- 不要只看 writeback，就判定真实链已成立。
- 不要在未确认新实例接管前，拿旧 packet 做结论。

## 新窗口衔接提示词

下面这段直接发给新窗口：

```text
继续接手 GM-Lite 主链路真实实战链修复，不要从零开始分析。

当前背景：
- Webview/runtime/UI 基本已修复，页面可正常工作。
- `Continue Current Chain` 基本可用。
- 今天的核心工作是把 `Resume Current Task` 从“本地伪闭环”改成“真实 execution_request 派发”。

必须先承认的既有结论：
1. 旧版本 `Resume Current Task` 曾通过本地 AutoProgressionService 直接伪造 success/writeback
2. 这条伪闭环已被切断
3. 当前最新有效 packet 已证明 dispatch 层成立

关键证据：
- 最新有效 packet:
  `D:\\gm-lite\\.gm_bus\\outbox\\4c0f9893-1a54-45a4-bd83-7bb686aab319.json`
- 该 packet 满足：
  - `payload.type.name = execution_request`
  - `task_id = bo1-task-001`
  - `to_participant = antigravity-1`
  - `review_required = true`
  - `context.original_payload_summary` 存在

关键源码：
- `D:\\gm-lite\\vscode-extension\\src\\core\\AutoProgressionService.ts`
- 这里今天已经做过净化：
  - 移除本地 success/writeback 直写链
  - 保留 claim/session 基础设施
  - 改为写真实 dispatch 到 `.gm_bus/outbox`

你现在不要重复修 UI，也不要重新讨论 webview。
你要做的是继续验证真实链是否真正推进：

1. 追踪 `4c0f9893-1a54-45a4-bd83-7bb686aab319.json` 之后的：
   - outbox
   - inbox
   - claims
   - writeback
   - continuations
   - feedback_events
2. 判断 `antigravity-1` 是否真实消费该 execution_request
3. 判断 review 是否真实出现
4. 判断 compliance 是否真实出现
5. 若链路仍断，明确断点发生在 execution / review / compliance 哪一层

执行要求：
- 先读代码和 `.gm_bus` 证据
- 不要立刻重构
- 不要把审计轮和修复轮混起来
- 结论必须基于真实文件证据，而不是猜测
```

