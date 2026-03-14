# P0 Governed Execution Action Plan

## Scope
- Target: `L6` authenticity closure only (`ISSUE-00` to `ISSUE-10`)
- Out of scope: `L4` implementation, `L5` marketplace binding

## Mode
- `mode: strict`
- Mandatory order per task: `Review -> Compliance -> Execution`

## Guard References
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` (if missing, block execution until restored)
- `multi-ai-collaboration.md`

## Hard Rules
- No `ComplianceAttestation(PASS)` -> no execution
- Side effects require `permit=VALID`
- No `EvidenceRef` -> task not complete

## Deliverables
- `task_dispatch.md`
- `tasks/Txx_*.md`
- `verification/*_execution_report.yaml`
- `verification/*_gate_decision.json`
- `verification/*_compliance_attestation.json`
- `verification/final_gate_decision.json`

## Final Gate Criteria
- All tasks have 3 records: Review + Compliance + Execution
- All compliance decisions are `PASS`
- P0 protocol tests (`T1-T5`) pass in CI
