#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed guard for permit binding + delivery completeness."
    )
    parser.add_argument("--permit", required=True, type=Path)
    parser.add_argument("--base-path", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    permit_result_path = args.out.parent / (args.out.stem + ".permit_check.json")
    delivery_result_path = args.out.parent / (args.out.stem + ".delivery_check.json")

    permit_cmd = [
        sys.executable,
        "scripts/validate_permit_binding.py",
        "--permit",
        str(args.permit),
        "--output",
        str(permit_result_path),
    ]
    delivery_cmd = [
        sys.executable,
        "scripts/validate_delivery_completeness.py",
        "--base-path",
        str(args.base_path),
        "--output",
        str(delivery_result_path),
    ]

    p_code, p_out, p_err = run_cmd(permit_cmd)
    d_code, d_out, d_err = run_cmd(delivery_cmd)

    permit_check = {}
    delivery_check = {}
    if permit_result_path.exists():
        permit_check = json.loads(permit_result_path.read_text(encoding="utf-8"))
    if delivery_result_path.exists():
        delivery_check = json.loads(delivery_result_path.read_text(encoding="utf-8"))

    blocking_reasons = []
    if p_code != 0:
        blocking_reasons.append("permit_binding_failed")
    if d_code != 0:
        blocking_reasons.append("delivery_completeness_failed")

    guard_status = "PASS" if not blocking_reasons else "FAIL"
    report = {
        "schema_version": "three_hash_permit_guard_v1",
        "guard_status": guard_status,
        "permit_check_exit_code": p_code,
        "delivery_check_exit_code": d_code,
        "permit_check": permit_check,
        "delivery_check": delivery_check,
        "blocking_reasons": blocking_reasons,
        "raw": {
            "permit_stdout": p_out.strip(),
            "permit_stderr": p_err.strip(),
            "delivery_stdout": d_out.strip(),
            "delivery_stderr": d_err.strip(),
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"guard_status={guard_status}")
    print(f"report={args.out}")
    return 0 if guard_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

