# GM 多 Agent 智能中控插件封装说明 v1

## 定位

- 本文档只做插件线封装，不启动插件开发主线
- 当前主线仍然是 `GM-SkillForge` 内的 skill / protocol / helper 推进
- 插件线当前只负责承接目标、接口映射、后期集成方向

## 一句话定义

- GM 插件不是普通 IDE 辅助工具
- GM 插件的目标是：`多 agent 智能中控`

它最终应承载四类能力：

1. 任务中控
2. 协议中控
3. 治理中控
4. 证据中控

## 当前不做的事

- 不把当前主线迁移到 `D:/NEW-GM`
- 不在本轮启动插件代码开发
- 不让插件线打断 skill 系统推进
- 不把尚未稳定的方法直接固化进大插件

## 当前已经成熟、可后续映射进插件的资产

### 方法层

- 主控官模式
- 三权分立任务拆分
- task board
- execution / review / compliance / final gate 回收
- backfill 追认机制

### 协议层

- `task_envelope_schema.yaml`
- `state_machine.md`
- `auto_relay_rules.md`
- `writeback_contract.md`
- `escalation_protocol.md`

### 半自动工具层

- `tools/task_dispatcher_relay_helper.py`
- `tools/task_board_updater.py`
- `tools/task_dispatcher_auto_sender.py`

## 插件未来应承载的核心模块

### 1. Task Board Panel

- 展示模块 / 子任务 / 当前波次
- 展示 execution / review / compliance / final gate 状态
- 展示异常任务与阻断原因

### 2. Dispatch Center

- 读取 task envelope
- 生成 dispatch packet
- 触发下一跳任务
- 聚合 writeback 路径

### 3. Relay Engine

- execution -> review
- review -> compliance
- compliance -> final gate

### 4. Escalation Center

- 统一接收升级包
- 统一显示升级原因
- 统一拉起主控官验收

### 5. Evidence / Audit Projection

- 把 writeback / evidence / escalation 统一投影到可审查面板

## 与 `D:/NEW-GM` 大框架的对位关系

### 宪法层 / 治理层

- 保持在 `NEW-GM` 既有宪法、门禁、北斗体系之上
- 插件不得削弱 Fail-Closed 和红灯规则

### 执行层

- 插件只做调度与承接
- 不得替代 Governor / Gate / Review / Release / Audit 裁决

### 支撑层

- 插件应复用 EvidencePack / DecisionPack / SedimentationPack 的证据思路
- 不得创造一套与主线冲突的新证据口径

## 当前阶段的约束

- 插件线现在只能做“封装说明”
- 后续是否启动插件开发，前提必须是：
  1. skill 主线继续稳定
  2. dispatcher protocol 继续可用
  3. 半自动 helper 在真实样板任务上能持续减轻体力劳动

## 后续启动条件

只有在满足以下条件后，才建议进入插件准备模块：

1. 至少 2 个真实任务样板已验证 relay / sender / updater 有效
2. 主控官确认当前半自动工具确实减少了手工转发和状态判断
3. skill 系统没有被插件线抢节奏

## 当前结论

- 插件线应先封装，后开发
- 当前主线仍然是 skill / protocol / helper
- 插件是后续承接平台，不是当前主战场

## gstack vs GM 多agent智能中控 对照表

