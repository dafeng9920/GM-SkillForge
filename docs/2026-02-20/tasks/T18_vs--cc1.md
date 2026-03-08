# Task Skill Spec

```yaml
task_id: "T18"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 80

input:
  description: "SEEDS-P0-2 Ruleset Revision：落盘 ruleset_manifest 并强制 GateDecision 携带 ruleset_revision"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "Ruleset 版本化要求"
    - path: "docs/2026-02-20/verification/T16_gate_decision.json"
      purpose: "决策文件结构参考"
  constants:
    job_id: "L45-D4-SEEDS-P0-20260220-004"
    skill_id: "l45_seeds_p0_foundation"

output:
  deliverables:
    - path: "orchestration/ruleset_manifest.yml"
      type: "新建"
      schema_ref: "ruleset manifest"
    - path: "skillforge/src/contracts/governance/gate_decision_envelope.schema.json"
      type: "修改"
      schema_ref: "add ruleset_revision"
    - path: "skillforge/tests/test_ruleset_revision_binding.py"
      type: "新建"
      schema_ref: "ruleset_revision 出现与一致性测试"
  constraints:
    - "每次 GateDecision 必带 ruleset_revision"
    - "at-time 回放路径可读取 ruleset_revision"
    - "缺 ruleset_revision 必须 fail-closed"

deny:
  - "不得允许无 ruleset_revision 的 ALLOW"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_ruleset_revision_binding.py"
      expect: "passed"
```

