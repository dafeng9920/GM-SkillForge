#!/usr/bin/env python3
"""
CLOUD-LOBSTER-CLOSED-LOOP ENFORCEMENT SCRIPT

HARD POLICY (Effective 2026-03-05):
- All CLOUD-ROOT tasks MUST use cloud-lobster-closed-loop-skill
- Any bypass of task_contract or verify_execution_receipt results in IMMEDIATE BLOCK
- All violations are written to docs/compliance_reviews/

Usage (run before ANY CLOUD-ROOT task dispatch):
    python scripts/enforce_cloud_lobster_closed_loop.py --task-id <task_id> --action dispatch
    python scripts/enforce_cloud_lobster_closed_loop.py --task-id <task_id> --action verify
"""

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Literal, Optional

# Compliance configuration
COMPLIANCE_DIR = pathlib.Path("docs/compliance_reviews")
REQUIRED_SKILL = "cloud-lobster-closed-loop-skill"
REQUIRED_CONTRACT_SCHEMA = "openclaw_task_contract_v1"
REQUIRED_RECEIPT_VERIFIER = "skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat() + "Z"


def read_json(path: pathlib.Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def detect_bypass(
    task_id: str,
    action: Literal["dispatch", "verify"],
    dispatch_dir: pathlib.Path = pathlib.Path(".tmp/openclaw-dispatch"),
) -> dict:
    """
    Detect if task execution bypassed cloud-lobster-closed-loop-skill.

    Returns dict with:
        - is_bypass: bool
        - bypass_reasons: list[str]
        - evidence: dict
    """
    task_dir = dispatch_dir / task_id
    contract_path = task_dir / "task_contract.json"
    receipt_path = task_dir / "execution_receipt.json"

    bypass_reasons = []
    evidence = {"task_id": task_id, "action": action, "task_dir_exists": task_dir.exists()}

    # Check 1: Contract must exist and use correct schema
    if action == "dispatch":
        if not contract_path.exists():
            bypass_reasons.append("NO_CONTRACT: task_contract.json not found before dispatch")
            evidence["contract_exists"] = False
        else:
            contract = read_json(contract_path)
            evidence["contract_schema"] = contract.get("schema_version")
            if contract.get("schema_version") != REQUIRED_CONTRACT_SCHEMA:
                bypass_reasons.append(f"INVALID_SCHEMA: expected {REQUIRED_CONTRACT_SCHEMA}, got {contract.get('schema_version')}")
            if not contract.get("command_allowlist"):
                bypass_reasons.append("NO_ALLOWLIST: command_allowlist missing or empty")
            if not contract.get("required_artifacts"):
                bypass_reasons.append("NO_ARTIFACTS: required_artifacts missing or empty")
            evidence["contract_valid"] = len(bypass_reasons) == 0

    # Check 2: Receipt must exist and be verified
    if action == "verify":
        if not receipt_path.exists():
            bypass_reasons.append("NO_RECEIPT: execution_receipt.json not found for verification")
            evidence["receipt_exists"] = False
        else:
            receipt = read_json(receipt_path)
            evidence["receipt_status"] = receipt.get("status")

            # Check if verify_execution_receipt.py was used
            verifier_path = pathlib.Path(REQUIRED_RECEIPT_VERIFIER)
            if not verifier_path.exists():
                bypass_reasons.append("VERIFIER_MISSING: required verify_execution_receipt.py not found")
            else:
                # Run the verifier
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(verifier_path), "--contract", str(contract_path), "--receipt", str(receipt_path)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    bypass_reasons.append(f"RECEIPT_VERIFICATION_FAILED: {result.stdout.strip() or result.stderr.strip()}")
                evidence["verification_run"] = True
                evidence["verification_exit_code"] = result.returncode

    # Check 3: Four artifacts must exist
    required_artifacts = ["execution_receipt.json", "stdout.log", "stderr.log", "audit_event.json"]
    missing = [f for f in required_artifacts if not (task_dir / f).exists()]
    if missing:
        bypass_reasons.append(f"MISSING_ARTIFACTS: {', '.join(missing)}")
    evidence["artifacts_present"] = [f for f in required_artifacts if (task_dir / f).exists()]

    return {
        "is_bypass": len(bypass_reasons) > 0,
        "bypass_reasons": bypass_reasons,
        "evidence": evidence,
    }


def write_block_record(
    task_id: str,
    bypass_reasons: list[str],
    evidence: dict,
    action: str,
) -> pathlib.Path:
    """Write a BLOCK decision to compliance reviews."""
    timestamp = utc_now()
    block_id = f"BLOCK_{task_id}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    block_record = {
        "block_id": block_id,
        "blocked_at_utc": timestamp,
        "task_id": task_id,
        "action": action,
        "decision": "BLOCK",
        "policy_violated": "CLOUD-LOBSTER-CLOSED-LOOP-MANDATORY",
        "policy_statement": f"All CLOUD-ROOT tasks MUST use {REQUIRED_SKILL}",
        "bypass_reasons": bypass_reasons,
        "evidence": evidence,
        "remediation": {
            "step_1": f"Use cloud-lobster-closed-loop-skill to generate task_contract.json",
            "step_2": f"Execute only commands in command_allowlist on CLOUD-ROOT",
            "step_3": f"Ensure all 4 artifacts (execution_receipt.json, stdout.log, stderr.log, audit_event.json) are returned",
            "step_4": f"Run verify_execution_receipt.py script for verification",
            "reference": "skills/cloud-lobster-closed-loop-skill/SKILL.md",
        },
        "reviewer": "Antigravity-Governance-Enforcer",
        "reviewer_role": "COMPLIANCE-ENFORCEMENT-AUTO",
        "execution_environment": "LOCAL-ANTIGRAVITY",
    }

    # Write to compliance reviews
    today_dir = COMPLIANCE_DIR / f"runs/{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')}"
    today_dir.mkdir(parents=True, exist_ok=True)

    block_path = today_dir / f"{block_id}.json"
    write_json(block_path, block_record)

    # Also update review_latest.json
    latest_path = COMPLIANCE_DIR / "review_latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(latest_path, block_record)

    # Also write markdown summary
    md_path = today_dir / f"{block_id}.md"
    md_content = f"""# BLOCK Decision: {block_id}

**Decision**: BLOCK
**Task ID**: {task_id}
**Action**: {action}
**Blocked At**: {timestamp}

## Policy Violated
CLOUD-LOBSTER-CLOSED-LOOP-MANDATORY

## Bypass Reasons
"""
    for reason in bypass_reasons:
        md_content += f"- {reason}\n"

    md_content += f"""
## Evidence
```json
{json.dumps(evidence, indent=2)}
```

## Remediation Steps
1. Use cloud-lobster-closed-loop-skill to generate task_contract.json
2. Execute only commands in command_allowlist on CLOUD-ROOT
3. Ensure all 4 artifacts are returned
4. Run verify_execution_receipt.py for verification

Reference: skills/cloud-lobster-closed-loop-skill/SKILL.md
"""
    md_path.write_text(md_content, encoding="utf-8")

    return block_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce cloud-lobster-closed-loop-skill for all CLOUD-ROOT tasks")
    parser.add_argument("--task-id", required=True, help="Task ID to validate")
    parser.add_argument(
        "--action",
        required=True,
        choices=["dispatch", "verify"],
        help="Action type: dispatch (before sending to CLOUD-ROOT) or verify (after execution)",
    )
    parser.add_argument("--dispatch-dir", default=".tmp/openclaw-dispatch", help="Dispatch directory base path")
    args = parser.parse_args()

    print(f"[CLOUD-LOBSTER-CLOSED-LOOP ENFORCEMENT]")
    print(f"Task ID: {args.task_id}")
    print(f"Action: {args.action}")
    print(f"Required Skill: {REQUIRED_SKILL}")
    print(f"Enforcing policy...")

    # Detect bypass
    result = detect_bypass(args.task_id, args.action, pathlib.Path(args.dispatch_dir))

    if result["is_bypass"]:
        print("\n[❌ BLOCK] Policy violation detected!")
        print("\nBypass Reasons:")
        for reason in result["bypass_reasons"]:
            print(f"  - {reason}")

        print("\nEvidence:")
        for key, value in result["evidence"].items():
            print(f"  {key}: {value}")

        # Write block record
        block_path = write_block_record(
            args.task_id,
            result["bypass_reasons"],
            result["evidence"],
            args.action,
        )
        print(f"\n[📝 BLOCK record written to: {block_path}]")
        print("[🚫 Task execution BLOCKED - follow remediation steps in the record]")
        return 1
    else:
        print("\n[✅ ALLOW] Task complies with cloud-lobster-closed-loop-skill")
        print(f"[📋 Task {args.task_id} may proceed to {args.action}]")
        return 0


if __name__ == "__main__":
    sys.exit(main())
