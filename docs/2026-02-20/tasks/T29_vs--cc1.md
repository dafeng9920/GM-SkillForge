# Task Skill Spec

```yaml
task_id: "T29"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 85

input:
  description: "运行时观测：registry/audit_events/usage 三账本健康指标与阈值告警"
  context_files:
    - path: "logs/audit_events.jsonl"
      purpose: "事件源"
    - path: "logs/usage.jsonl"
      purpose: "计量源"
    - path: "registry/skills.jsonl"
      purpose: "注册台账源"
  constants:
    job_id: "L45-D6-SEEDS-P2-20260220-006"
    skill_id: "l45_seeds_p2_operationalization"

output:
  deliverables:
    - path: "skillforge/src/ops/seeds_metrics.py"
      type: "新建"
      schema_ref: "metrics collector"
    - path: "docs/2026-02-20/L45_P2_METRICS_SLO_v1.md"
      type: "新建"
      schema_ref: "SLO 指标与阈值"
    - path: "docs/2026-02-20/verification/T29_metrics_snapshot.json"
      type: "新建"
      schema_ref: "运行快照"
  constraints:
    - "至少输出 ingest_rate/error_rate/missing_evidence_rate"
    - "阈值必须可配置"
    - "快照可复核"

deny:
  - "不得只输出图表不输出原始指标值"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_seeds_metrics.py"
      expect: "passed"
```

