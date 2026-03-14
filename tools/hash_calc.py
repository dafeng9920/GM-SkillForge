#!/usr/bin/env python3
"""
Hash Calc - Three-Hash Calculation Entry Point (v0)

Thin wrapper for the three-hash calculation implementation.
Provides the single entry point for calculating:
- demand_hash
- contract_hash
- decision_hash

This is the designated module for:
- Three-hash calculation for v0
- Permit binding operations
- EvidenceRef hashing

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
Implementation: scripts/hash_calc.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# Load the implementation directly from scripts/hash_calc.py
_scripts_path = Path(__file__).parent.parent / "scripts" / "hash_calc.py"
spec = importlib.util.spec_from_file_location("scripts_hash_calc", _scripts_path)
_impl = importlib.util.module_from_spec(spec)
sys.modules["scripts_hash_calc"] = _impl
spec.loader.exec_module(_impl)

__all__ = [
    "calc_three_hashes",
    "read_json",
    "read_yaml",
    "IMPLEMENTATION_SOURCE",
]

IMPLEMENTATION_SOURCE = "scripts/hash_calc.py"

# Re-export all functions
calc_three_hashes = _impl.calc_three_hashes
read_json = _impl.read_json
read_yaml = _impl.read_yaml


def main() -> int:
    """CLI entry point for hash calculation."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Calculate demand/contract/decision hashes (v0)")
    parser.add_argument("--demand", type=Path, required=True, help="Demand DSL file")
    parser.add_argument("--contract", type=Path, required=True, help="Constitution Contract file")
    parser.add_argument("--decision", type=Path, required=True, help="Gate Decisions file")
    parser.add_argument("--keysets", type=Path, default=Path("orchestration/hash_keysets.yml"), help="Hash keysets configuration")
    parser.add_argument("--out", type=Path, required=True, help="Output manifest file")
    args = parser.parse_args()

    # Load inputs
    try:
        demand_obj = read_json(args.demand)
        contract_obj = read_json(args.contract)
        decision_obj = read_json(args.decision)
        keysets = read_yaml(args.keysets)
    except Exception as e:
        print(f"ERROR: Failed to load inputs: {e}", file=sys.stderr)
        return 1

    # Calculate hashes
    try:
        result = calc_three_hashes(demand_obj, contract_obj, decision_obj, keysets)
    except Exception as e:
        print(f"ERROR: Failed to calculate hashes: {e}", file=sys.stderr)
        return 1

    # Write output
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"OK: Wrote {args.out}")
    print(f"demand_hash: {result['demand_hash']}")
    print(f"contract_hash: {result['contract_hash']}")
    print(f"decision_hash: {result['decision_hash']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
