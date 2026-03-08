# Task Skill Spec

```yaml
task_id: "T40"
executor: "Kior-C"
wave: "Wave 2"
depends_on: ["T35", "T36", "T37", "T38", "T39"]
estimated_minutes: 90

input:
  description: "前端 v1.0 主控收口：汇总验收并输出 READY_FOR_FE_V1.0 判定"
  context_files:
    - path: "docs/2026-02-20/task_dispatch_T35-T40_frontend_v1.0.md"
      purpose: "批次规则与收口标准"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T35-T40.md"
      purpose: "收集执行事实与证据"
  constants:
    job_id: "L45-FE-V10-20260220-007"
    skill_id: "l45_frontend_v10_execution_pack"
  execution_guard:
    proposal_guard_ref: "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    execution_guard_ref: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    required_artifacts:
      - "docs/2026-02-20/verification/T40_execution_contract.json"
      - "docs/2026-02-20/verification/T40_compliance_attestation.json"
      - "docs/2026-02-20/verification/T40_evidence_refs.json"
      - "docs/2026-02-20/verification/T35-T40_execution_guard_index.yaml"
    must_pass:
      - "T35-T39 compliance_decision all PASS"
      - "T35-T39 contract_hash_match all YES"
      - "all required guard artifacts exist"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_FRONTEND_V10_INTEGRATION_REPORT_v1.md"
      type: "新建"
      schema_ref: "前端 v1.0 集成验收报告"
    - path: "docs/2026-02-20/verification/T40_gate_decision.json"
      type: "新建"
      schema_ref: "ALLOW|REQUIRES_CHANGES|DENY"
    - path: "docs/2026-02-20/verification/T40_execution_report.yaml"
      type: "新建"
      schema_ref: "Execution Report"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T35-T40.md"
      type: "更新"
      schema_ref: "总控最终判定"
  constraints:
    - "必须给出实现/联调/基线三判定"
    - "必须核验 5 页路由已接线"
    - "必须核验 run_id/evidence_ref 交互链路"

deny:
  - "不得在并行任务未完成时提前签核"

gate:
  auto_checks:
    - command: "cd ui/app; npm run build"
      expect: "passed"
  deny_without_execution_guard: true
```
