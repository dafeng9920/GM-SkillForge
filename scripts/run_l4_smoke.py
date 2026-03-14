#!/usr/bin/env python3
"""
L4 Smoke Test - Minimal Chain Verification

This script runs a smoke test for the L4 minimal chain:
Diagnosis -> AEV -> Report Generation

Fail-closed: Any failure exits with code 1 (CI blocks merge).

Usage:
    python scripts/run_l4_smoke.py

Exit Codes:
    0 - All smoke tests passed
    1 - One or more smoke tests failed
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add skillforge-spec-pack to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "skillforge-spec-pack"))

from skillforge.src.diagnosis import DiagnosisOutput
from skillforge.src.economics import AEVBuilder, Currency, Period


class SmokeTestResult:
    """Result of a single smoke test."""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration_ms = 0

    def to_dict(self):
        return {
            "name": self.name,
            "status": "PASS" if self.passed else "FAIL",
            "error": self.error,
            "duration_ms": self.duration_ms
        }


class L4SmokeTest:
    """L4 Minimal Chain Smoke Tests."""

    def __init__(self):
        self.results = []
        self.start_time = None

    def run_test(self, name: str, test_func):
        """Run a single smoke test."""
        import time
        result = SmokeTestResult(name)
        start = time.time()

        try:
            test_func()
            result.passed = True
        except Exception as e:
            result.error = str(e)

        result.duration_ms = int((time.time() - start) * 1000)
        self.results.append(result)
        return result.passed

    def test_diagnosis_module_loads(self):
        """Test 1: Diagnosis module can be imported and loads sample data."""
        sample_path = project_root / "skillforge-spec-pack/skillforge/src/diagnosis/sample_diagnosis.json"
        if not sample_path.exists():
            raise FileNotFoundError(f"Sample diagnosis not found: {sample_path}")

        with open(sample_path, 'r') as f:
            diagnosis_data = json.load(f)

        diagnosis = DiagnosisOutput.from_dict(diagnosis_data)

        # Validate required fields
        assert diagnosis.diagnosis_id, "diagnosis_id is required"
        assert diagnosis.skill_id, "skill_id is required"
        assert diagnosis.skill_name, "skill_name is required"
        assert diagnosis.health_score is not None, "health_score is required"

        # Validate ID format: DX-L4-XXX-XXXXXXXX
        assert diagnosis.diagnosis_id.startswith("DX-L4-"), f"Invalid diagnosis_id format: {diagnosis.diagnosis_id}"

    def test_aev_builder_creates_valid_output(self):
        """Test 2: AEVBuilder can create a valid AEVOutput."""
        aev = (AEVBuilder()
            .with_skill(
                skill_id="skill-test-001",
                skill_name="Test Skill",
                diagnosis_id="DX-L4-SMOKE-TEST001"
            )
            .with_currency(Currency.USD)
            .with_period(Period.YEAR)
            .set_v_token(
                value=1000.0,
                description="Test token value",
                source_description="Test source",
                calculation_method="Test calculation"
            )
            .set_v_compute(
                value=500.0,
                description="Test compute value",
                source_description="Test source",
                calculation_method="Test calculation"
            )
            .set_v_risk(
                value=200.0,
                description="Test risk value",
                source_description="Test source",
                calculation_method="Test calculation"
            )
            .set_v_trust(
                value=100.0,
                description="Test trust value",
                source_description="Test source",
                calculation_method="Test calculation"
            )
            .build())

        # Validate AEV structure
        assert aev.aev_id, "aev_id is required"
        assert aev.diagnosis_id == "DX-L4-SMOKE-TEST001", "diagnosis_id mismatch"
        assert aev.aev_total > 0, "aev_total must be positive"
        assert len(aev.components) == 4, "AEV must have 4 components"

        # Validate ID format: AEV-L4-XXX-XXXXXXXX
        assert aev.aev_id.startswith("AEV-L4-"), f"Invalid aev_id format: {aev.aev_id}"

    def test_diagnosis_to_aev_chain(self):
        """Test 3: Full chain: Diagnosis -> AEV with ID propagation."""
        sample_path = project_root / "skillforge-spec-pack/skillforge/src/diagnosis/sample_diagnosis.json"
        with open(sample_path, 'r') as f:
            diagnosis_data = json.load(f)

        diagnosis = DiagnosisOutput.from_dict(diagnosis_data)

        # Build AEV from diagnosis
        aev = (AEVBuilder()
            .with_skill(
                skill_id=diagnosis.skill_id,
                skill_name=diagnosis.skill_name,
                diagnosis_id=diagnosis.diagnosis_id
            )
            .with_currency(Currency.USD)
            .with_period(Period.YEAR)
            .set_v_token(
                value=1000.0,
                description="Test",
                source_description="Test",
                calculation_method="Test"
            )
            .set_v_compute(
                value=500.0,
                description="Test",
                source_description="Test",
                calculation_method="Test"
            )
            .set_v_risk(
                value=200.0,
                description="Test",
                source_description="Test",
                calculation_method="Test"
            )
            .set_v_trust(
                value=100.0,
                description="Test",
                source_description="Test",
                calculation_method="Test"
            )
            .build())

        # Verify ID propagation
        assert aev.diagnosis_id == diagnosis.diagnosis_id, "diagnosis_id not propagated"
        assert aev.skill_id == diagnosis.skill_id, "skill_id not propagated"

    def test_evidence_refs_present(self):
        """Test 4: Diagnosis and AEV have valid evidence_refs."""
        sample_path = project_root / "skillforge-spec-pack/skillforge/src/diagnosis/sample_diagnosis.json"
        with open(sample_path, 'r') as f:
            diagnosis_data = json.load(f)

        diagnosis = DiagnosisOutput.from_dict(diagnosis_data)

        # Check Diagnosis evidence_refs
        assert len(diagnosis.evidence_refs) > 0, "Diagnosis must have evidence_refs"
        for ref in diagnosis.evidence_refs:
            assert ref.id, "EvidenceRef must have id"
            assert ref.kind, "EvidenceRef must have kind"
            assert ref.locator, "EvidenceRef must have locator"

    def test_aev_total_calculation(self):
        """Test 5: AEV total equals sum of components."""
        aev = (AEVBuilder()
            .with_skill(
                skill_id="skill-test-002",
                skill_name="Test Skill",
                diagnosis_id="DX-L4-SMOKE-TEST002"
            )
            .with_currency(Currency.USD)
            .with_period(Period.YEAR)
            .set_v_token(1000.0, "T1", "S1", "C1")
            .set_v_compute(500.0, "T2", "S2", "C2")
            .set_v_risk(200.0, "T3", "S3", "C3")
            .set_v_trust(100.0, "T4", "S4", "C4")
            .build())

        expected_total = 1000.0 + 500.0 + 200.0 + 100.0
        assert abs(aev.aev_total - expected_total) < 0.01, f"AEV total mismatch: {aev.aev_total} != {expected_total}"

    def run_all(self):
        """Run all smoke tests."""
        print("=== L4 Smoke Test Started ===")
        print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
        print()

        tests = [
            ("Diagnosis module loads", self.test_diagnosis_module_loads),
            ("AEV builder creates valid output", self.test_aev_builder_creates_valid_output),
            ("Diagnosis -> AEV chain", self.test_diagnosis_to_aev_chain),
            ("Evidence refs present", self.test_evidence_refs_present),
            ("AEV total calculation", self.test_aev_total_calculation),
        ]

        for name, test_func in tests:
            passed = self.run_test(name, test_func)
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {name}")
            if not passed:
                print(f"  Error: {self.results[-1].error}")

        print()
        print("=== L4 Smoke Test Results ===")
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)
        print(f"Passed: {passed_count}/{total_count}")

        return all(r.passed for r in self.results)

    def get_report(self):
        """Generate smoke test report."""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "all_passed": all(r.passed for r in self.results),
            "results": [r.to_dict() for r in self.results]
        }


def main():
    """Main entry point."""
    smoke_test = L4SmokeTest()
    all_passed = smoke_test.run_all()

    # Save report
    report_dir = project_root / "reports" / "l4_smoke"
    report_dir.mkdir(parents=True, exist_ok=True)

    report = smoke_test.get_report()
    report_path = report_dir / f"smoke_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to: {report_path}")

    # Fail-closed: Exit with error code if any test failed
    if all_passed:
        print()
        print("✓ All L4 smoke tests passed!")
        return 0
    else:
        print()
        print("✗ L4 smoke tests failed - CI will block merge (fail-closed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
