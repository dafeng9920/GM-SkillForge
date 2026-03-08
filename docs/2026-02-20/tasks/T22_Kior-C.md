# Task Skill Spec

```yaml
task_id: "T22"
executor: "Kior-C"
wave: "Wave 2"
depends_on: ["T17", "T18", "T19", "T20", "T21"]
estimated_minutes: 90

input:
  description: "完成 T17-T21 最终验收并输出 SEEDS-P0 Gate Decision（ALLOW/REQUIRES_CHANGES/DENY）"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "P0 DoD 作为验收标准"
    - path: "docs/2026-02-20/task_dispatch_T17-T21_seeds_p0.md"
      purpose: "批次规则与收口口径"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T17-T22.md"
      purpose: "汇总执行事实"
  constants:
    job_id: "L45-D4-SEEDS-P0-20260220-004"
    skill_id: "l45_seeds_p0_foundation"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_SEEDS_P0_INTEGRATION_REPORT_v1.md"
      type: "新建"
      schema_ref: "SEEDS P0 收口报告"
    - path: "docs/2026-02-20/verification/T22_gate_decision.json"
      type: "新建"
      schema_ref: "ALLOW|REQUIRES_CHANGES|DENY"
    - path: "docs/2026-02-20/verification/T22_execution_report.yaml"
      type: "新建"
      schema_ref: "Execution Report"
  constraints:
    - "必须逐条验证 P0 五项种子均满足 3要素（落盘+写入+读取）"
    - "至少一次演练后 registry/audit_events/usage 各新增 >=1 条"
    - "GateDecision 必含 ruleset_revision 与 provenance.repro_env（可占位）"
    - "任一关键项不满足不得 ALLOW"

deny:
  - "不得跳过自动化检查直接签 ALLOW"
  - "不得替上游任务补写实现代码"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_registry_store.py skillforge/tests/test_ruleset_revision_binding.py skillforge/tests/test_audit_event_writer.py skillforge/tests/test_usage_meter.py skillforge/tests/test_permit_required_policy.py"
      expect: "passed"
```

