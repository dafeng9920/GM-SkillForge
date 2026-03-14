#!/usr/bin/env python3
"""
N+1: Command Allowlist Verification

Verifies that all cloud executions strictly follow the command allowlist.
This is the first incremental security boundary for Fixed-Caliber governance.

Usage:
    python scripts/verify_n1_command_allowlist.py --task-id <task_id>
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


def read_json(path: pathlib.Path) -> dict:
    """Read JSON file."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def verify_allowlist(task_id: str) -> dict:
    """Verify command allowlist compliance for a task."""
    task_dir = pathlib.Path(f".tmp/openclaw-dispatch/{task_id}")
    contract_file = task_dir / "task_contract.json"
    receipt_file = task_dir / "execution_receipt.json"
    audit_file = task_dir / "audit_event.json"

    # Read contract and receipt
    contract = read_json(contract_file)
    receipt = read_json(receipt_file)
    audit = read_json(audit_file)

    # Verify contract exists
    if not contract:
        return {
            "status": "FAIL",
            "error": "Task contract not found",
            "boundary": "N+1_COMMAND_ALLOWLIST",
            "blocker": "CONTRACT_MISSING"
        }

    # Verify receipt exists
    if not receipt:
        return {
            "status": "FAIL",
            "error": "Execution receipt not found",
            "boundary": "N+1_COMMAND_ALLOWLIST",
            "blocker": "RECEIPT_MISSING"
        }

    # Get allowlist from contract
    allowlist = set(contract.get("command_allowlist", []))
    if not allowlist:
        return {
            "status": "FAIL",
            "error": "Allowlist is empty",
            "boundary": "N+1_COMMAND_ALLOWLIST",
            "blocker": "ALLOWLIST_EMPTY"
        }

    # Get executed commands from receipt
    executed = receipt.get("executed_commands", [])

    if not executed:
        return {
            "status": "FAIL",
            "error": "No commands executed",
            "boundary": "N+1_COMMAND_ALLOWLIST",
            "blocker": "NO_COMMANDS_EXECUTED"
        }

    # Check each executed command is in allowlist
    violations = []
    for cmd in executed:
        if cmd not in allowlist:
            violations.append(f"Command not in allowlist: {cmd}")

    # Check audit trail for authorization
    if audit:
        events = audit.get("events", [])
        if not events:
            return {
                "status": "FAIL",
                "error": "No audit trail found",
                "boundary": "N+1_COMMAND_ALLOWLIST",
                "blocker": "NO_AUDIT_TRAIL"
            }

        # Check if any unauthorized commands in audit
        for event in events:
            if event.get("event_type") in ["COMMAND_START", "PROCESS_QUERY", "LOG_READ", "NETWORK_QUERY"]:
                if event.get("status") != "AUTHORIZED":
                    violations.append(f"Unauthorized command in audit: {event.get('command')}")

    # Generate result
    if violations:
        return {
            "status": "FAIL",
            "error": "Command allowlist violations detected",
            "boundary": "N+1_COMMAND_ALLOWLIST",
            "blocker": "ALLOWLIST_VIOLATION",
            "violations": violations
        }

    return {
        "status": "PASS",
        "boundary": "N+1_COMMAND_ALLOWLIST",
        "summary": f"All {len(executed)} commands within allowlist",
        "details": {
            "total_commands": len(executed),
            "allowlist_size": len(allowlist),
            "violations": 0
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="N+1: Verify command allowlist compliance")
    parser.add_argument("--task-id", required=True, help="Task ID to verify")
    parser.add_argument("--out-dir", default="docs/2026-03-04/verification", help="Output directory")
    args = parser.parse_args()

    print(f"[N+1] Command Allowlist Verification")
    print(f"[N+1] Task ID: {args.task_id}")
    print()

    # Run verification
    result = verify_allowlist(args.task_id)

    # Write result
    output_dir = pathlib.Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"N+1_command_allowlist_{args.task_id}.json"
    output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Print result
    print(f"[N+1] Status: {result['status']}")
    print(f"[N+1] Boundary: {result['boundary']}")
    print(f"[N+1] Output: {output_file}")

    if result["status"] == "FAIL":
        print()
        print("[BLOCKER]")
        print(f"  {result['blocker']}")
        if "violations" in result:
            for v in result["violations"]:
                print(f"  - {v}")
        return 1

    print()
    print("[N+1] Command allowlist verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
