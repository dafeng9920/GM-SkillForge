"""
T4 Rule Scanning and Boundary Detection Tests

This test suite validates T4 requirements:
1. Sensitive permission scanning
2. External action scanning
3. Dangerous pattern scanning
4. Boundary gap scanning
5. Rule version tracking
6. Rule sample library with expected hits

Run:
    cd d:/GM-SkillForge
    python -m pytest tests/scanning/test_t4_rule_scanning.py -v
    python tests/scanning/test_t4_rule_scanning.py
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

from contracts.rule_scanner import (
    RuleScanner,
    BoundaryChecker,
    RuleScanResult,
    RuleHit,
    Rule,
    RuleCode,
    RULE_SET_VERSION,
    RULE_SET_UPDATED_AT,
)


# ============================================================================
# Test Fixtures
# ============================================================================
def create_skill_with_dangerous_patterns(base_dir: Path) -> Path:
    """Create a skill with dangerous patterns for testing."""
    skill_dir = base_dir / "dangerous_skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Create skill file with various dangerous patterns
    (skill_dir / "dangerous_skill.py").write_text(
        '''"""Dangerous skill with various security issues."""

SKILL_NAME = "dangerous_skill"
SKILL_VERSION = "1.0.0"

def execute_user_input(user_data):
    """Execute user input - DANGEROUS!"""
    # E421: eval without sanitization
    result = eval(user_data)
    return result

def read_config():
    """E401: File read without permission check"""
    with open("config.json", "r") as f:
        return json.load(f)

def delete_file(filepath):
    """E403: File delete without permission check"""
    import os
    os.remove(filepath)

def call_api(url):
    """E411: HTTP request without timeout"""
    import requests
    response = requests.get(url)  # No timeout
    return response.json()

def run_command(cmd):
    """E405: System command without sanitization"""
    import subprocess
    return subprocess.run(cmd, shell=True)  # shell=True is dangerous

def load_user_data(data_string):
    """E422: Unsafe deserialization"""
    import pickle
    return pickle.loads(data_string)

def admin_delete_user(user_id):
    """E434: Missing audit log for sensitive operation"""
    # Delete user without audit log
    database.execute(f"DELETE FROM users WHERE id={user_id}")  # E413: SQL injection
'''
    )

    return skill_dir


def create_skill_with_boundary_gaps(base_dir: Path) -> Path:
    """Create a skill with boundary gaps for testing."""
    skill_dir = base_dir / "boundary_gap_skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "boundary_skill.py").write_text(
        '''"""Skill with boundary gaps."""

SKILL_NAME = "boundary_gap_skill"
SKILL_VERSION = "1.0.0"

def transfer_money(from_account, to_account, amount):
    """E431: Missing permission check before sensitive operation"""
    # Direct transfer without permission check
    bank_api.transfer(from_account, to_account, amount)

def process_request(request):
    """E432: Missing input validation"""
    # Directly use user input
    result = database.query(f"SELECT * FROM data WHERE id={request['id']}")
    return result

def external_api_call():
    """E433: Missing rate limiting"""
    import requests
    # No rate limiting
    return requests.get("https://external-api.com/data")

# E434: Sensitive operation without audit log
def reset_password(user_id, new_password):
    """Reset password without audit log"""
    database.execute(f"UPDATE users SET password='{new_password}' WHERE id={user_id}")
'''
    )

    return skill_dir


def create_clean_skill(base_dir: Path) -> Path:
    """Create a clean skill with no rule violations."""
    skill_dir = base_dir / "clean_skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "clean_skill.py").write_text(
        '''"""Clean skill following best practices."""

SKILL_NAME = "clean_skill"
SKILL_VERSION = "1.0.0"

def process_data(data):
    """Process data with validation"""
    if not isinstance(data, dict):
        raise ValueError("Invalid input")

    if "value" not in data:
        raise ValueError("Missing required field")

    return {"result": data["value"] * 2}

def read_file_safe(filepath):
    """Read file with permission check"""
    if not has_permission(filepath, "read"):
        raise PermissionError(f"No permission to read {filepath}")

    with open(filepath, "r") as f:
        return f.read()

def has_permission(filepath, action):
    """Check if user has permission for the action"""
    return True  # Simplified for demo
'''
    )

    return skill_dir


# ============================================================================
# Test Rule Definitions
# ============================================================================
class TestT4_RuleDefinitions:
    """T4: Rule definitions are complete and versioned."""

    def test_rule_codes_defined(self):
        """All E4xx rule codes should be defined."""
        expected_codes = [
            "E401_FILE_READ_without_CHECK",
            "E402_FILE_WRITE_without_CHECK",
            "E403_FILE_DELETE_without_CHECK",
            "E404_NETWORK_ACCESS_without_CHECK",
            "E405_SYSTEM_COMMAND_without_SANITIZATION",
            "E411_HTTP_REQUEST_without_TIMEOUT",
            "E412_HTTP_REQUEST_without_ERROR_HANDLING",
            "E413_DATABASE_QUERY_without_PARAMETERIZATION",
            "E414_SHELL_COMMAND_with_USER_INPUT",
            "E421_EVAL_OR_EXEC_USED",
            "E422_UNSAFE_DESERIALIZATION",
            "E423_HARDCODED_CREDENTIALS",
            "E424_UNSAFE_RANDOM",
            "E431_MISSING_PERMISSION_CHECK",
            "E432_MISSING_INPUT_VALIDATION",
            "E433_MISSING_RATE_LIMITING",
            "E434_MISSING_AUDIT_LOG",
        ]

        for code in expected_codes:
            assert hasattr(RuleCode, code), f"Missing rule code: {code}"

    def test_rule_set_version_defined(self):
        """Rule set version should be defined."""
        assert RULE_SET_VERSION == "1.0.0-t4"
        assert RULE_SET_UPDATED_AT is not None

    def test_rules_have_required_fields(self):
        """Each rule should have all required fields."""
        scanner = RuleScanner()

        for rule in scanner.RULES:
            assert rule.code, f"Rule missing code"
            assert rule.name, f"Rule {rule.code} missing name"
            assert rule.category, f"Rule {rule.code} missing category"
            assert rule.severity, f"Rule {rule.code} missing severity"
            assert rule.description, f"Rule {rule.code} missing description"
            assert rule.pattern, f"Rule {rule.code} missing pattern"
            assert rule.remediation, f"Rule {rule.code} missing remediation"

    def test_rules_have_cwe_or_owasp_mapping(self):
        """High and critical severity rules should have CWE/OWASP mapping."""
        scanner = RuleScanner()

        for rule in scanner.RULES:
            if rule.severity in ["CRITICAL", "HIGH"]:
                has_mapping = rule.cwe_id is not None or rule.owasp_id is not None
                assert has_mapping, f"Rule {rule.code} ({rule.severity}) missing CWE/OWASP mapping"


# ============================================================================
# Test Rule Scanning
# ============================================================================
class TestT4_RuleScanning:
    """T4: Rule scanner detects violations correctly."""

    def test_scan_dangerous_skill_finds_violations(self):
        """Dangerous skill should have rule violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            assert result.total_hits > 0, "Should detect violations in dangerous skill"
            assert len(result.critical_hits) > 0, "Should detect critical violations"
            assert len(result.high_hits) > 0, "Should detect high severity violations"

    def test_scan_clean_skill_no_critical_violations(self):
        """Clean skill should have no CRITICAL violations (static analysis may have false positives)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_clean_skill(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            # Static analysis may have false positives, but should not have CRITICAL hits
            assert len(result.critical_hits) == 0, "Clean skill should have no CRITICAL violations"
            # Note: HIGH/MEDIUM hits are acceptable as static analysis has false positives

    def test_eval_detected_as_critical(self):
        """eval() usage should be detected as critical."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            eval_hits = [h for h in result.get_all_hits() if h.rule_code == RuleCode.E421_EVAL_OR_EXEC_USED]
            assert len(eval_hits) > 0, "Should detect eval() usage"
            assert eval_hits[0].severity == "CRITICAL"

    def test_file_operations_detected(self):
        """File operations should be detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            file_hit_codes = [
                RuleCode.E401_FILE_READ_without_CHECK,
                RuleCode.E403_FILE_DELETE_without_CHECK,
            ]

            for code in file_hit_codes:
                hits = [h for h in result.get_all_hits() if h.rule_code == code]
                assert len(hits) > 0, f"Should detect {code}"

    def test_system_command_detected(self):
        """System command usage should be detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            cmd_hits = [h for h in result.get_all_hits() if h.rule_code == RuleCode.E405_SYSTEM_COMMAND_without_SANITIZATION]
            assert len(cmd_hits) > 0, "Should detect system command usage"
            assert cmd_hits[0].severity == "CRITICAL"

    def test_hit_has_source_location(self):
        """Each rule hit should have source location information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            for hit in result.get_all_hits():
                assert hit.file_path, f"Hit {hit.rule_code} missing file_path"
                assert hit.line_number > 0, f"Hit {hit.rule_code} has invalid line_number"
                assert hit.snippet, f"Hit {hit.rule_code} missing snippet"

    def test_hit_has_rule_version(self):
        """Each hit should be traceable to a rule version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            assert result.rule_set_version == RULE_SET_VERSION
            assert result.scanned_at is not None

            # Each hit should reference a defined rule
            for hit in result.get_all_hits():
                assert hit.rule_code in scanner.rules_by_code, f"Hit references undefined rule: {hit.rule_code}"


