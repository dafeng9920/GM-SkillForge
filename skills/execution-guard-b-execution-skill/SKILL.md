---
name: execution-guard-b-execution-skill
description: Enforce execution compliance for agents. Require ComplianceAttestation PASS and permit validity before side effects. Use before and during execution to block overreach, fake completion, and policy bypass.
---

# execution-guard-b-execution-skill

Use this skill to gate execution behavior after proposal is drafted.

## Required Inputs

1. `execution_contract` (from A-skill)
2. `compliance_attestation` (must exist and be PASS)
3. `permit` (must be VALID when side effects exist)
4. `guard_signature` (optional but recommended)
5. `workspace`

## Mandatory Sequence

1. `Review` checks completeness and dependency coverage.
2. `Compliance` produces attestation with evidence.
3. `Execution` starts only when compliance is PASS and guards are valid.

If any role is missing, deny execution.

## RED Conditions (Immediate Deny)

1. Missing attestation or attestation not PASS.
2. Side effects requested without valid permit.
3. Contract hash mismatch with guard signature.
4. Requested action exceeds `side_effects` or `controls`.
5. Any sign of fabricated evidence or fake pass.

## Execution Hard Rules

1. Execute only contract-allowed actions; stop on overreach.
2. Never relax limits without explicit contract change.
3. Never claim completion without `EvidenceRef`.
4. Emit auditable events per key step.

## Fail Code Policy

- Validation/contract/signature failures: `SF_VALIDATION_ERROR` / `SF_CONTRACT_DRAFT_INVALID`
- Overreach/constitution bypass/no-permit side effects: `SF_RISK_CONSTITUTION_BLOCKED`
- Pack/evidence closure failures: `SF_PACK_AUDIT_FAILED`

## One-line Doctrine

No `Compliance PASS` + (if needed) `permit VALID` + (if enabled) valid guard signature => no execution.
No `EvidenceRef` => not completed.

## Reference

Use as canonical source:
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

