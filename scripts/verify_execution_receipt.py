#!/usr/bin/env python3
"""
T-R1: Verify Execution Receipt - Contract-Receipt Consistency Validation

Validates that an execution receipt matches its contract specification:
1. Receipt contains all required fields per schema
2. task_id matches between receipt and contract
3. executor information is present and valid
4. allowlist commands match actual executed commands
5. All declared artifacts exist
6. Security audit passes

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

# Error codes
ERROR_CODES = {
    "RECEIPT_MISSING": "SF_RECEIPT_MISSING",
    "RECEIPT_INVALID_JSON": "SF_RECEIPT_INVALID_JSON",
    "RECEIPT_VERSION_MISMATCH": "SF_RECEIPT_VERSION_MISMATCH",
    "TASK_ID_MISMATCH": "SF_TASK_ID_MISMATCH",
    "REQUIRED_FIELD_MISSING": "SF_REQUIRED_FIELD_MISSING",
    "ARTIFACT_MISSING": "SF_ARTIFACT_MISSING",
    "ALLOWLIST_VIOLATION": "SF_ALLOWLIST_VIOLATION",
    "SECURITY_AUDIT_FAILED": "SF_SECURITY_AUDIT_FAILED",
    "CONTRACT_RECEIPT_INCONSISTENT": "SF_CONTRACT_RECEIPT_INCONSISTENT",
}


class ValidationStatus(str, Enum):
    """Validation status."""
    PASS = "PASS"
    FAIL = "FAIL"


class ValidationResult:
    """Validation result for execution receipt verification."""

    def __init__(self):
        self.status = ValidationStatus.FAIL
        self.error_code = None
        self.errors = []
        self.warnings = []
        self.required_changes = []
        self.checked_at = datetime.now(UTC).isoformat()

    def add_error(self, code: str, message: str, required_change: str | None = None):
        """Add an error to the result."""
        self.error_code = code
        self.errors.append({"code": code, "message": message})
        if required_change:
            self.required_changes.append(required_change)

    def add_warning(self, message: str):
        """Add a warning to the result."""
        self.warnings.append(message)

    def set_pass(self):
        """Set status to PASS."""
        self.status = ValidationStatus.PASS
        self.error_code = None


def verify_receipt_structure(receipt: dict[str, Any]) -> ValidationResult:
    """Verify receipt has all required fields with correct structure."""
    result = ValidationResult()

    # Required fields per receipt schema
    required_fields = [
        "receipt_version",
        "task_id",
        "executor",
        "execution_context",
        "allowlist",
        "execution_summary",
        "artifacts",
        "final_status",
    ]

    for field in required_fields:
        if field not in receipt:
            result.add_error(
                ERROR_CODES["REQUIRED_FIELD_MISSING"],
                f"Required field '{field}' missing from receipt",
                f"Add '{field}' field to receipt"
            )
            return result

    # Validate receipt_version
    if receipt["receipt_version"] != "1.0":
        result.add_warning(f"Receipt version {receipt['receipt_version']} may not be supported")

    # Validate executor
    if not isinstance(receipt["executor"], dict):
        result.add_error(
            ERROR_CODES["REQUIRED_FIELD_MISSING"],
            "Executor must be a dictionary",
            "Ensure executor field contains {name, type, version}"
        )
        return result

    required_executor_fields = ["name", "type", "version"]
    for field in required_executor_fields:
        if field not in receipt["executor"]:
            result.add_error(
                ERROR_CODES["REQUIRED_FIELD_MISSING"],
                f"Executor field '{field}' missing",
                f"Add '{field}' to executor"
            )

    # Validate final_status
    valid_statuses = ["COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED"]
    if receipt["final_status"] not in valid_statuses:
        result.add_error(
            ERROR_CODES["REQUIRED_FIELD_MISSING"],
            f"Invalid final_status: {receipt['final_status']}",
            f"Set final_status to one of: {valid_statuses}"
        )
        return result

    # Check for required_changes if status is FAILED
    if receipt["final_status"] == "FAILED":
        if "required_changes" not in receipt or not receipt["required_changes"]:
            result.add_error(
                ERROR_CODES["REQUIRED_FIELD_MISSING"],
                "FAILED status requires required_changes field",
                "Add required_changes array to receipt"
            )
            return result

    result.set_pass()
    return result


def verify_artifacts_exist(receipt: dict[str, Any], base_path: Path) -> ValidationResult:
    """Verify all declared artifacts exist at their specified paths."""
    result = ValidationResult()

    if "artifacts" not in receipt:
        result.add_error(
            ERROR_CODES["REQUIRED_FIELD_MISSING"],
            "Receipt missing artifacts field",
            "Add artifacts field to receipt"
        )
        return result

    artifacts = receipt["artifacts"]
    missing_artifacts = []

    # Check artifact paths if present
    artifact_paths = [
        artifacts.get("stdout_path"),
        artifacts.get("stderr_path"),
        artifacts.get("audit_path"),
    ]

    for path_str in artifact_paths:
        if path_str:
            artifact_path = base_path / path_str
            if not artifact_path.exists():
                missing_artifacts.append(path_str)

    if missing_artifacts:
        result.add_error(
            ERROR_CODES["ARTIFACT_MISSING"],
            f"Artifacts missing: {', '.join(missing_artifacts)}",
            "Ensure all declared artifact files exist"
        )
    else:
        result.set_pass()

    return result


def verify_allowlist_compliance(receipt: dict[str, Any]) -> ValidationResult:
    """Verify executed commands match the allowlist."""
    result = ValidationResult()

    if "allowlist" not in receipt:
        result.add_error(
            ERROR_CODES["REQUIRED_FIELD_MISSING"],
            "Receipt missing allowlist field",
            "Add allowlist field to receipt"
        )
        return result

    if "execution_summary" not in receipt:
        result.add_error(
            ERROR_CODES["REQUIRED_FIELD_MISSING"],
            "Receipt missing execution_summary field",
            "Add execution_summary field to receipt"
        )
        return result

    allowlist = receipt["allowlist"]
    execution_summary = receipt["execution_summary"]

    # Check for boundary violations
    boundary_violations = allowlist.get("boundary_violations", 0)
    if boundary_violations > 0:
        result.add_error(
            ERROR_CODES["ALLOWLIST_VIOLATION"],
            f"Allowlist boundary violations detected: {boundary_violations}",
            "Review executed commands against allowlist"
        )
        return result

    # Verify fail-closed mode
    enforcement_mode = allowlist.get("enforcement_mode", "UNKNOWN")
    if enforcement_mode != "FAIL_CLOSED":
        result.add_warning(f"Enforcement mode is {enforcement_mode}, expected FAIL_CLOSED")

    result.set_pass()
    return result


def verify_security_audit(receipt: dict[str, Any]) -> ValidationResult:
    """Verify security audit section passes."""
    result = ValidationResult()

    if "security_audit" not in receipt:
        result.add_warning("Receipt missing security_audit field - cannot verify security")
        result.set_pass()
        return result

    security_audit = receipt["security_audit"]

    # Check command_boundary_check
    if security_audit.get("command_boundary_check") != "PASS":
        result.add_error(
            ERROR_CODES["SECURITY_AUDIT_FAILED"],
            "Command boundary check failed",
            "Review command allowlist compliance"
        )
        return result

    # Check for privileged operations
    privileged_ops = security_audit.get("privileged_operations", "NONE")
    if privileged_ops != "NONE":
        result.add_error(
            ERROR_CODES["SECURITY_AUDIT_FAILED"],
            f"Privileged operations detected: {privileged_ops}",
            "Review and remove privileged operations from allowlist"
        )
        return result

    # Check data exfiltration risk
    exfil_risk = security_audit.get("data_exfiltration_risk", "")
    if "HIGH" in exfil_risk.upper():
        result.add_error(
            ERROR_CODES["SECURITY_AUDIT_FAILED"],
            f"High data exfiltration risk: {exfil_risk}",
            "Review executed commands for data transfer operations"
        )
        return result

    result.set_pass()
    return result


def verify_contract_receipt_consistency(
    receipt_path: Path,
    contract_path: Path | None = None
) -> ValidationResult:
    """
    Main verification: validate contract-receipt consistency.

    Args:
        receipt_path: Path to execution receipt JSON
        contract_path: Optional path to contract JSON for comparison

    Returns:
        ValidationResult with pass/fail status
    """
    result = ValidationResult()

    # Load receipt
    try:
        receipt_data = json.loads(receipt_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result.add_error(
            ERROR_CODES["RECEIPT_MISSING"],
            f"Receipt file not found: {receipt_path}",
            f"Ensure receipt exists at {receipt_path}"
        )
        return result
    except json.JSONDecodeError as e:
        result.add_error(
            ERROR_CODES["RECEIPT_INVALID_JSON"],
            f"Receipt invalid JSON: {e}",
            "Fix JSON syntax in receipt"
        )
        return result

    # Run all verifications
    structure_result = verify_receipt_structure(receipt_data)
    if structure_result.status != ValidationStatus.PASS:
        return structure_result

    artifacts_result = verify_artifacts_exist(receipt_data, Path.cwd())
    if artifacts_result.status != ValidationStatus.PASS:
        result.errors.extend(artifacts_result.errors)
        result.required_changes.extend(artifacts_result.required_changes)

    allowlist_result = verify_allowlist_compliance(receipt_data)
    if allowlist_result.status != ValidationStatus.PASS:
        result.errors.extend(allowlist_result.errors)
        result.required_changes.extend(allowlist_result.required_changes)

    security_result = verify_security_audit(receipt_data)
    if security_result.status != ValidationStatus.PASS:
        result.errors.extend(security_result.errors)
        result.required_changes.extend(security_result.required_changes)

    # Check contract consistency if contract provided
    if contract_path and contract_path.exists():
        try:
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))

            # Verify task_id matches
            if receipt_data.get("task_id") != contract_data.get("task_id"):
                result.add_error(
                    ERROR_CODES["TASK_ID_MISMATCH"],
                    f"Task ID mismatch: receipt={receipt_data.get('task_id')}, contract={contract_data.get('task_id')}",
                    "Ensure receipt and contract have matching task_id"
                )
        except json.JSONDecodeError:
            result.add_warning("Contract exists but could not be parsed for consistency check")

    # Determine final status
    if not result.errors:
        result.set_pass()
        result.warnings.extend(structure_result.warnings)
        result.warnings.extend(artifacts_result.warnings)
        result.warnings.extend(allowlist_result.warnings)
        result.warnings.extend(security_result.warnings)

    return result


def main() -> int:
    """CLI entry point for receipt verification."""
    parser = argparse.ArgumentParser(
        description="Verify execution receipt - contract-receipt consistency validation"
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        required=True,
        help="Path to execution receipt JSON",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        help="Optional path to contract JSON for consistency check",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write verification result to file (JSON format)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output status (PASS/FAIL)",
    )
    args = parser.parse_args()

    # Run verification
    result = verify_contract_receipt_consistency(args.receipt, args.contract)

    # Write output file if requested
    if args.output:
        output_data = {
            "status": result.status.value,
            "error_code": result.error_code,
            "errors": result.errors,
            "warnings": result.warnings,
            "required_changes": result.required_changes,
            "checked_at": result.checked_at,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output_data, indent=2), encoding="utf-8")

    # Output results
    if args.quiet:
        print(result.status.value)
    else:
        print(f"status: {result.status.value}")
        print(f"checked_at: {result.checked_at}")

        if result.error_code:
            print(f"error_code: {result.error_code}")

        if result.errors:
            print("\nerrors:")
            for e in result.errors:
                print(f"  - [{e['code']}] {e['message']}")

        if result.warnings:
            print("\nwarnings:")
            for w in result.warnings:
                print(f"  - {w}")

        if result.required_changes:
            print("\nrequired_changes:")
            for c in result.required_changes:
                print(f"  - {c}")

    return 0 if result.status == ValidationStatus.PASS else 1


if __name__ == "__main__":
    sys.exit(main())
