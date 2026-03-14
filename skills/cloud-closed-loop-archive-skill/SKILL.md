---
name: cloud-closed-loop-archive-skill
description: Create and freeze cloud task archive records after dual-gate PASS. Use when a CLOUD-ROOT task has completed verification and you need to generate review_decision, final_gate, and update docs/VERIFICATION_MAP.md with evidence links under fail-closed governance.
---

# Cloud Closed-Loop Archive Skill

## Inputs
- `task_id`
- `baseline_id`
- `verification_date_dir` (e.g. `docs/2026-03-06/verification`)
- Dual gate evidence file (`<task_id>_dual_gate_verification.json`)

## Required outputs
1. `<task_id>_review_decision.json`
2. `<task_id>_final_gate.json`
3. `docs/VERIFICATION_MAP.md` new task entry

## Hard rules
- If dual gate is not `PASS`, do not create ALLOW archive.
- Keep `blocking_evidence` and `required_changes` explicit.
- All evidence refs must be real file paths in repo.
- Never edit historical locked entries; append only.

## JSON skeletons
Use [archive_templates.json](references/archive_templates.json).

## Minimal flow
1. Read dual gate result and assert `Gate1=PASS`, `Gate2=ALLOW`.
2. Write review decision JSON with evidence refs.
3. Write final gate JSON with chain-of-custody.
4. Append task section to `docs/VERIFICATION_MAP.md`.
5. Validate JSON syntax (`python -m json.tool`).
