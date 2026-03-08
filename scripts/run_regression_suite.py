#!/usr/bin/env python3
"""
Run Regression Suite - 回归测试套件入口

用于 CI 运行的回归测试入口。支持 --ci 模式，输出标准化结果。

Contract: docs/SEEDS_v0.md P2 (T32)
Job ID: L45-D6-SEEDS-P2-20260220-006

Usage:
    python scripts/run_regression_suite.py              # 运行所有回归测试
    python scripts/run_regression_suite.py --ci         # CI 模式
    python scripts/run_regression_suite.py --case 001   # 运行特定 case
    python scripts/run_regression_suite.py --nightly    # nightly 模式

Exit Codes:
    0: All tests passed
    1: One or more tests failed
    2: Configuration error
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Add skillforge src to path (for direct imports like `from storage...`)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "skillforge" / "src"))
# Add project root (for imports like `from skillforge.src...`)
sys.path.insert(0, str(PROJECT_ROOT))

# Set test signing key for gate_permit
os.environ["PERMIT_HS256_KEY"] = "test-signing-key-for-regression-suite-2026"

# Constants
REGRESSION_DIR = PROJECT_ROOT / "regression"
CASES_DIR = REGRESSION_DIR / "cases"
JOB_ID = "L45-D6-SEEDS-P2-20260220-006"


@dataclass
class RegressionResult:
    """Result of a single regression case execution."""
    case_id: str
    description: str
    passed: bool
    duration_ms: float
    error_message: Optional[str] = None
    details: dict = field(default_factory=dict)


@dataclass
class RegressionReport:
    """Overall regression suite report."""
    job_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    duration_ms: float
    results: list[RegressionResult]
    ci_mode: bool

    @property
    def success(self) -> bool:
        return self.failed_cases == 0

    def to_json(self) -> dict:
        return {
            "job_id": self.job_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "ci_mode": self.ci_mode,
            "results": [
                {
                    "case_id": r.case_id,
                    "description": r.description,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "error_message": r.error_message,
                    "details": r.details,
                }
                for r in self.results
            ],
        }


def discover_cases() -> list[str]:
    """Discover all regression case directories."""
    cases = []
    if CASES_DIR.exists():
        for case_dir in sorted(CASES_DIR.iterdir()):
            if case_dir.is_dir() and case_dir.name.startswith("case_"):
                input_file = case_dir / "input.json"
                if input_file.exists():
                    cases.append(case_dir.name)
    return cases


def run_case(case_id: str) -> RegressionResult:
    """Run a single regression case and return the result."""
    case_dir = CASES_DIR / case_id
    input_file = case_dir / "input.json"

    start_time = time.time()

    try:
        # Load input
        with open(input_file, "r", encoding="utf-8") as f:
            case_data = json.load(f)

        category = case_data.get("category", "unknown")
        description = case_data.get("description", "No description")
        input_data = case_data.get("input", {})

        # Execute based on category
        if category == "gate_permit":
            result = _run_gate_permit_case(case_data)
        elif category == "permit_required_policy":
            result = _run_permit_required_case(case_data)
        elif category == "registry_store":
            result = _run_registry_store_case(case_data)
        elif category == "audit_event_writer":
            result = _run_audit_event_case(case_data)
        elif category == "usage_meter":
            result = _run_usage_meter_case(case_data)
        else:
            result = {"passed": False, "error": f"Unknown category: {category}"}

        duration_ms = (time.time() - start_time) * 1000

        if result.get("passed", False):
            return RegressionResult(
                case_id=case_id,
                description=description,
                passed=True,
                duration_ms=duration_ms,
                details=result.get("details", {}),
            )
        else:
            return RegressionResult(
                case_id=case_id,
                description=description,
                passed=False,
                duration_ms=duration_ms,
                error_message=result.get("error", "Unknown error"),
                details=result.get("details", {}),
            )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return RegressionResult(
            case_id=case_id,
            description=f"Exception during execution",
            passed=False,
            duration_ms=duration_ms,
            error_message=str(e),
        )


def _run_gate_permit_case(case_data: dict) -> dict:
    """Run gate permit regression case."""
    from skills.gates.gate_permit import GatePermit

    gate = GatePermit()
    input_data = case_data.get("input", {})
    expected_gate_decision = case_data.get("expected_gate_decision")
    expected_error_code = case_data.get("expected_error_code")

    result = gate.execute(input_data)

    details = {
        "gate_decision": result.get("gate_decision"),
        "error_code": result.get("error_code"),
        "release_allowed": result.get("release_allowed"),
    }

    # Verify expectations
    if expected_gate_decision and result.get("gate_decision") != expected_gate_decision:
        return {
            "passed": False,
            "error": f"gate_decision mismatch: expected {expected_gate_decision}, got {result.get('gate_decision')}",
            "details": details,
        }

    if expected_error_code and result.get("error_code") != expected_error_code:
        return {
            "passed": False,
            "error": f"error_code mismatch: expected {expected_error_code}, got {result.get('error_code')}",
            "details": details,
        }

    return {"passed": True, "details": details}


def _run_permit_required_case(case_data: dict) -> dict:
    """Run permit required policy regression case."""
    from contracts.policy.permit_required import (
        DENY_WITHOUT_PERMIT_ERROR_CODE,
        PermitRequiredError,
        check_permit_or_raise,
        is_action_requiring_permit,
    )

    input_data = case_data.get("input", {})
    action = input_data.get("action")
    permit_valid = input_data.get("permit_valid", True)
    expected_requires_permit = case_data.get("expected_requires_permit")
    expected_error_code = case_data.get("expected_error_code")

    # Check if action requires permit
    requires_permit = is_action_requiring_permit(action)
    details = {
        "action": action,
        "requires_permit": requires_permit,
    }

    # Verify requires_permit expectation
    if expected_requires_permit is not None and requires_permit != expected_requires_permit:
        return {
            "passed": False,
            "error": f"requires_permit mismatch: expected {expected_requires_permit}, got {requires_permit}",
            "details": details,
        }

    # Test check_permit_or_raise
    if requires_permit and not permit_valid:
        try:
            check_permit_or_raise(action, permit_valid=permit_valid)
            return {
                "passed": False,
                "error": "Expected PermitRequiredError but none was raised",
                "details": details,
            }
        except PermitRequiredError as e:
            details["error_code"] = e.code
            if expected_error_code and e.code != expected_error_code:
                return {
                    "passed": False,
                    "error": f"error_code mismatch: expected {expected_error_code}, got {e.code}",
                    "details": details,
                }

    return {"passed": True, "details": details}


def _run_registry_store_case(case_data: dict) -> dict:
    """Run registry store regression case."""
    from storage.registry_store import RegistryStore, SkillRegistryEntry

    # Use a temp file for regression testing
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        temp_path = Path(f.name)

    try:
        store = RegistryStore(temp_path)

        input_data = case_data.get("input", {})
        entry = SkillRegistryEntry(
            skill_id=input_data.get("skill_id", "SKILL-TEST"),
            source={"type": "regression", "repo_url": "https://github.com/regression/test", "commit_sha": "abc123"},
            revision=input_data.get("revision", "REV-001"),
            pack_hash=input_data.get("pack_hash", ""),
            permit_id=input_data.get("permit_id", ""),
            tombstone_state=input_data.get("tombstone_state", "ACTIVE"),
        )

        # Append entry
        result = store.append(entry)
        if not result.success:
            return {
                "passed": False,
                "error": f"Append failed: {result.error_message}",
                "details": {"skill_id": entry.skill_id},
            }

        # Read latest - returns RegistryQueryResult with .entry attribute
        query_result = store.get_latest_active(entry.skill_id)

        details = {
            "skill_id": entry.skill_id,
            "appended_revision": entry.revision,
            "query_success": query_result.success,
        }

        if not query_result.success:
            return {
                "passed": False,
                "error": f"Query failed: {query_result.error_message}",
                "details": details,
            }

        if query_result.entry is None:
            return {
                "passed": False,
                "error": "Failed to read latest entry (entry is None)",
                "details": details,
            }

        details["latest_revision"] = query_result.entry.revision

        if query_result.entry.revision != entry.revision:
            return {
                "passed": False,
                "error": f"Revision mismatch: expected {entry.revision}, got {query_result.entry.revision}",
                "details": details,
            }

        return {"passed": True, "details": details}

    finally:
        if temp_path.exists():
            temp_path.unlink()


def _run_audit_event_case(case_data: dict) -> dict:
    """Run audit event writer regression case."""
    from skills.audit_event_writer import AuditEventWriter

    # Use a temp file for regression testing
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        temp_path = Path(f.name)

    try:
        writer = AuditEventWriter(temp_path)

        input_data = case_data.get("input", {})
        event_type = input_data.get("event_type", "GATE_FINISH")

        if event_type == "GATE_FINISH":
            writer.write_gate_finish(
                job_id=input_data.get("job_id", "JOB-TEST"),
                gate_node=input_data.get("gate_node", "test_gate"),
                decision=input_data.get("decision", "PASS"),
                error_code=input_data.get("error_code"),
                issue_keys=input_data.get("issue_keys", []),
                evidence_refs=input_data.get("evidence_refs", []),
            )

        # Verify write using query method
        events = writer.query(job_id=input_data.get("job_id", "JOB-TEST"))

        details = {
            "event_type": event_type,
            "job_id": input_data.get("job_id"),
            "events_count": len(events),
        }

        if len(events) == 0:
            return {
                "passed": False,
                "error": "No events written",
                "details": details,
            }

        return {"passed": True, "details": details}

    finally:
        if temp_path.exists():
            temp_path.unlink()


def _run_usage_meter_case(case_data: dict) -> dict:
    """Run usage meter regression case."""
    from contracts.policy.usage_meter import UsageMeter

    # Use a temp file for regression testing
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        temp_path = Path(f.name)

    try:
        meter = UsageMeter(temp_path)

        input_data = case_data.get("input", {})
        meter.record(
            account_id=input_data.get("account_id", "ACC-TEST"),
            action=input_data.get("action", "AUDIT_L3"),
            units=input_data.get("units", 1),
            job_id=input_data.get("job_id", "JOB-TEST"),
        )

        # Verify record
        usage = meter.get_usage(
            account_id=input_data.get("account_id", "ACC-TEST"),
            action=input_data.get("action"),
        )

        details = {
            "account_id": input_data.get("account_id"),
            "action": input_data.get("action"),
            "total_units": usage.total_units if usage else 0,
        }

        if usage is None or usage.total_units == 0:
            return {
                "passed": False,
                "error": "Usage not recorded",
                "details": details,
            }

        return {"passed": True, "details": details}

    finally:
        if temp_path.exists():
            temp_path.unlink()


def run_suite(ci_mode: bool = False, case_filter: Optional[str] = None, nightly: bool = False) -> RegressionReport:
    """Run the regression suite."""
    start_time = time.time()

    # Discover cases
    all_cases = discover_cases()

    # Filter if specified
    if case_filter:
        all_cases = [c for c in all_cases if case_filter in c]

    if not all_cases:
        print(f"No regression cases found in {CASES_DIR}")
        return RegressionReport(
            job_id=JOB_ID,
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            duration_ms=0,
            results=[],
            ci_mode=ci_mode,
        )

    print(f"\n{'='*60}")
    print(f"Regression Suite - {JOB_ID}")
    print(f"{'='*60}")
    print(f"Mode: {'CI' if ci_mode else 'Local'}")
    print(f"Cases discovered: {len(all_cases)}")
    print(f"{'='*60}\n")

    # Run each case
    results = []
    for case_id in all_cases:
        print(f"Running {case_id}...", end=" ")
        result = run_case(case_id)
        results.append(result)

        if result.passed:
            print(f"PASSED ({result.duration_ms:.1f}ms)")
        else:
            print(f"FAILED ({result.duration_ms:.1f}ms)")
            if result.error_message:
                print(f"  Error: {result.error_message}")

    # Calculate summary
    total_duration = (time.time() - start_time) * 1000
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    # Print summary
    print(f"\n{'='*60}")
    print(f"Results Summary")
    print(f"{'='*60}")
    print(f"Total:   {len(results)}")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Duration: {total_duration:.1f}ms")
    print(f"Status:  {'PASS' if failed == 0 else 'FAIL'}")
    print(f"{'='*60}\n")

    return RegressionReport(
        job_id=JOB_ID,
        total_cases=len(results),
        passed_cases=passed,
        failed_cases=failed,
        duration_ms=total_duration,
        results=results,
        ci_mode=ci_mode,
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Regression Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_regression_suite.py              # Run all
    python scripts/run_regression_suite.py --ci         # CI mode
    python scripts/run_regression_suite.py --case 001   # Run case_001
    python scripts/run_regression_suite.py --nightly    # Nightly mode
        """,
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Run in CI mode (exit code 1 on failure)",
    )
    parser.add_argument(
        "--case",
        type=str,
        help="Run specific case (e.g., '001' for case_001)",
    )
    parser.add_argument(
        "--nightly",
        action="store_true",
        help="Run in nightly mode (full suite with detailed output)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON report to file",
    )

    args = parser.parse_args()

    # Run suite
    report = run_suite(
        ci_mode=args.ci,
        case_filter=args.case,
        nightly=args.nightly,
    )

    # Output JSON report if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report.to_json(), f, indent=2)
        print(f"Report written to: {args.output}")

    # CI mode: output JSON and exit with proper code
    if args.ci:
        print("\nCI Mode Output:")
        print(json.dumps(report.to_json(), indent=2))

    # Exit code
    if report.failed_cases > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