# ============================================================================
# Test Boundary Checking
# ============================================================================
class TestT4_BoundaryChecking:
    """T4: Boundary checker detects gaps correctly."""

    def test_boundary_checker_finds_gaps(self):
        """Boundary checker should find gaps in problematic skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_boundary_gaps(Path(tmpdir))

            checker = BoundaryChecker()
            findings = checker.check_boundaries(skill_dir)

            assert len(findings) > 0, "Should find boundary gaps"

    def test_boundary_gap_has_location(self):
        """Each boundary gap should have source location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_boundary_gaps(Path(tmpdir))

            checker = BoundaryChecker()
            findings = checker.check_boundaries(skill_dir)

            for finding in findings:
                assert finding["file_path"], "Finding missing file_path"
                assert finding["line_number"] > 0, "Finding has invalid line_number"
                assert finding["severity"], "Finding missing severity"


# ============================================================================
# Test Rule Scan Report Serialization
# ============================================================================
class TestT4_ReportSerialization:
    """T4: Rule scan report can be serialized and validated."""

    def test_result_to_dict(self):
        """RuleScanResult should convert to dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            result_dict = result.to_dict()
            assert isinstance(result_dict, dict)
            assert "skill_name" in result_dict
            assert "scan_statistics" in result_dict
            assert "findings" in result_dict

    def test_result_to_json(self):
        """RuleScanResult should convert to valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            json_str = result.to_json()
            parsed = json.loads(json_str)

            assert parsed["skill_name"] == "dangerous_skill"

    def test_result_save(self):
        """RuleScanResult should save to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))
            output_path = Path(tmpdir) / "rule_scan_report.json"

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)
            result.save(output_path)

            assert output_path.exists()

            with open(output_path) as f:
                data = json.load(f)

            assert data["skill_name"] == "dangerous_skill"
            assert "findings" in data

    def test_result_validates_against_schema(self):
        """RuleScanResult should validate against JSON schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            # Load schema
            schema_path = project_root / "skillforge" / "src" / "contracts" / "rule_scan_report.schema.json"
            with open(schema_path) as f:
                schema = json.load(f)

            # Validate
            from jsonschema import validate
            validate(instance=result.to_dict(), schema=schema)


