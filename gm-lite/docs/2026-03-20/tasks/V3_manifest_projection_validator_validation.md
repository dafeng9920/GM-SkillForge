# 任务 V3

## 唯一事实源
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_BOUNDARY_RULES.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`

## 角色
- Execution: Kior-B
- Review: vs--cc3
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "V3"
  module: "gm_shared_task_bus_minimal_validation"
  role: "execution"
  assignee: "Kior-B"
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
    execution_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_execution_report.md"
    review_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_review_report.md"
    compliance_attestation: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_compliance_attestation.md"
    final_gate: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_final_gate.md"
  acceptance_criteria:
    - "manifest / task_board / projector / validator 边界清晰"
    - "样板链路可解释"
    - "无权威/投影视图混淆"
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
- 验证 manifest / projection / validator 边界与样板链。

## 禁止项
- 不补 watcher
- 不补 auto relay
- 不把 `task_board` 写成权威状态源

## 并行 / 串行依赖
- 串行（第二波，依赖 V1/V2）

## 标准写回路径
- execution: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_execution_report.md`
- review: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_review_report.md`
- compliance: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 V3 的执行者 Kior-B。
你不是审查者，也不是合规官。

唯一目标：
- 验证 manifest / projection / validator / 样板链关系是否自洽

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`vs--cc3`
- review 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_review_report.md`
```

## 发给 Review 的提示词
```text
你是任务 V3 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_review_report.md`

必须包含：
1. task_id: V3
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. manifest / projection / validator 审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_compliance_attestation.md`
```

## 发给 Compliance 的提示词
```text
你是任务 V3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V3_compliance_attestation.md`

必须包含：
1. task_id: V3
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
```
