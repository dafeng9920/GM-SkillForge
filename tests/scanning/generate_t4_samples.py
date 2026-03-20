"""
Generate T4 Rule Samples and Evidence

This script generates:
1. Rule sample library with expected hits
2. Evidence reports for each sample
3. Summary report

Run:
    cd d:/GM-SkillForge
    python tests/scanning/generate_t4_samples.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent.parent
skillforge_src = project_root / "skillforge" / "src"
contracts_path = skillforge_src / "contracts"

sys.path.insert(0, str(skillforge_src))
sys.path.insert(0, str(contracts_path))

from contracts.rule_scanner import RuleScanner, BoundaryChecker, RuleCode


# ============================================================================
# Sample Skills
# ============================================================================
SAMPLE_SKILLS = {
    "eval_usage": {
        "name": "eval_usage",
        "code": '''"""Skill with eval usage - CRITICAL violation."""

SKILL_NAME = "eval_usage"
SKILL_VERSION = "1.0.0"

def execute_untrusted_code(user_input):
    """E421: eval without sanitization - CRITICAL"""
    return eval(user_input)
''',
        "expected_hits": [
            {"code": "E421_EVAL_OR_EXEC_USED", "severity": "CRITICAL", "line": 9}
        ]
    },

    "subprocess_shell": {
        "name": "subprocess_shell",
        "code": '''"""Skill with subprocess shell=True - CRITICAL violation."""

SKILL_NAME = "subprocess_shell"
SKILL_VERSION = "1.0.0"

import subprocess

def run_user_command(cmd):
    """E405: subprocess with shell=True - CRITICAL"""
    return subprocess.run(cmd, shell=True)
''',
        "expected_hits": [
            {"code": "E405_SYSTEM_COMMAND_without_SANITIZATION", "severity": "CRITICAL", "line": 10}
        ]
    },

    "sql_injection": {
        "name": "sql_injection",
        "code": '''"""Skill with SQL injection risk - CRITICAL violation."""

SKILL_NAME = "sql_injection"
SKILL_VERSION = "1.0.0"

def get_user_data(user_id):
    """E413: SQL injection via string formatting - CRITICAL"""
    return execute("SELECT * FROM users WHERE id=%s" % user_id)
''',
        "expected_hits": [
            {"code": "E413_DATABASE_QUERY_without_PARAMETERIZATION", "severity": "CRITICAL", "line": 8}
        ]
    },

    "unsafe_pickle": {
        "name": "unsafe_pickle",
        "code": '''"""Skill with unsafe pickle - HIGH violation."""

SKILL_NAME = "unsafe_pickle"
SKILL_VERSION = "1.0.0"

import pickle

def load_data(data_string):
    """E422: unsafe pickle deserialization - HIGH"""
    return pickle.loads(data_string)
''',
        "expected_hits": [
            {"code": "E422_UNSAFE_DESERIALIZATION", "severity": "HIGH", "line": 10}
        ]
    },

    "http_no_timeout": {
        "name": "http_no_timeout",
        "code": '''"""Skill with HTTP request without timeout - MEDIUM violation."""

SKILL_NAME = "http_no_timeout"
SKILL_VERSION = "1.0.0"

import requests

def fetch_api_data(url):
    """E412: HTTP request without error handling - LOW"""
    response = requests.get(url)
    return response.json()
''',
        "expected_hits": [
            {"code": "E412_HTTP_REQUEST_without_ERROR_HANDLING", "severity": "LOW", "line": 10}
        ]
    },

    "clean_skill": {
        "name": "clean_skill",
        "code": '''"""Clean skill following best practices."""

SKILL_NAME = "clean_skill"
SKILL_VERSION = "1.0.0"

def process_data(data):
    """Process data with validation"""
    if not isinstance(data, dict):
        raise ValueError("Invalid input")
    return {"result": data.get("value", 0) * 2}
''',
        "expected_hits": []
    }
}


# ============================================================================
# Generate Samples
# ============================================================================
def generate_samples():
    """Generate rule samples and evidence reports."""
    evidence_dir = project_root / "run" / "T4_evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    samples_dir = evidence_dir / "rule_samples"
    samples_dir.mkdir(exist_ok=True)

    scanner = RuleScanner()
    summary = {
        "rule_set_version": RuleScanner.RULES[0].code.split("_")[0] + "_SERIES",
        "total_samples": len(SAMPLE_SKILLS),
        "samples": []
    }

    for sample_id, sample_data in SAMPLE_SKILLS.items():
        print(f"Generating sample: {sample_id}")

        # Create sample skill directory
        sample_dir = samples_dir / sample_id
        sample_dir.mkdir(exist_ok=True)

        # Write sample code
        (sample_dir / f"{sample_data['name']}.py").write_text(sample_data["code"])

        # Run scan
        result = scanner.scan_skill(sample_dir)

        # Save report
        report_path = sample_dir / "rule_scan_report.json"
        result.save(report_path)

        # Record in summary
        summary["samples"].append({
            "sample_id": sample_id,
            "name": sample_data["name"],
            "expected_hits": sample_data["expected_hits"],
            "actual_hits": result.total_hits,
            "critical_hits": len(result.critical_hits),
            "high_hits": len(result.high_hits),
            "report_path": f"rule_samples/{sample_id}/rule_scan_report.json"
        })

    # Save summary
    summary_path = evidence_dir / "rule_sample_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nGenerated {len(SAMPLE_SKILLS)} rule samples")
    print(f"Summary: {summary_path}")

    return summary


# ============================================================================
# Verify Expected Hits
# ============================================================================
def verify_expected_hits():
    """Verify that samples produce expected hits."""
    print("\n" + "=" * 60)
    print("Verifying Expected Hits")
    print("=" * 60)

    scanner = RuleScanner()
    all_passed = True

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        for sample_id, sample_data in SAMPLE_SKILLS.items():
            # Create sample file
            sample_dir = tmpdir / sample_id
            sample_dir.mkdir()
            (sample_dir / f"{sample_data['name']}.py").write_text(sample_data["code"])

            # Run scan
            result = scanner.scan_skill(sample_dir)
            hit_codes = [h.rule_code for h in result.get_all_hits()]
            expected_codes = [h["code"] for h in sample_data["expected_hits"]]

            # Check if expected hits were found
            passed = True
            for expected in sample_data["expected_hits"]:
                if expected["code"] not in hit_codes:
                    passed = False
                    print(f"  FAIL: {sample_id} - Expected {expected['code']} not found")

            if passed and len(expected_codes) > 0:
                print(f"  PASS: {sample_id} - All expected hits found")
            elif len(expected_codes) == 0:
                print(f"  PASS: {sample_id} - No hits expected (clean)")

            if not passed:
                all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("T4 Rule Sample Generator")
    print("=" * 60)

    # Verify expected hits first
    if verify_expected_hits():
        print("\n✓ All expected hits verified")
    else:
        print("\n✗ Some expected hits not found")
        sys.exit(1)

    # Generate samples
    print("\nGenerating rule samples...")
    summary = generate_samples()
    print("\n✓ Rule samples generated successfully")
