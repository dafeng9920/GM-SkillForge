# controller-orchestration-tri-split-skill

> 版本: v1  
> 适用场景: Codex 只做主控官，不做主实现；AI 军团负责执行 / 审查 / 合规；任务必须按三权分立、并行/串行依赖、标准写回路径、统一终验推进。

---

## 触发词

- `主控官模式`
- `拆分和分派给 AI 军团`
- `三权分立`
- `执行/审查/合规`
- `任务板`
- `回填追认`
- `统一终验`
- `并行/串行`
- `主控官速览`

---

## 目标

把模块推进固化成一套可重复使用的主控流程，让 Codex 一开工就知道：
- 先冻结什么
- 先写哪些主控文档
- 任务怎么拆
- 谁执行 / 谁审查 / 谁合规
- 哪些任务并行，哪些串行
- 每个结果必须写回哪个文档
- 缺件时如何 backfill
- 什么时候允许终验
- 如何按 dispatcher protocol 组织任务信封、状态流转、自动接力、升级到主控官
- 何时默认启用半自动底座（relay helper / task board updater / auto sender）

---

## 主控官职责

Codex 只负责：
- 冻结模块边界
- 冻结验收标准
- 建模块任务总表
- 建三权任务卡
- 标注并行 / 串行依赖
- 规定标准写回路径
- 回收军团产物
- 做统一终验
- 给出 `通过 / 局部退回 / 整体退回`

默认不得：
- 吞掉全部实现
- 绕过军团直接宣布完成
- 缺 `review / compliance` 文档就终验
- 用口头“做完了”代替标准回收件

如果需要自己动手，只允许：
- 极小补丁
- 命名修正
- 导出修正
- 非语义性整合

---

## 开工顺序

### 1. 先冻结模块，不先写实现

优先生成这批主控文档：
- `..._SCOPE.md`
- `..._BOUNDARY_RULES.md`
- `..._TASK_BOARD.md` 或 `..._TASK_SPLIT.md`
- `..._ACCEPTANCE.md`
- `..._REPORT.md`
- `..._CHANGE_CONTROL_RULES.md`
- `..._PROMPTS.md`

如果是返工/补件/冻结类模块，再补：
- `..._REWORK_PROMPTS.md`
- `..._BACKFILL_PROMPTS.md`
- `..._FROZEN_*.md`

### 2. 先定波次，再定任务

每个模块都先写清：
- 第一波哪些任务并行
- 第二波哪些任务依赖第一波
- 第三波哪些任务必须串行

默认规则：
- 无依赖冲突的任务可并行
- 后置任务必须等依赖任务完成回收
- Final Gate 必须等所有要求的 `execution / review / compliance` 齐全

### 3. 每张任务卡必须写死

每张任务卡必须明确：
1. `task_id`
2. `module`
3. `executor`
4. `reviewer`
5. `compliance_officer`
6. 唯一事实源
7. 目标
8. 禁止项 / 硬约束
9. 标准写回路径
10. 并行 / 串行依赖
11. `parallel_group`
12. `depends_on`
13. `acceptance_criteria`
14. `escalation_trigger`
15. `next_hop`

没有第 8 项，不发军团。

### 4. 标准写回路径必须先存在

每个任务默认三份回收件：
- `.../{task_id}_execution_report.md`
- `.../{task_id}_review_report.md`
- `.../{task_id}_compliance_attestation.md`

必要时再补：
- `.../{task_id}_final_gate.md`

无标准写回路径，不算任务书完成。

### 5. 主控官速览必须单独可读

任务板和 backfill 文档都必须先让主控官一眼看懂：
- 当前缺什么
- 谁补
- 写回哪个文件
- 补完后如何终验

先给总览表，再给逐任务提示词。

### 6. 协议版任务卡优先于旧版任务卡

只要模块允许使用半自动底座，默认优先生成协议版任务卡。

协议版任务卡至少要内嵌：
- `Task Envelope`
- `接力规则`
- `升级到主控官条件`
- 更完整的 review / compliance 写回要求

如果旧任务卡没有这些元素，先升级任务卡，再发军团。

---

## 三权分立写法

### Execution 提示词必须包含
- 你是谁
- 你不是谁
- 唯一目标
- 允许项
- 禁止项
- 必须写回的 `execution_report.md`
- 必须包含的字段

### Review 提示词必须包含
- 你是该任务审查者
- 你不是重做 execution
- 必须写回的 `review_report.md`
- 必须写 `PASS / REQUIRES_CHANGES / FAIL`
- 必须给 `EvidenceRef`