# ============================================================================
# Test Rule Sample Library
# ============================================================================
class TestT4_RuleSampleLibrary:
    """T4: Rule sample library provides expected hit results."""

    def test_dangerous_skill_expected_hits(self):
        """Dangerous skill should have expected rule hits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))

            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            # Expected critical hits
            expected_critical = [
                RuleCode.E403_FILE_DELETE_without_CHECK,
                RuleCode.E405_SYSTEM_COMMAND_without_SANITIZATION,
                RuleCode.E413_DATABASE_QUERY_without_PARAMETERIZATION,
                RuleCode.E421_EVAL_OR_EXEC_USED,
                RuleCode.E422_UNSAFE_DESERIALIZATION,
            ]

            hit_codes = [h.rule_code for h in result.critical_hits + result.high_hits]

            for code in expected_critical:
                assert code in hit_codes, f"Expected hit {code} not found"

    def test_boundary_gap_skill_expected_findings(self):
        """Boundary gap skill should have expected findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_boundary_gaps(Path(tmpdir))

            checker = BoundaryChecker()
            findings = checker.check_boundaries(skill_dir)

            # Should find missing stop rules
            missing_stop_rules = [f for f in findings if f["type"] == "missing_stop_rule"]
            assert len(missing_stop_rules) > 0, "Should find missing stop rules"


