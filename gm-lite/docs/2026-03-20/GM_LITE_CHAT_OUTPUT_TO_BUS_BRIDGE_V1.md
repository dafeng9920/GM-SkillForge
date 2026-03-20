# GM LITE Chat Output To Bus Bridge v1

## 一句话定义

`GM-LITE` 若要成为真实的多插件中控系统，必须解决：

- Codex 的输出不能只停留在聊天输入框
- Claude / Gemini / 其他插件不能依赖人工复制粘贴来接任务
- 任务必须从聊天产物转化为共享任务总线可消费的结构化对象

因此需要一层：

> `Chat Output -> Structured Object -> .gm_bus -> Plugin Adapter`

这就是 `chat-output-to-bus bridge`。

---

## 为什么它是成立前提

如果没有这层桥接：

- Codex 只能生成任务书
- 用户仍然要人工复制到其他插件
- 其他插件仍然只依赖自己的会话上下文
- `.gm_bus` 无法成为真正的共享任务现实

此时系统只能算：

- 高级任务生成器

而不能算：

- 多插件智能中控系统

---

## 问题的准确表述

真正的问题不是：

- “如何把一段聊天文字直接塞进另一个插件输入框”

而是：

- “如何把聊天输出转成插件无关的结构化任务对象，并写入共享任务总线，再由各插件 adapter 消费”

---

## 最小桥接链路

### 第 1 步：Codex 输出结构化对象

Codex 的输出不能只停留在自然语言。

必须能够落成以下任一对象：

- `task_card.md`
- `dispatch_packet.json`
- `escalation_pack.json`
- `final_gate_input.json`
- `next_hop.json`

### 第 2 步：写入 `.gm_bus`

结构化对象必须写入共享任务现实层，例如：

- `.gm_bus/outbox/`
- `.gm_bus/inbox/`
- `.gm_bus/writeback/`
- `.gm_bus/escalation/`
- `.gm_bus/archive/`

### 第 3 步：插件 adapter 读取

其他插件不读取 Codex 聊天上下文，而读取 `.gm_bus` 中的结构化对象。

插件 adapter 负责：

- 渲染任务输入
- 生成接单动作
- 生成标准写回

### 第 4 步：标准写回返回 `.gm_bus`

执行结果不回到聊天框作为唯一事实源，而回到：

- `.gm_bus/writeback/`
- 或标准 verification 路径

---

## Light 版边界

`GM-LITE` 当前只要求做到：

1. Codex 输出可落盘
2. 输出可转成 `.gm_bus` 对象
3. 插件可从 `.gm_bus` 读取任务
4. 写回可回到 `.gm_bus` 或标准 verification 路径

`GM-LITE` 当前不要求做到：

- 插件间直接消息互推
- 自动发送到其他插件输入框
- 自动接单确认 runtime
- timeout / retry runtime
- 完整插件 mesh

---

## Core 版边界

`GM-CORE` 后续才去解决：

- 插件 adapter 自动投递
- 自动接单确认
- receipt / lease / timeout
- 自动 relay
- 自动 escalation

---

## 与 `.gm_bus` 的关系

`.gm_bus` 是：

- 共享任务现实层

`chat-output-to-bus bridge` 是：

- 共享任务现实层的入口桥

没有这个入口桥，`.gm_bus` 只能承载静态文件，不能真正吸收 Codex / Claude / Gemini 的工作流输出。

---

## Light 版成立标准

只有当以下条件成立时，`GM-LITE` 才能宣称自己开始具备“多插件中控”属性：

1. Codex 任务输出可结构化落盘
2. `.gm_bus` 能接收这些结构化对象
3. 其他插件不依赖手工复制整段任务文本，也能消费这些对象
4. 写回件能重新进入共享任务现实

---

## 当前结论

当前 `GM-LITE` 已经具备：

- tri-split SOP
- shared task bus 准备定义
- 共享任务现实方向

当前仍未具备：

- chat output 到 bus 的正式桥接层

因此该问题属于：

> `GM-LITE` 成立的关键前置条件之一

不是可有可无的优化项。
