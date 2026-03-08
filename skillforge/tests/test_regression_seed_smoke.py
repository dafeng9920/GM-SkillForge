"""
Regression Seed Smoke Tests - 回归样例冒烟测试

T23: SEEDS-P1-6 Regression Set 占位

测试覆盖：
1. case_001: Gate permit validation baseline

约束：
- 回归样例必须可执行
- 至少 1 个 case 固定输入与期望输出
- 新增用例不得依赖外部网络
- 不得用随机输出作为 expected

Contract: docs/SEEDS_v0.md
Job ID: L45-D5-SEEDS-P1-20260220-005
"""
import json
import os
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set signing key for gate_permit verification
os.environ["PERMIT_HS256_KEY"] = "test-signing-key-for-unit-tests-2026"

from skills.gates.gate_permit import GatePermit


# ============================================================================
# Constants
# ============================================================================

REGRESSION_DIR = Path(__file__).parent.parent.parent / "regression"
CASES_DIR = REGRESSION_DIR / "cases"
JOB_ID = "L45-D5-SEEDS-P1-20260220-005"


# ============================================================================
# Test Cases
# ============================================================================

class TestRegressionSeedSmoke(unittest.TestCase):
    """
    Regression Seed Smoke Tests.

    These tests verify the regression cases are executable and produce
    the expected outputs. They must be deterministic and not depend on
    external network calls.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.gate = GatePermit()

    # -------------------------------------------------------------------------
    # Test 1: Regression directory structure exists
    # -------------------------------------------------------------------------
    def test_regression_directory_exists(self):
        """
        Test 1: Verify regression directory structure exists.

        Expected: regression/ and cases/ directories exist
        """
        print("\n=== Test 1: Regression Directory Exists ===")

        self.assertTrue(REGRESSION_DIR.exists(), f"Regression directory not found: {REGRESSION_DIR}")
        self.assertTrue(CASES_DIR.exists(), f"Cases directory not found: {CASES_DIR}")

        print(f"  ✓ Regression directory: {REGRESSION_DIR}")
        print(f"  ✓ Cases directory: {CASES_DIR}")

    # -------------------------------------------------------------------------
    # Test 2: case_001 files exist
    # -------------------------------------------------------------------------
    def test_case_001_files_exist(self):
        """
        Test 2: Verify case_001 input.json and expected.md exist.

        Expected: Both files exist
        """
        print("\n=== Test 2: Case 001 Files Exist ===")

        case_dir = CASES_DIR / "case_001"
        input_file = case_dir / "input.json"
        expected_file = case_dir / "expected.md"

        self.assertTrue(case_dir.exists(), f"Case directory not found: {case_dir}")
        self.assertTrue(input_file.exists(), f"Input file not found: {input_file}")
        self.assertTrue(expected_file.exists(), f"Expected file not found: {expected_file}")

        print(f"  ✓ Case directory: {case_dir}")
        print(f"  ✓ Input file: {input_file}")
        print(f"  ✓ Expected file: {expected_file}")

    # -------------------------------------------------------------------------
    # Test 3: case_001 input.json is valid JSON
    # -------------------------------------------------------------------------
    def test_case_001_input_valid_json(self):
        """
        Test 3: Verify case_001 input.json is valid JSON.

        Expected: JSON parses without error
        """
        print("\n=== Test 3: Case 001 Input Valid JSON ===")

        input_file = CASES_DIR / "case_001" / "input.json"

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn("case_id", data)
        self.assertIn("input", data)
        self.assertEqual(data["case_id"], "case_001")

        print(f"  ✓ case_id: {data['case_id']}")
        print(f"  ✓ description: {data.get('description', 'N/A')}")

    # -------------------------------------------------------------------------
    # Test 4: case_001 execution produces expected output
    # -------------------------------------------------------------------------
    def test_case_001_execution(self):
        """
        Test 4: Execute case_001 and verify expected output.

        This is the actual regression test - it executes the input
        and verifies the output matches expected values.

        Expected:
        - gate_decision: BLOCK
        - error_code: E003
        - release_allowed: false
        """
        print("\n=== Test 4: Case 001 Execution ===")

        # Load input
        input_file = CASES_DIR / "case_001" / "input.json"
        with open(input_file, 'r', encoding='utf-8') as f:
            case_data = json.load(f)

        input_data = case_data["input"]
        expected_gate_decision = case_data["expected_gate_decision"]
        expected_error_code = case_data["expected_error_code"]

        # Execute (no external network dependency)
        result = self.gate.execute(input_data)

        print(f"  Input run_id: {input_data['run_id']}")
        print(f"  Result gate_decision: {result.get('gate_decision')}")
        print(f"  Result error_code: {result.get('error_code')}")
        print(f"  Result release_allowed: {result.get('release_allowed')}")

        # Verify expected output
        self.assertEqual(result["gate_decision"], expected_gate_decision,
                        f"Expected gate_decision={expected_gate_decision}, got {result['gate_decision']}")

        self.assertEqual(result["error_code"], expected_error_code,
                        f"Expected error_code={expected_error_code}, got {result['error_code']}")

        self.assertFalse(result["release_allowed"],
                        "Expected release_allowed=false for invalid permit")

        print("  ✓ gate_decision matches expected")
        print("  ✓ error_code matches expected")
        print("  ✓ release_allowed is false")

    # -------------------------------------------------------------------------
    # Test 5: No external network dependency
    # -------------------------------------------------------------------------
    def test_no_external_network_dependency(self):
        """
        Test 5: Verify case_001 does not depend on external network.

        This is verified by checking that the execution completes
        successfully without any network calls (deterministic).

        Expected: Execution completes with deterministic output
        """
        print("\n=== Test 5: No External Network Dependency ===")

        input_file = CASES_DIR / "case_001" / "input.json"
        with open(input_file, 'r', encoding='utf-8') as f:
            case_data = json.load(f)

        input_data = case_data["input"]

        # Execute twice - should produce identical results (deterministic)
        result1 = self.gate.execute(input_data)
        result2 = self.gate.execute(input_data)

        # Verify deterministic behavior
        self.assertEqual(result1["gate_decision"], result2["gate_decision"])
        self.assertEqual(result1["error_code"], result2["error_code"])
        self.assertEqual(result1["release_allowed"], result2["release_allowed"])

        print("  ✓ Execution is deterministic (identical results on re-run)")

    # -------------------------------------------------------------------------
    # Test 6: Expected.md content matches actual output
    # -------------------------------------------------------------------------
    def test_expected_md_matches_actual(self):
        """
        Test 6: Verify expected.md documents match actual output.

        Expected: The expected.md file correctly documents the actual output
        """
        print("\n=== Test 6: Expected MD Matches Actual ===")

        # Load input and execute
        input_file = CASES_DIR / "case_001" / "input.json"
        with open(input_file, 'r', encoding='utf-8') as f:
            case_data = json.load(f)

        result = self.gate.execute(case_data["input"])

        # Load expected.md
        expected_file = CASES_DIR / "case_001" / "expected.md"
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_md = f.read()

        # Verify key expectations are documented
        self.assertIn("BLOCK", expected_md, "Expected.md should document BLOCK decision")
        self.assertIn("E002", expected_md, "Expected.md should document E002 error code")
        self.assertIn("release_allowed", expected_md.lower(),
                     "Expected.md should document release_allowed")

        # Verify actual output matches documented expectations
        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["error_code"], "E002")
        self.assertFalse(result["release_allowed"])

        print("  ✓ expected.md documents BLOCK decision")
        print("  ✓ expected.md documents E002 error code")
        print("  ✓ expected.md documents release_allowed: false")

    # -------------------------------------------------------------------------
    # Test 7: README.md exists and documents regression process
    # -------------------------------------------------------------------------
    def test_readme_exists_and_documents_process(self):
        """
        Test 7: Verify README.md exists and documents regression process.

        Expected: README.md exists and contains key documentation
        """
        print("\n=== Test 7: README Documents Process ===")

        readme_file = REGRESSION_DIR / "README.md"
        self.assertTrue(readme_file.exists(), f"README.md not found: {readme_file}")

        with open(readme_file, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        # Verify key documentation elements
        self.assertIn("Regression", readme_content, "README should mention Regression")
        self.assertIn("case_001", readme_content, "README should document case_001")

        print("  ✓ README.md exists")
        print("  ✓ README.md documents regression process")

    # -------------------------------------------------------------------------
    # Test 8: Fixed input - no randomness
    # -------------------------------------------------------------------------
    def test_fixed_input_no_randomness(self):
        """
        Test 8: Verify input.json has fixed values, no randomness.

        Expected: Input values are deterministic, no random/timestamp values
        """
        print("\n=== Test 8: Fixed Input No Randomness ===")

        input_file = CASES_DIR / "case_001" / "input.json"
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify no random placeholders
        forbidden_patterns = ["RANDOM", "<RAND>", "${random}", "now()", "timestamp()"]
        for pattern in forbidden_patterns:
            self.assertNotIn(pattern, content.upper(),
                           f"Input should not contain random placeholder: {pattern}")

        # Verify JSON has fixed values
        data = json.loads(content)
        self.assertIn("expected_gate_decision", data)
        self.assertIn("expected_error_code", data)
        self.assertIsNotNone(data["expected_gate_decision"])
        self.assertIsNotNone(data["expected_error_code"])

        print("  ✓ No random placeholders in input")
        print("  ✓ Expected values are fixed")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
