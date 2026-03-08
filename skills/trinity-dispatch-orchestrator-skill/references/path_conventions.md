# Path Conventions

Use these conventions for every dispatch batch.

## 1) Base Paths

- Dispatch file: `docs/{date}/task_dispatch_*.md`
- Prompt file: `docs/{date}/tasks/*_PROMPTS.md`
- Verification dir: `docs/{date}/verification/`

## 2) Verification Files

Per task `Txx`:

- `docs/{date}/verification/Txx_execution_report.yaml`
- `docs/{date}/verification/Txx_gate_decision.json`
- `docs/{date}/verification/Txx_compliance_attestation.json`

Batch final decision:

- `docs/{date}/verification/*_final_gate_decision.json`

## 3) Ownership Mapping Requirement

Every `Txx` row in dispatch must include explicit named owners:

- Execution owner
- Review owner
- Compliance owner

No anonymous role-only row is allowed.

## 4) Consistency Rule

Task IDs listed in:

1. dispatch table
2. prompt sections
3. verification output list

must match one-to-one with no missing or extra task.

