# Task Skill Spec: T-W3-C

```yaml
task_id: "T-W3-C"
executor: "Kior-C"
wave: "Wave 3"
input:
  impl: "skillforge/src/skills/experience_capture.py"
  contract: "skillforge/src/contracts/rag_3d.yaml"
output:
  files:
    - "docs/2026-02-17/verification/wave3_audit_report.md"
constraints:
  - "Must include 3 mandatory verification cases:"
    - "1. At-Time Replay Success (Valid at_time ref -> PASS)"
    - "2. Tombstone Interception (tombstone=true -> REJECT)"
    - "3. Auto Extraction (Valid inputs -> evolution.json updated)"
  - "Must confirm Fail-Closed behavior for invalid inputs"
  - "Must verify evolution.json appended correctly without overwriting"
```
