# Task Skill Spec: T-W2-C

```yaml
task_id: "T-W2-C"
executor: "vs--cc3"
wave: "Wave 2"
input:
  contract: "skillforge-spec-pack/skillforge/src/contracts/cognition_10d.intent.yaml"
  rubric: "skillforge-spec-pack/skillforge/src/contracts/cognition_10d_rubric.yaml"
  audit_sample: "docs/2026-02-17/samples/audit_pack_PASSED.json"
output:
  files:
    - "skillforge-spec-pack/skillforge/src/skills/cognition_10d_generator.py"
constraints:
  - "Must implement NodeHandler protocol"
  - "Must implement Fail-Closed logic (FC-1 to FC-7)"
  - "Must produce output identical to audit_sample when given same input"
  - "Must NOT use external LLM calls (use deterministic mock scoring for MVP)"
```
