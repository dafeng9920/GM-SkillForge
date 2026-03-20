# 任务 CI3

## 唯一事实源
- `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_REPORT.md`

## 角色
- Execution: Kior-B
- Review: vs--cc3
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "CI3"
  module: "gm_lite_controller_console_minimal_implementation"
  role: "execution"
  assignee: "Kior-B"
  depends_on:
    - "CI1"
    - "CI2"
  parallel_group: "PG-02"
  source_of_truth:
    - "gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md"
    - "gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_PREPARATION_V1_REPORT.md"
  writeback:
    execution_report: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_execution_report.md"
    review_report: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_review_report.md"
    compliance_attestation: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_compliance_attestation.md"
    final_gate: "gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_final_gate.md"
  acceptance_criteria:
    - "状态视图骨架存在"
    - "告警视图骨架存在"
    - "gate-ready 视图骨架存在"
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
- 落状态、告警、gate-ready 视图骨架。

## 标准写回路径
- execution: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_execution_report.md`
- review: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_review_report.md`
- compliance: `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_compliance_attestation.md`

## Token / Search Guard
- 默认只读取当前任务直接相关的最小事实源
- 写回只记录增量改动、核心结论、必要 EvidenceRef
- 默认只允许在 `gm-lite/` 当前模块相关目录内搜索，不跨库扫描

## 发给 Execution 的提示词
```text
你是任务 CI3 的执行者 Kior-B。
你不是审查者，也不是合规官。

唯一目标：
- 落状态视图、告警视图、gate-ready 视图骨架

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`vs--cc3`
- review 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_review_report.md`

若遇到以下情况，不得自行扩权，必须升级主控官：
- scope_violation
- blocking_dependency
- ambiguous_spec
```

## 发给 Review 的提示词
```text
你是任务 CI3 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_review_report.md`

必须包含：
1. task_id: CI3
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. 状态/告警/gate-ready 视图审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_compliance_attestation.md`

若给出 FAIL，必须触发升级，不得自行判定结案
```

## 发给 Compliance 的提示词
```text
你是任务 CI3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/CI3_compliance_attestation.md`

必须包含：
1. task_id: CI3
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
```
