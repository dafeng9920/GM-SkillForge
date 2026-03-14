# L4 n8n 最小闭环 Action Plan

## Scope

- 仅做 L4 最小实现闭环：`Diagnosis -> AEV`
- 仅做 n8n 接入基础，不进入 L5 规模化策略

## Deliverables

1. `docs/2026-02-26/l4-n8n-execution/tasks/*.md`
2. `docs/2026-02-26/l4-n8n-execution/verification/L4-*_execution_report.yaml`
3. `docs/2026-02-26/l4-n8n-execution/verification/L4-*_gate_decision.json`
4. `docs/2026-02-26/l4-n8n-execution/verification/L4-*_compliance_attestation.json`
5. `docs/2026-02-26/l4-n8n-execution/verification/final_gate_decision.json`

## Hard Rules

1. Review -> Compliance -> Execution
2. 无 Compliance PASS 不得执行
3. 无 EvidenceRef 不得宣称完成

## Final Gate Criteria

1. L4-01~L4-08 三件套完整
2. AEV 报告可追溯到 evidence_ref
3. 单条真实 run 可复核

