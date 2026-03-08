---
name: execution-guard-a-proposal-skill
description: Constrain proposal/planning output into a strict 3-part structure (PreflightChecklist, ExecutionContract, RequiredChanges) with no fake completion claims. Use when drafting plans, patches, or execution contracts before any agent execution.
---

# execution-guard-a-proposal-skill

Use this skill to produce proposal artifacts only, never execution claims.

## Required Output Shape

Return exactly 3 sections, in order:
1. `PreflightChecklist` (YAML or JSON)
2. `ExecutionContract` (JSON, schema-constrained)
3. `RequiredChanges` (mandatory whenever any MUST fails)

Do not add narrative outside these sections.

## Hard Rules

1. Never claim completed actions without `EvidenceRef`.
2. Declare all side effects explicitly in `side_effects`.
3. Include all three roles in `ExecutionContract.roles`: `execution`, `review`, `compliance`.
4. Map every acceptance test to evidence requirements.
5. If uncertain, output `UNKNOWN` plus `RequiredChanges`; do not fabricate.

## Traffic Light

- `RED`: reject progression; output `RequiredChanges` with fail code.
- `YELLOW`: proposal can continue, execution cannot; output `RequiredChanges`.
- `GREEN`: proposal quality is acceptable, still requires B-skill compliance pass before execution.

## Fail Code Policy

- Contract/schema/field failures: `SF_CONTRACT_DRAFT_INVALID` or `SF_VALIDATION_ERROR`
- Overreach or constitution bypass intent: `SF_RISK_CONSTITUTION_BLOCKED`

## Reference

Use as canonical source:
- `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`

