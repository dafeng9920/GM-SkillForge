# 任务 B4

## 唯一事实源
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_PREPARATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_PREPARATION_V1_BOUNDARY_RULES.md`

## 角色
- Execution: vs--cc1
- Review: Kior-A
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "B4"
  module: "gm_shared_task_bus_preparation"
  role: "execution"
  assignee: "vs--cc1"
  depends_on:
    - "B1"
    - "B2"
  parallel_group: "PG-02"
  source_of_truth:
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_PREPARATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_PREPARATION_V1_BOUNDARY_RULES.md"
  writeback:
    execution_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_execution_report.md"
    review_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_review_report.md"
    compliance_attestation: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_compliance_attestation.md"
    final_gate: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_final_gate.md"
  acceptance_criteria:
    - "Light 版当前不做事项清晰"
    - "change control 规则清晰"
    - "禁止项清晰"
  hard_constraints:
    - "no runtime"
    - "no adapter implementation"
    - "no plugin ui"
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
  next_hop: "review"
```

## 目标
- 定义 `GM-LITE` 当前明确不做的事项与 change control 规则。

## 禁止项
- 不进入实现
- 不提前定义 Core 版 runtime
- 不偷渡插件互调

## 并行 / 串行依赖
- 串行（第二波，依赖 B1/B2）

## 标准写回路径
- execution: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_execution_report.md`
- review: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_review_report.md`
- compliance: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_compliance_attestation.md`

## Token / Search Guard
- 默认只读取当前任务直接相关的最小事实源，不全量吞入无关全局定义
- 写回只记录增量改动、核心结论、必要 EvidenceRef
- 默认只允许在 `gm-lite/` 当前模块相关目录内搜索，不跨库扫描

## 发给 Execution 的提示词
```text
你是任务 B4 的执行者 vs--cc1。

你不是审查者，也不是合规官。
你的唯一目标是：定义 GM-LITE 当前明确不做什么，以及对应的 change control。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`Kior-A`
- review 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_review_report.md`

若遇到以下情况，不得自行扩权，必须升级主控官：
- scope_violation
- blocking_dependency
- ambiguous_spec
```

## 发给 Review 的提示词
```text
你是任务 B4 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_review_report.md`

必须包含：
1. task_id: B4
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. runtime exclusions / change control 审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_compliance_attestation.md`

若给出 `FAIL`，必须触发升级，不得自行判定结案
```

## 发给 Compliance 的提示词
```text
你是任务 B4 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/B4_compliance_attestation.md`

必须包含：
1. task_id: B4
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
```
