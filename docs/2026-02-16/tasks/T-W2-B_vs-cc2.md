# Task Skill Spec: T-W2-B

```yaml
task_id: "T-W2-B"
executor: "vs--cc2"
wave: "Wave 2"
input:
  doc: "docs/2026-02-17/GM-SkillForge · cognition_10d 四件套.md"
output:
  files:
    - "docs/2026-02-17/samples/audit_pack_PASSED.json"
    - "docs/2026-02-17/samples/audit_pack_REJECTED.json"
constraints:
  - "PASSED sample must have overall_pass_count >= 8 and no rejection_reasons"
  - "REJECTED sample must match FC-2 scenario (invalid commit_sha)"
```
