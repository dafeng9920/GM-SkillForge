# T2 Follow-up Dispatch (2026-03-07)

## Goal

Convert `T2` from parity/archive completion into actual mainline code migration closure.

This follow-up wave is mandatory because `T2` final gate on 2026-03-07 was `ALLOW with follow-up required`, not "all migration code landed".

Mode: `strict`

Reason:
- contract naming and mainline promotion affect core governance surface
- review/compliance must stay independent from execution
- planned intents cannot be promoted through fastlane batching without stronger guardrails

Completion record rule:
- every executor must write a shard completion record into daily docs before claiming completion
- minimum record contents: changed files, verification method, EvidenceRef, remaining risk, explicit status
- orchestrator (`Codex`) is the single collector for these records and performs unified review aggregation
- missing completion record means shard is automatically incomplete

---

## Follow-up Scope

### F1. Lifecycle and audit canonical contract normalization

- Source risk:
  - `generate_skill_from_repo` / `upgrade_skill_revision` / `tombstone_skill` / `audit_repo_skill`
    still have non-canonical contract names or live only under migration docs
- Objective:
  - normalize canonical `intent_id`, contract filename, and production contract location
  - align contract vocabulary to current dispatch/mainline naming
- Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no

Acceptance:

- each target intent has one canonical production contract
- dispatch naming, contract naming, and intent_map naming are aligned
- migration-doc copies are either superseded or explicitly marked non-authoritative
- no old alias remains ambiguous in active path

Archive target:

- `docs/2026-03-07/verification/F1_T2_contract_normalization_review.json`
- `docs/2026-03-07/verification/F1_T2_contract_normalization_gate.json`
- executor completion note must be written before review starts

### F2. Selective mainline promotion for outer intake/freeze intents

- Source risk:
  - `outer_intent_ingest` and `outer_contract_freeze` are marked `migrate now`
    but still remain `l42_planned`
- Objective:
  - promote these two intents into mainline contract + intent_map status
  - bind them to current gate path and evidence requirements
- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no, depends on F1 naming truth

Acceptance:

- both intents leave `l42_planned` and enter explicit mainline status
- each intent has contract path, gate path, and evidence requirements tied to current repo rules
- no placeholder-only migration_status remains for these two intents

Archive target:

- `docs/2026-03-07/verification/F2_T2_mainline_promotion_review.json`
- `docs/2026-03-07/verification/F2_T2_mainline_promotion_gate.json`
- executor completion note must be written before review starts

### F3. Parity regression and replay evidence pack

- Source risk:
  - default-deny, evidence-first, and `time_semantics` still lack current replay/parity regression artifacts
- Objective:
  - add executable parity/replay verification artifacts for:
    - constitutional default-deny stop behavior
    - evidence-first publish chain
    - `time_semantics` at_time replay discipline
- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes, but final sign-off waits for F1/F2

Acceptance:

- each of the three targets has one reproducible verification artifact
- artifacts bind to current archive flow and can be cited by EvidenceRef
- no purely narrative parity claim remains for those three items

Archive target:

- `docs/2026-03-07/verification/F3_T2_parity_regression_review.json`
- `docs/2026-03-07/verification/F3_T2_parity_regression_gate.json`
- executor completion note must be written before review starts

---

## Execution Order

### Wave F1

- `F1`
- `F3`

### Wave F2

- `F2` runs after `F1`, because mainline promotion must not fork canonical naming

### Final Aggregation

- orchestrator aggregates `F1/F2/F3`
- orchestrator collects all executor completion notes first
- update `docs/VERIFICATION_MAP.md`
- issue `T2 follow-up final review` and `T2 follow-up final gate`

---

## Exit Condition

T2 follow-up is complete only when:

1. `F1/F2/F3` all have execution, review, and compliance evidence
2. all three follow-up gates are `ALLOW`
3. canonical contract naming is no longer ambiguous for lifecycle/audit intents
4. `outer_intent_ingest` and `outer_contract_freeze` are not left in planned-only state
5. replay/parity artifacts exist for default-deny, evidence-first, and `time_semantics`
6. `docs/VERIFICATION_MAP.md` is updated with follow-up closure
7. every shard has a written executor completion record collected by orchestrator

---

## Rule

Do not claim `T2` code migration complete before this follow-up dispatch is closed, unless a separate explicit defer decision is signed and archived.
