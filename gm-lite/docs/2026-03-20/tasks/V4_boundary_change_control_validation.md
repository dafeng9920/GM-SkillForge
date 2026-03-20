# 任务 V4

## 唯一事实源
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_BOUNDARY_RULES.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`

## 角色
- Execution: vs--cc1
- Review: Kior-A
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "V4"
  module: "gm_shared_task_bus_minimal_validation"
  role: "execution"
  assignee: "vs--cc1"
  depends_on:
    - "V1"
    - "V2"
  parallel_group: "PG-02"
  source_of_truth:
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_BOUNDARY_RULES.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md"
  writeback:
    execution_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_execution_report.md"
    review_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_review_report.md"
    compliance_attestation: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_compliance_attestation.md"
    final_gate: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_final_gate.md"
  acceptance_criteria:
    - "未混入 runtime / SQLite / adapter"
    - "change control 与实现现状一致"
    - "边界无阻断性越界"
  hard_constraints:
    - "no runtime"
    - "no sqlite"
    - "no adapter"
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
  next_hop: "review"
```

## 目标
- 验证边界、禁止项和 change control 是否仍被遵守。

## 禁止项
- 不借验证轮加新功能
- 不把 bridge 文档直接变实现
- 不提前做插件互通

## 并行 / 串行依赖
- 串行（第二波，依赖 V1/V2）

## 标准写回路径
- execution: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_execution_report.md`
- review: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_review_report.md`
- compliance: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 V4 的执行者 vs--cc1。
你不是审查者，也不是合规官。

唯一目标：
- 验证边界、禁止项和 change control 是否仍被遵守

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`Kior-A`
- review 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_review_report.md`
```

## 发给 Review 的提示词
```text
你是任务 V4 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_review_report.md`

必须包含：
1. task_id: V4
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. 边界 / change control 审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_compliance_attestation.md`
```

## 发给 Compliance 的提示词
```text
你是任务 V4 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V4_compliance_attestation.md`

必须包含：
1. task_id: V4
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
```
