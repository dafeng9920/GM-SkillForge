"""
Skill Contract Validator - T3 Deliverable

This module implements deterministic validation for skill structure and contracts.
It enforces fail-closed rules for schema compliance, contract consistency,
and input/output field validation.

T3 Scope:
- Schema validation (JSON Schema conformance)
- Contract validation (input/output contract structure)
- Input/output consistency checks
- Required field validation
- Error codes with field paths
- Positive and negative test cases

T3 Hard Constraints:
- No pattern matching logic in validator
- No owner translation logic in validator
- No illegal schema/contract passes validation
- All failures must have error codes, field paths, and fix suggestions

Usage:
    from skillforge.src.contracts.skill_contract_validator import (
        SkillContractValidator,
        ValidationResult,
        ValidationErrorCode
    )

    validator = SkillContractValidator()
    result = validator.validate_skill_spec(normalized_skill_spec)

    if not result.is_valid:
        for failure in result.failures:
            print(f"{failure.code}: {failure.message}")
            print(f"  Field path: {failure.field_path}")
            print(f"  Fix: {failure.suggested_fix}")

Evidence paths:
    - run/<run_id>/validation_report.json
"""
from __future__ import annotations

import json
import re
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional


# ============================================================================
# Error Codes (T3)
# ============================================================================
class ValidationErrorCode:
    """Standard error codes for skill contract validation."""

    # Schema validation errors (E3xx)
    E301_SCHEMA_VALIDATION_FAILED = "E301_SCHEMA_VALIDATION_FAILED"
    E302_REQUIRED_FIELD_MISSING = "E302_REQUIRED_FIELD_MISSING"
    E303_FIELD_TYPE_MISMATCH = "E303_FIELD_TYPE_MISMATCH"
    E304_FIELD_PATTERN_MISMATCH = "E304_FIELD_PATTERN_MISMATCH"
    E305_INVALID_ENUM_VALUE = "E305_INVALID_ENUM_VALUE"
    E306_ARRAY_ITEM_INVALID = "E306_ARRAY_ITEM_INVALID"
    E307_MIN_LENGTH_VIOLATED = "E307_MIN_LENGTH_VIOLATED"
    E308_MAX_LENGTH_VIOLATED = "E308_MAX_LENGTH_VIOLATED"
    E309_MIN_VALUE_VIOLATED = "E309_MIN_VALUE_VIOLATED"
    E310_MAX_VALUE_VIOLATED = "E310_MAX_VALUE_VIOLATED"

    # Contract validation errors (E31x)
    E311_INPUT_CONTRACT_MISSING = "E311_INPUT_CONTRACT_MISSING"
    E312_OUTPUT_CONTRACT_MISSING = "E312_OUTPUT_CONTRACT_MISSING"
    E313_CONTRACT_SCHEMA_TYPE_INVALID = "E313_CONTRACT_SCHEMA_TYPE_INVALID"
    E314_CONTRACT_PROPERTIES_MISSING = "E314_CONTRACT_PROPERTIES_MISSING"
    E315_CONTRACT_REQUIRED_MISSING = "E315_CONTRACT_REQUIRED_MISSING"
    E316_CONTRACT_REQUIRED_NOT_IN_PROPERTIES = "E316_CONTRACT_REQUIRED_NOT_IN_PROPERTIES"

    # Consistency check errors (E32x)
    E321_VERSION_FORMAT_INVALID = "E321_VERSION_FORMAT_INVALID"
    E322_SKILL_ID_FORMAT_INVALID = "E322_SKILL_ID_FORMAT_INVALID"
    E323_SPEC_HASH_FORMAT_INVALID = "E323_SPEC_HASH_FORMAT_INVALID"
    E324_DEPENDENCY_NAME_EMPTY = "E324_DEPENDENCY_NAME_EMPTY"
    E325_DEPENDENCY_SOURCE_INVALID = "E325_DEPENDENCY_SOURCE_INVALID"
    E326_MANIFEST_HASH_INVALID = "E326_MANIFEST_HASH_INVALID"
    E327_DEPENDENCY_COUNT_MISMATCH = "E327_DEPENDENCY_COUNT_MISMATCH"


