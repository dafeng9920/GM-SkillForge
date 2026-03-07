# T2 Remediation Dispatch (2026-03-07)

## Goal

Repair the failed or incomplete `T2 follow-up` shards without reopening unrelated scope.

Target items:
- `F1-R`: rework canonical contracts after compliance fail
- `F3-R`: rework evidence-first parity semantics after compliance fail
- `F2-C`: issue valid independent compliance attestation for F2

Mode: `strict`

Hard rule:
- remediation must address the exact fail attestation findings
- no executor may self-approve
- no new scope may be introduced under the name of remediation

---

## Shards

### F1-R. Canonical contract restoration remediation

- Source:
  - `docs/2026-03-07/verification/T2-F1_compliance_attestation_FAIL.json`
- Objective:
  - restore the missing contract constraints removed during F1 normalization
  - keep canonical naming, but recover fail-closed semantics and evidence chain sections
- Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- production contracts preserve canonical naming and authoritative location
- missing `validation_rules`, `architecture_boundary`, `source_doc_ref`, and equivalent constraints are restored where required
- execution report no longer claims false consistency
- any remaining non-canonical contract path in active intent_map is either fixed or explicitly justified

Archive target:

- `docs/2026-03-07/verification/F1R_T2_contract_restoration_review.json`
- `docs/2026-03-07/verification/F1R_T2_contract_restoration_gate.json`

### F3-R. Evidence-first temporal semantics remediation

- Source:
  - `docs/2026-03-07/verification/T2-F3_compliance_attestation_FAIL.json`
- Objective:
  - make `evidence-first publish chain` verifiable as a temporal ordering claim, not just existence
  - add traceable decision/evidence timing fields and tests
- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- gate decision timestamp or equivalent decision-time field is persisted in the evidence chain
- tests verify ordering semantics, not only presence
- completion record and execution report describe the repaired semantics truthfully
- no fake closure language remains around `evidence-first`

Archive target:

- `docs/2026-03-07/verification/F3R_T2_temporal_evidence_review.json`
- `docs/2026-03-07/verification/F3R_T2_temporal_evidence_gate.json`

### F2-C. Independent compliance attestation replacement

- Source:
  - `docs/2026-03-07/T2-F2_completion_record.md`
  - `docs/2026-03-07/verification/T2-F2_execution_report.yaml`
  - `docs/2026-03-07/verification/T2-F2_review_decision.json`
- Objective:
  - produce a valid independent compliance attestation for F2 under corrected role separation
- Execution: none
- Review: none
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- compliance officer is independent from executor
- attestation explicitly checks no full-copy behavior, gate/evidence fit, and constitution alignment
- result is one of `PASS / FAIL` with EvidenceRef
- if fail, remediation is explicit; if pass, shard becomes closure-ready

Archive target:

- `docs/2026-03-07/verification/T2-F2_compliance_attestation.json`

---

## Execution Order

- `F1-R` and `F3-R` can run in parallel
- `F2-C` can run in parallel because it is a pure compliance replacement

---

## Exit Condition

T2 remediation is complete only when:

1. `F1-R` has execution, review, and compliance records with final `ALLOW/PASS`
2. `F3-R` has execution, review, and compliance records with final `ALLOW/PASS`
3. `F2-C` has a valid independent compliance attestation
4. orchestrator can update T2 follow-up aggregate status without contradiction