### Compliance 提示词必须包含
- 你是该任务合规官
- 你只做 B Guard 式硬审
- 必须写回的 `compliance_attestation.md`
- 必须写 `PASS / REQUIRES_CHANGES / FAIL`
- 必须检查 Zero Exception Directives

---

## 任务板最低要求

任务总表至少包含：

| Task | Scope | Execution | Review | Compliance | 并行/串行 | 目标 | 状态 |
|---|---|---|---|---|---|---|---|

并在表下再补：
- 统一回收路径
- Codex 回收规则
- 当前主控裁决
- Codex 最终验收区

状态词只用：
- `未开始`
- `进行中`
- `待审查`
- `待合规`
- `待验收`
- `通过`
- `退回`

---

## 回填追认规则

如果实际已经做了 review / compliance，但没写入标准文档：
- 定性为 `回填追认缺口`
- 不重做 execution
- 不重做原判断
- 只补标准写回件

这时必须单独生成：
- `..._BACKFILL_PROMPTS.md`

且该文档最前面必须有：
- 主控官速览
- 缺口总览表
- 谁补
- 写回哪个文件
- 主控官一句话判断标准

---

## Dispatcher Protocol 默认规则

主控官模式默认带以下 5 件协议对象一起工作：
- `task_envelope_schema`
- `state_machine`
- `writeback_contract`
- `auto_relay_rules`
- `escalation_protocol`

### Task Envelope 最小字段
- `task_id`
- `module`
- `role`
- `assignee`
- `depends_on`
- `parallel_group`
- `source_of_truth`
- `writeback`
- `acceptance_criteria`
- `hard_constraints`
- `escalation_trigger`

### 最小状态流转
- `PENDING`
- `ACCEPTED`
- `IN_PROGRESS`
- `WRITEBACK_DONE`
- `REVIEW_TRIGGERED`
- `REVIEW_DONE`
- `COMPLIANCE_TRIGGERED`
- `COMPLIANCE_DONE`
- `GATE_READY`

### 默认自动接力
- execution 写回后，生成 review 下一跳
- review 写回后，生成 compliance 下一跳
- compliance 写回后，任务进入 `GATE_READY`

### 默认半自动底座

主控官在以下场景应默认考虑调用本地 helper：
- execution 已写回，需要判断下一跳
- review/compliance 已写回，需要判断是否 `GATE_READY`
- 任务板状态需要从写回件投影
- 需要为下一跳生成可直接转发的 dispatch 包

默认工具：
- `tools/task_dispatcher_relay_helper.py`
- `tools/task_board_updater.py`
- `tools/task_dispatcher_auto_sender.py`

这些工具负责：
- 判断状态
- 生成下一跳
- 更新任务板
- 生成 dispatch packet / dispatch message

它们不负责：
- 真正自动发送
- 自动接单确认
- 自动重试 / 超时恢复

### 默认升级条件
- `scope_violation`
- `blocking_dependency`
- `ambiguous_spec`
- `review_deny`
- `compliance_fail`
- `state_timeout`

---

## 终验规则

只有以下条件全部满足，主控官才能终验：
1. 所有要求的回收件都在标准路径中存在
2. 并行 / 串行依赖顺序满足
3. 无阻断性越界问题
4. 文档与骨架口径一致
5. 模块边界未被扩张

不满足时：
- 明确 `局部退回` 或 `整体退回`
- 指出哪个任务面出问题
- 指出退回到哪个边界

---

## 最常见的 5 个错误

1. 任务卡没写具体回填路径
2. Review / Compliance 有角色名，没有具体提示词
3. 并行 / 串行依赖只在脑子里，没有写入文档
4. 回收时把“口头说完成”当成“标准回收完成”
5. 发现缺件后重做任务，而不是先做 backfill

优先避免这 5 个错误。

---

## 启动模板

开工时按这个顺序：
1. 冻结模块边界
2. 冻结验收标准
3. 建任务板
4. 建 task envelope
5. 建任务卡
6. 写并行 / 串行波次
7. 写标准回收路径
8. 写 next_hop / escalation 规则
9. 发军团
10. 回收
11. 必要时运行 relay / updater / sender
12. 终验

---

## 参考

使用时先看：
- [multi-ai-collaboration.md](../../multi-ai-collaboration.md)
- [references/templates.md](references/templates.md)
- [task_envelope_schema.yaml](../../docs/2026-03-19/task_envelope_schema.yaml)
- [state_machine.md](../../docs/2026-03-19/state_machine.md)
- [writeback_contract.md](../../docs/2026-03-19/writeback_contract.md)
- [auto_relay_rules.md](../../docs/2026-03-19/auto_relay_rules.md)
- [escalation_protocol.md](../../docs/2026-03-19/escalation_protocol.md)
