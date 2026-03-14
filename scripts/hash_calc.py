#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def path_exists(obj: Any, path: str) -> bool:
    cur = obj
    for seg in path.split("."):
        if not isinstance(cur, dict) or seg not in cur:
            return False
        cur = cur[seg]
    return True


def remove_fields_by_name(obj: Any, names: set[str]) -> Any:
    if isinstance(obj, dict):
        return {
            k: remove_fields_by_name(v, names)
            for k, v in obj.items()
            if k not in names
        }
    if isinstance(obj, list):
        return [remove_fields_by_name(v, names) for v in obj]
    return obj


def normalize_scalar(v: Any) -> Any:
    if isinstance(v, float):
        return round(v, 6)
    return v


def sort_list_items(items: list[Any], sort_keys: list[str]) -> list[Any]:
    if not sort_keys:
        try:
            return sorted(items, key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
        except Exception:
            return items

    def sort_key(item: Any) -> tuple[Any, ...]:
        if not isinstance(item, dict):
            return tuple("" for _ in sort_keys)
        return tuple(normalize_scalar(item.get(k)) for k in sort_keys)

    return sorted(items, key=sort_key)


def apply_sort_rules(obj: Any, rules: dict[str, list[str]], path: str = "") -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            subpath = f"{path}.{k}" if path else k
            out[k] = apply_sort_rules(v, rules, subpath)
        return out

    if isinstance(obj, list):
        list_path = path
        sorted_items = [apply_sort_rules(v, rules, path) for v in obj]
        if list_path in rules:
            return sort_list_items(sorted_items, rules[list_path])
        return sorted_items

    return normalize_scalar(obj)


def canonical_dump(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True)


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_demand_hash_input(raw: dict[str, Any], spec: dict[str, Any], global_excl: set[str]) -> dict[str, Any]:
    missing = [p for p in spec["required_paths"] if not path_exists(raw, p)]
    if missing:
        raise ValueError(f"demand missing required paths: {missing}")

    obj = copy.deepcopy(raw)
    obj = remove_fields_by_name(obj, global_excl | set(spec.get("exclude_field_names", [])))
    obj = apply_sort_rules(obj, spec.get("list_sort_rules", {}))
    return obj


def build_contract_hash_input(raw: dict[str, Any], spec: dict[str, Any], global_excl: set[str]) -> dict[str, Any]:
    missing = [p for p in spec["required_paths"] if not path_exists(raw, p)]
    if missing:
        raise ValueError(f"contract missing required paths: {missing}")

    obj = copy.deepcopy(raw)
    obj = remove_fields_by_name(obj, global_excl | set(spec.get("exclude_field_names", [])))
    obj = apply_sort_rules(obj, spec.get("list_sort_rules", {}))
    return obj


def build_decision_hash_input(raw: dict[str, Any], spec: dict[str, Any], global_excl: set[str]) -> dict[str, Any]:
    missing = [p for p in spec["required_paths"] if not path_exists(raw, p)]
    if missing:
        raise ValueError(f"decision missing required paths: {missing}")

    raw_decisions = raw.get("gate_decisions", [])
    by_gate: dict[str, dict[str, Any]] = {}
    include_fields = spec.get("include_fields_per_decision", [])
    for item in raw_decisions:
        if not isinstance(item, dict):
            continue
        gate = item.get("gate_name")
        if not gate:
            continue
        filtered = {k: copy.deepcopy(item.get(k)) for k in include_fields if k in item}
        filtered = remove_fields_by_name(filtered, global_excl)
        filtered = apply_sort_rules(filtered, spec.get("list_sort_rules", {}))
        by_gate[gate] = filtered

    ordered = []
    for gate in spec.get("fixed_gate_order", []):
        if gate in by_gate:
            ordered.append(by_gate[gate])

    return {"gate_decisions": ordered}


def calc_three_hashes(
    demand_obj: dict[str, Any],
    contract_obj: dict[str, Any],
    decision_obj: dict[str, Any],
    keysets: dict[str, Any],
) -> dict[str, Any]:
    global_excl = set(keysets["global"].get("exclude_field_names", []))

    demand_in = build_demand_hash_input(demand_obj, keysets["demand"], global_excl)
    contract_in = build_contract_hash_input(contract_obj, keysets["contract"], global_excl)
    decision_in = build_decision_hash_input(decision_obj, keysets["decision"], global_excl)

    demand_canonical = canonical_dump(demand_in)
    contract_canonical = canonical_dump(contract_in)
    decision_canonical = canonical_dump(decision_in)

    return {
        "hash_spec_version": keysets.get("hash_spec_version", "v0"),
        "demand_hash": sha256_of_text(demand_canonical),
        "contract_hash": sha256_of_text(contract_canonical),
        "decision_hash": sha256_of_text(decision_canonical),
        "canonical_inputs": {
            "demand": demand_in,
            "contract": contract_in,
            "decision": decision_in,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate demand/contract/decision hashes")
    parser.add_argument("--demand", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--keysets", type=Path, default=Path("orchestration/hash_keysets.yml"))
    parser.add_argument("--out", type=Path, required=True, help="Output manifest JSON")
    args = parser.parse_args()

    demand_obj = read_json(args.demand)
    contract_obj = read_json(args.contract)
    decision_obj = read_json(args.decision)
    keysets = read_yaml(args.keysets)

    result = calc_three_hashes(demand_obj, contract_obj, decision_obj, keysets)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: wrote {args.out}")
    print(f"demand_hash={result['demand_hash']}")
    print(f"contract_hash={result['contract_hash']}")
    print(f"decision_hash={result['decision_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
