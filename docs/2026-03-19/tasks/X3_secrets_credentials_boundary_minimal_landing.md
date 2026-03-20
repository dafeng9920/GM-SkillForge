# 任务 X3

## 唯一事实源
- `docs/2026-03-19/《外部执行与集成最小落地模块 v1｜Codex 主控分派提示词》.md`
- `docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_SCOPE.md`
- `docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md`

## 角色
- Execution: Antigravity-2
- Review: Kior-A
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "X3"
  module: "external_execution_and_integration_minimal_landing"
  role: "execution"
  assignee: "Antigravity-2"
  depends_on: []
  parallel_group: "PG-01"
  source_of_truth:
    - "docs/2026-03-19/《外部执行与集成最小落地模块 v1｜Codex 主控分派提示词》.md"
    - "docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_SCOPE.md"
    - "docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md"
  writeback:
    execution_report: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_execution_report.md"
    review_report: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_review_report.md"
    compliance_attestation: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_compliance_attestation.md"
    final_gate: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_final_gate.md"
  acceptance_criteria:
    - "secrets / credentials boundary 子面目录/文件骨架存在"
    - "secrets 分层规则文档存在"
    - "与 connector / gateway / policy 的边界说明存在"
    - "未进入 runtime"
    - "未接真实凭据"
    - "未改写 Evidence / AuditPack"
  hard_constraints:
    - "no real credentials"
    - "no runtime"
    - "no evidence mutation"
    - "no frozen mainline mutation"
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
    - "review_deny"
    - "compliance_fail"
    - "state_timeout"
  next_hop: "review"
```

## 目标
- 建立 secrets / credentials boundary 子面的最小目录骨架、分层规则与只读承接说明。

## 禁止项
- 不接真实凭据
- 不引入 runtime
- 不改写 Evidence / AuditPack
- 不回改 frozen 主线

## 并行 / 串行依赖
- 并行（第一波）

## 接力规则
- Execution 写回 `X3_execution_report.md` 后，进入 `REVIEW_TRIGGERED`
- Review 写回 `X3_review_report.md` 后，进入 `COMPLIANCE_TRIGGERED`
- Compliance 写回 `X3_compliance_attestation.md` 后，进入 `GATE_READY`

## 升级到主控官条件
- 出现 scope violation
- 前置依赖阻塞且无法自解
- 规格含糊无法合理推断
- review 给出 `FAIL`
- compliance 给出 `FAIL`
- 状态停滞超时

## 标准写回路径
- execution: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_execution_report.md`
- review: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_review_report.md`
- compliance: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 X3 的执行者 Antigravity-2。

你的唯一目标是：完成 secrets / credentials boundary 子面的最小落地骨架。

必须产出：
- 子面目录/文件骨架
- secrets 分层规则文档
- 与其余子面的边界说明

禁止：
- 真实凭据接线
- runtime
- 裁决逻辑
- 改写 frozen 主线

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_execution_report.md`

写回后默认下一跳：
- `review`

若遇到以下情况，不得自行扩权，必须升级主控官：
- scope_violation
- blocking_dependency
- ambiguous_spec
```

## 发给 Review 的提示词
```text
你是任务 X3 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_review_report.md`

必须包含：
1. task_id: X3
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. secrets / credentials boundary 的审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`

若给出 `FAIL`，必须触发升级，不得自行判定结案
```

## 发给 Compliance 的提示词
```text
你是任务 X3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X3_compliance_attestation.md`

必须包含：
1. task_id: X3
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
```
