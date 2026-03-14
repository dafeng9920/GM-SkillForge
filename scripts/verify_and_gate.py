#!/usr/bin/env python3
"""
Verify and Gate - Dual Gate Verification

Combines execution receipt verification with cloud lobster mandatory gate.
All verification results are saved to docs/<date>/verification/.

Usage:
    python scripts/verify_and_gate.py --task-id <task_id>
    python scripts/verify_and_gate.py --task-id <task_id> --skip-mandatory-gate
"""

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"


def read_json(path: pathlib.Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_execution_receipt(
    task_id: str,
    verifier_path: pathlib.Path = pathlib.Path("skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py"),
) -> dict:
    """Run verify_execution_receipt.py on the task."""
    task_dir = pathlib.Path(".tmp/openclaw-dispatch") / task_id
    contract_path = task_dir / "task_contract.json"
    receipt_path = task_dir / "execution_receipt.json"

    result = {
        "task_id": task_id,
        "timestamp": utc_now(),
        "status": "FAIL",
        "exit_code": -1,
        "stdout": "",
        "stderr": "",
    }

    if not verifier_path.exists():
        result["error"] = f"Verifier not found: {verifier_path}"
        return result

    if not contract_path.exists():
        result["error"] = f"Contract not found: {contract_path}"
        return result

    if not receipt_path.exists():
        result["error"] = f"Receipt not found: {receipt_path}"
        return result

    try:
        proc = subprocess.run(
            [sys.executable, str(verifier_path), "--contract", str(contract_path), "--receipt", str(receipt_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()
        result["status"] = "PASS" if proc.returncode == 0 else "FAIL"

    except subprocess.TimeoutExpired:
        result["error"] = "Verification timed out"
    except Exception as e:
        result["error"] = str(e)

    return result


def run_cloud_lobster_mandatory_gate(task_id: str) -> dict:
    """Run mandatory gate on the task using the enforced closed-loop policy."""
    enforce_script = pathlib.Path("scripts/enforce_cloud_lobster_closed_loop.py")
    legacy_gate_script = pathlib.Path("scripts/cloud_lobster_mandatory_gate.py")

    result = {
        "task_id": task_id,
        "timestamp": utc_now(),
        "status": "DENY",
        "exit_code": -1,
        "stdout": "",
        "stderr": "",
    }

    if not enforce_script.exists() and not legacy_gate_script.exists():
        result["error"] = f"Gate script not found: {enforce_script} or {legacy_gate_script}"
        return result

    try:
        if enforce_script.exists():
            cmd = [sys.executable, str(enforce_script), "--task-id", task_id, "--action", "verify"]
        else:
            cmd = [sys.executable, str(legacy_gate_script), "--task-id", task_id, "--quiet"]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()
        result["status"] = "ALLOW" if proc.returncode == 0 else "DENY"

    except subprocess.TimeoutExpired:
        result["error"] = "Gate check timed out"
    except Exception as e:
        result["error"] = str(e)

    return result


def save_verification_results(
    task_id: str,
    receipt_verification: dict,
    mandatory_gate: dict,
    verification_dir: pathlib.Path,
) -> pathlib.Path:
    """Save combined verification results."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = {
        "schema_version": "1.0.0",
        "report_type": "dual_gate_verification",
        "generated_at": utc_now(),
        "task_id": task_id,
        "dual_gate_decision": {
            "overall": "PASS",
            "reason": "",
        },
        "gates": {
            "receipt_verification": receipt_verification,
            "cloud_lobster_mandatory_gate": mandatory_gate,
        },
        "summary": {
            "total_gates": 2,
            "passed": 0,
            "failed": 0,
        },
    }

    # Calculate summary
    passed = 0
    failed = 0

    if receipt_verification.get("status") == "PASS":
        passed += 1
    else:
        failed += 1

    if mandatory_gate.get("status") == "ALLOW":
        passed += 1
    else:
        failed += 1

    results["summary"]["passed"] = passed
    results["summary"]["failed"] = failed

    # Overall decision
    if failed == 0:
        results["dual_gate_decision"]["overall"] = "PASS"
        results["dual_gate_decision"]["reason"] = "All gates passed"
    elif failed == 1:
        results["dual_gate_decision"]["overall"] = "PARTIAL"
        results["dual_gate_decision"]["reason"] = "One gate failed"
    else:
        results["dual_gate_decision"]["overall"] = "FAIL"
        results["dual_gate_decision"]["reason"] = "All gates failed"

    # Save to verification directory
    verification_dir.mkdir(parents=True, exist_ok=True)
    result_file = verification_dir / f"{task_id}_dual_gate_verification.json"
    write_json(result_file, results)

    # Also save markdown summary
    md_file = verification_dir / f"{task_id}_dual_gate_verification.md"
    md_content = f"""# Dual Gate Verification: {task_id}

**Generated At**: {utc_now()}
**Overall Decision**: {results['dual_gate_decision']['overall']}
**Reason**: {results['dual_gate_decision']['reason']}

## Summary

- **Total Gates**: 2
- **Passed**: {passed}
- **Failed**: {failed}

## Gate 1: Receipt Verification

**Status**: {receipt_verification.get('status', 'UNKNOWN')}
**Timestamp**: {receipt_verification.get('timestamp', 'N/A')}

{receipt_verification.get('stdout', '')}

{receipt_verification.get('stderr', '')}

## Gate 2: Cloud Lobster Mandatory Gate

**Status**: {mandatory_gate.get('status', 'UNKNOWN')}
**Timestamp**: {mandatory_gate.get('timestamp', 'N/A')}

{mandatory_gate.get('stdout', '')}

{mandatory_gate.get('stderr', '')}

## Overall Decision

{results['dual_gate_decision']['overall']}: {results['dual_gate_decision']['reason']}
"""
    md_file.write_text(md_content, encoding="utf-8")

    return result_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify and Gate - Dual Gate Verification for Cloud Tasks"
    )
    parser.add_argument("--task-id", required=True, help="Task ID to verify")
    parser.add_argument(
        "--verification-dir",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent.parent / f"docs/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}/verification",
        help="Verification output directory"
    )
    parser.add_argument(
        "--skip-receipt-verify",
        action="store_true",
        help="Skip receipt verification gate"
    )
    parser.add_argument(
        "--skip-mandatory-gate",
        action="store_true",
        help="Skip cloud lobster mandatory gate"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("VERIFY AND GATE - DUAL GATE VERIFICATION")
    print("=" * 60)
    print(f"Task ID: {args.task_id}")
    print(f"Time: {utc_now()}")
    print(f"Output: {args.verification_dir}")
    print("=" * 60)

    receipt_verification = {"status": "SKIPPED"}
    mandatory_gate = {"status": "SKIPPED"}

    # Gate 1: Receipt Verification
    if not args.skip_receipt_verify:
        print("\n[Gate 1] Running receipt verification...")
        receipt_verification = verify_execution_receipt(args.task_id)
        status = receipt_verification.get("status", "ERROR")
        print(f"[Gate 1] Result: {status}")
        if status == "FAIL":
            if "error" in receipt_verification:
                print(f"  Error: {receipt_verification['error']}")
            if receipt_verification.get("stdout"):
                print(f"  Output: {receipt_verification['stdout'][:200]}")
    else:
        print("\n[Gate 1] Skipped")

    # Gate 2: Cloud Lobster Mandatory Gate
    if not args.skip_mandatory_gate:
        print("\n[Gate 2] Running cloud lobster mandatory gate...")
        mandatory_gate = run_cloud_lobster_mandatory_gate(args.task_id)
        status = mandatory_gate.get("status", "ERROR")
        print(f"[Gate 2] Result: {status}")
        if status == "DENY":
            if "error" in mandatory_gate:
                print(f"  Error: {mandatory_gate['error']}")
    else:
        print("\n[Gate 2] Skipped")

    # Save results
    print("\n[Output] Saving verification results...")
    result_file = save_verification_results(
        args.task_id,
        receipt_verification,
        mandatory_gate,
        args.verification_dir,
    )
    print(f"[Output] Results saved to: {result_file}")

    # Final decision
    print("\n" + "=" * 60)
    passed = sum([
        1 if receipt_verification.get("status") == "PASS" else 0,
        1 if mandatory_gate.get("status") == "ALLOW" else 0,
    ])
    total = sum([
        0 if receipt_verification.get("status") == "SKIPPED" else 1,
        0 if mandatory_gate.get("status") == "SKIPPED" else 1,
    ])

    if passed == total:
        print(f"[✅ PASS] All {total} gate(s) passed")
        return 0
    elif passed > 0:
        print(f"[⚠️  PARTIAL] {passed}/{total} gate(s) passed")
        return 1
    else:
        print(f"[❌ FAIL] All {total} gate(s) failed")
        return 2


if __name__ == "__main__":
    sys.exit(main())
