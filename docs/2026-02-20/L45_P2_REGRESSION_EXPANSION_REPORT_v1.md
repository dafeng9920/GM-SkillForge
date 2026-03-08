# L4.5 SEEDS P2 Regression Expansion Report

> Job ID: `L45-D6-SEEDS-P2-20260220-006`
> Task ID: T32
> Executor: Kior-A
> Date: 2026-02-20

---

## Summary

This report documents the expansion of the regression suite for SEEDS P2 operationalization. The regression suite now covers all P0 seed capabilities with deterministic, reproducible test cases.

---

## Deliverables

| Path | Type | Description |
|------|------|-------------|
| `regression/cases/case_002/` | New | Permit Required Policy case |
| `regression/cases/case_003/` | New | Registry Store case |
| `regression/cases/case_004/` | New | Audit Event Writer case |
| `regression/cases/case_005/` | New | Usage Meter case |
| `scripts/run_regression_suite.py` | New | CI-ready regression entry point |

---

## Case Inventory

### Before T32

| Case ID | Category | Description | Status |
|---------|----------|-------------|--------|
| case_001 | gate_permit | Gate permit validation baseline | Active |

### After T32

| Case ID | Category | Description | Status |
|---------|----------|-------------|--------|
| case_001 | gate_permit | Gate permit validation baseline | Active |
| case_002 | permit_required_policy | PUBLISH_LISTING requires permit | **New** |
| case_003 | registry_store | Append-only behavior verification | **New** |
| case_004 | audit_event_writer | Gate finish event logging | **New** |
| case_005 | usage_meter | Quota accounting on enqueue | **New** |

---

## Constraints Verification

| Constraint | Status | Evidence |
|------------|--------|----------|
| New case has input + expected | PASS | All 4 new cases have input.json and expected.md |
| Regression entry supports CI | PASS | `--ci` flag with JSON output and exit codes |
| Output is deterministic | PASS | No random values, no network dependencies |

---

## Run Regression Suite

### Local Execution

```bash
# Run all regression tests
python scripts/run_regression_suite.py

# Run specific case
python scripts/run_regression_suite.py --case 001

# Run with JSON output
python scripts/run_regression_suite.py --output report.json
```

### CI Execution

```bash
# CI mode (exits 1 on failure, outputs JSON)
python scripts/run_regression_suite.py --ci
```

### Nightly Execution

```bash
# Nightly mode (full suite with detailed output)
python scripts/run_regression_suite.py --nightly
```

---

## Case Details

### Case 002: Permit Required Policy

**Category**: `permit_required_policy`

**Purpose**: Verify that PUBLISH_LISTING action requires a valid permit.

**Expected Behavior**:
- `permit_required("PUBLISH_LISTING")` returns `true`
- Missing permit raises `PermitRequiredError` with code `PERMIT_REQUIRED`
- Error code matches E001 -> PERMIT_REQUIRED mapping

**P0 Reference**: T21 - SEEDS-P0-3 Permit Required Policy

---

### Case 003: Registry Store

**Category**: `registry_store`

**Purpose**: Verify append-only storage behavior.

**Expected Behavior**:
- Entry can be appended to registry
- `get_latest_active()` returns correct revision
- History is not overwritten on subsequent appends

**P0 Reference**: T17 - SEEDS-P0-1 Registry

---

### Case 004: Audit Event Writer

**Category**: `audit_event_writer`

**Purpose**: Verify gate finish event logging.

**Expected Behavior**:
- Gate finish events are written to log
- Events can be queried by job_id
- Storage is append-only

**P0 Reference**: T19 - SEEDS-P0-4 Audit Events

---

### Case 005: Usage Meter

**Category**: `usage_meter`

**Purpose**: Verify usage recording on enqueue.

**Expected Behavior**:
- Usage is recorded when job is enqueued
- Usage can be queried by account_id
- Storage is append-only

**P0 Reference**: T20 - SEEDS-P0-5 Usage/Quota

---

## Architecture

```
scripts/
└── run_regression_suite.py    # Entry point for CI/nightly
    ├── discover_cases()       # Find all case_* directories
    ├── run_case()             # Execute single case
    └── run_suite()            # Run all cases, generate report

regression/
├── README.md                  # Documentation
└── cases/
    ├── case_001/              # Gate permit validation
    │   ├── input.json
    │   └── expected.md
    ├── case_002/              # Permit required policy
    │   ├── input.json
    │   └── expected.md
    ├── case_003/              # Registry store
    │   ├── input.json
    │   └── expected.md
    ├── case_004/              # Audit event writer
    │   ├── input.json
    │   └── expected.md
    └── case_005/              # Usage meter
        ├── input.json
        └── expected.md
```

---

## Deny Rules Verification

| Deny Rule | Status |
|-----------|--------|
| No README-only without runnable cases | PASS - 4 new runnable cases added |

---

## Gate Self-Check

```bash
python scripts/run_regression_suite.py --ci
```

Expected: `passed` (exit code 0)

---

## Conclusion

T32 has successfully expanded the regression suite with 4 new cases covering P0 seed capabilities. The regression entry point (`run_regression_suite.py`) is CI-ready with standardized output and exit codes.

**Status**: READY FOR INTEGRATION
