"""
T10 Compliance Verification Script

Verification for T10 JudgmentOverride and ReleaseDecision deliverables.
Zero Exception Directives enforced:
1. 判断覆盖洗白硬阻断项 → 直接 FAIL
2. release decision 无 supporting evidence → 直接 FAIL

Usage:
    python tests/contracts/verify_t10_compliance.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skillforge.src.contracts.judgment_overrides import (
    JudgmentOverrideErrorCode,
    can_override_finding,
)
from skillforge.src.contracts.release_decision import (
    ReleaseDecisionErrorCode,
    check_blockable_findings,
)


def verify_override_blocks_critical_confirmed():
    """Zero Exception: CRITICAL+CONFIRMED findings cannot be overridden."""
    result = can_override_finding(
        original_decision="REJECT",
        evidence_strength="STRONG",
        truth_assessment="CONFIRMED",
        severity="CRITICAL",
        evidence_count=2,
    )

    if result["allowed"]:
        return False, "FAIL: CRITICAL+CONFIRMED finding can be overridden"
    if JudgmentOverrideErrorCode.CRITICAL_RISK_NO_OVERRIDE not in result["reason"]:
        return False, f"FAIL: Wrong error code: {result['reason']}"

    return True, "PASS: CRITICAL+CONFIRMED findings blocked from override"


def verify_override_blocks_no_evidence():
    """Zero Exception: Findings with no evidence cannot be overridden."""
    result = can_override_finding(
        original_decision="REJECT",
        evidence_strength="INSUFFICIENT",
        truth_assessment="UNCERTAIN",
        severity="HIGH",
        evidence_count=0,
    )

    if result["allowed"]:
        return False, "FAIL: No evidence finding can be overridden"
    if JudgmentOverrideErrorCode.NO_EVIDENCE_OVERRIDE not in result["reason"]:
        return False, f"FAIL: Wrong error code: {result['reason']}"

    return True, "PASS: No evidence findings blocked from override"


def verify_override_blocks_insufficient_evidence():
    """Zero Exception: INSUFFICIENT evidence findings cannot be overridden."""
    result = can_override_finding(
        original_decision="REJECT",
        evidence_strength="INSUFFICIENT",
        truth_assessment="UNCERTAIN",
        severity="HIGH",
        evidence_count=1,  # Even with 1 evidence, INSUFFICIENT blocks override
    )

    if result["allowed"]:
        return False, "FAIL: INSUFFICIENT evidence finding can be overridden"
    if JudgmentOverrideErrorCode.MISSING_EVIDENCE not in result["reason"]:
        return False, f"FAIL: Wrong error code: {result['reason']}"

    return True, "PASS: INSUFFICIENT evidence findings blocked from override"


def verify_release_decision_requires_evidence():
    """
    Zero Exception: Release decision without supporting evidence should FAIL.

    NOTE: This test currently FAILS because make_release_decision() does not
    enforce the evidence_refs constraint. This is a Zero Exception Directive
    violation that must be fixed.
    """
    from skillforge.src.contracts.release_decision import make_release_decision, EvidenceRef

    # Try to make a release decision with NO evidence
    try:
        decision = make_release_decision(
            findings=[],  # Clean findings (no blockable)
            overrides=[],
            residual_risks=[],
            evidence_refs=[],  # ← NO EVIDENCE
            run_id="test",
            skill_id="test-skill",
        )

        # If we get here, the function allowed empty evidence_refs
        if decision.evidence_refs == []:
            return False, f"FAIL: Release decision allowed with NO evidence (outcome={decision.outcome.value})"

        return True, "PASS: Release decision requires evidence"
    except ValueError as e:
        # Expected behavior: function should raise error
        if "NO_EVIDENCE" in str(e) or ReleaseDecisionErrorCode.NO_EVIDENCE in str(e):
            return True, "PASS: Release decision correctly rejects empty evidence"
        return False, f"FAIL: Wrong error: {e}"


def verify_blockable_findings_detection():
    """Verify blockable findings are correctly identified."""
    findings = [
        # CRITICAL + CONFIRMED → blockable
        {
            "finding_id": "F-test-001",
            "what": {"severity": "CRITICAL"},
            "truth_assessment": "CONFIRMED",
            "evidence_refs": [{"kind": "FILE"}],
        },
        # No evidence → blockable
        {
            "finding_id": "F-test-002",
            "what": {"severity": "HIGH"},
            "evidence_refs": [],
        },
        # INSUFFICIENT evidence → blockable
        {
            "finding_id": "F-test-003",
            "what": {"severity": "MEDIUM"},
            "evidence_strength": "INSUFFICIENT",
            "evidence_refs": [],
        },
        # Clean finding → not blockable
        {
            "finding_id": "F-test-004",
            "what": {"severity": "LOW"},
            "truth_assessment": "LIKELY_FALSE",
            "evidence_refs": [{"kind": "FILE"}],
        },
    ]

    result = check_blockable_findings(findings, overridden_ids=set())

    if not result["has_blockable"]:
        return False, "FAIL: Blockable findings not detected"

    if len(result["blocking_findings"]) != 3:
        return False, f"FAIL: Expected 3 blockable, got {len(result['blocking_findings'])}"

    if "F-test-004" in result["blocking_findings"]:
        return False, "FAIL: Clean finding incorrectly marked as blockable"

    return True, "PASS: Blockable findings correctly detected"


def run_all_verifications():
    """Run all T10 compliance checks."""
    checks = [
        ("Zero Exception: CRITICAL+CONFIRMED blocked", verify_override_blocks_critical_confirmed),
        ("Zero Exception: No evidence blocked", verify_override_blocks_no_evidence),
        ("Zero Exception: INSUFFICIENT evidence blocked", verify_override_blocks_insufficient_evidence),
        ("Zero Exception: Release requires evidence", verify_release_decision_requires_evidence),
        ("Blockable findings detection", verify_blockable_findings_detection),
    ]

    print("=" * 60)
    print("T10 JudgmentOverride & ReleaseDecision Compliance Verification")
    print("Zero Exception Directives Enforced")
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
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All T10 compliance checks PASSED")
    else:
        print("✗ Some T10 compliance checks FAILED")
        print("\nACTION REQUIRED: Fix Zero Exception Directive violations")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = run_all_verifications()
    sys.exit(0 if success else 1)
