#!/usr/bin/env python3
"""
CLOUD-ROOT DISPATCH GUARD

Pre-flight guard for all CLOUD-ROOT task dispatch.
This MUST be called before sending any task to CLOUD-ROOT.

Usage:
    # Create contract and verify before dispatch
    python scripts/cloud_dispatch_guard.py --baseline-id "AG2-SOVEREIGNTY-ROOT-2026-03-05" \\
        --objective "Test deployment" --allow "pwd" --allow "ls"

    # Verify after execution
    python scripts/cloud_dispatch_guard.py --task-id "tg1-official-20260305-1500" \\
        --action verify --enforce-only

    # This will:
    # 1. Generate contract using cloud-lobster-closed-loop-skill
    # 2. Run enforcement check
    # 3. Output ALLOW/BLOCK decision
"""

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Literal


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run command and return result."""
    print(f"[exec] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        print(f"[error] Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def create_task_contract(
    task_id: str | None,
    baseline_id: str,
    objective: str,
    allowlist: list[str],
    target_dir: str = "/root/openclaw-box",
) -> pathlib.Path:
    """Generate task contract using cloud-lobster-closed-loop-skill."""
    contract_script = pathlib.Path("skills/cloud-lobster-closed-loop-skill/scripts/create_cloud_task_contract.py")
    if not contract_script.exists():
        raise FileNotFoundError(f"Contract script not found: {contract_script}")

    cmd = [
        sys.executable,
        str(contract_script),
    ]
    # Only add --task-id if provided (contract script will auto-generate if empty)
    if task_id:
        cmd.extend(["--task-id", task_id])
    cmd.extend([
        "--baseline-id", baseline_id,
        "--objective", objective,
        "--target-dir", target_dir,
    ])
    for cmd_allow in allowlist:
        cmd.extend(["--allow", cmd_allow])

    result = run_cmd(cmd, check=False)
    if result.returncode != 0:
        print("[error] Failed to create task contract")
        sys.exit(1)

    # Parse output to get contract path
    for line in result.stdout.splitlines():
        if line.startswith("[ok] contract="):
            return pathlib.Path(line.split("=", 1)[1])

    raise ValueError("Could not determine contract path from output")


def enforce_cloud_lobster_closed_loop(
    task_id: str,
    action: Literal["dispatch", "verify"],
) -> dict:
    """Run enforcement check."""
    enforce_script = pathlib.Path("scripts/enforce_cloud_lobster_closed_loop.py")
    if not enforce_script.exists():
        raise FileNotFoundError(f"Enforcement script not found: {enforce_script}")

    cmd = [
        sys.executable,
        str(enforce_script),
        "--task-id", task_id,
        "--action", action,
    ]

    result = run_cmd(cmd, check=False)
    return {
        "exit_code": result.returncode,
        "allowed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-flight guard for CLOUD-ROOT task dispatch")
    parser.add_argument("--task-id", help="Task ID (auto-generated if not provided)")
    parser.add_argument("--baseline-id", required=True, help="Baseline ID (e.g., AG2-SOVEREIGNTY-ROOT-2026-03-05)")
    parser.add_argument("--objective", required=True, help="Task objective")
    parser.add_argument("--target-dir", default="/root/openclaw-box", help="Target directory on CLOUD-ROOT")
    parser.add_argument("--allow", action="append", required=True, help="Command allowlist (can be repeated)")
    parser.add_argument("--contract-only", action="store_true", help="Only create contract, skip enforcement")
    parser.add_argument("--enforce-only", action="store_true", help="Only run enforcement, skip contract creation")
    parser.add_argument(
        "--action",
        choices=["dispatch", "verify"],
        default="dispatch",
        help="Action type: dispatch (before sending to CLOUD-ROOT) or verify (after execution)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("CLOUD-ROOT DISPATCH GUARD")
    print("=" * 60)
    print(f"Baseline: {args.baseline_id}")
    print(f"Objective: {args.objective}")
    print(f"Commands: {len(args.allow)}")
    print(f"Time: {now_iso()}")
    print("=" * 60)

    task_id = args.task_id
    contract_path = None

    # Step 1: Create contract
    if not args.enforce_only:
        print("\n[Step 1] Creating task contract...")
        contract_path = create_task_contract(
            task_id or "",  # Pass empty string if not provided, contract script will auto-generate
            args.baseline_id,
            args.objective,
            args.allow,
            args.target_dir,
        )
        print(f"[ok] Contract created: {contract_path}")

        # Extract task_id from contract if not provided
        if not task_id:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            task_id = contract["task_id"]
            print(f"[ok] Task ID: {task_id}")

    # Step 2: Enforcement check
    if not args.contract_only:
        if not task_id:
            print("[error] --task-id required for enforcement when --contract-only is not set")
            return 1

        print(f"\n[Step 2] Running enforcement check (action: {args.action})...")
        enforcement = enforce_cloud_lobster_closed_loop(task_id, args.action)

        if enforcement["allowed"]:
            print("\n" + "=" * 60)
            action_msg = "dispatch to CLOUD-ROOT" if args.action == "dispatch" else "verification"
            print(f"[✅ ALLOW] Task may proceed to {action_msg}")
            print("=" * 60)
            if args.action == "dispatch":
                print(f"\nNext steps:")
                print(f"  1. Send {task_id} to Antigravity-3 (小龙虾)")
                print(f"  2. Execute only commands in allowlist")
                print(f"  3. Return 4 artifacts to LOCAL-ANTIGRAVITY")
                print(f"  4. Run: python scripts/cloud_dispatch_guard.py --task-id {task_id} --enforce-only --action verify")
            return 0
        else:
            print("\n" + "=" * 60)
            print("[🚫 BLOCK] Policy violation detected")
            print("=" * 60)
            print(f"\nReview details in: docs/compliance_reviews/review_latest.json")
            return 1

    print("\n[ok] Contract-only mode complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
