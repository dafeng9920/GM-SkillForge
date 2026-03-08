# Wave 2: Asset Freeze Manifest

> **Status**: FROZEN
> **Date**: 2026-02-17
> **Version**: v1.0.0

## 1. Contracts & Rubrics

| Asset | Version | Path | SHA256 (Concept) |
|---|---|---|---|
| **Intent Schema** | v1.0.0 | `skillforge/src/contracts/cognition_10d.intent.yaml` | (tracked by git) |
| **Rubric** | v1.0.0 | `skillforge/src/contracts/cognition_10d_rubric.yaml` | (tracked by git) |

## 2. Test Cases (Regression Suite)

| Case ID | Path | Status |
|---|---|---|
| `case_pass_full_score` | `docs/2026-02-17/cognition_10d_cases/case_pass_full_score.yml` | ✅ FROZEN |
| `case_pass_boundary` | `docs/2026-02-17/cognition_10d_cases/case_pass_boundary.yml` | ✅ FROZEN |
| `case_reject_critical_fail` | `docs/2026-02-17/cognition_10d_cases/case_reject_critical_fail.yml` | ✅ FROZEN |
| `case_reject_input_invalid` | `docs/2026-02-17/cognition_10d_cases/case_reject_input_invalid.yml` | ✅ FROZEN |

## 3. Audit Samples (Standard Answers)

| Type | Path |
|---|---|
| **PASSED** | `docs/2026-02-17/samples/audit_pack_PASSED.json` |
| **REJECTED** | `docs/2026-02-17/samples/audit_pack_REJECTED.json` |

## 4. Permit & References

| Item | Value |
|---|---|
| **Skill Implementation** | `skillforge/src/skills/cognition_10d_generator.py` |
| **Audit Report** | `docs/2026-02-17/verification/wave2_audit_report.md` |
| **Permit Decision** | **ALLOW** (See `wave2_gate_decisions.md`) |
| **Audit Pack Ref** | `AuditPack/cognition_10d/a1b2c3d4e5f6789012345678901234567890abcd/` (from PASSED sample) |

---

**Signed-off by**: Kior-C (Verification Agent)
**Approved by**: Claude (Orchestrator)
