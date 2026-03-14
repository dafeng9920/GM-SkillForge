#!/usr/bin/env python3
"""
N+3: Time Window Enforcement Verification

Verifies that cloud executions complete within reasonable time windows.
This is the third incremental security boundary for Fixed-Caliber governance.

Usage:
    python scripts/verify_n3_time_window.py --task-id <task_id> [--max-duration-sec <seconds>] [--max-commands <count>]
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


def verify_time_window(task_id: str, max_duration_sec: int = 300, max_commands: int = 50) -> dict:
    """Verify time window compliance for a task."""
    task_dir = pathlib.Path(f".tmp/openclaw-dispatch/{task_id}")
    receipt_file = task_dir / "execution_receipt.json"

    # Read receipt
    receipt = read_json(receipt_file)

    # Verify receipt exists
    if not receipt:
        return {
            "status": "FAIL",
            "error": "Execution receipt not found",
            "boundary": "N+3_TIME_WINDOW_ENFORCEMENT",
            "blocker": "RECEIPT_MISSING"
        }

    # Get time elapsed
    time_elapsed = receipt.get("time_elapsed", 0)
    if time_elapsed == 0:
        # Try to calculate from timestamps
        started_at = receipt.get("started_at_utc", "")
        finished_at = receipt.get("finished_at_utc", "")
        if started_at and finished_at:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                finish = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
                time_elapsed = int((finish - start).total_seconds())
            except Exception:
                pass

    # Get command count
    executed_commands = receipt.get("executed_commands", [])
    command_count = len(executed_commands)

    # Check time limit
    violations = []
    if time_elapsed > max_duration_sec:
        violations.append(f"Execution time {time_elapsed}s exceeds limit {max_duration_sec}s")

    # Check command limit
    if command_count > max_commands:
        violations.append(f"Command count {command_count} exceeds limit {max_commands}")

    # Check for timeout
    status = receipt.get("status", "")
    if status == "TIMEOUT":
        violations.append("Task timed out during execution")

    # Check exit code for abnormal termination
    exit_code = receipt.get("exit_code", None)
    if exit_code is not None and exit_code < 0:
        violations.append(f"Abnormal termination with exit code: {exit_code}")

    # Generate result
    if violations:
        return {
            "status": "FAIL",
            "error": "Time window violation detected",
            "boundary": "N+3_TIME_WINDOW_ENFORCEMENT",
            "blocker": "TIME_WINDOW_VIOLATION",
            "violations": violations,
            "details": {
                "time_elapsed_sec": time_elapsed,
                "max_duration_sec": max_duration_sec,
                "command_count": command_count,
                "max_commands": max_commands,
                "status": status
            }
        }

    return {
        "status": "PASS",
        "boundary": "N+3_TIME_WINDOW_ENFORCEMENT",
        "summary": f"Execution completed within time window",
        "details": {
            "time_elapsed_sec": time_elapsed,
            "max_duration_sec": max_duration_sec,
            "command_count": command_count,
            "max_commands": max_commands,
            "utilization_pct": round((time_elapsed / max_duration_sec) * 100, 2) if max_duration_sec > 0 else 0
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="N+3: Verify time window enforcement")
    parser.add_argument("--task-id", required=True, help="Task ID to verify")
    parser.add_argument("--out-dir", default="docs/2026-03-04/verification", help="Output directory")
    parser.add_argument("--max-duration-sec", type=int, default=300,
                        help="Maximum allowed execution duration in seconds (default: 300)")
    parser.add_argument("--max-commands", type=int, default=50,
                        help="Maximum allowed command count (default: 50)")
    args = parser.parse_args()

    print(f"[N+3] Time Window Enforcement Verification")
    print(f"[N+3] Task ID: {args.task_id}")
    print(f"[N+3] Max Duration: {args.max_duration_sec}s")
    print(f"[N+3] Max Commands: {args.max_commands}")
    print()

    # Run verification
    result = verify_time_window(args.task_id, args.max_duration_sec, args.max_commands)

    # Write result
    output_dir = pathlib.Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"N+3_time_window_{args.task_id}.json"
    output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Print result
    print(f"[N+3] Status: {result['status']}")
    print(f"[N+3] Boundary: {result['boundary']}")
    print(f"[N+3] Output: {output_file}")

    if result["status"] == "PASS":
        details = result.get("details", {})
        print(f"[N+3] Time Elapsed: {details.get('time_elapsed_sec', 0)}s / {details.get('max_duration_sec', 0)}s")
        print(f"[N+3] Command Count: {details.get('command_count', 0)} / {details.get('max_commands', 0)}")
        print(f"[N+3] Utilization: {details.get('utilization_pct', 0)}%")
    else:
        print()
        print("[BLOCKER]")
        print(f"  {result['blocker']}")
        if "violations" in result:
            for v in result["violations"]:
                print(f"  - {v}")
        return 1

    print()
    print("[N+3] Time window verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
