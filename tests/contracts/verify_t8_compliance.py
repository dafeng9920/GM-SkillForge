"""
T8 Compliance Verification Script

Verification commands for T8 FindingAdjudication deliverables.
Run this script to verify all T8 hard constraints and deliverables.

Usage:
    python tests/contracts/verify_t8_compliance.py
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skillforge.src.contracts.adjudicator import (
    Adjudicator,
    Decision,
    EvidenceStrength,
    TruthAssessment,
    adjudicate_findings_report,
)


def verify_schema_exists():
    """Verify adjudication schema exists."""
    schema_path = project_root / "skillforge/src/contracts/adjudication_report.schema.json"
    if not schema_path.exists():
        return False, f"Schema not found: {schema_path}"

    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Check required top-level properties
    required_props = ["meta", "input_sources", "rule_decisions", "summary"]
    properties = schema.get("properties", {})
    for prop in required_props:
        if prop not in properties:
            return False, f"Schema missing property: {prop}"

    # Check RuleDecision definition
    if "definitions" not in schema or "rule_decision" not in schema["definitions"]:
        return False, "Schema missing rule_decision definition"

    rd_def = schema["definitions"]["rule_decision"]
    rd_required = [
        "finding_id", "decision", "truth_assessment", "impact_level",
        "evidence_strength", "primary_basis", "largest_uncertainty",
        "recommended_action", "adjudicated_at"
    ]
    for prop in rd_required:
        if prop not in rd_def.get("required", []):
            return False, f"RuleDecision missing required property: {prop}"

    return True, "Schema exists with all required properties"


def verify_adjudicator_module():
    """Verify adjudicator.py module exists and is importable."""
    try:
        from skillforge.src.contracts import adjudicator
        return True, "adjudicator.py module exists and is importable"
    except ImportError as e:
        return False, f"Failed to import adjudicator: {e}"


def verify_hard_constraint_no_pass_without_evidence():
    """T8 Hard Constraint: No PASS decision without evidence."""
    adjudicator = Adjudicator()

    # Finding without evidence
    finding_no_evidence = {
        "finding_id": "F-test-E301-noevidence",
        "source": {"type": "validation", "code": "E302_SCHEMA_VALIDATION_FAILED"},
        "what": {
            "title": "Test Finding",
            "description": "Test",
            "category": "schema_validation",
            "severity": "HIGH",
            "confidence": 0.95,
        },
        "where": {"file_path": "skill.py", "line_number": 42},
        "evidence_refs": [],  # No evidence
        "detected_at": "2026-03-16T12:00:00Z",
    }

    decision = adjudicator.adjudicate_finding(finding_no_evidence)

    if decision.decision == Decision.PASS:
        return False, "FAIL: Finding without evidence got PASS decision"

    if decision.evidence_strength != EvidenceStrength.INSUFFICIENT:
        return False, f"FAIL: Finding without evidence has strength {decision.evidence_strength}"

    return True, "Hard constraint verified: No PASS without evidence"


def verify_hard_constraint_structured_fields():
    """T8 Hard Constraint: All decision fields must be structured enums."""
    from skillforge.src.contracts.adjudicator import (
        Decision, TruthAssessment, ImpactLevel, EvidenceStrength,
        PrimaryBasis, LargestUncertainty, RecommendedAction,
    )

    # Verify all are Enums
    checks = [
        (Decision, "Decision"),
        (TruthAssessment, "TruthAssessment"),
        (ImpactLevel, "ImpactLevel"),
        (EvidenceStrength, "EvidenceStrength"),
        (PrimaryBasis, "PrimaryBasis"),
        (LargestUncertainty, "LargestUncertainty"),
        (RecommendedAction, "RecommendedAction"),
    ]

    for cls, name in checks:
        if not isinstance(cls, type):
            return False, f"{name} is not a class"
        # Check if it's an Enum-like class with value attribute
        if not hasattr(cls, "__members__"):
            return False, f"{name} is not an Enum class"

    return True, "Hard constraint verified: All fields are structured enums"


def verify_deterministic_decisions():
    """T8 Hard Constraint: Same input produces same decision."""
    adjudicator = Adjudicator()

    finding = {
        "finding_id": "F-test-E302-deterministic",
        "source": {"type": "validation", "code": "E302_SCHEMA_VALIDATION_FAILED"},
        "what": {
            "title": "Test Finding",
            "description": "Test",
            "category": "schema_validation",
            "severity": "HIGH",
            "confidence": 0.95,
        },
        "where": {"file_path": "skill.py", "line_number": 42},
        "evidence_refs": [
            {"kind": "FILE", "locator": "report.json", "note": "Report"},
        ],
        "detected_at": "2026-03-16T12:00:00Z",
    }

    decision1 = adjudicator.adjudicate_finding(finding)
    decision2 = adjudicator.adjudicate_finding(finding)

    if decision1.decision != decision2.decision:
        return False, f"Non-deterministic: {decision1.decision} vs {decision2.decision}"

    if decision1.truth_assessment != decision2.truth_assessment:
        return False, f"Non-deterministic truth: {decision1.truth_assessment} vs {decision2.truth_assessment}"

    return True, "Hard constraint verified: Decisions are deterministic"


def verify_sample_report():
    """Verify sample adjudication report exists and is valid."""
    sample_path = project_root / "tests/contracts/t8_samples/sample_adjudication_report.json"

    if not sample_path.exists():
        return False, f"Sample report not found: {sample_path}"

    with open(sample_path, "r") as f:
        sample = json.load(f)

    # Validate structure
    required = ["meta", "input_sources", "rule_decisions", "summary"]
    for prop in required:
        if prop not in sample:
            return False, f"Sample missing {prop}"

    # Check at least one of each decision type
    decisions = [d["decision"] for d in sample["rule_decisions"]]
    decision_types = set(decisions)

    expected_types = {"PASS", "FAIL", "WAIVE", "DEFER"}
    if not expected_types.issubset(decision_types):
        missing = expected_types - decision_types
        return False, f"Sample missing decision types: {missing}"

    return True, "Sample report valid with all decision types"


def verify_all_fields_present():
    """Verify all required fields are present in RuleDecision."""
    from skillforge.src.contracts.adjudicator import (
        RuleDecision, Decision, TruthAssessment, ImpactLevel,
        EvidenceStrength, PrimaryBasis, LargestUncertainty,
        RecommendedAction,
    )

    decision = RuleDecision(
        finding_id="F-test-E301-test",
        decision=Decision.PASS,
        truth_assessment=TruthAssessment.CONFIRMED,
        impact_level=ImpactLevel.HIGH,
        evidence_strength=EvidenceStrength.STRONG,
        primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
        largest_uncertainty=LargestUncertainty.NONE,
        recommended_action=RecommendedAction.MUST_FIX,
        adjudicated_at="2026-03-16T12:00:00Z",
    )

    result = decision.to_dict()

    required_fields = [
        "finding_id", "decision", "truth_assessment", "impact_level",
        "evidence_strength", "primary_basis", "largest_uncertainty",
        "recommended_action", "adjudicated_at", "confidence",
        "evidence_summary", "severity_adjustment"
    ]

    for field in required_fields:
        if field not in result:
            return False, f"RuleDecision missing field: {field}"

    return True, "All required fields present in RuleDecision"


def run_all_verifications():
    """Run all T8 verification checks."""
    checks = [
        ("Schema exists", verify_schema_exists),
        ("Adjudicator module", verify_adjudicator_module),
        ("Hard constraint: No PASS without evidence", verify_hard_constraint_no_pass_without_evidence),
        ("Hard constraint: Structured fields", verify_hard_constraint_structured_fields),
        ("Hard constraint: Deterministic decisions", verify_deterministic_decisions),
        ("Sample report", verify_sample_report),
        ("All fields present", verify_all_fields_present),
    ]

    print("=" * 60)
    print("T8 FindingAdjudication Compliance Verification")
    print("=" * 60)

    all_passed = True
    for name, check_fn in checks:
        try:
            passed, message = check_fn()
            status = "PASS" if passed else "FAIL"
            symbol = "✓" if passed else "✗"
            print(f"\n{symbol} {name}: {status}")
            print(f"  {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"\n✗ {name}: ERROR")
            print(f"  Exception: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All T8 compliance checks PASSED")
    else:
        print("✗ Some T8 compliance checks FAILED")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = run_all_verifications()
    sys.exit(0 if success else 1)
