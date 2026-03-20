# 任务 CC4

## 唯一事实源
- `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_BOUNDARY_RULES.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md`

## 角色
- Execution: vs--cc1
- Review: Kior-A
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "CC4"
  module: "gm_lite_controller_console_preparation"
  role: "execution"
  assignee: "vs--cc1"
  depends_on:
    - "CC1"
    - "CC2"
  parallel_group: "PG-02"
  source_of_truth:
    - "gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_BOUNDARY_RULES.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md"
  writeback:
    execution_report: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_execution_report.md"
    review_report: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_review_report.md"
    compliance_attestation: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_compliance_attestation.md"
    final_gate: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_final_gate.md"
  acceptance_criteria:
    - "不做什么清晰"
    - "change control 可执行"
    - "Light 版边界清晰"
  hard_constraints:
    - "no ui"
    - "no watcher"
    - "no runtime"
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
  next_hop: "review"
```

## 目标
- 定义控制台当前不做什么与 change control。

## 标准写回路径
- execution: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_execution_report.md`
- review: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_review_report.md`
- compliance: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 CC4 的执行者 vs--cc1。
你不是审查者，也不是合规官。

唯一目标：
- 定义 controller console 当前不做什么与 change control

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`Kior-A`
- review 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_review_report.md`
```

## 发给 Review 的提示词
```text
你是任务 CC4 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_review_report.md`

必须包含：
1. task_id: CC4
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. exclusions / change control 审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_compliance_attestation.md`
```

## 发给 Compliance 的提示词
```text
你是任务 CC4 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_preparation/CC4_compliance_attestation.md`
```
