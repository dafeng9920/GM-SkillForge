#!/usr/bin/env python3
"""
Policy Validation and Version Management Tool.

Usage:
    python scripts/validate_policy.py --policy configs/audit_policy_v1.json
    python scripts/validate_policy.py --policy configs/audit_policy_v1.json --compute-hash

This tool validates policy files against the audit_policy.schema.json and
computes policy hash for traceability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def compute_policy_hash(policy: dict[str, Any]) -> str:
    """
    Compute SHA256 hash of policy content for traceability.
    Excludes metadata.change_log from hash computation.
    """
    # Create a copy and exclude mutable metadata
    hash_content = dict(policy)
    if "metadata" in hash_content and "change_log" in hash_content["metadata"]:
        metadata_copy = dict(hash_content["metadata"])
        del metadata_copy["change_log"]
        hash_content["metadata"] = metadata_copy

    content = json.dumps(hash_content, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_policy_schema(policy: dict[str, Any], schema_path: Path) -> list[str]:
    """
    Validate policy against schema.
    Returns list of validation errors (empty if valid).
    """
    errors: list[str] = []

    try:
        import jsonschema
        from jsonschema import validate, ValidationError

        schema = load_json(schema_path)
        try:
            validate(instance=policy, schema=schema)
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message} at path {'/'.join(str(p) for p in e.path)}")
    except ImportError:
        # jsonschema not available, perform basic validation
        errors.extend(_basic_validate(policy))

    return errors


def _basic_validate(policy: dict[str, Any]) -> list[str]:
    """Basic validation without jsonschema library."""
    errors: list[str] = []

    required_fields = [
        "policy_version",
        "policy_name",
        "description",
        "token_estimator",
        "cost",
        "redundancy",
        "safety",
        "structure",
        "evidence_ready",
        "levels",
        "overall_weights",
        "gate",
        "metadata",
    ]

    for field in required_fields:
        if field not in policy:
            errors.append(f"Missing required field: {field}")

    # Validate version format
    if "policy_version" in policy:
        import re
        if not re.match(r"^v\d+\.\d+\.\d+(-[0-9]{8})?$", policy["policy_version"]):
            errors.append(f"Invalid policy_version format: {policy['policy_version']}")

    # Validate weights sum to ~1.0
    if "overall_weights" in policy:
        weights = policy["overall_weights"]
        total = sum(weights.get(k, 0) for k in ["L1_cost", "L2_redundancy", "L3_safety", "L4_structure", "L5_evidence_ready"])
        if abs(total - 1.0) > 0.01:
            errors.append(f"Overall weights sum to {total}, expected 1.0")

    # Validate levels
    if "levels" in policy:
        levels = policy["levels"]
        if levels.get("pass_min", 0) <= levels.get("warn_min", 0):
            errors.append("pass_min must be greater than warn_min")

    return errors


def validate_policy_file(policy_path: Path, schema_path: Path | None = None) -> dict[str, Any]:
    """
    Validate a policy file and return validation result.
    """
    result = {
        "valid": False,
        "policy_path": str(policy_path),
        "policy_version": None,
        "policy_hash": None,
        "errors": [],
        "warnings": [],
    }

    # Load policy
    try:
        policy = load_json(policy_path)
    except json.JSONDecodeError as e:
        result["errors"].append(f"JSON parse error: {e}")
        return result
    except FileNotFoundError:
        result["errors"].append(f"Policy file not found: {policy_path}")
        return result

    result["policy_version"] = policy.get("policy_version")

    # Determine schema path
    if schema_path is None:
        schema_path = Path(__file__).parent.parent / "schemas" / "audit_policy.schema.json"

    # Validate schema
    errors = validate_policy_schema(policy, schema_path)
    result["errors"].extend(errors)

    # Compute hash
    result["policy_hash"] = compute_policy_hash(policy)

    # Additional warnings
    if "metadata" in policy and "change_log" in policy["metadata"]:
        changelog = policy["metadata"]["change_log"]
        if not changelog:
            result["warnings"].append("Change log is empty")

    result["valid"] = len(result["errors"]) == 0
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate audit policy files")
    parser.add_argument("--policy", type=Path, required=True, help="Path to policy JSON file")
    parser.add_argument("--schema", type=Path, help="Path to schema file (default: schemas/audit_policy.schema.json)")
    parser.add_argument("--compute-hash", action="store_true", help="Compute and display policy hash")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = validate_policy_file(args.policy, args.schema)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Policy: {result['policy_path']}")
        print(f"Version: {result['policy_version']}")
        print(f"Hash: {result['policy_hash']}")

        if result["errors"]:
            print("\nErrors:")
            for e in result["errors"]:
                print(f"  - {e}")

        if result["warnings"]:
            print("\nWarnings:")
            for w in result["warnings"]:
                print(f"  - {w}")

        print(f"\nValid: {result['valid']}")

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
