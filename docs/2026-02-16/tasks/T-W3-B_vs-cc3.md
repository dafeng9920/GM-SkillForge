# Task Skill Spec: T-W3-B

```yaml
task_id: "T-W3-B"
executor: "vs--cc3"
wave: "Wave 3"
input:
  contract: "skillforge/src/contracts/rag_3d.yaml"
  constraints: "docs/2026-02-17/wave3_constraints.md"
output:
  files:
    - "skillforge/src/skills/experience_capture.py"
constraints:
  - "Must implement Experience Capture logic (IssueKey + EvidenceRef -> evolution.json)"
  - "Must enforce all Fail-Closed rules (FC-EXP-1 to FC-EXP-6, FC-EVO-1 to FC-EVO-4)"
  - "Must use appending write for evolution.json with content_hash deduplication"
  - "Must validate AtTimeReference before processing (FC-ATR-1 to FC-ATR-5)"
```
