# T13: Case Ledger & Anti-Collapse Report

**Task ID**: T13
**Executor**: Kior-B
**Deliverable Date**: 2026-03-16

## Overview

T13 establishes the **Case Ledger** and **Anti-Collapse Report** to provide minimal test scenario tracking with explicit boundary declarations, coverage honesty, and degradation classification.

## Deliverables

### 1. `case_ledger.schema.json`
JSON Schema defining the minimal case ledger structure for tracking test scenarios.

**Key Features**:
- `case_id`: Unique case identifier (format: `CASE-{category}-{seq}`)
- `input_scenario`: Input scenario definition with scenario type and parameters
- `expected_behavior`: Expected outcomes and assertions
- `execution_record`: Actual behavior, deviations, and evidence
- `adjudication`: PASS/FAIL/DEGRADED/WAIVE decision
- `residual_risks`: Risks associated with the case (even for PASS cases)
- `follow_up_actions`: Required follow-up actions

**Hard Constraints Enforced**:
- Maximum 100 cases (minimal case library, not large test suite)
- `boundary_declaration` required: in_scope and out_of_scope items
- Deviations MUST be recorded in `execution_record.actual_behavior.deviations`
- DEGRADED cases MUST specify `degradation_level`

### 2. `case_ledger.py`
Python implementation for creating and managing case ledgers.

**Key Classes**:
- `CaseLedger`: Main ledger with boundary declaration and cases
- `CaseRecord`: Individual test case record
- `BoundaryDeclaration`: Explicit in-scope and out-of-scope declarations
- `InputScenario`: Test input definition
- `ExpectedBehavior`: Expected outcomes
- `ExecutionRecord`: Execution results with deviations
- `Adjudication`: Decision on case execution

**Factory Functions**:
```python
from skillforge.src.contracts.case_ledger import (
    create_minimal_ledger,
    add_case_to_ledger,
    create_case_from_scenario
)

# Create minimal ledger
ledger = create_minimal_ledger(
    created_by="T13-Kior-B",
    in_scope_categories=[
        {"category": "happy_path", "description": "Basic scenarios"}
    ],
    out_of_scope_items=[
        {"category": "performance", "reason": "deferred"}
    ]
)

# Add case
case = create_case_from_scenario(
    category="HAPPY",
    seq=1,
    scenario_type="happy_path",
    inputs={"skill_name": "test"},
    expected_outcomes=[
        {"type": "return_value", "description": "Returns True"}
    ]
)
add_case_to_ledger(ledger, case)
```

### 3. `anti_collapse_report.schema.json`
JSON Schema defining the anti-collapse report that enforces boundary assertions, coverage integrity, degradation classification, and residual risk registration.

**Key Features**:
- `boundary_assertions`: Declared boundaries, violations, and uncovered items
- `coverage_integrity`: Claimed vs verified coverage with gap detection
- `degradation_classification`: Cases by status, degraded cases, misclassification detection
- `residual_risk_register`: All risks by category and severity
- `anti_collapse_score`: Overall score (0-1), posture, and release recommendation

**Hard Constraints Enforced**:
- Uncovered items MUST be explicitly declared (implicit uncovered detected)
- Cases with deviations marked as PASS are flagged as misclassifications
- Residual risks MUST be registered even for PASS cases
- `declaration_integrity_score` measures boundary transparency
- `classification_integrity_score` measures degradation honesty

### 4. `anti_collapse_report.py`
Python implementation for analyzing case ledgers and generating anti-collapse reports.

**Key Functions**:
```python
from skillforge.src.contracts.anti_collapse_report import (
    generate_anti_collapse_report
)

# Generate report from ledger
report = generate_anti_collapse_report(
    case_ledger=ledger,
    report_type="initial",
    created_by="T13-Kior-B"
)

# Check release readiness
print(f"Posture: {report.anti_collapse_score['posture']}")
print(f"Score: {report.anti_collapse_score['score']}")
print(f"Recommendation: {report.anti_collapse_score['release_recommendation']}")
```

