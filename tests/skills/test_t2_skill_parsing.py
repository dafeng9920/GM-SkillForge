"""
T2 Skill Parsing and Normalization Tests

This test suite validates T2 requirements:
1. Skill directory structure can be parsed
2. Manifest can be read (optional)
3. Dependencies can be extracted
4. Input/output contracts can be extracted
5. Field names are normalized (snake_case)
6. Valid skill parses successfully
7. Invalid skill fails with clear error

Run:
    cd d:/GM-SkillForge
    python -m pytest tests/skills/test_t2_skill_parsing.py -v
    python tests/skills/test_t2_skill_parsing.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

# Setup paths
project_root = Path(__file__).parent.parent.parent
skillforge_src = project_root / "skillforge" / "src"
contracts_path = skillforge_src / "contracts"

sys.path.insert(0, str(skillforge_src))
sys.path.insert(0, str(contracts_path))

from contracts.skill_spec import (
    SkillParser,
    ParseResult,
    NormalizedSkillSpec,
    Dependency,
    DependencyGraph,
    Contract,
    ManifestSnapshot,
    SkillSpecError,
    SkillSpecErrorCode,
    parse_skill_directory,
)


# ============================================================================
# Fixtures
# ============================================================================
def create_valid_skill_structure(base_dir: Path) -> Path:
    """Create a valid skill directory structure for testing."""
    skill_dir = base_dir / "test_skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    (skill_dir / "__init__.py").write_text(
        '"""Test skill for T2 parsing."""\n'
    )

    # Create main skill file
    (skill_dir / "test_skill.py").write_text(
        '"""Test skill - A valid skill for T2 testing."""\n\n'
        'SKILL_NAME = "test_skill"\n'
        'SKILL_VERSION = "1.0.0"\n'
        '\n'
        'def execute(input_data):\n'
        '    """Execute the skill."""\n'
        '    return {"result": "success"}\n'
    )

    # Create manifest.json
    manifest = {
        "skill_name": "test_skill",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            },
            "required": ["result"]
        }
    }
    with open(skill_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    return skill_dir


def create_invalid_skill_missing_name(base_dir: Path) -> Path:
    """Create skill without SKILL_NAME."""
    skill_dir = base_dir / "invalid_no_name"
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "invalid_skill.py").write_text(
        '"""Invalid skill - missing SKILL_NAME."""\n\n'
        '# SKILL_NAME is missing\n'
        'SKILL_VERSION = "1.0.0"\n'
    )

    return skill_dir


def create_skill_no_manifest(base_dir: Path) -> Path:
    """Create skill without manifest.json."""
    skill_dir = base_dir / "no_manifest"
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "no_manifest_skill.py").write_text(
        '"""Skill without manifest."""\n\n'
        'SKILL_NAME = "no_manifest_skill"\n'
        'SKILL_VERSION = "1.0.0"\n'
    )

    return skill_dir


# ============================================================================
# Test Classes
# ============================================================================
class TestT2_ValidSkillParsing:
    """T2: Valid skill can be parsed successfully."""

    def test_parse_valid_skill_succeeds(self):
        """Valid skill with manifest should parse successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid, f"Parse failed: {[e.message for e in result.errors]}"
            assert result.spec is not None
            assert result.spec.skill_name == "test_skill"
            assert result.spec.version == "1.0.0"

    def test_parsed_spec_has_all_required_fields(self):
        """NormalizedSkillSpec must have all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            spec = result.spec

            # Check required fields
            assert hasattr(spec, "skill_id")
            assert hasattr(spec, "skill_name")
            assert hasattr(spec, "version")
            assert hasattr(spec, "description")
            assert hasattr(spec, "entry_point")
            assert hasattr(spec, "skill_dir")
            assert hasattr(spec, "file_list")
            assert hasattr(spec, "dependencies")
            assert hasattr(spec, "input_contract")
            assert hasattr(spec, "output_contract")
            assert hasattr(spec, "manifest_snapshot")

    def test_field_names_are_snake_case(self):
        """All field names must be normalized to snake_case."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            spec_dict = result.spec.to_dict()

            # Check for camelCase or PascalCase (should not exist)
            for key in spec_dict.keys():
                # No lowercase followed by uppercase (camelCase pattern)
                # Exception: "skill_dir" has "ir" which is lowercase-lowercase
                # We check more carefully: look for lowercase letter followed by uppercase
                is_camel = any(
                    c.islower() and i + 1 < len(key) and key[i + 1].isupper()
                    for i, c in enumerate(key)
                )
                assert not is_camel, f"Field {key} appears to be camelCase"

    def test_skill_id_is_generated(self):
        """skill_id must be auto-generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            assert result.spec.skill_id is not None
            assert len(result.spec.skill_id) > 0
            # Format: name-version-hash
            assert result.spec.skill_name in result.spec.skill_id
            assert result.spec.version in result.spec.skill_id


class TestT2_DependencyExtraction:
    """T2: Dependencies can be extracted from skill."""

    def test_dependencies_extracted_from_imports(self):
        """Dependencies should be extracted from import statements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "dep_skill"
            skill_dir.mkdir()

            # Create skill with external imports
            (skill_dir / "dep_skill.py").write_text(
                '"""Skill with dependencies."""\n\n'
                'SKILL_NAME = "dep_skill"\n'
                'SKILL_VERSION = "1.0.0"\n'
                '\n'
                'import requests\n'
                'import numpy as np\n'
                'from pandas import DataFrame\n'
            )

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            deps = result.spec.dependencies.direct_dependencies

            # Should find requests, numpy, pandas
            dep_names = [d.name for d in deps]
            assert "requests" in dep_names
            assert "numpy" in dep_names
            assert "pandas" in dep_names

    def test_stdlib_imports_excluded(self):
        """Standard library imports should be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "stdlib_skill"
            skill_dir.mkdir()

            (skill_dir / "stdlib_skill.py").write_text(
                '"""Skill using stdlib."""\n\n'
                'SKILL_NAME = "stdlib_skill"\n'
                'SKILL_VERSION = "1.0.0"\n'
                '\n'
                'import os\n'
                'import sys\n'
                'import json\n'
                'import requests  # External\n'
            )

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            dep_names = [d.name for d in result.spec.dependencies.direct_dependencies]

            # Only requests should be listed
            assert "requests" in dep_names
            assert "os" not in dep_names
            assert "sys" not in dep_names
            assert "json" not in dep_names


class TestT2_ContractExtraction:
    """T2: Input/output contracts can be extracted."""

    def test_contracts_from_manifest(self):
        """Contracts should be read from manifest.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            input_contract = result.spec.input_contract
            output_contract = result.spec.output_contract

            # Check input contract
            assert input_contract.schema_type == "object"
            assert "query" in input_contract.properties
            assert "query" in input_contract.required

            # Check output contract
            assert output_contract.schema_type == "object"
            assert "result" in output_contract.properties
            assert "result" in output_contract.required

    def test_default_contracts_without_manifest(self):
        """Default contracts should be used when manifest is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_no_manifest(Path(tmpdir))

            parser = SkillParser(fail_on_missing_manifest=False)
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            # Should have default contracts
            assert result.spec.input_contract is not None
            assert result.spec.output_contract is not None


class TestT2_InvalidSkillHandling:
    """T2: Invalid skill fails with clear error."""

    def test_missing_skill_name_fails(self):
        """Skill without SKILL_NAME should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_invalid_skill_missing_name(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert not result.is_valid
            error_codes = [e.code for e in result.errors]
            assert SkillSpecErrorCode.E208_SKILL_NAME_MISSING in error_codes

    def test_nonexistent_directory_fails(self):
        """Parsing nonexistent directory should fail."""
        parser = SkillParser()
        result = parser.parse_skill("/nonexistent/path")

        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert SkillSpecErrorCode.E201_SKILL_DIR_NOT_FOUND in error_codes

    def test_missing_manifest_with_strict_flag_fails(self):
        """With fail_on_missing_manifest=True, missing manifest causes failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_no_manifest(Path(tmpdir))

            parser = SkillParser(fail_on_missing_manifest=True)
            result = parser.parse_skill(skill_dir)

            assert not result.is_valid
            error_codes = [e.code for e in result.errors]
            assert SkillSpecErrorCode.E205_MANIFEST_FILE_MISSING in error_codes


class TestT2_ManifestSnapshot:
    """T2: Manifest snapshot is captured correctly."""

    def test_manifest_snapshot_exists_when_present(self):
        """manifest_snapshot.exists should be True when manifest exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            assert result.spec.manifest_snapshot.exists
            assert result.spec.manifest_snapshot.content_hash is not None
            assert len(result.spec.manifest_snapshot.content_hash) == 64  # SHA-256

    def test_manifest_snapshot_not_exists_when_absent(self):
        """manifest_snapshot.exists should be False when manifest absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_no_manifest(Path(tmpdir))

            parser = SkillParser(fail_on_missing_manifest=False)
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            assert not result.spec.manifest_snapshot.exists


class TestT2_Serialization:
    """T2: NormalizedSkillSpec can be serialized."""

    def test_to_dict_returns_dict(self):
        """to_dict() should return a dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            spec_dict = result.spec.to_dict()

            assert isinstance(spec_dict, dict)
            assert "skill_id" in spec_dict
            assert "skill_name" in spec_dict

    def test_to_json_produces_valid_json(self):
        """to_json() should produce valid JSON string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            json_str = result.spec.to_json()

            # Should be parseable
            parsed = json.loads(json_str)
            assert parsed["skill_name"] == "test_skill"

    def test_save_writes_file(self):
        """save() should write JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))
            output_path = Path(tmpdir) / "normalized_skill_spec.json"

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            assert result.is_valid
            result.spec.save(output_path)

            assert output_path.exists()

            with open(output_path) as f:
                data = json.load(f)
            assert data["skill_name"] == "test_skill"


