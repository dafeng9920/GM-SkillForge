# gm-taskflow-tri-split-skill

> 版本: v1  
> 定位: `GM-LITE` 第一号系统级 skill  
> 用途: 固定主控官分派 -> execution -> review -> compliance -> `GATE_READY` 的标准流转方式

---

## 一句话定义

这是 `GM-LITE` 的任务流转 SOP skill。

它不负责业务实现。
它只负责把以下事情固定下来：

1. 三权分立任务卡格式
2. 标准写回路径
3. 下一跳接棒规则
4. `GATE_READY` 条件
5. backfill 规则
6. 主控官终验前检查项

---

## 适用场景

当任务属于以下任一类型时，应优先使用本 skill：

- 模块级 preparation
- 模块级 minimal implementation
- 模块级 validation
- 模块级 frozen judgment
- 需要 execution / review / compliance 三权分立的任务
- 需要标准写回和统一终验的任务

---

## 角色定义

### 主控官

负责：
- 冻结边界
- 冻结验收标准
- 建任务板
- 建任务卡
- 分派任务
- 回收结果
- 最终验收

不负责：
- 默认直接吞掉主实现

### Execution

负责：
- 按任务卡完成执行面工作
- 只写 `execution_report`

不负责：
- review
- compliance
- final gate

### Review

负责：
- 只做 review
- 只写 `review_report`

不负责：
- 重做 execution
- compliance
- final gate

### Compliance

负责：
- 只做 B Guard 式硬审
- 只写 `compliance_attestation`

不负责：
- execution
- review
- final gate

---

## 标准任务卡结构

每张任务卡必须至少包含：

1. `task_id`
2. 唯一事实源
3. Execution / Review / Compliance 角色
4. `Task Envelope`
5. 目标
6. 禁止项
7. 并行 / 串行依赖
8. 标准写回路径
9. Execution 提示词
10. Review 提示词
11. Compliance 提示词

---

## Task Envelope 最小字段

```yaml
task_envelope:
  task_id: "B1"
  module: "module_name"
  role: "execution"
  assignee: "agent_name"
  depends_on: []
  parallel_group: "PG-01"
  source_of_truth:
    - "scope.md"
    - "boundary_rules.md"
  writeback:
    execution_report: "..."
    review_report: "..."
    compliance_attestation: "..."
    final_gate: "..."
  acceptance_criteria:
    - "..."
  hard_constraints:
    - "..."
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
  next_hop: "review"
```

---

## Token 降噪与防流控规则

### 1. 最小事实源投影

当全局 `scope / boundary_rules / prompts` 过大时：

- 不要求执行体完整吞入全部全局文档
- 主控官应优先为子任务提供与当前任务直接相关的极简上下文投影
- 可使用：
  - `*_CONTEXT_SNAPSHOT.md`
  - 任务卡内嵌的局部边界摘录

规则：

- 子任务只读与当前任务直接相关的最小事实源
- 避免为了遵守规则而加载大量无关背景定义

### 2. 原子化写回

写回件只允许输出：

- 增量改动
- 核心结论
- 必要 EvidenceRef

禁止：

- 大段复述任务卡原文
- 把任务书再抄一遍到 `execution / review / compliance` 报告里
- 自引用式循环写回

规则：

- 写回件必须短、准、可验
- 以“本轮新增什么 / 发现什么 / 结论是什么”为主

### 3. 搜索范围节流

执行体默认只在当前任务相关目录内搜索。

除非任务卡显式允许，否则：

- 不跨库扫描
- 不全盘 `rg` 两个以上大型仓库
- 不因不确定性自动扩大搜索半径

规则：

- 搜索范围优先锁在：
  - 当前项目
  - 当前模块
  - 当前任务涉及目录
- 需要跨库时，必须在任务卡或主控放行中明确写出

### 4. 主控官回收最小化

主控官默认优先读取：

- task board
- report
- verification 文件名清单

只有出现 `FAIL / REQUIRES_CHANGES / 路径冲突 / 权威状态不一致` 时，才深入读正文。

### 5. 回填优先，不重跑优先

若任务已完成但标准路径缺件：

- 优先回填追认
- 不默认重跑整轮任务

### 6. 单任务上下文预算

单任务默认不应依赖超过：

- 1 张任务卡
- 2 份边界文档
- 1 份局部 snapshot

---

## 标准写回规则

每个任务默认三件套：

- `{task_id}_execution_report.md`
- `{task_id}_review_report.md`
- `{task_id}_compliance_attestation.md`

必要时补：

- `{task_id}_final_gate.md`

规则：

- Execution 只能写 `execution_report`
- Review 只能写 `review_report`
- Compliance 只能写 `compliance_attestation`
- 不写到标准路径，不算完成

---

## 下一跳规则

### Execution 写回后

必须明确：

- 下一跳类型：`review`
- 接棒者是谁
- review 写回目标文件

### Review 写回后

必须明确：

- 下一跳类型：`compliance`
- 接棒者是谁
- compliance 写回目标文件

### Compliance 写回后

若三件套齐全，则进入：

- `GATE_READY`

---

## 升级到主控官的条件

以下情况才允许升级：

- `scope_violation`
- `blocking_dependency`
- `ambiguous_spec`
- `review_deny`
- `compliance_fail`
- `state_timeout`

规则：

- execution 不得自行扩权
- review 给出 `FAIL` 不得自行结案
- compliance 给出 `FAIL` 不得自行结案

---

## Backfill 规则

如果实际已经做了，但没写入标准路径：

- 定性为 `回填追认`
- 不默认重做任务
- 只补缺失写回件

必须生成：

- backfill prompt
- 缺口总览表
- 主控官一句话判断标准

---

## GATE_READY 条件

只有以下条件同时满足，任务才进入 `GATE_READY`：

1. `execution_report` 存在
2. `review_report` 存在
3. `compliance_attestation` 存在
4. 当前无阻断性越界问题

---

## 主控官终验前检查项

主控官只检查：

1. 三件套是否齐全
2. 并行 / 串行依赖是否满足
3. 是否存在阻断性越界问题
4. 模块报告与任务板是否一致
5. 当前状态是否已进入 `GATE_READY` 或 `待验收`

缺一项，不终验。

---

## 默认状态词

只使用以下状态词：

- `未开始`
- `进行中`
- `待审查`
- `待合规`
- `待验收`
- `通过`
- `退回`

---

## 与半自动底座的关系

本 skill 默认兼容以下工具：

- `task_dispatcher_relay_helper.py`
- `task_board_updater.py`
- `task_dispatcher_auto_sender.py`

但本 skill 本身不依赖它们才能成立。

也就是说：

- 没有 helper 时，这是一套人工可执行 SOP
- 有 helper 时，这是一套半自动可执行 SOP

---

## 成功标准

如果用户只给任务包，而系统能稳定生成：

- 三权任务卡
- 标准写回路径
- 明确接棒者
- 明确下一跳
- 明确 `GATE_READY`

那么本 skill 就算成立。
