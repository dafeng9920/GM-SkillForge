#!/usr/bin/env python3
"""
Unified Validation Gate - Single Entry Point for GM-SkillForge Verification

Task: T-ASM-03
Execution Agent: C

This script provides a minimal unified validation entry point that orchestrates
all validation checks required by the mainline workflow while preserving fail-closed
semantics and maintaining existing validation capabilities.

MAINLINE VALIDATION CHAINS:
1. Antigravity-2 Guard (Permit + Delivery + Three-Hash)
2. N-Boundary Verification (N1 + N2 + N3)
3. Pre-Absorb Check

CLOUD EXECUTION VALIDATION:
4. Receipt Verification
5. Evidence Chain (optional, standalone)

Usage:
    # Full mainline validation
    python scripts/unified_validation_gate.py --mode mainline --permit permits/task/permit.json

    # Cloud task verification
    python scripts/unified_validation_gate.py --mode cloud --task-id TASK-001

    # Quick permit check
    python scripts/unified_validation_gate.py --mode quick --permit permits/task/permit.json

Spec source: docs/2026-03-04/v0-L5/
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class ValidationMode(str, Enum):
    """Validation execution modes."""
    MAINLINE = "mainline"  # Full Antigravity-2 + N-Boundary checks
    CLOUD = "cloud"  # Cloud task verification
    QUICK = "quick"  # Permit + Delivery only
    ABSORB = "absorb"  # Pre-absorb gate


class GateDecision(str, Enum):
    """Gate decision values."""
    ALLOW = "ALLOW"
    DENY = "DENY"


class UnifiedValidationResult:
    """Result of unified validation gate."""

    def __init__(self, mode: ValidationMode):
        self.mode = mode
        self.status = GateDecision.DENY
        self.decision_time = datetime.now(UTC).isoformat()
        self.checks = {}
        self.errors = []
        self.warnings = []
        self.required_changes = []
        self.evidence_refs = []

    def add_check_result(self, name: str, result: dict[str, Any]):
        """Add a check result."""
        self.checks[name] = result

    def add_error(self, code: str, message: str, required_change: str | None = None):
        """Add an error."""
        self.errors.append({"code": code, "message": message})
        if required_change:
            self.required_changes.append(required_change)

    def add_warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)

    def add_evidence_ref(self, ref: str):
        """Add an evidence reference."""
        self.evidence_refs.append(ref)

    def set_allow(self):
        """Set status to ALLOW."""
        self.status = GateDecision.ALLOW


def run_script(script_path: Path, args: list[str], timeout: int = 120) -> dict[str, Any]:
    """Run a validation script and capture output."""
    result = {
        "script": str(script_path),
        "exit_code": -1,
        "stdout": "",
        "stderr": "",
        "status": "FAIL",
    }

    if not script_path.exists():
        result["error"] = f"Script not found: {script_path}"
        return result

    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd(),
        )
        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()
        result["status"] = "PASS" if proc.returncode == 0 else "FAIL"

    except subprocess.TimeoutExpired:
        result["error"] = f"Script timed out after {timeout}s"
    except Exception as e:
        result["error"] = str(e)

    return result


def run_antigravity_2_guard(
    permit_path: Path,
    demand_path: Path | None = None,
    contract_path: Path | None = None,
    decision_path: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """
    Run Antigravity-2 Guard - Three-stage validation:
    1. Permit five-field validation
    2. Fixed-caliber binding (optional)
    3. Delivery completeness (six items)
    4. Three-hash consistency

    This is the PRIMARY mainline validation gate.
    """
    guard_script = Path(__file__).parent / "antigravity_2_guard.py"

    args = ["--permit", str(permit_path)]

    if demand_path:
        args.extend(["--demand", str(demand_path)])
    if contract_path:
        args.extend(["--contract", str(contract_path)])
    if decision_path:
        args.extend(["--decision", str(decision_path)])
    if manifest_path:
        args.extend(["--manifest", str(manifest_path)])

    return run_script(guard_script, args)


def run_n_boundary_verification(task_id: str) -> dict[str, Any]:
    """
    Run N-Boundary verification for cloud tasks:
    - N1: Command allowlist
    - N2: Artifact completeness
    - N3: Time window enforcement

    Returns combined N-boundary check result.
    """
    n_checks = {}

    # N1: Command allowlist
    n1_script = Path(__file__).parent / "verify_n1_command_allowlist.py"
    n1_result = run_script(n1_script, ["--task-id", task_id])
    n_checks["n1_command_allowlist"] = n1_result

    # N2: Artifact completeness
    n2_script = Path(__file__).parent / "verify_n2_artifact_completeness.py"
    n2_result = run_script(n2_script, ["--task-id", task_id])
    n_checks["n2_artifact_completeness"] = n2_result

    # N3: Time window
    n3_script = Path(__file__).parent / "verify_n3_time_window.py"
    n3_result = run_script(n3_script, ["--task-id", task_id])
    n_checks["n3_time_window"] = n3_result

    # Overall N-boundary status
    all_passed = all(
        c.get("status") == "PASS" or c.get("status") == "ALLOW"
        for c in [n1_result, n2_result, n3_result]
    )

    return {
        "overall_status": "PASS" if all_passed else "FAIL",
        "n1_command_allowlist": n1_result,
        "n2_artifact_completeness": n2_result,
        "n3_time_window": n3_result,
    }


def run_pre_absorb_check(task_id: str) -> dict[str, Any]:
    """Run pre-absorb gate check."""
    check_script = Path(__file__).parent / "pre_absorb_check.sh"
    result = {
        "script": str(check_script),
        "exit_code": -1,
        "stdout": "",
        "stderr": "",
        "status": "FAIL",
    }

    if not check_script.exists():
        result["error"] = f"Script not found: {check_script}"
        return result

    try:
        proc = subprocess.run(
            ["bash", str(check_script), task_id],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path.cwd(),
        )
        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()
        result["status"] = "PASS" if proc.returncode == 0 else "FAIL"

    except subprocess.TimeoutExpired:
        result["error"] = "Check timed out"
    except Exception as e:
        result["error"] = str(e)

    return result


def run_mainline_validation(
    permit_path: Path,
    demand_path: Path | None = None,
    contract_path: Path | None = None,
    decision_path: Path | None = None,
    manifest_path: Path | None = None,
    run_n_boundary: bool = False,
    task_id: str | None = None,
) -> UnifiedValidationResult:
    """
    Run full mainline validation.

    Mainline = Antigravity-2 Guard (required) + N-Boundary (optional for cloud tasks)
    """
    result = UnifiedValidationResult(ValidationMode.MAINLINE)

    print(f"[UVG] Mainline Validation Mode")
    print(f"[UVG] Permit: {permit_path}")
    print("=" * 60)

    # Stage 1: Antigravity-2 Guard (REQUIRED)
    print("\n[Stage 1] Antigravity-2 Guard")
    ag2_result = run_antigravity_2_guard(
        permit_path, demand_path, contract_path, decision_path, manifest_path
    )
    result.add_check_result("antigravity_2_guard", ag2_result)

    # Parse decision from output
    if "ALLOW" in ag2_result.get("stdout", ""):
        print("[Stage 1] Result: ALLOW")
        result.add_evidence_ref("antigravity_2_guard:ALLOW")
    else:
        print("[Stage 1] Result: DENY")
        result.add_error(
            "AG2_DENY",
            "Antigravity-2 Guard denied the request",
            "Fix permit binding, delivery completeness, or three-hash consistency"
        )
        return result

    # Stage 2: N-Boundary (optional, for cloud tasks)
    if run_n_boundary and task_id:
        print("\n[Stage 2] N-Boundary Verification")
        n_boundary_result = run_n_boundary_verification(task_id)
        result.add_check_result("n_boundary", n_boundary_result)

        if n_boundary_result["overall_status"] == "PASS":
            print("[Stage 2] Result: PASS")
            result.add_evidence_ref(f"n_boundary:{task_id}:PASS")
        else:
            print("[Stage 2] Result: FAIL")
            result.add_error(
                "N_BOUNDARY_FAIL",
                "N-Boundary verification failed",
                "Review command allowlist, artifact completeness, and time window"
            )
            return result

    # All checks passed
    result.set_allow()
    return result


def run_cloud_validation(task_id: str) -> UnifiedValidationResult:
    """
    Run cloud task validation.

    Cloud = Receipt verification + N-Boundary
    """
    result = UnifiedValidationResult(ValidationMode.CLOUD)

    print(f"[UVG] Cloud Validation Mode")
    print(f"[UVG] Task ID: {task_id}")
    print("=" * 60)

    # Stage 1: Receipt verification
    print("\n[Stage 1] Receipt Verification")
    receipt_script = Path(__file__).parent / "verify_execution_receipt.py"
    task_dir = Path(".tmp/openclaw-dispatch") / task_id
    receipt_path = task_dir / "execution_receipt.json"
    contract_path = task_dir / "task_contract.json"

    receipt_result = run_script(
        receipt_script,
        ["--receipt", str(receipt_path), "--contract", str(contract_path)]
    )
    result.add_check_result("receipt_verification", receipt_result)

    if receipt_result.get("status") == "PASS":
        print("[Stage 1] Result: PASS")
        result.add_evidence_ref(f"receipt:{task_id}:PASS")
    else:
        print("[Stage 1] Result: FAIL")
        result.add_error(
            "RECEIPT_FAIL",
            "Receipt verification failed",
            "Ensure receipt matches contract specification"
        )
        return result

    # Stage 2: N-Boundary
    print("\n[Stage 2] N-Boundary Verification")
    n_boundary_result = run_n_boundary_verification(task_id)
    result.add_check_result("n_boundary", n_boundary_result)

    if n_boundary_result["overall_status"] == "PASS":
        print("[Stage 2] Result: PASS")
        result.add_evidence_ref(f"n_boundary:{task_id}:PASS")
    else:
        print("[Stage 2] Result: FAIL")
        result.add_error(
            "N_BOUNDARY_FAIL",
            "N-Boundary verification failed",
            "Review command allowlist, artifact completeness, and time window"
        )
        return result

    # All checks passed
    result.set_allow()
    return result


def run_quick_validation(permit_path: Path) -> UnifiedValidationResult:
    """
    Run quick validation (Permit + Delivery only, skip three-hash).

    Useful for development iteration.
    """
    result = UnifiedValidationResult(ValidationMode.QUICK)

    print(f"[UVG] Quick Validation Mode")
    print(f"[UVG] Permit: {permit_path}")
    print("=" * 60)

    # Run Antigravity-2 with --skip-three-hash
    guard_script = Path(__file__).parent / "antigravity_2_guard.py"
    args = ["--permit", str(permit_path), "--skip-three-hash"]

    ag2_result = run_script(guard_script, args)
    result.add_check_result("antigravity_2_guard_quick", ag2_result)

    if "ALLOW" in ag2_result.get("stdout", ""):
        print("[UVG] Result: ALLOW")
        result.add_evidence_ref("antigravity_2_guard_quick:ALLOW")
        result.set_allow()
    else:
        print("[UVG] Result: DENY")
        result.add_error(
            "QUICK_VALIDATION_FAIL",
            "Quick validation failed",
            "Fix permit binding or delivery completeness"
        )

    return result


def run_absorb_validation(task_id: str) -> UnifiedValidationResult:
    """Run pre-absorb gate validation."""
    result = UnifiedValidationResult(ValidationMode.ABSORB)

    print(f"[UVG] Absorb Gate Mode")
    print(f"[UVG] Task ID: {task_id}")
    print("=" * 60)

    absorb_result = run_pre_absorb_check(task_id)
    result.add_check_result("pre_absorb_check", absorb_result)

    if absorb_result.get("status") == "PASS":
        print("[UVG] Result: ALLOW")
        result.add_evidence_ref(f"pre_absorb:{task_id}:PASS")
        result.set_allow()
    else:
        print("[UVG] Result: DENY")
        result.add_error(
            "ABSORB_CHECK_FAIL",
            "Pre-absorb check failed",
            "Review task package completeness and environment variables"
        )

    return result


def save_validation_result(
    result: UnifiedValidationResult,
    output_path: Path | None = None,
) -> Path | None:
    """Save validation result to file."""
    output_data = {
        "schema_version": "1.0.0",
        "mode": result.mode.value,
        "decision": result.status.value,
        "decision_time": result.decision_time,
        "checks": result.checks,
        "errors": result.errors,
        "warnings": result.warnings,
        "required_changes": result.required_changes,
        "evidence_refs": result.evidence_refs,
        "summary": {
            "total_checks": len(result.checks),
            "failed_checks": sum(1 for c in result.checks.values() if c.get("status") not in ["PASS", "ALLOW"]),
        },
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(output_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        return output_path

    # Default output path
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    default_dir = Path("docs") / date_str / "verification"
    default_dir.mkdir(parents=True, exist_ok=True)
    default_path = default_dir / f"unified_validation_{result.mode.value}_{datetime.now(UTC).strftime('%H%M%S')}.json"
    default_path.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    return default_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified Validation Gate - Single Entry Point for GM-SkillForge Verification"
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--mode",
        choices=["mainline", "cloud", "quick", "absorb"],
        help="Validation mode"
    )
    mode_group.add_argument(
        "--mainline",
        action="store_const",
        const="mainline",
        dest="mode",
        help="Run mainline validation (Antigravity-2)"
    )
    mode_group.add_argument(
        "--cloud",
        action="store_const",
        const="cloud",
        dest="mode",
        help="Run cloud task validation"
    )
    mode_group.add_argument(
        "--quick",
        action="store_const",
        const="quick",
        dest="mode",
        help="Run quick validation (skip three-hash)"
    )
    mode_group.add_argument(
        "--absorb",
        action="store_const",
        const="absorb",
        dest="mode",
        help="Run pre-absorb gate check"
    )

    # Mainline mode arguments
    parser.add_argument("--permit", type=Path, help="Path to permit JSON file")
    parser.add_argument("--demand", type=Path, help="Path to demand JSON file")
    parser.add_argument("--contract", type=Path, help="Path to contract file")
    parser.add_argument("--decision", type=Path, help="Path to decision JSON file")
    parser.add_argument("--manifest", type=Path, help="Path to manifest JSON file")

    # Cloud mode arguments
    parser.add_argument("--task-id", help="Task ID for cloud/absorb modes")

    # N-Boundary option for mainline mode
    parser.add_argument(
        "--with-n-boundary",
        action="store_true",
        help="Include N-boundary verification (for cloud tasks in mainline mode)"
    )

    # Output options
    parser.add_argument("--output", type=Path, help="Output file path (JSON)")
    parser.add_argument("--quiet", action="store_true", help="Only output decision")

    args = parser.parse_args()

    # Dispatch based on mode
    mode = ValidationMode(args.mode)
    result: UnifiedValidationResult | None = None

    if mode == ValidationMode.MAINLINE:
        if not args.permit:
            print("--permit is required for mainline mode", file=sys.stderr)
            return 1

        result = run_mainline_validation(
            permit_path=args.permit,
            demand_path=args.demand,
            contract_path=args.contract,
            decision_path=args.decision,
            manifest_path=args.manifest,
            run_n_boundary=args.with_n_boundary,
            task_id=args.task_id,
        )

    elif mode == ValidationMode.CLOUD:
        if not args.task_id:
            print("--task-id is required for cloud mode", file=sys.stderr)
            return 1

        result = run_cloud_validation(args.task_id)

    elif mode == ValidationMode.QUICK:
        if not args.permit:
            print("--permit is required for quick mode", file=sys.stderr)
            return 1

        result = run_quick_validation(args.permit)

    elif mode == ValidationMode.ABSORB:
        if not args.task_id:
            print("--task-id is required for absorb mode", file=sys.stderr)
            return 1

        result = run_absorb_validation(args.task_id)

    # Save result
    if result is None:
        print("[UVG] ERROR: Validation result is None", file=sys.stderr)
        return 1

    output_file = save_validation_result(result, args.output)

    # Print summary
    print("\n" + "=" * 60)
    print(f"[UVG] Final Decision: {result.status.value}")
    print(f"[UVG] Evidence Refs: {', '.join(result.evidence_refs) if result.evidence_refs else 'None'}")
    if output_file:
        print(f"[UVG] Output: {output_file}")

    if result.status == GateDecision.DENY:
        print(f"\n[UVG] Errors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  [{e['code']}] {e['message']}")
        if result.required_changes:
            print(f"\n[UVG] Required Changes:")
            for c in result.required_changes:
                print(f"  - {c}")

    print("=" * 60)

    if args.quiet:
        print(result.status.value)

    return 0 if result.status == GateDecision.ALLOW else 1


if __name__ == "__main__":
    sys.exit(main())
