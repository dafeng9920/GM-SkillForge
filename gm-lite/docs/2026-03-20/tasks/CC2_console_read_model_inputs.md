# 任务 CC2

## 唯一事实源
- `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_BOUNDARY_RULES.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md`
- `gm-lite/docs/2026-03-20/GM_LITE_CHAT_OUTPUT_TO_BUS_BRIDGE_V1.md`

## 角色
- Execution: Antigravity-2
- Review: vs--cc1
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "CC2"
  module: "gm_lite_controller_console_preparation"
  role: "execution"
  assignee: "Antigravity-2"
  depends_on: []
  parallel_group: "PG-01"
  source_of_truth:
    - "gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_BOUNDARY_RULES.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md"
    - "gm-lite/docs/2026-03-20/GM_LITE_CHAT_OUTPUT_TO_BUS_BRIDGE_V1.md"
  writeback:
    execution_report: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_execution_report.md"
    review_report: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_review_report.md"
    compliance_attestation: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_compliance_attestation.md"
    final_gate: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_final_gate.md"
  acceptance_criteria:
    - "控制台最小读取对象清晰"
    - "输入源边界清晰"
    - "未混入写源语义"
  hard_constraints:
    - "no ui"
    - "no watcher"
    - "no adapter"
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
  next_hop: "review"
```

## 目标
- 定义控制台读取对象与最小视图输入。

## 标准写回路径
- execution: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_execution_report.md`
- review: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_review_report.md`
- compliance: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 CC2 的执行者 Antigravity-2。
你不是审查者，也不是合规官。

唯一目标：
- 定义 controller console 的最小读取对象与输入源边界

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`vs--cc1`
- review 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_review_report.md`
```

## 发给 Review 的提示词
```text
你是任务 CC2 的审查者 vs--cc1。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_review_report.md`

必须包含：
1. task_id: CC2
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. 读取对象 / 输入源边界审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_compliance_attestation.md`
```

## 发给 Compliance 的提示词
```text
你是任务 CC2 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC2_compliance_attestation.md`
```
