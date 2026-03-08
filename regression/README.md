# Regression Set (v1)

> Purpose: Prevent drift in audit/plan outputs.
> Job ID: L45-D6-SEEDS-P2-20260220-006
> Skill ID: l45_seeds_p2_operationalization

---

## Overview

This directory contains fixed regression test cases to prevent output drift in SkillForge audit and plan outputs.

**Principles:**
1. **Fixed Inputs**: All inputs are deterministic and version-controlled.
2. **Fixed Expectations**: Expected outputs are documented and cannot be random.
3. **No External Network**: Cases must not depend on external network calls.
4. **Executable**: All cases must have corresponding executable tests.

---

## Directory Structure

```
regression/
├── README.md                    # This file
└── cases/
    ├── case_001/               # Gate permit validation baseline
    │   ├── input.json          # Fixed input
    │   └── expected.md         # Expected output summary
    ├── case_002/               # Permit Required Policy
    │   ├── input.json
    │   └── expected.md
    ├── case_003/               # Registry Store
    │   ├── input.json
    │   └── expected.md
    ├── case_004/               # Audit Event Writer
    │   ├── input.json
    │   └── expected.md
    └── case_005/               # Usage Meter
        ├── input.json
        └── expected.md
```

---

## Running Regression Tests

### Using run_regression_suite.py (Recommended)

```bash
# Run all regression tests
python scripts/run_regression_suite.py

# Run in CI mode (exit code 1 on failure, JSON output)
python scripts/run_regression_suite.py --ci

# Run specific case
python scripts/run_regression_suite.py --case 001

# Run in nightly mode (full suite with detailed output)
python scripts/run_regression_suite.py --nightly

# Output JSON report to file
python scripts/run_regression_suite.py --output report.json
```

### Using pytest (Legacy)

```bash
# Run all regression seed tests
python -m pytest -q skillforge/tests/test_regression_seed_smoke.py

# Run specific case
python -m pytest -q skillforge/tests/test_regression_seed_smoke.py -k "case_001"
```

---

## Adding New Cases

1. Create a new directory under `cases/` (e.g., `case_006/`)
2. Add `input.json` with fixed, deterministic input
3. Add `expected.md` with documented expected output
4. Update `scripts/run_regression_suite.py` to handle the new category (if needed)
5. Ensure the test does not depend on external network

**Important Rules:**
- **NO** random outputs in `expected.md`
- **NO** external network dependencies
- **NO** timestamps or time-dependent values in assertions
- **YES** deterministic, reproducible inputs and outputs

---

## Case Inventory

| Case ID | Category | Description | Status |
|---------|----------|-------------|--------|
| case_001 | gate_permit | Gate permit validation baseline | ✅ Active |
| case_002 | permit_required_policy | PUBLISH_LISTING requires permit | ✅ Active |
| case_003 | registry_store | Append-only behavior verification | ✅ Active |
| case_004 | audit_event_writer | Gate finish event logging | ✅ Active |
| case_005 | usage_meter | Quota accounting on enqueue | ✅ Active |

---

## DoD (Definition of Done)

- [x] At least 1 case with fixed input and expected output
- [x] Corresponding test file exists and passes
- [x] No external network dependencies
- [x] No random outputs in expected.md
- [x] CI-ready regression entry point (`scripts/run_regression_suite.py`)
- [x] All cases cover P0 seed capabilities

---

## Contract Reference

Per `docs/SEEDS_v0.md`:
> 6. **Regression Set 占位**：固定样例防输出漂移。
> - Keep inputs + expected summaries stable.
> - Every upgrade must run: `gm validate --regression`.