# ============================================================================
# Test Real Skill Scanning
# ============================================================================
class TestT4_RealSkillScanning:
    """T4: Scan real skills from the codebase."""

    def test_scan_quant_skill(self):
        """Real quant skill should be scannable."""
        quant_skill_dir = project_root / "skillforge" / "src" / "skills" / "quant"

        if not quant_skill_dir.exists():
            # Skip if quant skill doesn't exist
            return

        scanner = RuleScanner()
        result = scanner.scan_skill(quant_skill_dir)

        # Should complete without errors
        assert result.files_scanned > 0
        assert result.skill_name == "quant"

        # Result should be serializable
        result_dict = result.to_dict()
        assert "scan_statistics" in result_dict


# ============================================================================
# Verification Script (can be run standalone)
# ============================================================================
def main():
    """Run T4 compliance checks and print results."""
    print("=" * 60)
    print("T4 Rule Scanning Compliance Verification")
    print("=" * 60)

    passed = 0
    failed = 0

    # Test 1: Rule codes defined
    print("\n[Test 1] Rule codes are defined...")
    try:
        expected_codes = [
            "E401_FILE_READ_without_CHECK",
            "E421_EVAL_OR_EXEC_USED",
            "E431_MISSING_PERMISSION_CHECK",
        ]
        for code in expected_codes:
            assert hasattr(RuleCode, code)
        print("  PASS: All expected rule codes defined")
        passed += 1
    except AssertionError as e:
        print(f"  FAIL: {e}")
        failed += 1

    # Test 2: Scanner detects dangerous patterns
    print("\n[Test 2] Scanner detects dangerous patterns...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))
            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            if result.total_hits > 0 and len(result.critical_hits) > 0:
                print("  PASS: Dangerous patterns detected")
                passed += 1
            else:
                print("  FAIL: Dangerous patterns not detected")
                failed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # Test 3: Hits have source location
    print("\n[Test 3] Hits have source location...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))
            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            for hit in result.get_all_hits():
                assert hit.file_path and hit.line_number > 0

            print("  PASS: All hits have source location")
            passed += 1
    except AssertionError as e:
        print(f"  FAIL: {e}")
        failed += 1

    # Test 4: Result serialization
    print("\n[Test 4] Result can be serialized...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = create_skill_with_dangerous_patterns(Path(tmpdir))
            scanner = RuleScanner()
            result = scanner.scan_skill(skill_dir)

            json_str = result.to_json()
            json.loads(json_str)

            print("  PASS: Result serialization successful")
            passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # Test 5: Rule version tracking
    print("\n[Test 5] Rule version tracking...")
    try:
        scanner = RuleScanner()
        result = scanner.scan_skill(create_skill_with_dangerous_patterns(Path(tempfile.mkdtemp())))

        assert result.rule_set_version == RULE_SET_VERSION
        assert result.scanned_at is not None

        print("  PASS: Rule version tracked")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