| 对照项 | gstack | GM 多agent智能中控 |
|---|---|---|
| 核心定位 | 岗位化 AI 工作流 | 岗位化 AI 工作流 + 调度中枢 + 治理中枢 |
| 主要形态 | Claude Code 斜杠命令 / role prompt system | 本地中控插件 / 协议层 / helper / 后续运行时 |
| 核心目标 | 让 AI 扮演不同专业岗位，提高交付效率 | 让多 agent 在可治理、可审计、可阻断条件下协作推进 |
| 关注重点 | 岗位职责、工作分工、交付速度 | 任务投递、状态流转、写回契约、升级路径、Fail-Closed |
| 人类角色 | 发起者 / 决策者 | 发起者 / 最终确认者 / 主控官监督对象 |
| AI 角色 | CEO、review、ship、qa、design 等岗位 | execution、review、compliance、final gate、主控官等岗位 |
| 是否强调岗位化 | 强 | 强 |
| 是否强调三权分立 | 弱到中 | 强 |
| 是否强调标准写回 | 相对弱 | 强，必须有 execution / review / compliance / final gate |
| 是否有显式状态机 | 不一定 | 有，`task_dispatcher_protocol` 已明确 |
| 是否有自动接力设计 | 倾向由命令链串联 | 显式存在 `relay helper / auto sender / task board updater` |
| 是否有 permit / evidence / audit pack 约束 | 弱 | 强 |
| 是否有 fail-closed / 红灯治理 | 弱 | 强 |
| 是否要求执行层不得裁决 | 不一定强调 | 强调，执行层只承接不裁决 |
| 是否适合作为公司工作台 | 是 | 是，但治理密度更高 |
| 是否适合作为多 agent 中控插件底座 | 部分适合 | 直接面向该目标设计 |

## 对照结论

- gstack 解决的是：`如何让 AI 形成岗位化团队`
- GM 多agent智能中控要解决的是：`如何让岗位化 AI 团队在治理、证据、状态机和升级协议下稳定协作`

一句话：

- `gstack` 更像岗位化 AI 公司工作台
- `GM 多agent智能中控` 更像岗位化 AI 公司工作台 + 调度总线 + 治理总线 + 审计总线

## 当前吸收策略

当前对 gstack 的吸收应只限于：

1. 岗位化思路
2. 命令即岗位的提示词组织方式
3. 人类从“亲自干”转向“定规则 + 审批”的组织逻辑

当前不直接照搬的部分：

1. 只靠 slash command 组织流程
2. 缺少标准写回契约的岗位切换
3. 缺少 permit / evidence / audit pack / escalation 的治理约束

## 当前定位不变

- gstack 可作为岗位层参考
- GM 插件仍按“多agent智能中控”定位封装
- 当前依然不启动插件主线开发，不抢 `GM-SkillForge` 的 skill 主线

## GM 插件 Light 的用户原则

### 核心原则

- 用户需要这些能力存在：
  - 协议
  - 任务卡
  - 写回路径
  - 状态机
  - 升级条件
- 但用户不应承担这些能力的手工配置劳动

一句话：

- `用户给任务，插件补协议`

### 用户真正想要的不是

- 手工写 `task envelope`
- 手工配 `writeback contract`
- 手工定义 `state machine`
- 手工列 `escalation trigger`
- 手工拼 execution / review / compliance 任务卡

### 用户真正想要的是

1. 给出需求或模块任务包
2. 看见插件自动拆分任务
3. 看见插件自动挂接 execution / review / compliance
4. 看见状态自动推进
5. 看见主控官最终验收结果

### 因此 Light 版必须内置

1. 固定 skill / preset
2. 默认 `task envelope`
3. 默认 `writeback contract`
4. 默认 `state machine`
5. 默认 `next_hop / escalation rules`
6. 默认任务卡模板
7. 默认 backfill 机制

### 不应转嫁给用户的复杂性

- 协议复杂性
- 状态流转复杂性
- 写回规则复杂性
- 升级路径复杂性

这些复杂性应该由：
- 插件内部系统能力
- 内置模板
- 内置 preset
- 内置 skill runtime

共同消化。

### Light 版产品判断标准

如果插件还要求用户每次都手工完成以下动作：

- 定协议
- 定任务卡
- 定写回路径
- 定状态机
- 定升级条件

那么它还不算真正的 GM 插件 Light，只能算“流程辅助工具”。

只有当插件做到以下状态，才算方向正确：

- 协议存在，但由插件默认补全
- 任务卡存在，但由插件自动生成
- 写回路径存在，但由插件自动挂接
- 状态机存在，但由插件自动投影
- 升级条件存在，但由插件自动判定

## 当前对 Light 版的补充定位

- Light 版的价值，不是让用户学会协议
- Light 版的价值，是让插件把协议吃掉
- 用户只负责给任务、看状态、收结果

## Light / Core 路线的能力上限说明

