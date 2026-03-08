# Task Skill Spec

```yaml
task_id: "T33"
executor: "Kior-C"
wave: "Wave 2"
depends_on: ["T28", "T29", "T30", "T31", "T32"]
estimated_minutes: 90

input:
  description: "P2 技术收口：完成 T28-T32 验收并输出 Gate Decision"
  context_files:
    - path: "docs/2026-02-20/task_dispatch_T28-T34.md"
      purpose: "批次规则与收口标准"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T28-T34.md"
      purpose: "汇总执行事实"
  constants:
    job_id: "L45-D6-SEEDS-P2-20260220-006"
    skill_id: "l45_seeds_p2_operationalization"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_SEEDS_P2_TECH_CLOSEOUT_v1.md"
      type: "新建"
      schema_ref: "技术收口报告"
    - path: "docs/2026-02-20/verification/T33_gate_decision.json"
      type: "新建"
      schema_ref: "ALLOW|REQUIRES_CHANGES|DENY"
    - path: "docs/2026-02-20/verification/T33_execution_report.yaml"
      type: "新建"
      schema_ref: "Execution Report"
  constraints:
    - "必须给出实现/回归/基线三判定"
    - "任一关键项失败时不得 ALLOW"
    - "阻塞项必须列出整改项"

deny:
  - "不得跳过自动化结果核验"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_seeds_metrics.py skillforge/tests/test_feature_flag_loader.py skillforge/tests/test_provenance_loader.py"
      expect: "passed"
```

