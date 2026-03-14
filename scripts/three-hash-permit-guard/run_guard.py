#!/usr/bin/env python3
"""
Three-Hash Permit Guard - Permit Five-Field + Delivery Completeness Validation

Validates that a Permit contains all five required fields:
1. demand_hash
2. contract_hash
3. decision_hash
4. audit_pack_hash
5. revision

AND validates delivery completeness:
- Blueprint (contracts/dsl/*.yml)
- Skill (skills/*/)
- n8n (workflows/**/*.json)
- Evidence (artifacts/*/)
- AuditPack (audit_pack/*.json)
- Permit (permits/*/*.json)

FAIL-CLOSED: Any validation failure returns FAIL with required_changes.

Spec source: docs/2026-03-04/v0-L5/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import the existing validators
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from validate_permit_binding import validate_permit_binding, ERROR_CODES
    from validate_delivery_completeness import validate_delivery_completeness
except ImportError as e:
    print(f"ERROR: Failed to import validator modules: {e}", file=sys.stderr)
    sys.exit(1)


class GuardDecision(str, Enum):
    """Guard decision values."""
    ALLOW = "ALLOW"
    DENY = "DENY"


class GuardResult:
    """Result of the three-hash permit guard check."""

    def __init__(self):
        self.status = GuardDecision.DENY
        self.permit_binding_result = None
        self.delivery_completeness_result = None
        self.error_code = None
        self.errors = []
        self.required_changes = []
        self.checked_at = datetime.now(UTC).isoformat()

    def add_error(self, code: str, message: str, required_change: str):
        """Add an error and set DENY status."""
        self.error_code = code
        self.errors.append({"code": code, "message": message})
        self.required_changes.append(required_change)

    def set_allow(self):
        """Set status to ALLOW."""
        self.status = GuardDecision.ALLOW
        self.error_code = None


def run_guard(
    permit_path: Path,
    base_path: Path | None = None,
    strict_mode: bool = True
) -> GuardResult:
    """
    Run the three-hash permit guard validation.

    Args:
        permit_path: Path to permit JSON file
        base_path: Base path for delivery completeness check (default: current directory)
        strict_mode: If True, DENY on any validation failure

    Returns:
        GuardResult with ALLOW/DENY decision
    """
    result = GuardResult()

    if base_path is None:
        base_path = Path.cwd()

    # 1) Validate permit binding (five fields)
    print(f"[GUARD] Validating permit binding: {permit_path}")
    permit_binding = validate_permit_binding(permit_path)
    result.permit_binding_result = {
        "status": permit_binding["status"],
        "error_code": permit_binding.get("error_code"),
        "missing_hashes": permit_binding.get("missing_hashes", []),
        "missing_fields": permit_binding.get("missing_fields", []),
        "invalid_hashes": permit_binding.get("invalid_hashes", []),
    }

    # Check for permit binding failures
    if permit_binding["status"] != "PASS":
        error_code = permit_binding.get("error_code", "UNKNOWN")
        if error_code == "SF_PERMIT_MISSING":
            result.add_error(
                "SF_PERMIT_MISSING",
                f"Permit file not found: {permit_path}",
                f"Ensure permit exists at {permit_path}"
            )
        elif "HASH" in error_code:
            missing_hashes = permit_binding.get("missing_hashes", [])
            missing_fields = permit_binding.get("missing_fields", [])
            result.add_error(
                error_code,
                f"Permit binding incomplete: missing {', '.join(missing_hashes + missing_fields)}",
                "Add all required fields to permit (demand_hash, contract_hash, decision_hash, audit_pack_hash, revision)"
            )
        elif error_code == "SF_HASH_FORMAT_INVALID":
            invalid_hashes = permit_binding.get("invalid_hashes", [])
            for h in invalid_hashes:
                result.add_error(
                    error_code,
                    f"Invalid hash format for {h['name']}: {h['value']}",
                    f"Fix hash format for {h['name']} (sha256:<64hex> or <64hex>)"
                )
        else:
            result.add_error(
                error_code,
                f"Permit binding validation failed: {error_code}",
                "Review permit and ensure all five required fields are present"
            )

        # FAIL-CLOSED: Exit early if permit binding fails
        return result

    print(f"[GUARD] Permit binding: PASS")

    # 2) Validate delivery completeness
    print(f"[GUARD] Validating delivery completeness at: {base_path}")
    delivery_result = validate_delivery_completeness(base_path)
    result.delivery_completeness_result = {
        "status": delivery_result["status"],
        "error_code": delivery_result.get("error_code"),
        "missing_items": delivery_result.get("missing_items", []),
        "present_items": delivery_result.get("present_items", []),
    }

    # Check for delivery completeness failures
    if delivery_result["status"] != "PASS":
        error_code = delivery_result.get("error_code", "UNKNOWN")
        missing_items = delivery_result.get("missing_items", [])
        required_changes = delivery_result.get("required_changes", [])

        result.add_error(
            error_code,
            f"Delivery incomplete: missing {len(missing_items)} items",
            f"Add missing delivery items: {'; '.join(required_changes)}"
        )

        # FAIL-CLOSED: Exit early if delivery incomplete
        return result

    print(f"[GUARD] Delivery completeness: PASS")

    # 3) All checks passed
    result.set_allow()

    return result


def main() -> int:
    """CLI entry point for three-hash permit guard."""
    parser = argparse.ArgumentParser(
        description="Three-Hash Permit Guard - Validate permit five fields + delivery completeness (FAIL-CLOSED)"
    )
    parser.add_argument(
        "--permit",
        type=Path,
        required=True,
        help="Path to permit JSON file",
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Base path for delivery completeness check (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write guard decision to file (JSON format)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output decision (ALLOW/DENY)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Strict mode: DENY on any validation failure (default: True)",
    )
    args = parser.parse_args()

    # Run guard
    print(f"[GUARD] Three-Hash Permit Guard starting at {datetime.now(UTC).isoformat()}")
    print(f"[GUARD] Permit: {args.permit}")
    print(f"[GUARD] Base path: {args.base_path}")
    print(f"[GUARD] Strict mode: {args.strict}")
    print("-" * 60)

    result = run_guard(args.permit, args.base_path, args.strict)

    print("-" * 60)
    print(f"[GUARD] Decision: {result.status.value}")

    if result.status == GuardDecision.DENY:
        print(f"[GUARD] Error code: {result.error_code}")
        print(f"[GUARD] Errors: {len(result.errors)}")
        for e in result.errors:
            print(f"  - [{e['code']}] {e['message']}")
        print(f"[GUARD] Required changes: {len(result.required_changes)}")
        for i, c in enumerate(result.required_changes, 1):
            print(f"  {i}. {c}")
    else:
        print("[GUARD] All validations passed - ALLOW")

    # Write output file if requested
    if args.output:
        output_data = {
            "decision": result.status.value,
            "error_code": result.error_code,
            "errors": result.errors,
            "required_changes": result.required_changes,
            "permit_binding": result.permit_binding_result,
            "delivery_completeness": result.delivery_completeness_result,
            "checked_at": result.checked_at,
            "guard_version": "v0",
            "fail_closed_policy": True,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
        print(f"[GUARD] Decision written to: {args.output}")

    if args.quiet:
        print(result.status.value)

    return 0 if result.status == GuardDecision.ALLOW else 1


if __name__ == "__main__":
    sys.exit(main())
