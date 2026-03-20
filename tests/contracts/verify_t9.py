#!/usr/bin/env python3
"""
T9 Delivery Verification Script.

Verifies T9 deliverables:
1. Schema files exist and are valid JSON
2. Python modules exist and can be imported
3. Sample files exist and are valid
4. Evidence levels are correctly defined (E1-E5)
5. Coverage statement structure is correct

Usage: python tests/contracts/verify_t9.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Colors
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
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


def check_warn(msg: str) -> None:
    """Record a warning."""
    print(f"{YELLOW}⚠ WARN{NC}: {msg}")


def main() -> int:
    """Run all verification checks."""
    global passed, failed

    project_root = Path(__file__).parent.parent.parent

    # Add project root to Python path for imports
    import sys
    sys.path.insert(0, str(project_root))

    print("=" * 60)
    print("T9 Delivery Verification")
    print("=" * 60)
    print()

    # ========================================================================
    # 1. Schema Files
    # ========================================================================
    print("1. Checking schema files...")
    schema_files = [
        "skillforge/src/contracts/coverage_statement.schema.json",
        "skillforge/src/contracts/evidence_level.schema.json",
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
        "skillforge.src.contracts.coverage_statement",
        "skillforge.src.contracts.evidence_level",
    ]

    for module in python_modules:
        try:
            __import__(module)
            check_pass(f"{module} can be imported")
        except ImportError as e:
            check_fail(f"{module} cannot be imported: {e}")

    print()

    # ========================================================================
    # 3. Sample Files
    # ========================================================================
    print("3. Checking sample files...")
    sample_files = [
        "tests/contracts/T9/coverage_statement.sample.json",
        "tests/contracts/T9/evidence_level.json",
    ]

    for rel_path in sample_files:
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
    # 4. Evidence Level Definitions
    # ========================================================================
    print("4. Checking evidence level definitions (E1-E5)...")
    evidence_file = project_root / "tests/contracts/T9/evidence_level.json"

    if evidence_file.exists():
        with open(evidence_file) as f:
            evidence_data = json.load(f)

        level_count = len(evidence_data.get("levels", []))
        if level_count == 5:
            check_pass("Exactly 5 evidence levels defined (E1-E5)")
        else:
            check_fail(f"Expected 5 levels, found {level_count}")

        level_ids = sorted([l["level_id"] for l in evidence_data.get("levels", [])])
        if level_ids == ["E1", "E2", "E3", "E4", "E5"]:
            check_pass("All evidence level IDs correct (E1-E5)")
        else:
            check_fail(f"Evidence level IDs incorrect: {level_ids}")

        strengths = [str(l["strength"]) for l in evidence_data.get("levels", [])]
        if strengths == ["1", "2", "3", "4", "5"]:
            check_pass("Evidence levels correctly ordered by strength (1-5)")
        else:
            check_fail(f"Strength ordering incorrect: {strengths}")
    else:
        check_fail("evidence_level.json not found")

    print()

    # ========================================================================
    # 5. Coverage Statement Structure
    # ========================================================================
    print("5. Checking coverage statement structure...")
    sample_file = project_root / "tests/contracts/T9/coverage_statement.sample.json"

    if sample_file.exists():
        with open(sample_file) as f:
            sample_data = json.load(f)

        required_fields = [
            "statement_id",
            "artifact_id",
            "artifact_type",
            "declared_at",
            "declared_by",
            "covered_items",
            "uncovered_items",
            "exclusions",
            "coverage_summary",
        ]

        missing = []
        for field in required_fields:
            if field not in sample_data:
                missing.append(field)

        if not missing:
            check_pass("All required fields present in coverage_statement.sample.json")
        else:
            for field in missing:
                check_fail(f"Missing required field: {field}")

        # Check evidence levels in covered items
        valid_levels = True
        for item in sample_data.get("covered_items", []):
            if item.get("evidence_level") not in ["E1", "E2", "E3", "E4", "E5"]:
                valid_levels = False
                break

        if valid_levels:
            check_pass("All covered items have valid evidence levels")
        else:
            check_fail("Some covered items have invalid evidence levels")
    else:
        check_fail("coverage_statement.sample.json not found")

    print()

    # ========================================================================
    # 6. Test Suite
    # ========================================================================
    print("6. Running test suite...")
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/contracts/test_t9_coverage.py", "-v", "--tb=short"],
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
        print(f"{GREEN}✓ T9 DELIVERY VERIFIED{NC}")
        return 0
    else:
        print(f"{RED}✗ T9 DELIVERY HAS ISSUES{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
