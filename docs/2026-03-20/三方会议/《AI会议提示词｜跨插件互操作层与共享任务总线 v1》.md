# AI会议提示词｜跨插件互操作层与共享任务总线 v1

## 会议目的

请你作为外部架构审查者，评估以下问题：

- 当 Codex 插件、Claude Code 插件、Gemini/其他 agent 插件并不共享同一会话、同一内部状态、同一插件 API 时，
- GM 多agent智能中控插件应如何设计“跨插件互操作层”，让多个插件共享同一个任务现实，
- 从而实现：
  - 任务投递
  - 写回归档
  - 状态流转
  - 自动接力
  - 主控官升级

本次讨论不是让你写代码，而是让你从系统架构角度给出：
- 正确的分层
- 最小可落地方案
- 风险点
- 优先级
- 不该走的弯路

---

## 背景

我们当前已经有：

1. skill 层
- 主控官模式
- 三权分立
- execution / review / compliance / final gate

2. protocol 层
- task envelope
- state machine
- writeback contract
- auto relay rules
- escalation protocol

3. 半自动 helper 层
- relay helper
- task board updater
- auto dispatch sender

当前仍未打通的是：

- Codex 插件与 AI 军团插件之间的真实互通
- 自动发送
- 自动接单确认
- timeout / retry / escalation runtime

目前的真实情况是：

- Codex 插件：负责主控、拆分、验收、裁决
- Claude Code / Gemini 等插件：负责 execution / review / compliance
- 用户当前是多个插件之间的人工搬运总线

我们认为：

- 真正最大的难点，不是 prompt
- 而是“不同插件如何共享同一个任务现实”

---

## 已有共识

我们倾向于以下判断：

1. 插件不应直接互读聊天上下文
2. 应建立共享任务仓 / 共享状态层
3. 应通过统一协议交互，而不是自由文本互通
4. 应由插件 adapter 接入统一中间层
5. 最稳的第一步应是：
   - 共享文件总线
   - 再到 SQLite 状态层
   - 再到插件 adapter
   - 最后再做自动接力

---

## 请重点回答的 8 个问题

### 1. 架构判断
你是否同意：
- “跨插件共享任务总线”才是 GM 插件从 Light 走向 Core 的真正核心难点？

请给出：
- 同意 / 不同意
- 原因

### 2. 最小中间层
如果只能先做一个最小版本，你建议这个共享中间层最少包括哪些对象？

例如是否至少需要：
- task envelope
- dispatch packet
- receipt
- writeback
- escalation pack
- state log

### 3. 文件总线 vs 直接插件互调
你更推荐先做：
- 共享文件总线
- SQLite 状态层
- 直接插件 API 对接
- 其他方式

请说明：
- 哪种最稳
- 哪种最容易失控

### 4. receipt / acknowledgment
“接单确认”这一层最小应该如何设计？
请给出：
- 最小字段
- 状态变化
- 幂等建议

### 5. 状态机设计
当前状态机已有：
- PENDING
- ACCEPTED
- IN_PROGRESS
- WRITEBACK_DONE
- REVIEW_TRIGGERED
- REVIEW_DONE
- COMPLIANCE_TRIGGERED
- COMPLIANCE_DONE
- GATE_READY

请评估：
- 是否足够
- 是否还缺关键状态
- `REQUIRES_CHANGES` 应该是状态还是结果标签

### 6. 插件 adapter 设计
请给出：
- Codex adapter 的最小职责
- Claude adapter 的最小职责
- Gemini adapter 的最小职责

### 7. 最大风险点
请列出 3-5 个最大的系统级风险，例如：
- 状态不一致
- 重复投递
- receipt 丢失
- writeback 与任务错位
- escalation 误触发

并给出你建议的第一道防线。

### 8. 下一阶段建议
如果要把这个方向正式立项，你建议下一步最合理的是：
- `跨插件互操作层准备模块`
- `共享任务总线最小实现模块`
- `插件 adapter 准备模块`
- 其他

并请给出理由。

---

## 输出要求

请按以下结构输出：

1. 总判断
2. 你认同的已有方向
3. 你不同意或需要修正的地方
4. 最小可落地方案
5. 主要风险
6. 推荐的下一模块

要求：
- 不要泛泛而谈
- 直接面向多插件、多 agent、共享任务现实这个问题
- 优先给“最小可落地”的答案，而不是理想完全体
