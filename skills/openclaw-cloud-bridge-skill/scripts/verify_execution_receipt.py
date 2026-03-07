#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys
from typing import List


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_keys(obj: dict, keys: List[str], label: str, errors: List[str]) -> None:
    for key in keys:
        if key not in obj:
            errors.append(f"{label}: missing key `{key}`")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify cloud execution receipt against task contract.")
    parser.add_argument("--contract", required=True, help="Path to task_contract.json")
    parser.add_argument("--receipt", required=True, help="Path to execution_receipt.json")
    parser.add_argument("--quiet", action="store_true", help="Only output PASS/FAIL status")
    args = parser.parse_args()

    contract_path = pathlib.Path(args.contract)
    receipt_path = pathlib.Path(args.receipt)

    try:
        contract = read_json(contract_path)
    except FileNotFoundError:
        print("FAIL")
        if not args.quiet:
            print(f"- contract file not found: {contract_path}")
        return 1
    try:
        receipt = read_json(receipt_path)
    except FileNotFoundError:
        print("FAIL")
        if not args.quiet:
            print(f"- receipt file not found: {receipt_path}")
        return 1
    errors: List[str] = []

    ensure_keys(
        contract,
        ["task_id", "command_allowlist", "required_artifacts", "acceptance"],
        "contract",
        errors,
    )
    ensure_keys(
        receipt,
        ["task_id", "status", "executed_commands", "exit_code", "artifacts", "summary"],
        "receipt",
        errors,
    )

    if errors:
        print("FAIL")
        if not args.quiet:
            for item in errors:
                print(f"- {item}")
        return 1

    if receipt["task_id"] != contract["task_id"]:
        errors.append("task_id mismatch between contract and receipt")

    allowset = set(contract["command_allowlist"])
    contract_policy = contract.get("policy", {})
    max_commands = int(contract_policy.get("max_commands", max(1, len(allowset))))
    executed = receipt.get("executed_commands", [])
    if len(executed) > max_commands:
        errors.append("executed_commands exceeded policy.max_commands")
    for cmd in executed:
        if cmd not in allowset:
            errors.append(f"executed command not allowed: {cmd}")

    required_artifacts = set(contract["required_artifacts"])
    actual_artifacts = set(receipt.get("artifacts", []))
    missing = sorted(required_artifacts - actual_artifacts)
    if missing:
        errors.append(f"missing required artifacts: {', '.join(missing)}")

    status = receipt.get("status")
    exit_code = int(receipt.get("exit_code", -1))
    if status != "success":
        errors.append(f"receipt status must be success for acceptance, got: {status}")
    if status == "success" and exit_code != 0:
        errors.append("status=success but exit_code is not 0")
    if status not in {"success", "failure"}:
        errors.append("status must be success or failure")

    if not receipt.get("summary", "").strip():
        errors.append("summary is empty")

    if errors:
        print("FAIL")
        if not args.quiet:
            for item in errors:
                print(f"- {item}")
        return 1

    print("PASS")
    if not args.quiet:
        print(f"- task_id: {contract['task_id']}")
        print(f"- executed_commands: {len(executed)}")
        print(f"- acceptance_items: {len(contract.get('acceptance', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
