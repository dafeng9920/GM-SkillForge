# Task Skill Spec: T-W2-D

```yaml
task_id: "T-W2-D"
executor: "Kior-C"
wave: "Wave 2"
input:
  impl: "skillforge/src/skills/cognition_10d_generator.py"
  cases_dir: "docs/2026-02-17/cognition_10d_cases/"
output:
  files:
    - "docs/2026-02-17/verification/wave2_audit_report.md"
constraints:
  - "Must run all regression cases"
  - "Must verify L5 G1-G5 compliance for the new skill"
  - "Must confirm 'audit_pack_ref' points to valid files"
```