# ============================================================================
# Validation Failure
# ============================================================================
@dataclass(frozen=True)
class ValidationFailure:
    """A single validation failure with structured information."""

    code: str  # Error code from ValidationErrorCode
    message: str  # Human-readable error message
    field_path: str  # JSON path to the invalid field (e.g., "input_contract.properties.user_id")
    severity: Literal["ERROR", "WARNING"] = "ERROR"
    suggested_fix: Optional[str] = None  # Suggested fix for the issue
    actual_value: Optional[str] = None  # Actual value found (for debugging)
    expected_value: Optional[str] = None  # Expected value (for debugging)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "code": self.code,
            "message": self.message,
            "field_path": self.field_path,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value,
        }


# ============================================================================
# Validation Result
# ============================================================================
@dataclass
class ValidationResult:
    """Result of skill contract validation."""

    is_valid: bool
    failures: list[ValidationFailure] = field(default_factory=list)
    warnings: list[ValidationFailure] = field(default_factory=list)
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validator_version: str = "1.0.0-t3"

    def add_failure(
        self,
        code: str,
        message: str,
        field_path: str,
        suggested_fix: Optional[str] = None,
        actual_value: Optional[str] = None,
        expected_value: Optional[str] = None,
    ) -> None:
        """Add a validation failure."""
        failure = ValidationFailure(
            code=code,
            message=message,
            field_path=field_path,
            severity="ERROR",
            suggested_fix=suggested_fix,
            actual_value=str(actual_value) if actual_value is not None else None,
            expected_value=str(expected_value) if expected_value is not None else None,
        )
        self.failures.append(failure)
        self.is_valid = False

    def add_warning(
        self,
        code: str,
        message: str,
        field_path: str,
        suggested_fix: Optional[str] = None,
    ) -> None:
        """Add a validation warning."""
        warning = ValidationFailure(
            code=code,
            message=message,
            field_path=field_path,
            severity="WARNING",
            suggested_fix=suggested_fix,
        )
        self.warnings.append(warning)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "failures": [f.to_dict() for f in self.failures],
            "warnings": [w.to_dict() for w in self.warnings],
            "validated_at": self.validated_at,
            "validator_version": self.validator_version,
            "failure_count": len(self.failures),
            "warning_count": len(self.warnings),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save validation report to a JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically via temp file
        temp_path = output_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            temp_path.replace(output_path)
        except OSError as e:
            raise IOError(f"Failed to save validation report to {output_path}: {e}")


