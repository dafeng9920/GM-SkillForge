#!/usr/bin/env python3
"""
R1 Cloud Smoke Test - Stable Local Verification

Stable smoke test for CLOUD-ROOT baseline verification.
Tests: contract structure, command allowlist, artifact requirements.

Usage:
    python scripts/run_r1_smoke_stable.py
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from datetime import UTC
from pathlib import Path


def utc_now() -> str:
    return dt.datetime.now(UTC).isoformat()


def run_smoke_test(task_id: str | None = None) -> dict:
    """Run smoke test on a prepared task contract."""
    dispatch_dir = Path(".tmp/openclaw-dispatch")
    
    if task_id:
        task_dir = dispatch_dir / task_id
    else:
        # Find most recent task directory
        if not dispatch_dir.exists():
            return {"status": "FAIL", "error": "Dispatch directory does not exist", "checks": []}
        
        task_dirs = sorted([d for d in dispatch_dir.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
        if not task_dirs:
            return {"status": "FAIL", "error": "No task directories found", "checks": []}
        
        task_dir = task_dirs[0]
        task_id = task_dir.name

    result = {
        "task_id": task_id,
        "timestamp": utc_now(),
        "status": "FAIL",
        "checks": [],
    }

    # Check 1: Contract exists
    contract_path = task_dir / "task_contract.json"
    if not contract_path.exists():
        result["checks"].append({"name": "contract_exists", "status": "FAIL", "error": f"Contract not found: {contract_path}"})
        return result
    result["checks"].append({"name": "contract_exists", "status": "PASS", "path": str(contract_path)})

    # Check 2: Contract structure
    try:
        with open(contract_path, encoding="utf-8") as f:
            contract = json.load(f)
        
        required_fields = ["task_id", "command_allowlist", "required_artifacts"]
        missing = [f for f in required_fields if f not in contract]
        
        if missing:
            result["checks"].append({"name": "contract_structure", "status": "FAIL", "error": f"Missing fields: {missing}"})
        else:
            result["checks"].append({"name": "contract_structure", "status": "PASS"})
    except json.JSONDecodeError as e:
        result["checks"].append({"name": "contract_structure", "status": "FAIL", "error": f"Invalid JSON: {e}"})
        return result
    except Exception as e:
        result["checks"].append({"name": "contract_structure", "status": "FAIL", "error": str(e)})
        return result

    # Check 3: Command allowlist
    if contract.get("command_allowlist"):
        result["checks"].append({
            "name": "command_allowlist",
            "status": "PASS",
            "count": len(contract["command_allowlist"])
        })
    else:
        result["checks"].append({"name": "command_allowlist", "status": "FAIL", "error": "Empty allowlist"})

    # Check 4: Required artifacts
    if contract.get("required_artifacts"):
        result["checks"].append({
            "name": "required_artifacts",
            "status": "PASS",
            "count": len(contract["required_artifacts"])
        })
    else:
        result["checks"].append({"name": "required_artifacts", "status": "FAIL", "error": "No required artifacts"})

    # Check 5: Environment
    if contract.get("environment") == "CLOUD-ROOT":
        result["checks"].append({"name": "environment", "status": "PASS", "value": "CLOUD-ROOT"})
    else:
        result["checks"].append({"name": "environment", "status": "FAIL", "error": f"Invalid environment: {contract.get('environment')}"})

    # Overall status
    failed = [c for c in result["checks"] if c.get("status") == "FAIL"]
    result["status"] = "PASS" if not failed else "PARTIAL" if len(failed) < len(result["checks"]) else "FAIL"
    result["summary"] = {"total": len(result["checks"]), "passed": len(result["checks"]) - len(failed), "failed": len(failed)}

    return result


def main() -> int:
    import argparse
    
    parser = argparse.ArgumentParser(description="R1 Cloud Smoke Test - Stable Local Verification")
    parser.add_argument("--task-id", help="Task ID to verify (uses most recent if not provided)")
    parser.add_argument("--output", type=Path, default=Path("reports/smoke_tests"), help="Output directory for reports")
    args = parser.parse_args()

    print("=" * 60)
    print("R1 SMOKE TEST - STABLE VERIFICATION")
    print("=" * 60)
    
    result = run_smoke_test(args.task_id)
    
    print(f"\nTask ID: {result['task_id']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']['passed']}/{result['summary']['total']} checks passed")
    
    for check in result["checks"]:
        symbol = "✓" if check["status"] == "PASS" else "✗"
        print(f"  {symbol} {check['name']}: {check['status']}")
        if "error" in check:
            print(f"      Error: {check['error']}")
        if "count" in check:
            print(f"      Count: {check['count']}")

    # Save report
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / f"{result['task_id']}_smoke_{dt.datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved: {report_path}")

    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
