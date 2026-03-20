"""
T3 Contract Validation Tests

This test suite validates T3 requirements:
1. Schema validation (JSON Schema conformance)
2. Contract validation (input/output contract structure)
3. Input/output consistency checks
4. Required field validation
5. Error codes with field paths
6. Positive and negative test cases

Run:
    cd d:/GM-SkillForge
    python -m pytest tests/contracts/test_t3_contract_validation.py -v
    python tests/contracts/test_t3_contract_validation.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

# Setup paths
project_root = Path(__file__).parent.parent.parent
skillforge_src = project_root / "skillforge" / "src"
contracts_path = skillforge_src / "contracts"

sys.path.insert(0, str(skillforge_src))
sys.path.insert(0, str(contracts_path))

from skill_contract_validator import (
    SkillContractValidator,
    ValidationResult,
    ValidationErrorCode,
    SchemaValidator,
    ContractValidator,
    ConsistencyValidator,
)


# ============================================================================
# Test Fixtures
# ============================================================================
def create_valid_skill_spec() -> dict[str, Any]:
    """Create a valid skill spec for positive testing."""
    return {
        "skill_id": "test_skill-1.0.0-abc12345",
        "skill_name": "test_skill",
        "version": "1.0.0",
        "description": "A test skill for validation",
        "entry_point": "skill.py",
        "skill_dir": "/path/to/skill",
        "file_list": ["skill.py", "__init__.py"],
        "dependencies": {
            "direct_dependencies": [
                {"name": "requests", "version": "2.28.0", "source": "import"},
                {"name": "pytest", "version": None, "source": "requirements.txt"}
            ],
            "transitive_dependencies": [],
            "dependency_count": 2
        },
        "input_contract": {
            "schema_type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "amount": {"type": "number"}
            },
            "required": ["user_id"],
            "description": "Input for processing"
        },
        "output_contract": {
            "schema_type": "object",
            "properties": {
                "result": {"type": "boolean"},
                "message": {"type": "string"}
            },
            "required": ["result"],
            "description": "Output from processing"
        },
        "manifest_snapshot": {
            "exists": True,
            "content_hash": "a" * 64,
            "raw_data": {}
        },
        "capabilities": ["http", "json"],
        "constraints": ["max_retries: 3"],
        "parsed_at": datetime.now(timezone.utc).isoformat(),
        "parser_version": "1.0.0-t2",
        "spec_hash": "a" * 64
    }


# ============================================================================
# Schema Validation Tests
# ============================================================================
class TestT3_SchemaValidation:
    """T3: Schema validation tests."""

    def test_valid_spec_passes_schema_validation(self):
        """Valid skill spec should pass schema validation."""
        spec = create_valid_skill_spec()
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert result.is_valid, "Valid spec should pass validation"
        assert len(result.failures) == 0, f"Should have no failures, got: {result.failures}"

    def test_missing_required_field_fails(self):
        """Missing required field should produce failure with error code."""
        spec = create_valid_skill_spec()
        del spec["skill_name"]  # Remove required field

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Missing required field should fail"
        assert any(
            f.code == ValidationErrorCode.E302_REQUIRED_FIELD_MISSING and
            f.field_path == "skill_name"
            for f in result.failures
        ), "Should have E302 error for skill_name"

    def test_invalid_field_type_fails(self):
        """Invalid field type should produce failure with error code."""
        spec = create_valid_skill_spec()
        spec["version"] = 123  # Should be string, not int

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid field type should fail"
        assert any(
            f.code == ValidationErrorCode.E303_FIELD_TYPE_MISMATCH and
            f.field_path == "version"
            for f in result.failures
        ), "Should have E303 error for version type mismatch"

    def test_invalid_version_format_fails(self):
        """Invalid version format should produce consistency failure."""
        spec = create_valid_skill_spec()
        spec["version"] = "not-a-version"

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid version format should fail"
        assert any(
            f.code == ValidationErrorCode.E321_VERSION_FORMAT_INVALID and
            f.field_path == "version"
            for f in result.failures
        ), "Should have E321 error for invalid version"

    def test_invalid_skill_id_format_fails(self):
        """Invalid skill_id format should produce consistency failure."""
        spec = create_valid_skill_spec()
        spec["skill_id"] = "invalid-id"

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid skill_id format should fail"
        assert any(
            f.code == ValidationErrorCode.E322_SKILL_ID_FORMAT_INVALID and
            f.field_path == "skill_id"
            for f in result.failures
        ), "Should have E322 error for invalid skill_id"


# ============================================================================
# Contract Validation Tests
# ============================================================================
class TestT3_ContractValidation:
    """T3: Contract validation tests."""

    def test_missing_input_contract_fails(self):
        """Missing input contract should produce failure with error code."""
        spec = create_valid_skill_spec()
        del spec["input_contract"]

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Missing input_contract should fail"
        assert any(
            f.code == ValidationErrorCode.E311_INPUT_CONTRACT_MISSING and
            f.field_path == "input_contract"
            for f in result.failures
        ), "Should have E311 error for missing input_contract"

    def test_missing_output_contract_fails(self):
        """Missing output contract should produce failure with error code."""
        spec = create_valid_skill_spec()
        del spec["output_contract"]

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Missing output_contract should fail"
        assert any(
            f.code == ValidationErrorCode.E312_OUTPUT_CONTRACT_MISSING and
            f.field_path == "output_contract"
            for f in result.failures
        ), "Should have E312 error for missing output_contract"

    def test_invalid_schema_type_fails(self):
        """Invalid schema_type in contract should produce failure."""
        spec = create_valid_skill_spec()
        spec["input_contract"]["schema_type"] = "invalid_type"

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid schema_type should fail"
        assert any(
            f.code == ValidationErrorCode.E313_CONTRACT_SCHEMA_TYPE_INVALID and
            "input_contract.schema_type" in f.field_path
            for f in result.failures
        ), "Should have E313 error for invalid schema_type"

    def test_required_field_not_in_properties_fails(self):
        """Required field not in properties should produce failure."""
        spec = create_valid_skill_spec()
        spec["input_contract"]["required"] = ["nonexistent_field"]

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Required field not in properties should fail"
        assert any(
            f.code == ValidationErrorCode.E316_CONTRACT_REQUIRED_NOT_IN_PROPERTIES and
            "input_contract.required" in f.field_path
            for f in result.failures
        ), "Should have E316 error for required not in properties"


# ============================================================================
# Consistency Validation Tests
# ============================================================================
class TestT3_ConsistencyValidation:
    """T3: Consistency validation tests."""

    def test_dependency_count_mismatch_fails(self):
        """Dependency count mismatch should produce failure."""
        spec = create_valid_skill_spec()
        spec["dependencies"]["dependency_count"] = 999  # Wrong count

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Dependency count mismatch should fail"
        assert any(
            f.code == ValidationErrorCode.E327_DEPENDENCY_COUNT_MISMATCH and
            "dependencies.dependency_count" in f.field_path
            for f in result.failures
        ), "Should have E327 error for dependency count mismatch"

    def test_empty_dependency_name_fails(self):
        """Empty dependency name should produce failure."""
        spec = create_valid_skill_spec()
        spec["dependencies"]["direct_dependencies"].append({
            "name": "",
            "source": "import"
        })

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Empty dependency name should fail"
        assert any(
            f.code == ValidationErrorCode.E324_DEPENDENCY_NAME_EMPTY and
            "direct_dependencies" in f.field_path
            for f in result.failures
        ), "Should have E324 error for empty dependency name"

    def test_invalid_dependency_source_fails(self):
        """Invalid dependency source should produce failure."""
        spec = create_valid_skill_spec()
        spec["dependencies"]["direct_dependencies"].append({
            "name": "test",
            "source": "invalid_source"
        })

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid dependency source should fail"
        assert any(
            f.code == ValidationErrorCode.E325_DEPENDENCY_SOURCE_INVALID and
            "direct_dependencies" in f.field_path
            for f in result.failures
        ), "Should have E325 error for invalid dependency source"

    def test_invalid_spec_hash_format_fails(self):
        """Invalid spec_hash format should produce failure."""
        spec = create_valid_skill_spec()
        spec["spec_hash"] = "not-a-hash"

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid spec_hash should fail"
        assert any(
            f.code == ValidationErrorCode.E323_SPEC_HASH_FORMAT_INVALID and
            f.field_path == "spec_hash"
            for f in result.failures
        ), "Should have E323 error for invalid spec_hash"


# ============================================================================
# Field Path and Suggested Fix Tests
# ============================================================================
class TestT3_FieldPathsAndFixes:
    """T3: Field paths and suggested fixes tests."""

    def test_failure_includes_field_path(self):
        """Each failure must include field_path."""
        spec = create_valid_skill_spec()
        del spec["version"]

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Should have validation failure"
        for failure in result.failures:
            assert failure.field_path, f"Failure {failure.code} missing field_path"

    def test_failure_includes_suggested_fix(self):
        """Each failure should include suggested fix."""
        spec = create_valid_skill_spec()
        spec["version"] = "invalid"

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        # Check that at least the E321 error has a suggested fix
        e321_failures = [f for f in result.failures if f.code == ValidationErrorCode.E321_VERSION_FORMAT_INVALID]
        assert len(e321_failures) > 0, "Should have E321 failure"
        assert e321_failures[0].suggested_fix, "E321 failure should have suggested_fix"

    def test_failure_includes_actual_and_expected_values(self):
        """Failures should include actual_value for debugging."""
        spec = create_valid_skill_spec()
        spec["version"] = "wrong-format"

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        e321_failures = [f for f in result.failures if f.code == ValidationErrorCode.E321_VERSION_FORMAT_INVALID]
        assert len(e321_failures) > 0, "Should have E321 failure"
        assert e321_failures[0].actual_value == "wrong-format", "Should include actual_value"
        assert e321_failures[0].expected_value, "Should include expected_value"


# ============================================================================
# Validation Report Tests
# ============================================================================
class TestT3_ValidationReport:
    """T3: Validation report structure tests."""

    def test_validation_report_has_required_fields(self):
        """Validation report must have required fields."""
        spec = create_valid_skill_spec()
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        result_dict = result.to_dict()

        # Check required fields
        assert "is_valid" in result_dict
        assert "failures" in result_dict
        assert "warnings" in result_dict
        assert "validated_at" in result_dict
        assert "validator_version" in result_dict
        assert "failure_count" in result_dict
        assert "warning_count" in result_dict

    def test_validation_report_serializes_to_json(self):
        """Validation report should serialize to JSON correctly."""
        spec = create_valid_skill_spec()
        spec["version"] = "invalid"  # Trigger a failure

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        # Should not raise exception
        json_str = result.to_json()
        parsed = json.loads(json_str)

        assert parsed["is_valid"] == False
        assert len(parsed["failures"]) > 0

    def test_validation_report_saves_to_file(self):
        """Validation report should save to file correctly."""
        import tempfile

        spec = create_valid_skill_spec()
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "validation_report.json"
            result.save(output_path)

            assert output_path.exists(), "Report file should be created"

            with open(output_path) as f:
                loaded = json.load(f)

            assert loaded["is_valid"] == result.is_valid
            assert loaded["failure_count"] == len(result.failures)


# ============================================================================
# Negative Test Cases
# ============================================================================
class TestT3_NegativeTestCases:
    """T3: Negative test cases - illegal specs must be rejected."""

    def test_spec_missing_all_contracts_fails(self):
        """Spec missing both input and output contracts should fail."""
        spec = create_valid_skill_spec()
        del spec["input_contract"]
        del spec["output_contract"]

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Missing all contracts should fail"
        assert len(result.failures) >= 2, "Should have at least 2 failures"

    def test_spec_with_invalid_contract_structure_fails(self):
        """Spec with invalid contract structure should fail."""
        spec = create_valid_skill_spec()
        spec["input_contract"] = "not-an-object"  # Invalid type

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid contract structure should fail"

    def test_spec_with_empty_dependencies_fails(self):
        """Spec with dependency_count mismatch (0 vs actual) should fail."""
        spec = create_valid_skill_spec()
        spec["dependencies"]["direct_dependencies"] = []
        spec["dependencies"]["dependency_count"] = 1  # Wrong count

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Dependency count mismatch should fail"

    def test_spec_with_invalid_manifest_hash_fails(self):
        """Spec with invalid manifest hash should fail."""
        spec = create_valid_skill_spec()
        spec["manifest_snapshot"]["content_hash"] = "not-64-char-hex"

        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)

        assert not result.is_valid, "Invalid manifest hash should fail"


# ============================================================================
# Verification Script (can be run standalone)
# ============================================================================
def main():
    """Run T3 validation checks and print results."""
    import tempfile

    print("=" * 60)
    print("T3 Contract Validation Verification")
    print("=" * 60)

    passed = 0
    failed = 0

    # Test 1: Valid spec passes
    print("\n[Test 1] Valid spec should pass validation...")
    try:
        spec = create_valid_skill_spec()
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        if result.is_valid:
            print("  PASS: Valid spec correctly accepted")
            passed += 1
        else:
            print(f"  FAIL: Valid spec was rejected with {len(result.failures)} errors")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 2: Missing required field fails
    print("\n[Test 2] Missing required field should fail...")
    try:
        spec = create_valid_skill_spec()
        del spec["skill_name"]
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        if not result.is_valid and any(
            f.code == ValidationErrorCode.E302_REQUIRED_FIELD_MISSING and
            f.field_path == "skill_name"
            for f in result.failures
        ):
            print("  PASS: Missing required field correctly rejected")
            passed += 1
        else:
            print("  FAIL: Missing required field was not properly rejected")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 3: Invalid version format fails
    print("\n[Test 3] Invalid version format should fail...")
    try:
        spec = create_valid_skill_spec()
        spec["version"] = "not-a-version"
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        if not result.is_valid and any(
            f.code == ValidationErrorCode.E321_VERSION_FORMAT_INVALID
            for f in result.failures
        ):
            print("  PASS: Invalid version format correctly rejected")
            passed += 1
        else:
            print("  FAIL: Invalid version format was not properly rejected")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 4: Missing input contract fails
    print("\n[Test 4] Missing input contract should fail...")
    try:
        spec = create_valid_skill_spec()
        del spec["input_contract"]
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        if not result.is_valid and any(
            f.code == ValidationErrorCode.E311_INPUT_CONTRACT_MISSING
            for f in result.failures
        ):
            print("  PASS: Missing input contract correctly rejected")
            passed += 1
        else:
            print("  FAIL: Missing input contract was not properly rejected")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 5: Field paths present
    print("\n[Test 5] All failures must include field_path...")
    try:
        spec = create_valid_skill_spec()
        spec["version"] = "invalid"
        del spec["skill_name"]
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        if all(f.field_path for f in result.failures):
            print("  PASS: All failures have field_path")
            passed += 1
        else:
            print("  FAIL: Some failures missing field_path")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 6: Suggested fixes present
    print("\n[Test 6] Failures should include suggested_fix...")
    try:
        spec = create_valid_skill_spec()
        spec["version"] = "invalid"
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        e321_failures = [f for f in result.failures if f.code == ValidationErrorCode.E321_VERSION_FORMAT_INVALID]
        if e321_failures and e321_failures[0].suggested_fix:
            print("  PASS: Failure has suggested_fix")
            passed += 1
        else:
            print("  FAIL: Failure missing suggested_fix")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 7: Validation report saves
    print("\n[Test 7] Validation report should save to file...")
    try:
        spec = create_valid_skill_spec()
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "validation_report.json"
            result.save(output_path)
            if output_path.exists():
                with open(output_path) as f:
                    loaded = json.load(f)
                if loaded["is_valid"] == result.is_valid:
                    print("  PASS: Validation report saved and loaded correctly")
                    passed += 1
                else:
                    print("  FAIL: Saved report doesn't match result")
                    failed += 1
            else:
                print("  FAIL: Report file was not created")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 8: Dependency count mismatch detected
    print("\n[Test 8] Dependency count mismatch should be detected...")
    try:
        spec = create_valid_skill_spec()
        spec["dependencies"]["dependency_count"] = 999
        validator = SkillContractValidator()
        result = validator.validate_skill_spec(spec)
        if not result.is_valid and any(
            f.code == ValidationErrorCode.E327_DEPENDENCY_COUNT_MISMATCH
            for f in result.failures
        ):
            print("  PASS: Dependency count mismatch correctly detected")
            passed += 1
        else:
            print("  FAIL: Dependency count mismatch was not detected")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
