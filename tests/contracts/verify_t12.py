#!/usr/bin/env python3
"""
T12 Delivery Verification Script.

Verifies T12 deliverables:
1. IssueRecord and FixRecommendation schema files exist
2. Python modules can be imported
3. Finding -> IssueRecord -> FixRecommendation chain works
4. Only PASS/FAIL decisions create issues (WAIVE/DEFER do not)
5. FixRecommendation always references issue_id

Usage: python tests/contracts/verify_t12.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Colors
GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"

# Track results
passed = 0
failed = 0


def check_pass(msg: str) -> None:
    """Record a passed check."""
    global passed
    print(f"{GREEN}✓ PASS{NC}: {msg}")
    passed += 1


def check_fail(msg: str) -> None:
    """Record a failed check."""
    global failed
    print(f"{RED}✗ FAIL{NC}: {msg}")
    failed += 1


def main() -> int:
    """Run all verification checks."""
    global passed, failed

    project_root = Path(__file__).parent.parent.parent

    # Add to path
    sys.path.insert(0, str(project_root))

    print("=" * 60)
    print("T12 Delivery Verification")
    print("=" * 60)
    print()

    # ========================================================================
    # 1. Schema Files
    # ========================================================================
    print("1. Checking schema files...")
    schema_files = [
        "skillforge/src/contracts/issue_record.schema.json",
        "skillforge/src/contracts/fix_recommendation.schema.json",
    ]

    for rel_path in schema_files:
        full_path = project_root / rel_path
        if full_path.exists():
            try:
                with open(full_path) as f:
                    json.load(f)
                check_pass(f"{rel_path} exists and is valid JSON")
            except json.JSONDecodeError:
                check_fail(f"{rel_path} is not valid JSON")
        else:
            check_fail(f"{rel_path} does not exist")

    print()

    # ========================================================================
    # 2. Python Modules
    # ========================================================================
    print("2. Checking Python modules...")
    python_modules = [
        "skillforge.src.contracts.issue_record",
        "skillforge.src.contracts.fix_recommendation",
    ]

    for module in python_modules:
        try:
            __import__(module)
            check_pass(f"{module} can be imported")
        except ImportError as e:
            check_fail(f"{module} cannot be imported: {e}")

    print()

    # ========================================================================
    # 3. Chain Verification
    # ========================================================================
    print("3. Checking Finding -> IssueRecord -> FixRecommendation chain...")

    try:
        from skillforge.src.contracts.issue_record import (
            create_issue_from_decision,
            IssueRecord,
        )
        from skillforge.src.contracts.fix_recommendation import (
            create_recommendation_for_issue,
            FixOption,
        )

        # Create sample finding
        finding = {
            "finding_id": "F-test-E000-chain001",
            "source": {"type": "validation", "code": "E000_TEST"},
            "what": {
                "title": "Test finding",
                "description": "Test",
                "category": "schema_validation",
                "severity": "HIGH",
                "confidence": 0.9,
            },
            "where": {"file_path": "test.json", "line_number": 1},
            "evidence_refs": [{"kind": "FILE", "locator": "test.json"}],
        }

        # Create PASS decision (should create issue)
        rule_decision_pass = {
            "finding_id": "F-test-E000-chain001",
            "decision": "PASS",
            "truth_assessment": "CONFIRMED",
            "impact_level": "HIGH",
            "evidence_strength": "STRONG",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }

        issue = create_issue_from_decision(rule_decision_pass, finding)
        check_pass("Finding -> IssueRecord chain works (PASS decision)")

        # Verify issue properties
        assert issue.finding_id == finding["finding_id"]
        assert issue.rule_decision_ref.decision == "PASS"
        check_pass("IssueRecord correctly references finding and decision")

        # Create recommendation
        options = [
            FixOption(
                option_id="OPT-1",
                name="Fix",
                tier="RECOMMENDED",
                description="Fix it",
            )
        ]

        recommendation = create_recommendation_for_issue(
            issue=issue,
            recommendation_type="CODE_FIX",
            options=options,
        )
        check_pass("IssueRecord -> FixRecommendation chain works")

        # Verify recommendation references issue
        assert recommendation.issue_id == issue.issue_id
        check_pass("FixRecommendation correctly references issue_id")

    except Exception as e:
        check_fail(f"Chain verification failed: {e}")

    print()

    # ========================================================================
    # 4. WAIVE/DEFER Do Not Create Issues
    # ========================================================================
    print("4. Checking WAIVE/DEFER decisions do NOT create issues...")

    try:
        from skillforge.src.contracts.issue_record import (
            create_issue_from_decision,
        )

        finding = {
            "finding_id": "F-test-E000-waive001",
            "source": {"type": "validation", "code": "E000_TEST"},
            "what": {
                "title": "Test finding",
                "description": "Test",
                "category": "schema_validation",
                "severity": "LOW",
                "confidence": 0.5,
            },
            "where": {"file_path": "test.json"},
        }

        # WAIVE decision
        rule_decision_waive = {
            "finding_id": "F-test-E000-waive001",
            "decision": "WAIVE",
            "truth_assessment": "FALSE_POSITIVE",
            "impact_level": "NEGLIGIBLE",
            "evidence_strength": "STRONG",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }

        try:
            create_issue_from_decision(rule_decision_waive, finding)
            check_fail("WAIVE decision incorrectly created an issue")
        except ValueError:
            check_pass("WAIVE decision correctly does NOT create issue")

        # DEFER decision
        rule_decision_defer = {
            "finding_id": "F-test-E000-defer001",
            "decision": "DEFER",
            "truth_assessment": "UNCERTAIN",
            "impact_level": "MEDIUM",
            "evidence_strength": "INSUFFICIENT",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }

        try:
            create_issue_from_decision(rule_decision_defer, finding)
            check_fail("DEFER decision incorrectly created an issue")
        except ValueError:
            check_pass("DEFER decision correctly does NOT create issue")

    except Exception as e:
        check_fail(f"WAIVE/DEFER verification failed: {e}")

    print()

    # ========================================================================
    # 5. Test Suite
    # ========================================================================
    print("5. Running test suite...")
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/contracts/test_t12_issue_tracking.py", "-v"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Parse test count
        for line in result.stdout.split("\n"):
            if "passed" in line:
                check_pass(f"Test suite passed ({line.strip()})")
                break
        else:
            check_pass("Test suite passed")
    else:
        check_fail("Test suite failed")

    print()

    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"{GREEN}Passed: {passed}{NC}")
    print(f"{RED}Failed: {failed}{NC}")
    print()

    if failed == 0:
        print(f"{GREEN}✓ T12 DELIVERY VERIFIED{NC}")
        return 0
    else:
        print(f"{RED}✗ T12 DELIVERY HAS ISSUES{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