# ============================================================================
# Schema Validator
# ============================================================================
class SchemaValidator:
    """Validates skill spec against JSON Schema."""

    # Pattern cache
    PATTERNS = {
        "skill_id": re.compile(r"^[a-z0-9_]+-\d+\.\d+\.\d+-[a-f0-9]{8}$"),
        "version": re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$"),
        "sha256": re.compile(r"^[a-f0-9]{64}$"),
        "semver": re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$"),
        "iso8601": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
    }

    ENUMS = {
        "dependency_source": ["import", "from_import", "requirements.txt", "manifest"],
    }

    def __init__(self, schema_path: Optional[str | Path] = None):
        """
        Initialize schema validator.

        Args:
            schema_path: Path to normalized_skill_spec.schema.json
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / "normalized_skill_spec.schema.json"
        self.schema_path = Path(schema_path)

        # Load schema
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

    def validate(self, spec: dict[str, Any], result: ValidationResult) -> None:
        """
        Validate skill spec against schema.

        Args:
            spec: Normalized skill spec as dictionary
            result: ValidationResult to accumulate failures
        """
        # Check required top-level fields
        required_fields = self.schema.get("required", [])
        for field_name in required_fields:
            if field_name not in spec:
                result.add_failure(
                    code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
                    message=f"Required field '{field_name}' is missing",
                    field_path=field_name,
                    suggested_fix=f"Add '{field_name}' to the skill spec",
                )

        # Validate each field
        properties = self.schema.get("properties", {})
        for field_name, field_spec in properties.items():
            if field_name not in spec:
                continue

            field_value = spec[field_name]
            self._validate_field(field_name, field_value, field_spec, result, "")

    def _validate_field(
        self,
        field_name: str,
        field_value: Any,
        field_spec: dict[str, Any],
        result: ValidationResult,
        path_prefix: str,
    ) -> None:
        """Validate a single field against its schema specification."""
        field_path = f"{path_prefix}{field_name}" if path_prefix else field_name
        field_type = field_spec.get("type")

        # Type check
        if not self._check_type(field_value, field_type):
            result.add_failure(
                code=ValidationErrorCode.E303_FIELD_TYPE_MISMATCH,
                message=f"Field '{field_path}' has incorrect type",
                field_path=field_path,
                actual_value=type(field_value).__name__,
                expected_value=field_type,
                suggested_fix=f"Change '{field_path}' to type {field_type}",
            )
            return  # Don't continue validation if type is wrong

        # Pattern check (for strings)
        if field_type == "string" and "pattern" in field_spec:
            pattern_str = field_spec["pattern"]
            pattern = re.compile(pattern_str)
            if not pattern.match(str(field_value)):
                result.add_failure(
                    code=ValidationErrorCode.E304_FIELD_PATTERN_MISMATCH,
                    message=f"Field '{field_path}' does not match required pattern",
                    field_path=field_path,
                    actual_value=str(field_value),
                    expected_value=pattern_str,
                    suggested_fix=f"Ensure '{field_path}' matches pattern: {pattern_str}",
                )

        # Enum check
        if "enum" in field_spec:
            enum_values = field_spec["enum"]
            if field_value not in enum_values:
                result.add_failure(
                    code=ValidationErrorCode.E305_INVALID_ENUM_VALUE,
                    message=f"Field '{field_path}' has invalid enum value",
                    field_path=field_path,
                    actual_value=str(field_value),
                    expected_value=f"One of {enum_values}",
                    suggested_fix=f"Set '{field_path}' to one of: {enum_values}",
                )

        # Length checks (for strings and arrays)
        if field_type == "string":
            if "minLength" in field_spec and len(str(field_value)) < field_spec["minLength"]:
                result.add_failure(
                    code=ValidationErrorCode.E307_MIN_LENGTH_VIOLATED,
                    message=f"Field '{field_path}' is too short",
                    field_path=field_path,
                    actual_value=str(len(field_value)),
                    expected_value=f">= {field_spec['minLength']}",
                    suggested_fix=f"Ensure '{field_path}' has at least {field_spec['minLength']} characters",
                )
            if "maxLength" in field_spec and len(str(field_value)) > field_spec["maxLength"]:
                result.add_failure(
                    code=ValidationErrorCode.E308_MAX_LENGTH_VIOLATED,
                    message=f"Field '{field_path}' is too long",
                    field_path=field_path,
                    actual_value=str(len(field_value)),
                    expected_value=f"<= {field_spec['maxLength']}",
                    suggested_fix=f"Ensure '{field_path}' has at most {field_spec['maxLength']} characters",
                )

        # Numeric range checks
        if field_type == "integer":
            if "minimum" in field_spec and field_value < field_spec["minimum"]:
                result.add_failure(
                    code=ValidationErrorCode.E309_MIN_VALUE_VIOLATED,
                    message=f"Field '{field_path}' is below minimum",
                    field_path=field_path,
                    actual_value=str(field_value),
                    expected_value=f">= {field_spec['minimum']}",
                    suggested_fix=f"Ensure '{field_path}' is at least {field_spec['minimum']}",
                )
            if "maximum" in field_spec and field_value > field_spec["maximum"]:
                result.add_failure(
                    code=ValidationErrorCode.E310_MAX_VALUE_VIOLATED,
                    message=f"Field '{field_path}' exceeds maximum",
                    field_path=field_path,
                    actual_value=str(field_value),
                    expected_value=f"<= {field_spec['maximum']}",
                    suggested_fix=f"Ensure '{field_path}' is at most {field_spec['maximum']}",
                )

        # Array item validation
        if field_type == "array" and isinstance(field_value, list):
            items_spec = field_spec.get("items", {})
            for i, item in enumerate(field_value):
                if isinstance(items_spec, dict):
                    item_path = f"{field_path}[{i}]"
                    if isinstance(item, dict):
                        # Validate object items against properties
                        item_required = items_spec.get("required", [])
                        for req_field in item_required:
                            if req_field not in item:
                                result.add_failure(
                                    code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
                                    message=f"Array item '{item_path}' missing required field '{req_field}'",
                                    field_path=f"{item_path}.{req_field}",
                                    suggested_fix=f"Add '{req_field}' to array item at index {i}",
                                )

        # Object property validation
        if field_type == "object" and isinstance(field_value, dict):
            nested_props = field_spec.get("properties", {})
            nested_required = field_spec.get("required", [])

            # Check required nested fields
            for req_field in nested_required:
                if req_field not in field_value:
                    result.add_failure(
                        code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
                        message=f"Object '{field_path}' missing required field '{req_field}'",
                        field_path=f"{field_path}.{req_field}",
                        suggested_fix=f"Add '{req_field}' to object at '{field_path}'",
                    )

            # Validate nested properties
            for prop_name, prop_value in field_value.items():
                if prop_name in nested_props:
                    self._validate_field(
                        prop_name,
                        prop_value,
                        nested_props[prop_name],
                        result,
                        f"{field_path}.",
                    )

    def _check_type(self, value: Any, expected_type: str | list) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        # Handle union types like ["string", "null"]
        if isinstance(expected_type, list):
            return any(self._check_type(value, t) for t in expected_type)

        if expected_type in type_map:
            py_type = type_map[expected_type]
            return isinstance(value, py_type)

        return True


# ============================================================================
# Contract Validator
# ============================================================================
class ContractValidator:
    """Validates input/output contract structure and consistency."""

    VALID_SCHEMA_TYPES = ["object", "array", "string", "number", "integer", "boolean", "null"]

    def validate_contracts(self, spec: dict[str, Any], result: ValidationResult) -> None:
        """
        Validate input and output contracts.

        Args:
            spec: Normalized skill spec as dictionary
            result: ValidationResult to accumulate failures
        """
        # Validate input contract
        if "input_contract" not in spec:
            result.add_failure(
                code=ValidationErrorCode.E311_INPUT_CONTRACT_MISSING,
                message="Input contract is missing",
                field_path="input_contract",
                suggested_fix="Add input_contract to the skill spec with schema_type, properties, and required fields",
            )
        else:
            self._validate_contract("input_contract", spec["input_contract"], result)

        # Validate output contract
        if "output_contract" not in spec:
            result.add_failure(
                code=ValidationErrorCode.E312_OUTPUT_CONTRACT_MISSING,
                message="Output contract is missing",
                field_path="output_contract",
                suggested_fix="Add output_contract to the skill spec with schema_type, properties, and required fields",
            )
        else:
            self._validate_contract("output_contract", spec["output_contract"], result)

    def _validate_contract(
        self, contract_name: str, contract: Any, result: ValidationResult
    ) -> None:
        """Validate a single contract (input or output)."""
        base_path = contract_name

        # Check if contract is a dict
        if not isinstance(contract, dict):
            result.add_failure(
                code=ValidationErrorCode.E303_FIELD_TYPE_MISMATCH,
                message=f"Contract '{contract_name}' must be an object",
                field_path=base_path,
                actual_value=type(contract).__name__,
                expected_value="object",
                suggested_fix=f"Ensure {contract_name} is an object with schema_type, properties, and required fields",
            )
            return  # Don't continue validation if type is wrong

        # Check required contract fields
        required_fields = ["schema_type", "properties", "required"]
        for field in required_fields:
            if field not in contract:
                result.add_failure(
                    code=getattr(ValidationErrorCode, f"E31{required_fields.index(field) + 3}_CONTRACT_{field.upper()}_MISSING"),
                    message=f"Contract '{contract_name}' missing required field '{field}'",
                    field_path=f"{base_path}.{field}",
                    suggested_fix=f"Add '{field}' to {contract_name}",
                )

        # Validate schema_type
        if "schema_type" in contract:
            schema_type = contract["schema_type"]
            if schema_type not in self.VALID_SCHEMA_TYPES:
                result.add_failure(
                    code=ValidationErrorCode.E313_CONTRACT_SCHEMA_TYPE_INVALID,
                    message=f"Contract '{contract_name}' has invalid schema_type",
                    field_path=f"{base_path}.schema_type",
                    actual_value=schema_type,
                    expected_value=f"One of {self.VALID_SCHEMA_TYPES}",
                    suggested_fix=f"Set schema_type to one of: {self.VALID_SCHEMA_TYPES}",
                )

        # Validate that all required fields exist in properties
        if "required" in contract and "properties" in contract:
            properties = contract["properties"]
            required = contract["required"]

            for req_field in required:
                if req_field not in properties:
                    result.add_failure(
                        code=ValidationErrorCode.E316_CONTRACT_REQUIRED_NOT_IN_PROPERTIES,
                        message=f"Required field '{req_field}' is not defined in properties",
                        field_path=f"{base_path}.required",
                        suggested_fix=f"Add '{req_field}' to {contract_name}.properties or remove from required list",
                    )


# ============================================================================
# Consistency Validator
# ============================================================================
class ConsistencyValidator:
    """Validates internal consistency of skill spec."""

    PATTERNS = {
        "version": re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$"),
        "skill_id": re.compile(r"^[a-z0-9_]+-\d+\.\d+\.\d+-[a-f0-9]{8}$"),
        "sha256": re.compile(r"^[a-f0-9]{64}$"),
        "iso8601": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
    }

    def validate_consistency(self, spec: dict[str, Any], result: ValidationResult) -> None:
        """
        Validate internal consistency of skill spec.

        Args:
            spec: Normalized skill spec as dictionary
            result: ValidationResult to accumulate failures
        """
        # Validate version format
        if "version" in spec:
            version = spec["version"]
            if isinstance(version, str) and not self.PATTERNS["version"].match(version):
                result.add_failure(
                    code=ValidationErrorCode.E321_VERSION_FORMAT_INVALID,
                    message="Version does not follow semantic versioning format",
                    field_path="version",
                    actual_value=version,
                    expected_value="X.Y.Z (e.g., 1.0.0)",
                    suggested_fix="Update version to follow semver format (e.g., 1.0.0, 2.1.3-beta)",
                )

        # Validate skill_id format
        if "skill_id" in spec:
            skill_id = spec["skill_id"]
            if isinstance(skill_id, str) and not self.PATTERNS["skill_id"].match(skill_id):
                result.add_failure(
                    code=ValidationErrorCode.E322_SKILL_ID_FORMAT_INVALID,
                    message="skill_id does not follow required format",
                    field_path="skill_id",
                    actual_value=skill_id,
                    expected_value="{skill_name}-{version}-{8_char_hash}",
                    suggested_fix="Format skill_id as: {skill_name}-{version}-{hash_suffix}",
                )

        # Validate spec_hash format
        if "spec_hash" in spec:
            spec_hash = spec["spec_hash"]
            if isinstance(spec_hash, str) and not self.PATTERNS["sha256"].match(spec_hash):
                result.add_failure(
                    code=ValidationErrorCode.E323_SPEC_HASH_FORMAT_INVALID,
                    message="spec_hash is not a valid SHA-256 hash",
                    field_path="spec_hash",
                    actual_value=spec_hash,
                    expected_value="64-character hexadecimal string",
                    suggested_fix="Ensure spec_hash is a SHA-256 hash (64 hex characters)",
                )

        # Validate manifest_hash format if present
        if "manifest_snapshot" in spec:
            manifest = spec["manifest_snapshot"]
            if isinstance(manifest, dict) and "content_hash" in manifest:
                content_hash = manifest["content_hash"]
                if content_hash and isinstance(content_hash, str) and not self.PATTERNS["sha256"].match(content_hash):
                    result.add_failure(
                        code=ValidationErrorCode.E326_MANIFEST_HASH_INVALID,
                        message="manifest content_hash is not a valid SHA-256 hash",
                        field_path="manifest_snapshot.content_hash",
                        actual_value=content_hash,
                        expected_value="64-character hexadecimal string or null",
                        suggested_fix="Ensure manifest content_hash is a SHA-256 hash or null",
                    )

        # Validate dependencies
        if "dependencies" in spec:
            self._validate_dependencies(spec["dependencies"], result)

    def _validate_dependencies(self, dependencies: dict[str, Any], result: ValidationResult) -> None:
        """Validate dependency structure."""
        base_path = "dependencies"

        # Validate direct_dependencies
        if "direct_dependencies" in dependencies:
            for i, dep in enumerate(dependencies["direct_dependencies"]):
                if not isinstance(dep, dict):
                    result.add_failure(
                        code=ValidationErrorCode.E303_FIELD_TYPE_MISMATCH,
                        message=f"Dependency at index {i} is not an object",
                        field_path=f"{base_path}.direct_dependencies[{i}]",
                        suggested_fix="Ensure each dependency is an object with 'name' and 'source' fields",
                    )
                    continue

                dep_path = f"{base_path}.direct_dependencies[{i}]"

                # Check name
                if "name" not in dep or not dep["name"]:
                    result.add_failure(
                        code=ValidationErrorCode.E324_DEPENDENCY_NAME_EMPTY,
                        message=f"Dependency at index {i} has missing or empty name",
                        field_path=f"{dep_path}.name",
                        suggested_fix="Add 'name' field to dependency",
                    )

                # Check source
                if "source" in dep:
                    source = dep["source"]
                    valid_sources = ["import", "from_import", "requirements.txt", "manifest"]
                    if source not in valid_sources:
                        result.add_failure(
                            code=ValidationErrorCode.E325_DEPENDENCY_SOURCE_INVALID,
                            message=f"Dependency at index {i} has invalid source",
                            field_path=f"{dep_path}.source",
                            actual_value=source,
                            expected_value=f"One of {valid_sources}",
                            suggested_fix=f"Set source to one of: {valid_sources}",
                        )

        # Validate dependency_count consistency
        if "dependency_count" in dependencies and "direct_dependencies" in dependencies:
            expected_count = len(dependencies["direct_dependencies"])
            actual_count = dependencies["dependency_count"]
            if expected_count != actual_count:
                result.add_failure(
                    code=ValidationErrorCode.E327_DEPENDENCY_COUNT_MISMATCH,
                    message="dependency_count does not match actual number of direct_dependencies",
                    field_path=f"{base_path}.dependency_count",
                    actual_value=str(actual_count),
                    expected_value=str(expected_count),
                    suggested_fix=f"Update dependency_count to {expected_count}",
                )


# ============================================================================
# Main Skill Contract Validator
# ============================================================================
class SkillContractValidator:
    """
    Main validator for skill contracts and structure.

    T3 Deliverable: Comprehensive validation of NormalizedSkillSpec.
    """

    def __init__(self, schema_path: Optional[str | Path] = None):
        """
        Initialize validator.

        Args:
            schema_path: Path to normalized_skill_spec.schema.json
        """
        self.schema_validator = SchemaValidator(schema_path)
        self.contract_validator = ContractValidator()
        self.consistency_validator = ConsistencyValidator()

    def validate_skill_spec(
        self, spec: dict[str, Any] | str | Path
    ) -> ValidationResult:
        """
        Validate a normalized skill spec.

        Args:
            spec: Normalized skill spec as dict, JSON string, or path to JSON file

        Returns:
            ValidationResult with all failures and warnings
        """
        result = ValidationResult(is_valid=True)

        # Load spec if path or JSON string provided
        if isinstance(spec, (str, Path)) and Path(spec).exists():
            with open(spec, "r", encoding="utf-8") as f:
                spec = json.load(f)
        elif isinstance(spec, str):
            spec = json.loads(spec)

        # Run validators
        self.schema_validator.validate(spec, result)
        self.contract_validator.validate_contracts(spec, result)
        self.consistency_validator.validate_consistency(spec, result)

        return result

    def validate_and_report(
        self, spec: dict[str, Any] | str | Path, output_path: str | Path
    ) -> ValidationResult:
        """
        Validate spec and save report to file.

        Args:
            spec: Normalized skill spec as dict, JSON string, or path to JSON file
            output_path: Path to save validation_report.json

        Returns:
            ValidationResult with all failures and warnings
        """
        result = self.validate_skill_spec(spec)
        result.save(output_path)
        return result


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for skill contract validation."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Validate skill contract and structure (T3)"
    )
    parser.add_argument(
        "spec",
        help="Path to normalized_skill_spec.json or skill directory",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="validation_report.json",
        help="Output path for validation_report.json",
    )
    parser.add_argument(
        "--schema",
        help="Path to normalized_skill_spec.schema.json (default: skillforge/src/contracts/)",
    )

    args = parser.parse_args()

    # Determine spec path
    spec_path = Path(args.spec)
    if spec_path.is_dir():
        # If directory, look for normalized_skill_spec.json
        spec_path = spec_path / "normalized_skill_spec.json"

    if not spec_path.exists():
        print(f"Error: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    # Run validation
    validator = SkillContractValidator(schema_path=args.schema)
    result = validator.validate_and_report(spec_path, args.output)

    # Print summary
    if result.is_valid:
        print(f"✅ Validation PASSED")
        if result.warnings:
            print(f"   {len(result.warnings)} warning(s)")
        print(f"   Report saved to: {args.output}")
    else:
        print(f"❌ Validation FAILED")
        print(f"   {len(result.failures)} error(s), {len(result.warnings)} warning(s)")
        print(f"   Report saved to: {args.output}")
        print()
        print("Errors:")
        for failure in result.failures[:10]:  # Show first 10
            print(f"   [{failure.code}] {failure.field_path}")
            print(f"      {failure.message}")
        if len(result.failures) > 10:
            print(f"   ... and {len(result.failures) - 10} more")

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
