# T1 Follow-up Dispatch (2026-03-07)

## Goal

Close the remaining T1 follow-up risks before moving to `T2`.

This follow-up wave is mandatory because the previous `T1` final gate was `ALLOW with follow-up required`, not "all residual risks eliminated".

---

## Follow-up Scope

### F1. T1-A unrelated diff cleanup

- Source risk:
  - unrelated change noted in `adapters/quant/__init__.py`
- Objective:
  - confirm whether the diff is accidental, stale, or required
  - remove it from the T1-A remediation footprint if unrelated
- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- unrelated diff is either removed or explicitly justified
- no hidden behavior change remains attached to T1-A
- evidence points to exact file change and final disposition

Archive target:

- `docs/2026-03-07/verification/F1_T1A_diff_cleanup_review.json`
- `docs/2026-03-07/verification/F1_T1A_diff_cleanup_gate.json`

### F2. T1-C unregistered skill closure

- Source risk:
  - 7 skills remain outside tier registry baseline
- Objective:
  - classify the 7 skills into `register now / tombstone / merge / defer with reason`
  - eliminate unknown status
- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no

Acceptance:

- each of the 7 skills has a final disposition
- registry state and explanation are aligned
- no "unregistered but ignored" leftovers remain

Archive target:

- `docs/2026-03-07/verification/F2_T1C_unregistered_skill_closure_review.json`
- `docs/2026-03-07/verification/F2_T1C_unregistered_skill_closure_gate.json`

### F3. T1-D immediate-fix execution split

- Source risk:
  - T1-D backlog pack contains 8 immediate-fix items still pending
- Objective:
  - split immediate-fix items into executable batches
  - define what must be fixed before `T2` and what can remain backlog
- Execution: `vs--cc3`
- Review: `Kior-C`
- Compliance: `Antigravity-1`
- Parallel: yes

Acceptance:

- all 8 immediate-fix items are classified into `execute now / defer with justification`
- each execute-now item has owner, DoD, and estimated batch slot
- no vague "later" bucket remains

Archive target:

- `docs/2026-03-07/verification/F3_T1D_immediate_fix_split_review.json`
- `docs/2026-03-07/verification/F3_T1D_immediate_fix_split_gate.json`

---

## Execution Order

### Wave F1

- `F1` and `F3` can run in parallel

### Wave F2

- `F2` runs after `F1`, because registry closure should not carry unresolved accidental diff noise from T1-A

---

## Exit Condition

T1 follow-up is complete only when:

1. `F1/F2/F3` all have execution, review, and compliance evidence
2. all three follow-up gates are `ALLOW`
3. no residual T1 item remains in ambiguous state
4. `docs/VERIFICATION_MAP.md` is updated with follow-up closure

---

## Rule

Do not start `T2` before this follow-up dispatch is closed, unless a separate explicit defer decision is signed and archived.
