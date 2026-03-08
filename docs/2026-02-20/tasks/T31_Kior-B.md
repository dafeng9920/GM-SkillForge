# Task Skill Spec

```yaml
task_id: "T31"
executor: "Kior-B"
wave: "Wave 1"
depends_on: []
estimated_minutes: 85

input:
  description: "Provenance 强制化：所有 GateDecision 必含 ruleset_revision + provenance.repro_env"
  context_files:
    - path: "orchestration/ruleset_manifest.yml"
      purpose: "ruleset_revision 来源"
    - path: "templates/provenance.json"
      purpose: "repro_env 模板"
    - path: "skillforge/src/contracts/governance/gate_decision_envelope.schema.json"
      purpose: "决策 schema"
  constants:
    job_id: "L45-D6-SEEDS-P2-20260220-006"
    skill_id: "l45_seeds_p2_operationalization"

output:
  deliverables:
    - path: "skillforge/src/contracts/governance/gate_decision_envelope.schema.json"
      type: "修改"
      schema_ref: "enforce fields"
    - path: "docs/2026-02-20/L45_P2_PROVENANCE_ENFORCEMENT_REPORT_v1.md"
      type: "新建"
      schema_ref: "强制化验收报告"
  constraints:
    - "缺 ruleset_revision 必须拒绝"
    - "缺 provenance.repro_env 必须拒绝"
    - "报告给出拒绝样例"

deny:
  - "不得将 required 字段降级为 optional"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_provenance_loader.py skillforge/tests/test_ruleset_revision_binding.py"
      expect: "passed"
```

