#!/usr/bin/env python3
"""
PR2-T1: Delivery Completeness Gate Validation

Validates that all required delivery items are present:
- Blueprint (contracts/dsl/*.yml)
- Skill (skills/*/)
- n8n (workflows/**/*.json)
- Evidence (artifacts/*/)
- AuditPack (audit_pack/*.json)
- Permit (permits/*/*.json)

Missing any item => FAIL with missing_items list.

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md

T1-B Enhancement: Added structured logging and exception handling for observability.
Maintains fail-closed semantics - any exception results in FAIL status.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict
import uuid


# Error codes per v0-L5 specification
ERROR_CODES = {
    "BLUEPRINT_MISSING": "SF_DELIVERY_BLUEPRINT_MISSING",
    "SKILL_MISSING": "SF_DELIVERY_SKILL_MISSING",
    "N8N_MISSING": "SF_DELIVERY_N8N_MISSING",
    "EVIDENCE_MISSING": "SF_DELIVERY_EVIDENCE_MISSING",
    "AUDIT_PACK_MISSING": "SF_DELIVERY_AUDIT_PACK_MISSING",
    "PERMIT_MISSING": "SF_DELIVERY_PERMIT_MISSING",
    "DELIVERY_INCOMPLETE": "SF_DELIVERY_INCOMPLETE",
    "VALIDATOR_CRASH": "SF_DELIVERY_VALIDATOR_CRASH",
    "PATH_ACCESS_ERROR": "SF_DELIVERY_PATH_ACCESS_ERROR",
    "UNEXPECTED_ERROR": "SF_DELIVERY_UNEXPECTED_ERROR",
}


# Structured logging setup
def setup_structured_logging(log_dir: Path | None = None) -> logging.Logger:
    """Setup structured logging with JSON output to file."""
    logger = logging.getLogger("delivery_validator")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers = []

    # Console handler with readable format
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with JSON format if log_dir specified
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"delivery_validator_{datetime.now(UTC).strftime('%Y%m%d')}.jsonl"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        # Use JSON format for machine-readable logs
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def log_structured(
    logger: logging.Logger,
    level: str,
    event_type: str,
    execution_id: str,
    **kwargs: Any
) -> None:
    """Log structured event as JSON."""
    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": event_type,
        "execution_id": execution_id,
        **kwargs,
    }

    # Log to file as JSON
    json_log = json.dumps(log_entry, ensure_ascii=False)
    logger.debug(json_log)

    # Log to console for visibility
    if level.upper() == "ERROR":
        logger.error(f"[{event_type}] {json_log}")
    elif level.upper() == "WARNING":
        logger.warning(f"[{event_type}] {json_log}")
    else:
        logger.info(f"[{event_type}] {json_log}")


class DeliveryCheckResult(TypedDict):
    """Machine-readable delivery check result."""
    status: str  # "PASS" or "FAIL"
    error_code: str | None
    error_message: str | None
    missing_items: list[dict[str, Any]]  # Changed to Any to support error field
    present_items: list[dict[str, str]]
    required_changes: list[str]
    checked_at: str
    base_path: str
    execution_id: str
    log_file: str | None
    exception_details: dict[str, Any] | None


def check_item_exists(
    base_path: Path,
    category: str,
    pattern: str,
    required: bool = True,
    logger: logging.Logger | None = None,
    execution_id: str = "",
) -> dict[str, str | bool]:
    """
    Check if delivery item exists.

    Returns dict with category, path, found status, and required flag.

    Exceptions are caught and logged, but re-raised to maintain fail-closed.
    """
    try:
        matching_files = list(base_path.glob(pattern))
        found = len(matching_files) > 0

        if logger:
            log_structured(
                logger,
                "INFO",
                "item_check",
                execution_id,
                category=category,
                pattern=pattern,
                found=found,
                required=required,
                matching_count=len(matching_files),
            )

        return {
            "category": category,
            "pattern": pattern,
            "found": found,
            "required": required,
            "path": str(matching_files[0]) if found and matching_files else f"{pattern} (not found)",
        }
    except PermissionError as e:
        if logger:
            log_structured(
                logger,
                "ERROR",
                "permission_error",
                execution_id,
                category=category,
                pattern=pattern,
                error=str(e),
                base_path=str(base_path),
            )
        raise  # Re-raise to maintain fail-closed
    except Exception as e:
        if logger:
            log_structured(
                logger,
                "ERROR",
                "unexpected_error",
                execution_id,
                category=category,
                pattern=pattern,
                error=type(e).__name__,
                error_message=str(e),
                traceback=traceback.format_exc(),
            )
        raise  # Re-raise to maintain fail-closed


def validate_delivery_completeness(
    base_path: Path,
    allow_partial: bool = False,
    execution_id: str = "",
    logger: logging.Logger | None = None,
    log_dir: Path | None = None,
) -> DeliveryCheckResult:
    """
    Validate delivery completeness - all required items must be present.

    Args:
        base_path: Base path to check for delivery items
        allow_partial: If True, missing non-required items won't cause FAIL
        execution_id: Unique execution ID for tracing
        logger: Logger instance for structured logging
        log_dir: Directory for log files

    Returns:
        Machine-readable result dict with status and missing items.

    IMPORTANT: This function maintains fail-closed semantics.
        Any exception results in status="FAIL" with error details.
    """
    if not execution_id:
        execution_id = str(uuid.uuid4())

    if not logger:
        logger = setup_structured_logging(log_dir)

    log_file = None
    if log_dir:
        log_file = str(log_dir / f"delivery_validator_{datetime.now(UTC).strftime('%Y%m%d')}.jsonl")

    result: DeliveryCheckResult = {
        "status": "FAIL",  # Default to FAIL (fail-closed)
        "error_code": None,
        "error_message": None,
        "missing_items": [],
        "present_items": [],
        "required_changes": [],
        "checked_at": datetime.now(UTC).isoformat(),
        "base_path": str(base_path),
        "execution_id": execution_id,
        "log_file": log_file,
        "exception_details": None,
    }

    log_structured(
        logger,
        "INFO",
        "validation_start",
        execution_id,
        base_path=str(base_path),
        allow_partial=allow_partial,
    )

    try:
        # Validate base path exists
        if not base_path.exists():
            error_msg = f"Base path does not exist: {base_path}"
            log_structured(
                logger,
                "ERROR",
                "path_not_found",
                execution_id,
                base_path=str(base_path),
                error=error_msg,
            )
            result["error_code"] = ERROR_CODES["PATH_ACCESS_ERROR"]
            result["error_message"] = error_msg
            result["exception_details"] = {
                "error_type": "PathNotFoundError",
                "error_message": error_msg,
                "base_path": str(base_path),
            }
            return result  # FAIL status (fail-closed)

        # Define required delivery items per PR2 spec
        # Each item is: (category, glob_pattern, required)
        delivery_items = [
            # 1) Blueprint - contracts/dsl/*.yml
            ("Blueprint", "contracts/dsl/*.yml", True),

            # 2) Skill - skills/*/
            ("Skill", "skills/*/", True),

            # 3) n8n - workflows/**/*.json
            ("n8n", "workflows/**/*.json", True),

            # 4) Evidence - artifacts/*/
            ("Evidence", "artifacts/*/", True),

            # 5) AuditPack - audit_pack/*.json
            ("AuditPack", "audit_pack/*.json", True),

            # 6) Permit - permits/*/*.json (nested structure)
            ("Permit", "permits/*/*.json", True),
        ]

        missing_required = []

        for category, pattern, required in delivery_items:
            try:
                check = check_item_exists(
                    base_path, category, pattern, required, logger, execution_id
                )

                if check["found"]:
                    result["present_items"].append({
                        "category": category,
                        "path": check["path"],
                    })
                else:
                    result["missing_items"].append({
                        "category": category,
                        "pattern": pattern,
                    })
                    result["required_changes"].append(
                        f"add required delivery item: {category} at pattern {pattern}"
                    )
                    if required:
                        missing_required.append(category)
            except Exception as e:
                # Individual item check failed - log and continue
                # This allows us to report ALL issues, not just the first one
                error_type = type(e).__name__
                log_structured(
                    logger,
                    "ERROR",
                    "item_check_failed",
                    execution_id,
                    category=category,
                    pattern=pattern,
                    error_type=error_type,
                    error_message=str(e),
                    traceback=traceback.format_exc(),
                )

                # Treat failed checks as missing (fail-closed)
                result["missing_items"].append({
                    "category": category,
                    "pattern": pattern,
                    "error": str(error_type),
                })
                result["required_changes"].append(
                    f"check failed for {category} at {pattern}: {error_type} - {str(e)}"
                )
                if required:
                    missing_required.append(category)

        # Determine overall status
        if missing_required:
            # Use specific error code for first missing required item
            first_missing = missing_required[0].upper()
            error_key = f"{first_missing}_MISSING"
            result["error_code"] = ERROR_CODES.get(
                error_key,
                ERROR_CODES["DELIVERY_INCOMPLETE"]
            )
        elif result["missing_items"]:
            # Non-required items missing (if allow_partial is False, still fail)
            if not allow_partial:
                result["error_code"] = ERROR_CODES["DELIVERY_INCOMPLETE"]
            else:
                result["status"] = "PASS"
        else:
            result["status"] = "PASS"

        log_structured(
            logger,
            "INFO" if result["status"] == "PASS" else "WARNING",
            "validation_complete",
            execution_id,
            status=result["status"],
            error_code=result["error_code"],
            present_count=len(result["present_items"]),
            missing_count=len(result["missing_items"]),
        )

        return result

    except Exception as e:
        # Catch-all for unexpected errors during validation
        # This maintains fail-closed while providing observability
        error_type = type(e).__name__
        error_msg = f"Unexpected error during validation: {error_type} - {str(e)}"

        log_structured(
            logger,
            "ERROR",
            "validator_crash",
            execution_id,
            error_type=error_type,
            error_message=str(e),
            traceback=traceback.format_exc(),
            base_path=str(base_path),
        )

        result["error_code"] = ERROR_CODES["VALIDATOR_CRASH"]
        result["error_message"] = error_msg
        result["exception_details"] = {
            "error_type": error_type,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "base_path": str(base_path),
        }

        # Return FAIL status (fail-closed)
        return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate delivery completeness - all required items must be present"
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Base path to check for delivery items (default: current directory)",
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
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Allow partial delivery (non-required items missing won't cause FAIL)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("logs/delivery_validator"),
        help="Directory for structured log files (default: logs/delivery_validator)",
    )
    parser.add_argument(
        "--execution-id",
        type=str,
        default="",
        help="Custom execution ID for tracing (default: auto-generated UUID)",
    )
    args = parser.parse_args()

    # Generate execution ID if not provided
    execution_id = args.execution_id or str(uuid.uuid4())

    # Setup structured logging
    logger = setup_structured_logging(args.log_dir)

    # Run validation
    result = validate_delivery_completeness(
        args.base_path,
        args.allow_partial,
        execution_id,
        logger,
        args.log_dir,
    )

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
        print(f"execution_id: {result['execution_id']}")
        print(f"base_path: {result['base_path']}")
        print(f"checked_at: {result['checked_at']}")

        if result["log_file"]:
            print(f"log_file: {result['log_file']}")

        if result["error_code"]:
            print(f"error_code: {result['error_code']}")

        if result["error_message"]:
            print(f"error_message: {result['error_message']}")

        if result["present_items"]:
            print("\npresent_items:")
            for item in result["present_items"]:
                print(f"  - {item['category']}: {item['path']}")

        if result["missing_items"]:
            print("\nmissing_items:")
            for item in result["missing_items"]:
                if "error" in item:
                    print(f"  - {item['category']}: {item['pattern']} (ERROR: {item['error']})")
                else:
                    print(f"  - {item['category']}: {item['pattern']}")
        if result["required_changes"]:
            print("\nrequired_changes:")
            for change in result["required_changes"]:
                print(f"  - {change}")

        if result["exception_details"]:
            print("\nexception_details:")
            print(f"  error_type: {result['exception_details']['error_type']}")
            print(f"  error_message: {result['exception_details']['error_message']}")
            if "traceback" in result["exception_details"]:
                print(f"  traceback: {result['exception_details']['traceback'][:200]}...")

    # Exit code: 0 = PASS, 1 = FAIL
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
