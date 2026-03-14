#!/usr/bin/env python3
"""
PR2-T1: Permit Binding Validation - Three Hash Enforcement

Validates that a Permit contains all required binding fields:
- demand_hash
- contract_hash
- decision_hash
- audit_pack_hash
- revision

Missing any field => FAIL with machine-readable output.

Spec source: docs/2026-03-04/v0-L5/"三哈希口径"落成validate.py 的硬校验（v0）.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path


# Error codes per v0-L5 specification
ERROR_CODES = {
    "PERMIT_MISSING": "SF_PERMIT_MISSING",
    "PERMIT_INVALID_JSON": "SF_PERMIT_INVALID_JSON",
    "DEMAND_HASH_MISSING": "SF_DEMAND_HASH_MISSING",
    "CONTRACT_HASH_MISSING": "SF_CONTRACT_HASH_MISSING",
    "DECISION_HASH_MISSING": "SF_DECISION_HASH_MISSING",
    "HASH_FORMAT_INVALID": "SF_HASH_FORMAT_INVALID",
    "PERMIT_BINDING_INCOMPLETE": "SF_PERMIT_BINDING_INCOMPLETE",
    "AUDIT_PACK_HASH_MISSING": "SF_AUDIT_PACK_HASH_MISSING",
    "REVISION_MISSING": "SF_REVISION_MISSING",
}

# SHA256 hash pattern (64 hex chars, optional sha256: prefix)
SHA256_PATTERN = re.compile(r'^(sha256:)?[0-9a-f]{64}$')


def validate_hash_format(value: str | None) -> bool:
    """Validate hash is in correct SHA256 format."""
    if value is None:
        return False
    return bool(SHA256_PATTERN.match(value.strip()))


def validate_permit_binding(permit_path: Path) -> dict:
    """
    Validate Permit contains all three required hashes.

    Returns machine-readable result dict with:
    - status: "PASS" or "FAIL"
    - error_code: error code if failed
    - missing_hashes: list of missing hash names
    - invalid_hashes: list of invalid format hashes
    - permit_data: raw permit data if valid JSON
    """
    result = {
        "status": "FAIL",
        "error_code": None,
        "missing_hashes": [],
        "invalid_hashes": [],
        "missing_fields": [],
        "required_changes": [],
        "permit_data": None,
        "permit_path": str(permit_path),
    }

    # Check if permit file exists
    if not permit_path.exists():
        result["error_code"] = ERROR_CODES["PERMIT_MISSING"]
        return result

    # Try to parse JSON
    try:
        permit_data = json.loads(permit_path.read_text(encoding="utf-8"))
        result["permit_data"] = permit_data
    except json.JSONDecodeError as e:
        result["error_code"] = ERROR_CODES["PERMIT_INVALID_JSON"]
        result["parse_error"] = str(e)
        return result

    # Required binding fields per v0 hard rule
    required_hashes = ["demand_hash", "contract_hash", "decision_hash", "audit_pack_hash"]
    required_fields = required_hashes + ["revision"]

    # Check for missing required fields
    for field_name in required_fields:
        if field_name not in permit_data or permit_data[field_name] is None or str(permit_data[field_name]).strip() == "":
            result["missing_fields"].append(field_name)
            if field_name in required_hashes:
                result["missing_hashes"].append(field_name)
            result["required_changes"].append(f"populate permit field: {field_name}")

    # Check hash format for present hashes
    for hash_name in required_hashes:
        if hash_name in permit_data and permit_data[hash_name] is not None:
            if not validate_hash_format(permit_data[hash_name]):
                result["invalid_hashes"].append({
                    "name": hash_name,
                    "value": permit_data[hash_name]
                })
                result["required_changes"].append(f"fix hash format for: {hash_name} (sha256:<64hex> or <64hex>)")

    # Determine overall status
    if result["missing_fields"]:
        result["error_code"] = ERROR_CODES["PERMIT_BINDING_INCOMPLETE"]
        if "demand_hash" in result["missing_hashes"]:
            result["error_code"] = ERROR_CODES["DEMAND_HASH_MISSING"]
        elif "contract_hash" in result["missing_hashes"]:
            result["error_code"] = ERROR_CODES["CONTRACT_HASH_MISSING"]
        elif "decision_hash" in result["missing_hashes"]:
            result["error_code"] = ERROR_CODES["DECISION_HASH_MISSING"]
        elif "audit_pack_hash" in result["missing_hashes"]:
            result["error_code"] = ERROR_CODES["AUDIT_PACK_HASH_MISSING"]
        elif "revision" in result["missing_fields"]:
            result["error_code"] = ERROR_CODES["REVISION_MISSING"]
    elif result["invalid_hashes"]:
        result["error_code"] = ERROR_CODES["HASH_FORMAT_INVALID"]
    else:
        result["status"] = "PASS"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Permit binding with required fields (demand/contract/decision/audit_pack_hash/revision)"
    )
    parser.add_argument(
        "--permit",
        type=Path,
        required=True,
        help="Path to permit JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write machine-readable result to file (JSON format)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output status (PASS/FAIL), no details",
    )
    args = parser.parse_args()

    result = validate_permit_binding(args.permit)

    # Write output file if requested
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    if args.quiet:
        print(result["status"])
    else:
        print(f"status: {result['status']}")
        if result["error_code"]:
            print(f"error_code: {result['error_code']}")
        if result["missing_hashes"]:
            print(f"missing_hashes: {', '.join(result['missing_hashes'])}")
        if result["missing_fields"]:
            print(f"missing_fields: {', '.join(result['missing_fields'])}")
        if result["invalid_hashes"]:
            print("invalid_hashes:")
            for h in result["invalid_hashes"]:
                print(f"  - {h['name']}: {h['value']}")
        if result["required_changes"]:
            print("required_changes:")
            for c in result["required_changes"]:
                print(f"  - {c}")

    # Exit code: 0 = PASS, 1 = FAIL
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