**Analysis Components**:
- `analyze_boundary_integrity()`: Detects uncovered items not declared
- `analyze_coverage_integrity()`: Verifies claimed vs actual coverage
- `analyze_degradation_classification()`: Flags PASS with deviations
- `analyze_residual_risks()`: Checks for missing risk assessments
- `calculate_anti_collapse_score()`: Computes overall score and posture

### 5. Sample Files

#### `T13_samples/sample_case_ledger.json`
Sample case ledger demonstrating:
- Boundary declaration with 3 in-scope and 2 out-of-scope items
- 3 test cases (1 PASS, 1 DEGRADED-minor, 1 pending)
- Residual risks registered for all cases
- Proper deviation recording

#### `T13_samples/sample_anti_collapse_report.json`
Sample anti-collapse report showing:
- Score: 0.88 (MODERATE posture)
- Boundary transparency: 90%
- Coverage honesty: 70% (1 unverified case)
- Degradation honesty: 100% (no misclassifications)
- Release recommendation: "caution"

## Hard Constraints (T13)

1. **No Large Case Library**
   - Maximum 100 cases enforced
   - Focus on minimal, representative scenarios
   - Not a replacement for full test suite

2. **Uncovered ≠ Completed**
   - Uncovered scenarios MUST be declared in `boundary_declaration.out_of_scope`
   - `implicit_uncovered_detected` flags items not declared
   - `declaration_integrity_score` < 1.0 indicates gaps

3. **Degradable ≠ Fully Successful**
   - Cases with deviations MUST be classified as DEGRADED
   - `misclassification_detected` lists PASS cases with deviations
   - `classification_integrity_score` < 1.0 indicates false success claims

4. **Residual Risks for All**
   - Residual risks MUST be registered even for PASS cases
   - `risk_register_complete` = false if cases lack risk assessment
   - `gaps_detected` lists cases with missing risk assessment

## Anti-Collapse Posture Levels

| Score | Posture | Release | Description |
|-------|---------|---------|-------------|
| ≥0.90 | STRONG | clear | High confidence in boundary and coverage honesty |
| 0.70-0.89 | MODERATE | caution | Some gaps detected, review recommended |
| 0.50-0.69 | WEAK | blocked | Significant integrity issues, misclassifications |
| <0.50 | CRITICAL | blocked | Fundamental governance failures |

## Usage Example

```bash
# Create a minimal case ledger
python -m skillforge.src.contracts.case_ledger \
  --output run/latest/case_ledger.json \
  --in-scope happy_path edge_case \
  --out-of-scope "performance:deferred" "security:out_of_project_scope"

# Generate anti-collapse report
python -m skillforge.src.contracts.anti_collapse_report \
  --case-ledger run/latest/case_ledger.json \
  --output run/latest/anti_collapse_report.json \
  --report-type initial
```

## Integration with Gate System

The case ledger and anti-collapse report integrate with the governance gate system:

1. **Entry Gate**: Validate boundary declaration before testing
2. **Exit Gate**: Validate anti-collapse score before release
3. **Receipt**: References to `case_ledger.json` and `anti_collapse_report.json`

## Evidence Paths

```
run/<run_id>/
├── case_ledger.json              # T13 deliverable
├── anti_collapse_report.json     # T13 deliverable
├── entry_gate_decision.json      # References T13 artifacts
└── exit_gate_decision.json       # References T13 artifacts
```

## Compliance

This deliverable follows **Antigravity-1** standards:
- ✅ Closed-loop contract structure (ledger → report → gates)
- ✅ Explicit boundary declarations
- ✅ Evidence-based coverage claims
- ✅ Residual risk registration
- ✅ No false success claims

## Related Contracts

- `coverage_statement.schema.json`: T9 coverage declaration framework
- `residual_risks.schema.json`: T10 risk tracking
- `issue_record.schema.json`: T12 issue records from findings

## Future Enhancements

- [ ] Automatic case generation from skill specifications
- [ ] Integration with test runners for automatic execution
- [ ] Historical trend analysis of anti-collapse scores
- [ ] Risk-based sampling recommendations
