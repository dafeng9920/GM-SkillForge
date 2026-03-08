# Task Skill Spec: T-W3-A

```yaml
task_id: "T-W3-A"
executor: "vs--cc1"
wave: "Wave 3"
input:
  requirements:
    - "3D RAG at-time 引用化: evidence_ref -> {uri, commit_sha, at_time, tombstone}"
    - "Experience Capture: IssueKey + EvidenceRef -> evolution.json"
    - "Fail-Closed"
output:
  files:
    - "docs/2026-02-17/wave3_constraints.md"
    - "skillforge/src/contracts/rag_3d.yaml"
constraints:
  - "rag_3d.yaml MUST define schemas for 'AtTimeReference' and 'ExperienceEntry'"
  - "wave3_constraints.md MUST include the 4 acceptance criteria defined by User"
```
