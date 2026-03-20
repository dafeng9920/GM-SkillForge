"""
Generate T3 positive and negative sample skill specs with validation reports.

This script creates sample normalized_skill_spec.json files and their
corresponding validation_report.json files for T3 evidence.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

# Setup paths
project_root = Path(__file__).parent.parent.parent
skillforge_src = project_root / "skillforge" / "src"
contracts_path = skillforge_src / "contracts"

import sys
sys.path.insert(0, str(skillforge_src))
sys.path.insert(0, str(contracts_path))

from skill_contract_validator import SkillContractValidator

# ============================================================================
# Sample 1: Valid (Positive Example)
# ============================================================================
def create_positive_sample():
    """Create a valid skill spec (positive example)."""
    return {
        "skill_id": "example_skill-1.0.0-a1b2c3d4",
        "skill_name": "example_skill",
        "version": "1.0.0",
        "description": "A valid example skill for T3 validation",
        "entry_point": "skill.py",
        "skill_dir": "/skills/example_skill",
        "file_list": ["skill.py", "__init__.py", "utils.py"],
        "dependencies": {
            "direct_dependencies": [
                {"name": "requests", "version": "2.28.0", "source": "import"},
                {"name": "jsonschema", "version": "4.17.0", "source": "requirements.txt"}
            ],
            "transitive_dependencies": [],
            "dependency_count": 2
        },
        "input_contract": {
            "schema_type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User identifier"},
                "action": {"type": "string", "description": "Action to perform"},
                "params": {"type": "object", "description": "Additional parameters"}
            },
            "required": ["user_id", "action"],
            "description": "Input contract for example skill"
        },
        "output_contract": {
            "schema_type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "result": {"type": "object"},
                "error": {"type": "string"}
            },
            "required": ["success"],
            "description": "Output contract for example skill"
        },
        "manifest_snapshot": {
            "exists": True,
            "content_hash": "a" * 64,
            "raw_data": {"name": "example_skill", "version": "1.0.0"}
        },
        "capabilities": ["http", "json", "validation"],
        "constraints": ["max_retries: 3", "timeout: 30s"],
        "parsed_at": datetime.now(timezone.utc).isoformat(),
        "parser_version": "1.0.0-t2",
        "spec_hash": "a" * 64
    }


# ============================================================================
# Sample 2: Missing Required Field (Negative Example)
# ============================================================================
def create_negative_missing_field():
    """Create a skill spec with missing required field."""
    spec = create_positive_sample()
    del spec["skill_name"]  # Remove required field
    return spec, "missing_skill_name"


# ============================================================================
# Sample 3: Invalid Version Format (Negative Example)
# ============================================================================
def create_negative_invalid_version():
    """Create a skill spec with invalid version format."""
    spec = create_positive_sample()
    spec["version"] = "not-a-valid-version"
    return spec, "invalid_version_format"


# ============================================================================
# Sample 4: Contract Conflict (Negative Example)
# ============================================================================
def create_negative_contract_conflict():
    """Create a skill spec with contract conflict (required not in properties)."""
    spec = create_positive_sample()
    spec["input_contract"]["required"] = ["user_id", "nonexistent_field"]
    return spec, "contract_required_not_in_properties"


# ============================================================================
# Sample 5: Missing Input Contract (Negative Example)
# ============================================================================
def create_negative_missing_input_contract():
    """Create a skill spec with missing input contract."""
    spec = create_positive_sample()
    del spec["input_contract"]
    return spec, "missing_input_contract"


# ============================================================================
# Sample 6: Dependency Count Mismatch (Negative Example)
# ============================================================================
def create_negative_dependency_count_mismatch():
    """Create a skill spec with dependency count mismatch."""
    spec = create_positive_sample()
    spec["dependencies"]["dependency_count"] = 999  # Wrong count
    return spec, "dependency_count_mismatch"


# ============================================================================
# Generate Samples
# ============================================================================
def main():
    """Generate all T3 sample files."""
    validator = SkillContractValidator()

    evidence_dir = Path("run/T3_evidence")
    positive_dir = evidence_dir / "positive_examples"
    negative_dir = evidence_dir / "negative_examples"

    # Create directories
    positive_dir.mkdir(parents=True, exist_ok=True)
    negative_dir.mkdir(parents=True, exist_ok=True)

    print("Generating T3 samples...")
    print("=" * 60)

    # Positive example
    print("\n[Positive Example] Valid skill spec...")
    spec = create_positive_sample()
    result = validator.validate_and_report(
        spec,
        positive_dir / "normalized_skill_spec.json"
    )
    # Save validation report
    result.save(positive_dir / "validation_report.json")
    print(f"  Created: {positive_dir}/normalized_skill_spec.json")
    print(f"  Created: {positive_dir}/validation_report.json")
    print(f"  Result: {'PASS' if result.is_valid else 'FAIL'}")

    # Negative examples
    negative_samples = [
        create_negative_missing_field(),
        create_negative_invalid_version(),
        create_negative_contract_conflict(),
        create_negative_missing_input_contract(),
        create_negative_dependency_count_mismatch(),
    ]

    for i, (spec, name) in enumerate(negative_samples, 1):
        print(f"\n[Negative Example {i}] {name}...")
        sample_dir = negative_dir / f"{i}_{name}"
        sample_dir.mkdir(exist_ok=True)

        result = validator.validate_and_report(
            spec,
            sample_dir / "normalized_skill_spec.json"
        )
        # Save validation report
        result.save(sample_dir / "validation_report.json")
        print(f"  Created: {sample_dir}/normalized_skill_spec.json")
        print(f"  Created: {sample_dir}/validation_report.json")
        print(f"  Result: {'PASS' if result.is_valid else 'FAIL'} ({len(result.failures)} errors)")

    # Summary
    print("\n" + "=" * 60)
    print("T3 Sample Generation Complete")
    print(f"  Positive examples: {positive_dir}")
    print(f"  Negative examples: {negative_dir}")
    print(f"  Total: 1 positive + {len(negative_samples)} negative")
    print("=" * 60)


if __name__ == "__main__":
    main()
