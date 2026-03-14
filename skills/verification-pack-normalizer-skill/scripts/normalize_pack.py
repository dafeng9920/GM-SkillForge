#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def expected_names(prefix: str) -> dict[str, str]:
    return {
        "execution": f"{prefix}_execution_report.yaml",
        "review": f"{prefix}_review_decision.json",
        "compliance": f"{prefix}_compliance_attestation.json",
        "final_gate": f"{prefix}_final_gate_decision.json",
    }


def find_variants(vdir: Path, prefix: str, key: str) -> list[Path]:
    patterns = {
        "execution": f"{prefix}_execution_report*.y*ml",
        "review": f"{prefix}_review_decision*.json",
        "compliance": f"{prefix}_compliance_attestation*.json",
        "final_gate": f"{prefix}_final_gate_decision*.json",
    }
    return [m for m in sorted(vdir.glob(patterns[key])) if m.is_file()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize verification pack naming.")
    parser.add_argument("--verification-dir", required=True, type=Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    vdir = args.verification_dir
    expect = expected_names(args.prefix)
    report = {
        "schema_version": "verification_pack_normalizer_v1",
        "prefix": args.prefix,
        "verification_dir": str(vdir),
        "normalized": False,
        "canonical": {},
        "variants": {},
        "actions": [],
        "missing": [],
    }

    for key, fname in expect.items():
        canonical = vdir / fname
        variants = find_variants(vdir, args.prefix, key)
        report["variants"][key] = [v.name for v in variants]
        if canonical.exists():
            report["canonical"][key] = canonical.name
            continue
        if variants:
            if args.apply:
                shutil.copyfile(variants[0], canonical)
                report["actions"].append(f"created alias: {canonical.name} <- {variants[0].name}")
                report["canonical"][key] = canonical.name
            else:
                report["missing"].append(fname)
                report["actions"].append(f"missing canonical {fname}; candidate {variants[0].name}")
        else:
            report["missing"].append(fname)
            report["actions"].append(f"missing canonical {fname}; no variant")

    report["normalized"] = len(report["missing"]) == 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"normalized={str(report['normalized']).lower()}")
    print(f"report={args.out}")
    return 0 if report["normalized"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

