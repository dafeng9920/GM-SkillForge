#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hash_calc import calc_three_hashes, read_json, read_yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate three-hash manifest consistency")
    parser.add_argument("--demand", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--keysets", type=Path, default=Path("orchestration/hash_keysets.yml"))
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"FAIL\n- manifest not found: {args.manifest}")
        return 1

    manifest = read_json(args.manifest)
    keysets = read_yaml(args.keysets)
    computed = calc_three_hashes(read_json(args.demand), read_json(args.contract), read_json(args.decision), keysets)

    errors: list[str] = []
    for k in ("hash_spec_version", "demand_hash", "contract_hash", "decision_hash"):
        if manifest.get(k) != computed.get(k):
            errors.append(f"{k} mismatch: manifest={manifest.get(k)} computed={computed.get(k)}")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1

    print("PASS")
    print(f"- hash_spec_version: {computed['hash_spec_version']}")
    print(f"- demand_hash: {computed['demand_hash']}")
    print(f"- contract_hash: {computed['contract_hash']}")
    print(f"- decision_hash: {computed['decision_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
