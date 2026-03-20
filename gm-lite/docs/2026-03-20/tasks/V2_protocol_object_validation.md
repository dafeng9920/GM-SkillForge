# 任务 V2

## 唯一事实源
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_BOUNDARY_RULES.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`

## 角色
- Execution: Antigravity-2
- Review: vs--cc1
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "V2"
  module: "gm_shared_task_bus_minimal_validation"
  role: "execution"
  assignee: "Antigravity-2"
  depends_on: []
  parallel_group: "PG-01"
  source_of_truth:
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_VALIDATION_V1_BOUNDARY_RULES.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_SCOPE.md"
    - "gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md"
  writeback:
    execution_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_execution_report.md"
    review_report: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_review_report.md"
    compliance_attestation: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_compliance_attestation.md"
    final_gate: "gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_final_gate.md"
  acceptance_criteria:
    - "6 个协议对象最小定义齐备"
    - "对象边界与命名清晰"
    - "无协议级阻断缺口"
  hard_constraints:
    - "no runtime"
    - "no sqlite"
    - "no plugin direct-connect"
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
  next_hop: "review"
```

## 目标
- 验证 6 个协议对象最小定义与边界。

## 禁止项
- 不扩协议范围
- 不补运行时字段
- 不引入 adapter 语义

## 并行 / 串行依赖
- 并行（第一波）

## 标准写回路径
- execution: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_execution_report.md`
- review: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_review_report.md`
- compliance: `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 V2 的执行者 Antigravity-2。
你不是审查者，也不是合规官。

唯一目标：
- 验证 6 个协议对象最小定义是否齐备、清晰、无阻断缺口

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`vs--cc1`
- review 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_review_report.md`
```

## 发给 Review 的提示词
```text
你是任务 V2 的审查者 vs--cc1。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_review_report.md`

必须包含：
1. task_id: V2
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. 协议对象审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_compliance_attestation.md`
```

## 发给 Compliance 的提示词
```text
你是任务 V2 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/V2_compliance_attestation.md`

必须包含：
1. task_id: V2
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
```
