# 任务 X5

## 唯一事实源
- `docs/2026-03-19/《外部执行与集成最小落地模块 v1｜Codex 主控分派提示词》.md`
- `docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_SCOPE.md`
- `docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md`

## 角色
- Execution: vs--cc3
- Review: Kior-A
- Compliance: Kior-C

## Task Envelope
```yaml
task_envelope:
  task_id: "X5"
  module: "external_execution_and_integration_minimal_landing"
  role: "execution"
  assignee: "vs--cc3"
  depends_on:
    - "X2"
    - "X4"
  parallel_group: "PG-03"
  source_of_truth:
    - "docs/2026-03-19/《外部执行与集成最小落地模块 v1｜Codex 主控分派提示词》.md"
    - "docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_SCOPE.md"
    - "docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md"
  writeback:
    execution_report: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_execution_report.md"
    review_report: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_review_report.md"
    compliance_attestation: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_compliance_attestation.md"
    final_gate: "docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_final_gate.md"
  acceptance_criteria:
    - "retry / compensation boundary 子面目录/文件骨架存在"
    - "retry / compensation 边界文档存在"
    - "runtime 排除说明存在"
    - "未进入 runtime"
    - "未实现真实补偿逻辑"
    - "未绕过 permit"
  hard_constraints:
    - "no runtime"
    - "no real compensation implementation"
    - "no permit bypass"
    - "no evidence or audit mutation"
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
- 建立 retry / compensation boundary 子面的最小目录骨架与 runtime 排除说明。

## 禁止项
- 不实现真实补偿逻辑
- 不引入 runtime
- 不绕过 permit
- 不改写 Evidence / AuditPack

## 并行 / 串行依赖
- 串行（第三波，依赖 X2/X4）

## 接力规则
- Execution 写回 `X5_execution_report.md` 后，进入 `REVIEW_TRIGGERED`
- Review 写回 `X5_review_report.md` 后，进入 `COMPLIANCE_TRIGGERED`
- Compliance 写回 `X5_compliance_attestation.md` 后，进入 `GATE_READY`

## 升级到主控官条件
- 出现 scope violation
- 前置依赖阻塞且无法自解
- 规格含糊无法合理推断
- review 给出 `FAIL`
- compliance 给出 `FAIL`
- 状态停滞超时

## 标准写回路径
- execution: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_execution_report.md`
- review: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_review_report.md`
- compliance: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 X5 的执行者 vs--cc3。

你不是审查者，也不是合规官。
你现在只做 retry / compensation boundary 最小落地，不做真实补偿实现。

必须产出：
- 子面目录/文件骨架
- retry / compensation 边界文档
- 与 runtime 的排除说明

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_execution_report.md`

写回后默认下一跳：
- `review`
- 接棒者：`Kior-A`
- review 写回目标：
  - `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_review_report.md`

若遇到以下情况，不得自行扩权，必须升级主控官：
- scope_violation
- blocking_dependency
- ambiguous_spec
```

## 发给 Review 的提示词
```text
你是任务 X5 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_review_report.md`

必须包含：
1. task_id: X5
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. retry / compensation boundary 的审查重点
5. 最少 EvidenceRef

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- compliance 写回目标：
  - `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_compliance_attestation.md`

若给出 `FAIL`，必须触发升级，不得自行判定结案
```

## 发给 Compliance 的提示词
```text
你是任务 X5 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X5_compliance_attestation.md`

必须包含：
1. task_id: X5
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
```
