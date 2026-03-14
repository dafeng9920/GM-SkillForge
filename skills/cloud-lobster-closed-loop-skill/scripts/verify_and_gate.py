#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Tuple


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_verify(contract_path: pathlib.Path, receipt_path: pathlib.Path) -> Tuple[bool, list[str]]:
    verifier = pathlib.Path("skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py")
    cmd = [
        sys.executable,
        str(verifier),
        "--contract",
        str(contract_path),
        "--receipt",
        str(receipt_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    ok = result.returncode == 0 and lines and lines[0] == "PASS"
    details = lines[1:] if len(lines) > 1 else []
    if not ok and not details:
        details = [line.strip() for line in result.stderr.splitlines() if line.strip()]
    return ok, details


def main() -> int:
    parser = argparse.ArgumentParser(description="Run receipt verification and emit review/final gate decisions.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--dispatch-dir", default=".tmp/openclaw-dispatch")
    parser.add_argument("--verification-dir", required=True)
    parser.add_argument("--reviewer", default="Kior-C")
    parser.add_argument("--gatekeeper", default="Antigravity-1")
    args = parser.parse_args()

    dispatch_base = pathlib.Path(args.dispatch_dir) / args.task_id
    contract_path = dispatch_base / "task_contract.json"
    receipt_path = dispatch_base / "execution_receipt.json"
    verification_dir = pathlib.Path(args.verification_dir)

    missing = [str(p.as_posix()) for p in [contract_path, receipt_path] if not p.exists()]
    if missing:
        print("FAIL")
        for item in missing:
            print(f"- missing required file: {item}")
        return 1

    contract = read_json(contract_path)
    receipt = read_json(receipt_path)
    ok, details = run_verify(contract_path, receipt_path)
    decision = "ALLOW" if ok else "DENY"
    now = utc_now()
    blocking_evidence = [] if ok else [f"verify_execution_receipt failed for {args.task_id}"]
    required_changes = [] if ok else details

    review = {
        "review_meta": {
            "reviewer": args.reviewer,
            "reviewed_at_utc": now,
            "execution_environment": "LOCAL-ANTIGRAVITY",
            "task_id": args.task_id,
            "baseline_id": contract.get("baseline_id"),
        },
        "review_decision": {
            "status": decision,
            "fail_closed_policy": True,
            "blocking_evidence": blocking_evidence,
            "required_changes": required_changes,
        },
        "evidence_refs": {
            "task_contract": contract_path.as_posix(),
            "execution_receipt": receipt_path.as_posix(),
            "stdout_log": (dispatch_base / "stdout.log").as_posix(),
            "stderr_log": (dispatch_base / "stderr.log").as_posix(),
            "audit_event": (dispatch_base / "audit_event.json").as_posix(),
        },
    }

    final_gate = {
        "schema_version": "final_gate_decision_v1",
        "task_id": args.task_id,
        "decision": decision,
        "decision_issued_at": now,
        "decision_issued_by": args.gatekeeper,
        "execution_environment": "LOCAL-ANTIGRAVITY",
        "baseline_id": contract.get("baseline_id"),
        "blocking_evidence": blocking_evidence,
        "required_changes": required_changes,
        "verification_summary": {
            "verify_execution_receipt_py": "PASS" if ok else "FAIL",
            "receipt_status": receipt.get("status"),
            "commands_executed": len(receipt.get("executed_commands", [])),
            "acceptance_items": len(contract.get("acceptance", [])),
        },
    }

    review_path = verification_dir / f"{args.task_id}_review_decision.json"
    gate_path = verification_dir / f"{args.task_id}_final_gate.json"
    write_json(review_path, review)
    write_json(gate_path, final_gate)

    print(f"[ok] decision={decision}")
    print(f"[ok] review={review_path.as_posix()}")
    print(f"[ok] final_gate={gate_path.as_posix()}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

