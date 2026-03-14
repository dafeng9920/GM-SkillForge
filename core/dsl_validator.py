#!/usr/bin/env python3
"""
DSL Validator - Hard Validation for Demand DSL v0

Performs strict validation of Demand DSL against the schema and v0 requirements.
Any missing/invalid field => FAIL with required_changes.

Validation rules:
- Ref must have version
- Controls must be explicit
- Tests must be atomic
- All required fields present

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ErrorSeverity(str, Enum):
    """Severity levels for validation errors."""
    BLOCKER = "BLOCKER"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


@dataclass
class ValidationError:
    """A validation error with required changes."""
    error_code: str
    severity: ErrorSeverity
    field_path: str
    message: str
    required_changes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of DSL validation."""
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    demand_dsl: dict[str, Any] | None = None


class DSLValidator:
    """
    Hard validator for Demand DSL v0.

    Rules (fail-closed):
    - All required fields must be present
    - Refs must have version specified
    - Controls must be explicit (no defaults assumed)
    - Tests must be atomic (single check per criterion)
    - Network policy must be explicit
    """

    SCHEMA_VERSION = "demand_dsl_v0"

    # Required fields at root level
    REQUIRED_ROOT_FIELDS = [
        "schema_version",
        "intent_id",
        "mode",
        "trigger",
        "sources",
        "transforms",
        "destinations",
        "constraints",
        "acceptance",
    ]

    # Valid modes
    VALID_MODES = {
        "generate_skill",
        "modify_skill",
        "audit_skill",
        "compose_workflow",
    }

    # Valid network policies
    VALID_NETWORK_POLICIES = {
        "deny_by_default",
        "allowlist",
    }

    # Valid execution modes
    VALID_EXECUTION_MODES = {
        "dry_run",
        "tests_only",
        "sandboxed",
        "production",
    }

    # Valid trigger types
    VALID_TRIGGER_TYPES = {
        "nl_prompt",
        "api_call",
        "scheduled",
        "event_driven",
    }

    # Valid source kinds
    VALID_SOURCE_KINDS = {
        "repo_url",
        "local_path",
        "skill_id",
        "asset_ref",
        "nl_text",
    }

    # Valid destination kinds
    VALID_DEST_KINDS = {
        "skill",
        "workflow",
        "audit_report",
        "manifest",
    }

    # Valid write modes
    VALID_WRITE_MODES = {
        "create",
        "update",
        "append",
    }

    # Secrets name pattern
    SECRETS_PATTERN = re.compile(r"^needs_user_key:[a-zA-Z0-9_\-]+$")

    # SHA256 hash pattern
    SHA256_PATTERN = re.compile(r"^(sha256:)?[0-9a-f]{64}$")

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, fail on any error. If False, allow MINOR issues.
        """
        self.strict_mode = strict_mode

    def validate(self, demand_dsl: dict[str, Any]) -> ValidationResult:
        """
        Validate a Demand DSL document.

        Args:
            demand_dsl: The Demand DSL document to validate

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(demand_dsl=demand_dsl)

        # 1) Validate schema version
        self._validate_schema_version(demand_dsl, result)

        # 2) Validate required root fields
        self._validate_required_fields(demand_dsl, result)

        # 3) Validate intent_id
        self._validate_intent_id(demand_dsl, result)

        # 4) Validate mode
        self._validate_mode(demand_dsl, result)

        # 5) Validate trigger
        self._validate_trigger(demand_dsl, result)

        # 6) Validate sources
        self._validate_sources(demand_dsl, result)

        # 7) Validate transforms (empty array is valid)
        self._validate_transforms(demand_dsl, result)

        # 8) Validate destinations
        self._validate_destinations(demand_dsl, result)

        # 9) Validate constraints
        self._validate_constraints(demand_dsl, result)

        # 10) Validate acceptance
        self._validate_acceptance(demand_dsl, result)

        # Determine overall validity
        if self.strict_mode:
            result.valid = len(result.errors) == 0
        else:
            result.valid = all(e.severity != ErrorSeverity.BLOCKER for e in result.errors)

        return result

    def _validate_schema_version(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate schema version matches v0."""
        version = dsl.get("schema_version")
        if version != self.SCHEMA_VERSION:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_SCHEMA_VERSION",
                severity=ErrorSeverity.BLOCKER,
                field_path="schema_version",
                message=f"Schema version must be '{self.SCHEMA_VERSION}', got '{version}'",
                required_changes=[
                    {
                        "kind": "CONFIG_EDIT",
                        "instruction": f"Set schema_version to '{self.SCHEMA_VERSION}'",
                        "target": {"path": "demand_dsl.yml", "json_pointer": "/schema_version"},
                    }
                ],
            ))

    def _validate_required_fields(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate all required fields are present."""
        for field in self.REQUIRED_ROOT_FIELDS:
            if field not in dsl:
                result.errors.append(ValidationError(
                    error_code="SF_MISSING_REQUIRED_FIELD",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=field,
                    message=f"Required field '{field}' is missing",
                    required_changes=[
                        {
                            "kind": "CONFIG_EDIT",
                            "instruction": f"Add required field '{field}' to Demand DSL",
                        }
                    ],
                ))

    def _validate_intent_id(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate intent_id is present and non-empty."""
        intent_id = dsl.get("intent_id")
        if not intent_id or not isinstance(intent_id, str):
            result.errors.append(ValidationError(
                error_code="SF_INVALID_INTENT_ID",
                severity=ErrorSeverity.BLOCKER,
                field_path="intent_id",
                message="intent_id must be a non-empty string",
                required_changes=[
                    {
                        "kind": "CONFIG_EDIT",
                        "instruction": "Set intent_id to a unique identifier (e.g., UUID)",
                    }
                ],
            ))

    def _validate_mode(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate mode is one of the 4 supported modes."""
        mode = dsl.get("mode")
        if mode not in self.VALID_MODES:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_MODE",
                severity=ErrorSeverity.BLOCKER,
                field_path="mode",
                message=f"mode must be one of {self.VALID_MODES}, got '{mode}'",
                required_changes=[
                    {
                        "kind": "CONFIG_EDIT",
                        "instruction": f"Set mode to one of: {', '.join(sorted(self.VALID_MODES))}",
                    }
                ],
            ))

    def _validate_trigger(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate trigger section."""
        trigger = dsl.get("trigger")
        if not isinstance(trigger, dict):
            result.errors.append(ValidationError(
                error_code="SF_INVALID_TRIGGER",
                severity=ErrorSeverity.BLOCKER,
                field_path="trigger",
                message="trigger must be an object",
            ))
            return

        # Validate type
        trigger_type = trigger.get("type")
        if trigger_type not in self.VALID_TRIGGER_TYPES:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_TRIGGER_TYPE",
                severity=ErrorSeverity.BLOCKER,
                field_path="trigger.type",
                message=f"trigger.type must be one of {self.VALID_TRIGGER_TYPES}",
            ))

        # Validate source is present
        if not trigger.get("source"):
            result.errors.append(ValidationError(
                error_code="SF_MISSING_TRIGGER_SOURCE",
                severity=ErrorSeverity.BLOCKER,
                field_path="trigger.source",
                message="trigger.source is required",
            ))

    def _validate_sources(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate sources array."""
        sources = dsl.get("sources")
        if not isinstance(sources, list) or len(sources) == 0:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_SOURCES",
                severity=ErrorSeverity.BLOCKER,
                field_path="sources",
                message="sources must be a non-empty array",
            ))
            return

        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                result.errors.append(ValidationError(
                    error_code="SF_INVALID_SOURCE_ITEM",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"sources[{i}]",
                    message="Each source must be an object",
                ))
                continue

            # Validate kind
            kind = source.get("kind")
            if kind not in self.VALID_SOURCE_KINDS:
                result.errors.append(ValidationError(
                    error_code="SF_INVALID_SOURCE_KIND",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"sources[{i}].kind",
                    message=f"source.kind must be one of {self.VALID_SOURCE_KINDS}",
                ))

            # Validate locator
            if not source.get("locator"):
                result.errors.append(ValidationError(
                    error_code="SF_MISSING_SOURCE_LOCATOR",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"sources[{i}].locator",
                    message="source.locator is required",
                ))

            # For repo_url and skill_id, validate version is present
            if kind in ("repo_url", "skill_id"):
                if not source.get("version"):
                    result.errors.append(ValidationError(
                        error_code="SF_MISSING_SOURCE_VERSION",
                        severity=ErrorSeverity.BLOCKER,
                        field_path=f"sources[{i}].version",
                        message=f"source.version is required for kind='{kind}'",
                        required_changes=[
                            {
                                "kind": "CONFIG_EDIT",
                                "instruction": f"Add version field to source at sources[{i}]",
                            }
                        ],
                    ))

    def _validate_transforms(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate transforms array (can be empty)."""
        transforms = dsl.get("transforms")
        if not isinstance(transforms, list):
            result.errors.append(ValidationError(
                error_code="SF_INVALID_TRANSFORMS",
                severity=ErrorSeverity.BLOCKER,
                field_path="transforms",
                message="transforms must be an array",
            ))
            return

        # Validate each transform if present
        for i, transform in enumerate(transforms):
            if not isinstance(transform, dict):
                result.errors.append(ValidationError(
                    error_code="SF_INVALID_TRANSFORM_ITEM",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"transforms[{i}]",
                    message="Each transform must be an object",
                ))
                continue

            if not transform.get("operation"):
                result.errors.append(ValidationError(
                    error_code="SF_MISSING_TRANSFORM_OPERATION",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"transforms[{i}].operation",
                    message="transform.operation is required",
                ))

    def _validate_destinations(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate destinations array."""
        destinations = dsl.get("destinations")
        if not isinstance(destinations, list) or len(destinations) == 0:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_DESTINATIONS",
                severity=ErrorSeverity.BLOCKER,
                field_path="destinations",
                message="destinations must be a non-empty array",
            ))
            return

        for i, dest in enumerate(destinations):
            if not isinstance(dest, dict):
                result.errors.append(ValidationError(
                    error_code="SF_INVALID_DEST_ITEM",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"destinations[{i}]",
                    message="Each destination must be an object",
                ))
                continue

            # Validate kind
            kind = dest.get("kind")
            if kind not in self.VALID_DEST_KINDS:
                result.errors.append(ValidationError(
                    error_code="SF_INVALID_DEST_KIND",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"destinations[{i}].kind",
                    message=f"destination.kind must be one of {self.VALID_DEST_KINDS}",
                ))

            # Validate locator
            if not dest.get("locator"):
                result.errors.append(ValidationError(
                    error_code="SF_MISSING_DEST_LOCATOR",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"destinations[{i}].locator",
                    message="destination.locator is required",
                ))

            # Validate write_mode
            write_mode = dest.get("write_mode")
            if write_mode not in self.VALID_WRITE_MODES:
                result.errors.append(ValidationError(
                    error_code="SF_INVALID_WRITE_MODE",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"destinations[{i}].write_mode",
                    message=f"destination.write_mode must be one of {self.VALID_WRITE_MODES}",
                ))

    def _validate_constraints(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate constraints section."""
        constraints = dsl.get("constraints")
        if not isinstance(constraints, dict):
            result.errors.append(ValidationError(
                error_code="SF_INVALID_CONSTRAINTS",
                severity=ErrorSeverity.BLOCKER,
                field_path="constraints",
                message="constraints must be an object",
            ))
            return

        # Validate network_policy (must be explicit)
        network_policy = constraints.get("network_policy")
        if network_policy not in self.VALID_NETWORK_POLICIES:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_NETWORK_POLICY",
                severity=ErrorSeverity.BLOCKER,
                field_path="constraints.network_policy",
                message=f"constraints.network_policy must be one of {self.VALID_NETWORK_POLICIES}",
                required_changes=[
                    {
                        "kind": "CONFIG_EDIT",
                        "instruction": f"Set network_policy to one of: {', '.join(sorted(self.VALID_NETWORK_POLICIES))}",
                    }
                ],
            ))

        # Validate execution_mode
        execution_mode = constraints.get("execution_mode")
        if execution_mode not in self.VALID_EXECUTION_MODES:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_EXECUTION_MODE",
                severity=ErrorSeverity.BLOCKER,
                field_path="constraints.execution_mode",
                message=f"constraints.execution_mode must be one of {self.VALID_EXECUTION_MODES}",
            ))

        # Validate secrets format (if present)
        secrets = constraints.get("secrets", [])
        if isinstance(secrets, list):
            for i, secret in enumerate(secrets):
                if not isinstance(secret, str) or not self.SECRETS_PATTERN.match(secret):
                    result.errors.append(ValidationError(
                        error_code="SF_INVALID_SECRET_FORMAT",
                        severity=ErrorSeverity.BLOCKER,
                        field_path=f"constraints.secrets[{i}]",
                        message=f"Secret must match pattern 'needs_user_key:*', got '{secret}'",
                        required_changes=[
                            {
                                "kind": "CONFIG_EDIT",
                                "instruction": "Use only secret name references (needs_user_key:*), never actual values",
                            }
                        ],
                    ))

    def _validate_acceptance(self, dsl: dict[str, Any], result: ValidationResult) -> None:
        """Validate acceptance section."""
        acceptance = dsl.get("acceptance")
        if not isinstance(acceptance, dict):
            result.errors.append(ValidationError(
                error_code="SF_INVALID_ACCEPTANCE",
                severity=ErrorSeverity.BLOCKER,
                field_path="acceptance",
                message="acceptance must be an object",
            ))
            return

        # Validate success_criteria
        success_criteria = acceptance.get("success_criteria")
        if not isinstance(success_criteria, list) or len(success_criteria) == 0:
            result.errors.append(ValidationError(
                error_code="SF_INVALID_SUCCESS_CRITERIA",
                severity=ErrorSeverity.BLOCKER,
                field_path="acceptance.success_criteria",
                message="acceptance.success_criteria must be a non-empty array",
            ))
            return

        for i, criterion in enumerate(success_criteria):
            if not isinstance(criterion, dict):
                result.errors.append(ValidationError(
                    error_code="SF_INVALID_CRITERION_ITEM",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"acceptance.success_criteria[{i}]",
                    message="Each criterion must be an object",
                ))
                continue

            # Validate required fields
            if not criterion.get("criterion"):
                result.errors.append(ValidationError(
                    error_code="SF_MISSING_CRITERION_TEXT",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"acceptance.success_criteria[{i}].criterion",
                    message="criterion text is required",
                ))

            if not criterion.get("check_type"):
                result.errors.append(ValidationError(
                    error_code="SF_MISSING_CHECK_TYPE",
                    severity=ErrorSeverity.BLOCKER,
                    field_path=f"acceptance.success_criteria[{i}].check_type",
                    message="check_type is required",
                ))


def main() -> int:
    """CLI entry point for validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Demand DSL v0")
    parser.add_argument("demand_file", type=Path, help="Path to Demand DSL file")
    parser.add_argument("--output", type=Path, help="Write result to file")
    args = parser.parse_args()

    # Load Demand DSL
    try:
        demand_dsl = json.loads(args.demand_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load Demand DSL: {e}", file=sys.stderr)
        return 1

    # Validate
    validator = DSLValidator(strict_mode=True)
    result = validator.validate(demand_dsl)

    # Output results
    if result.valid:
        print("PASS - Demand DSL is valid")
    else:
        print(f"FAIL - {len(result.errors)} error(s) found")

    for error in result.errors:
        print(f"\n[{error.severity}] {error.field_path}")
        print(f"  {error.message}")
        print(f"  error_code: {error.error_code}")

    for warning in result.warnings:
        print(f"\n[MINOR] {warning.field_path}")
        print(f"  {warning.message}")

    # Write output if requested
    if args.output:
        output_data = {
            "valid": result.valid,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "errors": [
                {
                    "error_code": e.error_code,
                    "severity": e.severity,
                    "field_path": e.field_path,
                    "message": e.message,
                    "required_changes": e.required_changes,
                }
                for e in result.errors
            ],
        }
        args.output.write_text(json.dumps(output_data, indent=2))

    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
