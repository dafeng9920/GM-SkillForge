# Task Skill Spec

```yaml
task_id: "T27"
executor: "Kior-C"
wave: "Wave 2"
depends_on: ["T23", "T24", "T25", "T26"]
estimated_minutes: 90

input:
  description: "完成 T23-T26 最终验收并输出 SEEDS-P1 Gate Decision（ALLOW/REQUIRES_CHANGES/DENY）"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "P1 种子与DoD口径"
    - path: "docs/2026-02-20/task_dispatch_T23-T27_seeds_p1.md"
      purpose: "批次规则与收口目标"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T23-T27.md"
      purpose: "汇总执行事实"
  constants:
    job_id: "L45-D5-SEEDS-P1-20260220-005"
    skill_id: "l45_seeds_p1_guardrails"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_SEEDS_P1_INTEGRATION_REPORT_v1.md"
      type: "新建"
      schema_ref: "SEEDS P1 收口报告"
    - path: "docs/2026-02-20/verification/T27_gate_decision.json"
      type: "新建"
      schema_ref: "ALLOW|REQUIRES_CHANGES|DENY"
    - path: "docs/2026-02-20/verification/T27_execution_report.yaml"
      type: "新建"
      schema_ref: "Execution Report"
  constraints:
    - "P1 四项种子均满足 3要素（落盘+写入+读取）"
    - "必须验证 feature flag 与 provenance 占位可被读取"
    - "任一关键项失败不得 ALLOW"

deny:
  - "不得跳过自动化检查直接签 ALLOW"
  - "不得替上游任务补写实现代码"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_regression_seed_smoke.py skillforge/tests/test_i18n_contract_loader.py skillforge/tests/test_feature_flag_loader.py skillforge/tests/test_provenance_loader.py"
      expect: "passed"
```

