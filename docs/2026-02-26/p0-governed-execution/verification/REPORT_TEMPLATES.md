# Verification Report Templates

## 1) Execution Report (`Txx_execution_report.yaml`)
```yaml
task_id: "Txx"
executor: "name"
status: "完成|部分完成|阻塞"
deliverables:
  - path: "path/to/file"
    action: "新建|修改"
    lines_changed: 0
gate_self_check:
  - command: "command"
    result: "result"
notes: ""
evidence_refs:
  - id: "EV-..."
    kind: "LOG|FILE|DIFF|SNIPPET"
    locator: "path:line"
```

## 2) Gate Decision (`Txx_gate_decision.json`)
```json
{
  "task_id": "Txx",
  "reviewer": "name",
  "decision": "ALLOW",
  "reasons": ["..."],
  "evidence_refs": [
    {
      "id": "EV-...",
      "kind": "FILE",
      "locator": "path:line"
    }
  ]
}
```

## 3) Compliance Attestation (`Txx_compliance_attestation.json`)
```json
{
  "task_id": "Txx",
  "compliance_officer": "name",
  "decision": "PASS",
  "reasons": ["..."],
  "evidence_refs": [
    {
      "id": "EV-...",
      "kind": "FILE",
      "locator": "path:line"
    }
  ],
  "contract_hash": "sha256:...",
  "reviewed_at": "2026-02-26T00:00:00Z",
  "required_changes": []
}
```

## 4) Final Gate (`final_gate_decision.json`)
```json
{
  "batch": "P0",
  "decision": "ALLOW|REQUIRES_CHANGES|DENY",
  "reasons": ["..."],
  "missing_records": [],
  "reviewed_at": "2026-02-26T00:00:00Z"
}
```
