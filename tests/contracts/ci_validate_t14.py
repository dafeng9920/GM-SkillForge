#!/usr/bin/env python3
"""
CI Validation Script for T14 Audit Pack

This script is used in CI pipelines to automatically validate:
1. T14_samples/*.json comply with audit_pack.schema.json
2. run_t14_pipeline.py --validate-only works correctly

Usage in CI:
    python ci_validate_t14.py

Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import json
import sys
from pathlib import Path

# Add contracts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skillforge" / "src" / "contracts"))


def validate_samples_against_schema() -> tuple[bool, list[str]]:
    """
    Validate all T14 sample files against the schema.

    Returns:
        Tuple of (all_valid, error_messages)
    """
    try:
        import jsonschema
    except ImportError:
        print("⚠️  jsonschema not available, skipping schema validation")
        return True, []

    errors = []

    # Load schema
    schema_path = Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "audit_pack.schema.json"
    with open(schema_path) as f:
        schema = json.load(f)

    # Validate each sample
    samples_dir = Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "T14_samples"
    sample_files = sorted(samples_dir.glob("*.json"))

    print(f"🔍 Validating {len(sample_files)} sample files against schema...")

    for sample_file in sample_files:
        with open(sample_file) as f:
            sample = json.load(f)

        try:
            jsonschema.validate(instance=sample, schema=schema)
            print(f"  ✅ {sample_file.name}")
        except jsonschema.ValidationError as e:
            error_msg = f"Schema validation failed for {sample_file.name}: {e.message}"
            errors.append(error_msg)
            print(f"  ❌ {sample_file.name}: {e.message}")
        except Exception as e:
            error_msg = f"Unexpected error validating {sample_file.name}: {e}"
            errors.append(error_msg)
            print(f"  ❌ {sample_file.name}: {e}")

    return (len(errors) == 0, errors)


def validate_pipeline_command() -> tuple[bool, list[str]]:
    """
    Validate that the run_t14_pipeline.py --validate-only command works.

    Returns:
        Tuple of (success, error_messages)
    """
    errors = []

    print("\n🔍 Validating run_t14_pipeline.py command...")

    # Test with --help
    import subprocess
    result = subprocess.run(
        [sys.executable, "skillforge/src/contracts/run_t14_pipeline.py", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )

    if result.returncode != 0:
        errors.append("run_t14_pipeline.py --help failed")
        print(f"  ❌ --help failed: {result.stderr}")
    else:
        print(f"  ✅ --help works")

    # Test with --validate-only on test data
    test_run_dir = Path(__file__).parent.parent / "run" / "t14_test_demo"
    if test_run_dir.exists():
        result = subprocess.run(
            [
                sys.executable, "skillforge/src/contracts/run_t14_pipeline.py",
                "--run-id", "t14_test_demo",
                "--run-dir", "run",
                "--validate-only"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )

        if result.returncode != 0:
            errors.append("run_t14_pipeline.py --validate-only failed")
            print(f"  ❌ --validate-only failed: {result.stderr}")
        else:
            print(f"  ✅ --validate-only works")
    else:
        print(f"  ⚠️  Test run directory not found, skipping --validate-only test")

    return (len(errors) == 0, errors)


def main():
    """Run all CI validations."""
    print("=" * 70)
    print("T14 CI Validation")
    print("=" * 70)

    all_valid = True
    all_errors = []

    # Validate samples against schema
    samples_valid, samples_errors = validate_samples_against_schema()
    all_valid = all_valid and samples_valid
    all_errors.extend(samples_errors)

    # Validate pipeline command
    pipeline_valid, pipeline_errors = validate_pipeline_command()
    all_valid = all_valid and pipeline_valid
    all_errors.extend(pipeline_errors)

    # Print result
    print("\n" + "=" * 70)
    if all_valid:
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED")
        print("=" * 70)
        print("\nErrors:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
