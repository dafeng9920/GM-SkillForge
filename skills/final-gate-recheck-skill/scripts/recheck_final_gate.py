#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pick_value(obj: dict, keys: list[str]) -> str:
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def pick_nested_value(obj: dict, path: list[str]) -> str:
    cur: object = obj
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return ""
        cur = cur[k]
    return cur.strip() if isinstance(cur, str) else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Recheck final gate consistency.")
    parser.add_argument("--verification-dir", required=True, type=Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    p = args.prefix
    vdir = args.verification_dir
    files = {
        "execution": vdir / f"{p}_execution_report.yaml",
        "review": vdir / f"{p}_review_decision.json",
        "compliance": vdir / f"{p}_compliance_attestation.json",
        "final_gate": vdir / f"{p}_final_gate_decision.json",
    }
    missing = [k for k, path in files.items() if not path.exists()]
    data = {}
    blockers = []
    required_changes = []

    for k, path in files.items():
        if path.exists() and path.suffix.lower() == ".json":
            data[k] = read_json(path)

    review_decision = pick_value(data.get("review", {}), ["decision", "final_decision", "final_verdict"]).upper()
    compliance_obj = data.get("compliance", {})
    compliance_decision = pick_value(compliance_obj, ["decision", "status", "final_decision"]).upper()
    if not compliance_decision:
        compliance_decision = pick_nested_value(compliance_obj, ["final_decision", "decision"]).upper()
    final_gate_decision = pick_value(data.get("final_gate", {}), ["decision", "final_decision", "final_verdict"]).upper()

    if missing:
        blockers.append(f"missing_records:{','.join(missing)}")
        for m in missing:
            required_changes.append(f"create missing record file for {m}")

    if review_decision and "ALLOW" not in review_decision:
        blockers.append(f"review_not_allow:{review_decision}")
        required_changes.append("rerun review and persist ALLOW decision if criteria are met")

    if compliance_decision and ("PASS" not in compliance_decision and "ALLOW" not in compliance_decision):
        blockers.append(f"compliance_not_pass:{compliance_decision}")
        required_changes.append("fix compliance blockers and regenerate compliance attestation")

    if final_gate_decision and "DENY" in final_gate_decision and not blockers:
        blockers.append("final_gate_deny_without_upstream_blocker")
        required_changes.append("rerun final gate with current execution/review/compliance records")

    status = "CONSISTENT" if not blockers else "INCONSISTENT"
    report = {
        "schema_version": "final_gate_recheck_v1",
        "prefix": p,
        "verification_dir": str(vdir),
        "recheck_status": status,
        "decisions": {
            "review": review_decision or None,
            "compliance": compliance_decision or None,
            "final_gate": final_gate_decision or None,
        },
        "missing_records": missing,
        "blockers": blockers,
        "required_changes": required_changes,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"recheck_status={status}")
    print(f"report={args.out}")
    return 0 if status == "CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())

