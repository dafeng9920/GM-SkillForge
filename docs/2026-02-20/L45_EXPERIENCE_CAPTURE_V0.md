# L4.5 Experience Capture v0

## Goal

Introduce a minimal "learning seed" without autonomous code rewriting:
- Append-only machine memory: `evolution.json`
- Human-readable summary: `SKILL.md`
- Evidence-first gate: missing evidence is marked `MISSING_EVIDENCE`

## Implemented

- Core module: `skillforge/src/skills/experience_capture.py`
- Template reader layer:
  - `ExperienceCaptureV0.retrieve_templates(...)`
  - `retrieve_experience_templates(...)`
- Reader supports filtering by:
  - `IssueKey` (exact / prefix with `*`)
  - `FixKind`
  - `GateNode`
- Triggered in gate execute paths:
  - `intake_repo`
  - `repo_scan_fit_score`
  - `draft_skill_spec`
  - `constitution_risk_gate`
  - `scaffold_skill_impl`
  - `sandbox_test_and_trace`
  - `pack_audit_and_publish`
  - `permit_gate`
- Retrieval consumption:
  - `scaffold_skill_impl` now returns `experience_templates` for downstream template reuse.

## Entry Schema (v0)

Required fields:
- `issue_key`
- `evidence_ref`
- `gate_node`
- `summary`
- `fix_kind`
- `content_hash` (auto-generated SHA-256)

Behavior:
- Missing `evidence_ref` -> not captured to canonical entries
- Missing evidence record is appended to `rejected_entries` with `status=MISSING_EVIDENCE`
- Duplicate entries are skipped by `content_hash`

## Storage

- `AuditPack/experience/evolution.json` (append-only)
- `AuditPack/experience/SKILL.md` (aggregated summary)

## FixKind Enum (v0)

- `ADD_CONTRACT`
- `ADD_TESTS`
- `UPDATE_SCAFFOLD`
- `APPLY_PATCH`
- `PUBLISH_PACK`
- `GATE_DECISION`

## Test Coverage

- `tests/gates/test_experience_capture.py`
- `tests/gates/test_experience_template_reader_integration.py`
- Regression safety:
  - `tests/gates/test_intake_scan.py`
  - `tests/gates/test_logic.py`
  - `skillforge/tests/test_gate_permit.py`
  - `skillforge/tests/test_n8n_orchestration.py`
