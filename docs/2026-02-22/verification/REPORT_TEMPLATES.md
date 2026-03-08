# 2026-02-22 执行回执模板

## 1) ExecutionReport（执行者提交）
```yaml
task_id: "Txx"
executor: "name"
status: "完成|部分完成|阻塞"
deliverables:
  - path: "..."
    action: "新建|修改"
    lines_changed: 0
gate_self_check:
  - command: "..."
    result: "..."
evidence_refs:
  - id: "EV-..."
    kind: "LOG|FILE|DIFF|SNIPPET"
    locator: "path:line"
notes: "..."
```

## 2) GateDecision（审查者提交）
```json
{
  "task_id": "Txx",
  "reviewer": "name",
  "decision": "ALLOW|REQUIRES_CHANGES|DENY",
  "reasons": ["..."],
  "evidence_refs": ["EV-..."],
  "generated_at": "2026-02-22T00:00:00Z"
}
```

## 3) ComplianceAttestation（合规者提交，执行前必须 PASS）
```json
{
  "task_id": "Txx",
  "compliance_officer": "name",
  "decision": "PASS|FAIL",
  "reasons": ["..."],
  "evidence_refs": ["EV-..."],
  "contract_hash": "sha256:...",
  "reviewed_at": "2026-02-22T00:00:00Z"
}
```

## 4) 文件落盘规范
- `docs/2026-02-22/verification/Txx_execution_report.yaml`
- `docs/2026-02-22/verification/Txx_gate_decision.json`
- `docs/2026-02-22/verification/Txx_compliance_attestation.json`