class TestT2_RealSkillParsing:
    """T2: Parse real skills from the codebase."""

    def test_parse_quant_skill(self):
        """Real quant skill should be parseable."""
        # Use actual project path
        quant_skill_dir = project_root / "skillforge" / "src" / "skills" / "quant"

        if not quant_skill_dir.exists():
            # Skip if quant skill doesn't exist
            return

        parser = SkillParser()
        result = parser.parse_skill(quant_skill_dir)

        # Should parse successfully (even if no manifest)
        if result.is_valid:
            assert result.spec.skill_name is not None
            assert result.spec.version is not None
        else:
            # Check if error is acceptable (e.g., missing SKILL_NAME)
            error_codes = [e.code for e in result.errors]
            # Allow missing metadata but not structural errors
            assert SkillSpecErrorCode.E201_SKILL_DIR_NOT_FOUND not in error_codes
            assert SkillSpecErrorCode.E202_NOT_A_DIRECTORY not in error_codes


# ============================================================================
# Verification Script (can be run standalone)
# ============================================================================
def main():
    """Run T2 compliance checks and print results."""
    print("=" * 60)
    print("T2 Skill Parsing Compliance Verification")
    print("=" * 60)

    passed = 0
    failed = 0

    # Test 1: Valid skill parses
    print("\n[Test 1] Valid skill should parse successfully...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))
            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            if result.is_valid and result.spec.skill_name == "test_skill":
                print("  PASS: Valid skill parsed correctly")
                passed += 1
            else:
                print(f"  FAIL: Parse failed or incorrect: {[e.message for e in result.errors]}")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 2: Missing SKILL_NAME fails
    print("\n[Test 2] Missing SKILL_NAME should fail...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_invalid_skill_missing_name(Path(tmpdir))
            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            if not result.is_valid:
                error_codes = [e.code for e in result.errors]
                if SkillSpecErrorCode.E208_SKILL_NAME_MISSING in error_codes:
                    print("  PASS: Missing SKILL_NAME correctly rejected")
                    passed += 1
                else:
                    print(f"  FAIL: Wrong error code: {error_codes}")
                    failed += 1
            else:
                print("  FAIL: Invalid skill was not rejected")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 3: Dependencies extracted
    print("\n[Test 3] Dependencies should be extracted...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "dep_skill"
            skill_dir.mkdir()
            (skill_dir / "dep_skill.py").write_text(
                'SKILL_NAME = "dep_skill"\nSKILL_VERSION = "1.0.0"\nimport requests\n'
            )

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            if result.is_valid:
                dep_names = [d.name for d in result.spec.dependencies.direct_dependencies]
                if "requests" in dep_names:
                    print("  PASS: Dependencies extracted correctly")
                    passed += 1
                else:
                    print(f"  FAIL: Dependencies not found: {dep_names}")
                    failed += 1
            else:
                print(f"  FAIL: Parse failed: {[e.message for e in result.errors]}")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 4: Contracts from manifest
    print("\n[Test 4] Contracts should be read from manifest...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))
            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            if result.is_valid and result.spec.manifest_snapshot.exists:
                if "query" in result.spec.input_contract.properties:
                    print("  PASS: Contracts extracted from manifest")
                    passed += 1
                else:
                    print("  FAIL: Input contract not extracted")
                    failed += 1
            else:
                print("  FAIL: Parse failed or manifest not found")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 5: JSON serialization
    print("\n[Test 5] NormalizedSkillSpec should serialize to JSON...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))
            output_path = Path(tmpdir) / "normalized_skill_spec.json"

            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            if result.is_valid:
                result.spec.save(output_path)
                if output_path.exists():
                    with open(output_path) as f:
                        data = json.load(f)
                    if data.get("skill_name") == "test_skill":
                        print("  PASS: JSON serialization successful")
                        passed += 1
                    else:
                        print("  FAIL: Incorrect data in JSON")
                        failed += 1
                else:
                    print("  FAIL: JSON file not created")
                    failed += 1
            else:
                print(f"  FAIL: Parse failed: {[e.message for e in result.errors]}")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 6: Field names are snake_case
    print("\n[Test 6] Field names should be snake_case...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_valid_skill_structure(Path(tmpdir))
            parser = SkillParser()
            result = parser.parse_skill(skill_dir)

            if result.is_valid:
                spec_dict = result.spec.to_dict()
                # Check for camelCase
                has_camel = any(
                    any(c.islower() and i + 1 < len(key) and key[i + 1].isupper()
                        for i, c in enumerate(key))
                    for key in spec_dict.keys()
                )
                if not has_camel:
                    print("  PASS: Field names are snake_case")
                    passed += 1
                else:
                    print("  FAIL: Found camelCase field names")
                    failed += 1
            else:
                print(f"  FAIL: Parse failed: {[e.message for e in result.errors]}")
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
