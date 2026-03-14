# Unified Validation Gate - T-ASM-03 Delivery Summary

**Task ID**: T-ASM-03
**Execution Agent**: C
**Date**: 2026-03-10
**Status**: COMPLETE

---

## Executive Summary

Delivered a **minimal unified validation entry point** for GM-SkillForge that consolidates all current mainline verification capabilities while preserving fail-closed semantics and maintaining individual script independence.

### Key Deliverable
- **File**: [unified_validation_gate.py](../../scripts/unified_validation_gate.py)
- **Lines**: ~610
- **Purpose**: Single entry point for all validation workflows

---

## Validation Script Inventory

### Mainline Core Scripts (Included)

| Script | Purpose | Status |
|--------|---------|--------|
| `antigravity_2_guard.py` | Antigravity-2: Permit + Delivery + Three-Hash (Primary Gate) | **INCLUDED** |
| `validate_permit_binding.py` | Permit five-field validation (demand_hash, contract_hash, decision_hash, audit_pack_hash, revision) | **INCLUDED** (via AG-2) |
| `validate_delivery_completeness.py` | Delivery six-item check (Blueprint, Skill, n8n, Evidence, AuditPack, Permit) | **INCLUDED** (via AG-2) |
| `validate_three_hashes.py` | Three-hash consistency validation | **INCLUDED** (via AG-2) |
| `verify_n1_command_allowlist.py` | N1: Command allowlist verification | **INCLUDED** (N-boundary) |
| `verify_n2_artifact_completeness.py` | N2: Artifact completeness verification | **INCLUDED** (N-boundary) |
| `verify_n3_time_window.py` | N3: Time window enforcement | **INCLUDED** (N-boundary) |
| `pre_absorb_check.sh` | Pre-absorb gate check | **INCLUDED** |

### Cloud Execution Scripts (Included)

| Script | Purpose | Status |
|--------|---------|--------|
| `verify_execution_receipt.py` | Receipt verification | **INCLUDED** (cloud mode) |
| `verify_and_gate.py` | Dual gate verification (wrapper) | **REPLACED** by unified gate |

### Standalone Scripts (Excluded from Mainline)

| Script | Purpose | Reason for Exclusion |
|--------|---------|---------------------|
| `verify_evidence_chain.py` | Evidence SHA256 chain verification | Optional/standalone tool |
| `validate_phase1.py` | Phase 1 validation | Legacy phase validation |
| `validate_phase2.py` | Phase 2 validation | Legacy phase validation |
| `validate_phase3_4.py` | Phase 3/4 validation | Legacy phase validation |
| `validate_phase5.py` | Phase 5 validation | Legacy phase validation |
| `validate_iteration_artifacts.py` | Iteration artifact check | Specialized use case |
| `three-hash-permit-guard/run_guard.py` | Three-hash permit guard | Functionality merged into AG-2 |

---

## Unified Validation Gate Usage

### Mode 1: Mainline Validation (Default)

**Full Antigravity-2 compliance check:**

```bash
# Basic mainline check
python scripts/unified_validation_gate.py --mode mainline --permit permits/task/permit.json

# With explicit three-rights paths
python scripts/unified_validation_gate.py --mode mainline \
  --permit permits/task/permit.json \
  --demand docs/2026-02-22/量化/demand.json \
  --contract contracts/dsl/contract.yml \
  --decision artifacts/decision.json \
  --manifest artifacts/MANIFEST.json

# With N-boundary (for cloud tasks)
python scripts/unified_validation_gate.py --mode mainline \
  --permit permits/task/permit.json \
  --with-n-boundary \
  --task-id TASK-001
```

### Mode 2: Cloud Task Validation

**Verify cloud execution:**

```bash
python scripts/unified_validation_gate.py --mode cloud --task-id TASK-001
```

### Mode 3: Quick Validation

**Fast development iteration (skip three-hash):**

```bash
python scripts/unified_validation_gate.py --mode quick --permit permits/task/permit.json
```

### Mode 4: Absorb Gate

**Pre-absorb validation:**

```bash
python scripts/unified_validation_gate.py --mode absorb --task-id TASK-001
```

---

## Validation Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     UNIFIED VALIDATION GATE (UVG)                          │
│                         unified_validation_gate.py                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              ┌─────▼─────┐   ┌────▼────┐   ┌─────▼─────┐
              │ MAINLINE  │   │ CLOUD   │   │   QUICK   │
              └─────┬─────┘   └────┬────┘   └─────┬─────┘
                    │              │               │
        ┌───────────┼──────────────┼───────────────┤
        │           │              │               │
   ┌────▼───┐  ┌───▼────┐   ┌────▼────┐   ┌─────▼─────┐
   │ AG-2   │  │ Receipt│   │  N-Bound │   │ AG-2 Quick │
   │ Guard  │  │ Verify │   │  (N1+N2  │   │ (no 3-hash) │
   │        │  │        │   │   +N3)   │   │            │
   └────┬───┘  └───┬────┘   └────┬────┘   └─────┬─────┘
        │          │              │               │
   ┌────▼───┐  ┌───▼────┐   ┌────▼────┐         │
   │Permit  │  │N1:Cmd  │   │Absorb   │         │
   │Delivery│  │N2:Art  │   │Check    │         │
   │3-Hash  │  │N3:Time │   │(opt)    │         │
   └────┬───┘  └───┬────┘   └─────────┘         │
        │          │                            │
        └──────────┴────────────────────────────┘
                          │
                  ┌───────▼────────┐
                  │ ALLOW / DENY   │
                  │ + Evidence Refs│
                  └────────────────┘
