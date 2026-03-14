#!/usr/bin/env python3
"""
L6 Authenticity Protocol Gate Script

This script runs the T1-T5 protocol tests and enforces fail-closed behavior.
If any test fails, the gate blocks the pipeline.

Task: T10 - ISSUE-09: CI 强制 Gate 接入
Executor: vs--cc3

Usage:
    python scripts/run_l6_protocol_gate.py

Exit codes:
    0: All tests passed
    1: Some tests failed (gate blocked)
"""

import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path


def run_protocol_tests():
    """Run the L6 protocol tests and return results."""
    print("=" * 60)
    print("L6 Authenticity Protocol Gate")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print()

    # Define test categories
    test_categories = [
        ("T1", "Tampering Detection", "test_l6_protocol.py::TestT1TamperingDetection"),
        ("T2", "Replay Attack Prevention", "test_l6_protocol.py::TestT2ReplayAttackPrevention"),
        ("T3", "Expiration Detection", "test_l6_protocol.py::TestT3ExpirationDetection"),
        ("T4", "Forged Signature Detection", "test_l6_protocol.py::TestT4ForgedSignatureDetection"),
        ("T5", "Unregistered Node Detection", "test_l6_protocol.py::TestT5UnregisteredNodeDetection"),
    ]

    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "categories": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
        },
        "gate_decision": None,
    }

    all_passed = True

    for test_id, name, test_path in test_categories:
        print(f"\n[{test_id}] {name}")
        print("-" * 40)

        cmd = [
            sys.executable, "-m", "pytest",
            f"skillforge/tests/{test_path}",
            "-v", "--tb=short", "-q"
        ]

        result = subprocess.run(
            cmd,
            cwd="skillforge-spec-pack",
            capture_output=True,
            text=True
        )

        # Parse output
        passed = result.returncode == 0

        # Extract test counts from output
        output = result.stdout + result.stderr

        category_result = {
            "test_id": test_id,
            "name": name,
            "passed": passed,
            "returncode": result.returncode,
        }

        results["categories"][test_id] = category_result
        results["summary"]["total"] += 1

        if passed:
            results["summary"]["passed"] += 1
            print(f"  ✓ PASS")
        else:
            results["summary"]["failed"] += 1
            all_passed = False
            print(f"  ✗ FAIL")
            print(f"  Output: {output[-500:]}")  # Last 500 chars

    # Run full test suite for counts
    print("\n" + "=" * 60)
    print("Full Protocol Test Suite")
    print("=" * 60)

    cmd = [
        sys.executable, "-m", "pytest",
        "skillforge/tests/test_l6_protocol.py",
        "-v", "--tb=line", "-q"
    ]

    full_result = subprocess.run(
        cmd,
        cwd="skillforge-spec-pack",
        capture_output=True,
        text=True
    )

    print(full_result.stdout)

    # Determine gate decision
    if all_passed:
        results["gate_decision"] = "ALLOW"
        print("\n" + "=" * 60)
        print("GATE DECISION: ALLOW")
        print("All T1-T5 protocol tests passed")
        print("=" * 60)
    else:
        results["gate_decision"] = "DENY"
        print("\n" + "=" * 60)
        print("GATE DECISION: DENY")
        print("Some T1-T5 protocol tests failed")
        print("=" * 60)

    # Write results to file
    output_dir = Path("reports/l6_protocol_gate")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"gate_result_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to: {output_file}")

    # Fail-closed: exit 1 if any test failed
    return 0 if all_passed else 1


def main():
    """Main entry point."""
    # Check if we're in the repo root
    if not Path("skillforge-spec-pack").exists():
        print("Error: Must run from repository root")
        sys.exit(1)

    exit_code = run_protocol_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