### 当前人工上限问题

当前多 agent 协作的真实瓶颈，不只是模型数量，而是：

1. 人工转发上限
2. 人工状态跟踪上限
3. 人工缺件检查上限
4. 人工升级判断上限

也就是说，限制系统规模的往往不是 agent 本身，而是：
- 主控官能否盯住
- 用户能否转发得过来
- 人脑能否记住谁该接谁

### Light 版的作用

Light 版即使不做真实自动互通，也应先把以下上限往上抬：

1. 状态判断自动化
2. 下一跳生成自动化
3. 任务板投影自动化
4. 缺件识别自动化
5. dispatch packet 生成自动化

这意味着：
- agent 数量的上限开始从“人工可控上限”向“系统可控上限”迁移

### Core 版的作用

Core 版一旦实现：

1. 真实互通
2. 自动发送
3. 接单确认
4. timeout / retry / recovery
5. escalation center
6. state store / event log

那么系统的 agent 上限就不再主要受用户人工转发能力限制，而主要取决于：

- 本地机器性能
- 通道承载能力
- 状态存储与调度能力

### 能力上限的一句话定义

- Light：提升“人工管理多 agent”的上限
- Core：把上限提升到“系统管理多 agent”的级别

### 与 gstack 的差异

gstack 更偏：
- 岗位化提高单体效率

GM 多agent智能中控如果做成，则更偏：
- 岗位化 + 中控化 + 协议化
- 提升可控 agent 数量上限

### 当前结论

- 插件价值不仅在于减轻用户劳动
- 还在于把 agent 上限从“人脑可管理规模”提升到“系统可管理规模”

## 跨插件互操作层：真正的核心难点

### 问题定义

当前系统不是单一插件内部协作，而是：

- Codex 插件负责主控、拆分、验收、裁决
- Claude Code / Gemini / 其他 AI 军团插件负责 execution / review / compliance
- 用户当前充当多个插件之间的人工搬运总线

因此，真正最大的难点不是：
- prompt 怎么写
- task card 怎么写
- task board 怎么显示

而是：
- 不同插件、不同会话、不同 agent 容器，如何共享同一个任务现实

### 当前壁垒

1. 会话隔离
- Codex 插件与 Claude / Gemini 插件天然处于不同上下文
- 双方无法直接共享内部状态

2. 插件 API 不统一
- 不同插件有不同的输入输出方式
- 不能假设它们天然可互调

3. 输出格式不统一
- 一个插件可能输出聊天文本
- 一个插件可能输出 patch
- 一个插件可能只在自身会话中宣告完成

4. 缺少共享状态层
- 当前没有统一的 task store / receipt store / event log / state store

### 正确解法方向

不是让插件直接“读懂彼此聊天记录”，而是建立：

1. 共享任务仓
2. 统一消息格式
3. 各插件 adapter

也就是：

- 插件不直接互连
- 插件都接入同一个共享协议层和共享状态层

### 最小共享中间层

后续应优先考虑的中间层最小组成：

1. 共享任务仓
- 存 task envelope
- 存 dispatch packet
- 存 receipt
- 存 writeback
- 存 escalation pack

2. 统一消息格式
- `dispatch_packet.json`
- `receipt.json`
- `execution_report.md`
- `review_report.md`
- `compliance_attestation.md`
- `final_gate_input.json`

3. 插件适配器
- Codex adapter
- Claude adapter
- Gemini / 其他 agent adapter
- OpenClaw adapter

### 推荐实现顺序

#### Phase 1
- 共享文件总线
- 不追求插件直接互调
- 先实现“都读写同一个共享目录”

#### Phase 2
- SQLite 状态层
- 把 task state / receipts / event log 稳定下来

#### Phase 3
- 插件 adapter
- 让 Codex / Claude / Gemini / OpenClaw 都接入同一协议层

#### Phase 4
- 自动接力
- 自动升级
- 自动超时恢复

### 当前结论

- 跨插件互操作层不是小功能
- 这是 GM 插件从 Light 走向 Core 的真正硬骨头
- 但这层一旦打通，用户就不再需要做人肉中继站