```

---

## Included Checks Detail

### Antigravity-2 Guard (Primary Mainline Check)

**Three-stage validation:**

1. **Permit Five-Field Validation** (`validate_permit_binding.py`)
   - demand_hash (required)
   - contract_hash (required)
   - decision_hash (required)
   - audit_pack_hash (required)
   - revision (required)

2. **Fixed-Caliber Binding** (optional, if config exists)
   - Prevents cross-batch file mixing
   - Enforces single-caliber consistency

3. **Delivery Completeness** (`validate_delivery_completeness.py`)
   - Blueprint (contracts/dsl/*.yml)
   - Skill (skills/*/)
   - n8n (workflows/**/*.json)
   - Evidence (artifacts/*/)
   - AuditPack (audit_pack/*.json)
   - Permit (permits/*/*.json)

4. **Three-Hash Consistency** (`validate_three_hashes.py`)
   - demand_hash
   - contract_hash
   - decision_hash

### N-Boundary Verification (Cloud Task Check)

**Three incremental security boundaries:**

1. **N1: Command Allowlist** (`verify_n1_command_allowlist.py`)
   - All executed commands must be in allowlist
   - Fail-closed enforcement

2. **N2: Artifact Completeness** (`verify_n2_artifact_completeness.py`)
   - execution_receipt.json (required)
   - stdout.log (required)
   - stderr.log (required)
   - audit_event.json (required)

3. **N3: Time Window** (`verify_n3_time_window.py`)
   - Max duration enforcement (default: 300s)
   - Max command count (default: 50)
   - Timeout detection

### Absorb Gate Check

**Pre-absorb validation** (`pre_absorb_check.sh`):
- Environment variables check
- Manifest whitelist validation
- Task package completeness

---

## Excluded Checks (Preserved as Standalone)

1. **Evidence Chain Verification** (`verify_evidence_chain.py`)
   - Purpose: Blockchain-like evidence trail
   - Usage: Optional audit trail tool
   - Status: Available as standalone

2. **Legacy Phase Validators** (`validate_phase*.py`)
   - Purpose: Historical phase validation
   - Status: Preserved for reference, not in mainline

---

## Evidence References

The unified gate generates evidence references in the format:

```
antigravity_2_guard:ALLOW
n_boundary:TASK-001:PASS
receipt:TASK-001:PASS
pre_absorb:TASK-001:PASS
```

These references are:
- Written to output JSON
- Included in verification reports
- Traceable to source validation scripts

---

## Fail-Closed Policy

**ALL validations maintain fail-closed semantics:**

- Any validation failure = DENY
- No partial passes in mainline mode
- Exit code 1 on failure, 0 on success
- Detailed error reporting with required_changes

---

## Changed Files

| File | Change |
|------|--------|
| `scripts/unified_validation_gate.py` | NEW - Unified validation entry point |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Unified gate becomes single point of failure | Individual scripts remain callable directly |
| Integration complexity | Each mode is independent; fail-fast on errors |
| Version drift in called scripts | Gate passes through to existing scripts; no duplication |
| Misconfiguration | Explicit arguments per mode; clear help text |

---

## Next Steps

1. **Integration**: Wire unified gate into CI/CD pipeline
2. **Documentation**: Update CLAUDE.md with validation commands
3. **Monitoring**: Collect validation metrics from gate output
4. **Testing**: Run smoke tests with existing permits

---

## Appendix: Quick Reference

```bash
# Mainline (full compliance check)
python scripts/unified_validation_gate.py --mainline --permit permits/TASK/permit.json

# Cloud task verification
python scripts/unified_validation_gate.py --cloud --task-id TASK-001

# Quick development iteration
python scripts/unified_validation_gate.py --quick --permit permits/TASK/permit.json

# Pre-absorb check
python scripts/unified_validation_gate.py --absorb --task-id TASK-001

# With output file
python scripts/unified_validation_gate.py --mainline --permit permits/TASK/permit.json --output validation.json

# Quiet mode (status only)
python scripts/unified_validation_gate.py --mainline --permit permits/TASK/permit.json --quiet
```

---

**Signature**: Agent C / T-ASM-03 / 2026-03-10
