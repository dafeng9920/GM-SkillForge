#!/usr/bin/env python3
"""
N+2: Artifact Completeness Verification

Verifies that all cloud executions return the complete 4-artifact set.
This is the second incremental security boundary for Fixed-Caliber governance.

Usage:
    python scripts/verify_n2_artifact_completeness.py --task-id <task_id>
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


def verify_artifact_completeness(task_id: str) -> dict:
    """Verify 4-artifact completeness for a task."""
    task_dir = pathlib.Path(f".tmp/openclaw-dispatch/{task_id}")

    # Required artifacts
    required = {
        "execution_receipt.json": "execution_receipt",
        "stdout.log": "stdout",
        "stderr.log": "stderr",
        "audit_event.json": "audit_event"
    }

    missing = []
    incomplete = []

    for artifact_name, artifact_type in required.items():
        artifact_path = task_dir / artifact_name

        if not artifact_path.exists():
            missing.append(f"{artifact_type}:{artifact_name}")
            continue

        # For JSON artifacts, validate basic structure
        if artifact_path.suffix == ".json":
            try:
                data = read_json(artifact_path)
                if not data:
                    incomplete.append(f"{artifact_type}:{artifact_name} is empty")
            except Exception as e:
                incomplete.append(f"{artifact_type}:{artifact_name} invalid JSON - {e}")

    # Check execution_receipt specifically
    receipt_path = task_dir / "execution_receipt.json"
    if receipt_path.exists():
        receipt = read_json(receipt_path)
        required_fields = [
            "schema_version", "task_id", "started_at_utc", "finished_at_utc",
            "status", "executed_commands", "exit_code", "artifacts", "summary"
        ]
        missing_fields = [f for f in required_fields if f not in receipt]
        if missing_fields:
            incomplete.append(f"execution_receipt missing fields: {missing_fields}")

    # Generate result
    if missing or incomplete:
        return {
            "status": "FAIL",
            "error": "Artifact completeness check failed",
            "boundary": "N+2_ARTIFACT_COMPLETENESS",
            "blocker": "ARTIFACT_INCOMPLETE",
            "missing": missing,
            "incomplete": incomplete
        }

    return {
        "status": "PASS",
        "boundary": "N+2_ARTIFACT_COMPLETENESS",
        "summary": f"All 4 artifacts present and valid",
        "details": {
            "total_artifacts": 4,
            "present_artifacts": 4,
            "missing_artifacts": 0,
            "valid_artifacts": 4
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="N+2: Verify artifact completeness")
    parser.add_argument("--task-id", required=True, help="Task ID to verify")
    parser.add_argument("--out-dir", default="docs/2026-03-04/verification", help="Output directory")
    args = parser.parse_args()

    print(f"[N+2] Artifact Completeness Verification")
    print(f"[N+2] Task ID: {args.task_id}")
    print()

    # Run verification
    result = verify_artifact_completeness(args.task_id)

    # Write result
    output_dir = pathlib.Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"N+2_artifact_completeness_{args.task_id}.json"
    output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Print result
    print(f"[N+2] Status: {result['status']}")
    print(f"[N+2] Boundary: {result['boundary']}")
    print(f"[N+2] Output: {output_file}")

    if result["status"] == "FAIL":
        print()
        print("[BLOCKER]")
        print(f"  {result['blocker']}")
        if "missing" in result and result["missing"]:
            for m in result["missing"]:
                print(f"  - {m}")
        if "incomplete" in result and result["incomplete"]:
            for i in result["incomplete"]:
                print(f"  - {i}")
        return 1

    print()
    print("[N+2] Artifact completeness verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
