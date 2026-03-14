#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_PR_FILES = [
    "PR1_final_gate_decision.json",
    "PR2_final_gate_decision.json",
    "PR3_final_gate_decision.json",
    "PR4_final_gate_decision.json",
    "PR5_final_gate_decision.json",
]
REQUIRED_EXTRA = ["PR5_compliance_attestation.json"]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def decision_is_allow(obj: dict) -> bool:
    fields = [
        str(obj.get("final_verdict", "")).upper(),
        str(obj.get("decision", "")).upper(),
        str(obj.get("final_decision", "")).upper(),
    ]
    return any("ALLOW" in f for f in fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue V0 seal decision artifacts.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--verification-dir", required=True, type=Path)
    parser.add_argument("--source-of-truth", default="")
    args = parser.parse_args()

    vdir = args.verification_dir
    missing: list[str] = []
    invalid: list[str] = []
    for name in REQUIRED_PR_FILES + REQUIRED_EXTRA:
        if not (vdir / name).exists():
            missing.append(name)

    pr_status = {}
    if not missing:
        for name in REQUIRED_PR_FILES:
            obj = read_json(vdir / name)
            ok = decision_is_allow(obj)
            pr_status[name] = "ALLOW" if ok else "NOT_ALLOW"
            if not ok:
                invalid.append(name)

    allow = not missing and not invalid
    decision_path = vdir / f"V0_SEAL_DECISION_{args.date}.json"
    board_path = vdir / f"V0_SEAL_BOARD_{args.date}.md"

    decision_obj = {
        "schema_version": "v0_seal_decision_v1",
        "seal_id": f"V0-SEAL-{args.date.replace('-', '')}",
        "date": args.date,
        "source_of_truth": args.source_of_truth,
        "status": "ALLOW" if allow else "DENY",
        "v0_seal": "GRANTED" if allow else "DENIED",
        "checks": {
            "missing_files": missing,
            "invalid_decisions": invalid,
            "pr_status": pr_status,
        },
    }
    decision_path.write_text(json.dumps(decision_obj, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# V0 Seal Decision ({args.date})",
        "",
        f"- `FINAL_DECISION={'ALLOW' if allow else 'DENY'}`",
        f"- `V0_SEAL={'GRANTED' if allow else 'DENIED'}`",
        "",
        "## Checks",
        f"- Missing files: {', '.join(missing) if missing else 'None'}",
        f"- Invalid decisions: {', '.join(invalid) if invalid else 'None'}",
    ]
    board_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"V0_SEAL={'GRANTED' if allow else 'DENIED'}")
    print(f"WROTE: {decision_path}")
    print(f"WROTE: {board_path}")
    return 0 if allow else 1


if __name__ == "__main__":
    raise SystemExit(main())

