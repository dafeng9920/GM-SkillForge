"""
Tests for Diagnosis Module (L4-03)

Run: python -m pytest skillforge/tests/test_diagnosis.py -v
"""
from __future__ import annotations

import json
import pytest

from skillforge.src.diagnosis import (
    HealthStatus,
    CategoryName,
    CategoryStatus,
    Severity,
    Priority,
    EvidenceRef,
    Finding,
    Recommendation,
    Category,
    DiagnosisOutput,
    DiagnosisBuilder,
    create_diagnosis,
    validate_diagnosis,
)


# =============================================================================
# Test Enums
# =============================================================================
class TestEnums:
    """Tests for enum values."""

    def test_health_status_values(self):
        """HealthStatus should have correct values."""
        assert HealthStatus.HEALTHY.value == "HEALTHY"
        assert HealthStatus.DEGRADED.value == "DEGRADED"
        assert HealthStatus.CRITICAL.value == "CRITICAL"
        assert HealthStatus.UNKNOWN.value == "UNKNOWN"

    def test_category_name_values(self):
        """CategoryName should have correct values."""
        assert CategoryName.CODE_QUALITY.value == "code_quality"
        assert CategoryName.TEST_COVERAGE.value == "test_coverage"
        assert CategoryName.DOCUMENTATION.value == "documentation"
        assert CategoryName.SECURITY.value == "security"
        assert CategoryName.PERFORMANCE.value == "performance"
        assert CategoryName.MAINTAINABILITY.value == "maintainability"

    def test_severity_values(self):
        """Severity should have correct values."""
        assert Severity.INFO.value == "INFO"
        assert Severity.WARNING.value == "WARNING"
        assert Severity.ERROR.value == "ERROR"
        assert Severity.CRITICAL.value == "CRITICAL"


# =============================================================================
# Test EvidenceRef
# =============================================================================
class TestEvidenceRef:
    """Tests for EvidenceRef class."""

    def test_evidence_ref_generation(self):
        """EvidenceRef should generate valid ID."""
        ev = EvidenceRef.generate(
            evidence_type="DX",
            sequence=1,
            kind="FILE",
            locator="test.py",
            description="Test file"
        )

        assert ev.id.startswith("EV-DX-001-")
        assert len(ev.id) == 18  # EV-DX-001-XXXXXXXX (8 char hash)
        assert ev.kind == "FILE"
        assert ev.locator == "test.py"

    def test_evidence_ref_to_dict(self):
        """EvidenceRef.to_dict() should serialize correctly."""
        ev = EvidenceRef(
            id="EV-DX-001-ABC12345",
            kind="FILE",
            locator="test.py",
            description="Test file",
            content_hash="abc123"
        )

        d = ev.to_dict()
        assert d["id"] == "EV-DX-001-ABC12345"
        assert d["kind"] == "FILE"
        assert d["content_hash"] == "abc123"


# =============================================================================
# Test Finding and Recommendation
# =============================================================================
class TestFinding:
    """Tests for Finding class."""

    def test_finding_creation(self):
        """Finding should be created correctly."""
        finding = Finding(
            severity=Severity.WARNING,
            message="Test warning",
            evidence_ref="EV-DX-001-ABC12345"
        )

        assert finding.severity == Severity.WARNING
        assert finding.message == "Test warning"

    def test_finding_to_dict(self):
        """Finding.to_dict() should serialize correctly."""
        finding = Finding(
            severity=Severity.ERROR,
            message="Test error",
            evidence_ref="EV-DX-001-ABC12345",
            category="security",
            location="test.py:10"
        )

        d = finding.to_dict()
        assert d["severity"] == "ERROR"
        assert d["category"] == "security"
        assert d["location"] == "test.py:10"


class TestRecommendation:
    """Tests for Recommendation class."""

    def test_recommendation_creation(self):
        """Recommendation should be created correctly."""
        rec = Recommendation(
            priority=Priority.HIGH,
            action="Fix security issue",
            evidence_ref="EV-DX-001-ABC12345"
        )

        assert rec.priority == Priority.HIGH
        assert rec.action == "Fix security issue"


# =============================================================================
# Test Category
# =============================================================================
class TestCategory:
    """Tests for Category class."""

    def test_category_creation(self):
        """Category should be created correctly."""
        cat = Category(
            name=CategoryName.CODE_QUALITY,
            status=CategoryStatus.PASS,
            score=85.0
        )

        assert cat.name == CategoryName.CODE_QUALITY
        assert cat.status == CategoryStatus.PASS
        assert cat.score == 85.0

    def test_category_with_findings(self):
        """Category should handle findings."""
        finding = Finding(
            severity=Severity.INFO,
            message="Code looks good",
            evidence_ref="EV-DX-001-ABC12345"
        )

        cat = Category(
            name=CategoryName.CODE_QUALITY,
            status=CategoryStatus.PASS,
            score=85.0,
            findings=[finding]
        )

        assert len(cat.findings) == 1
        d = cat.to_dict()
        assert len(d["findings"]) == 1


# =============================================================================
# Test DiagnosisBuilder
# =============================================================================
class TestDiagnosisBuilder:
    """Tests for DiagnosisBuilder class."""

    def test_builder_minimal(self):
        """Builder should create diagnosis with minimal fields."""
        diagnosis = (DiagnosisBuilder()
            .with_skill("skill-001")
            .add_category(CategoryName.CODE_QUALITY, CategoryStatus.PASS, 85)
            .build())

        assert diagnosis.skill_id == "skill-001"
        assert len(diagnosis.categories) == 1
        assert diagnosis.diagnosis_id.startswith("DX-L4-")

    def test_builder_missing_skill_id(self):
        """Builder should raise error if skill_id is missing."""
        with pytest.raises(ValueError, match="skill_id is required"):
            (DiagnosisBuilder()
                .add_category(CategoryName.CODE_QUALITY, CategoryStatus.PASS, 85)
                .build())

    def test_builder_full_diagnosis(self):
        """Builder should create complete diagnosis."""
        diagnosis = (DiagnosisBuilder()
            .with_skill("skill-001", "My Skill")
            .add_category(CategoryName.CODE_QUALITY, CategoryStatus.PASS, 90)
            .add_category(CategoryName.TEST_COVERAGE, CategoryStatus.PASS, 85)
            .add_evidence_ref("FILE", "test.py", "Test file")
            .add_finding(CategoryName.CODE_QUALITY, Severity.INFO, "Good code", "EV-DX-001-ABC12345")
            .add_recommendation(Priority.MEDIUM, "Add tests", "EV-DX-001-ABC12345")
            .build())

        assert diagnosis.skill_name == "My Skill"
        assert len(diagnosis.categories) == 2
        assert len(diagnosis.evidence_refs) == 1
        assert len(diagnosis.recommendations) == 1

    def test_builder_health_calculation(self):
        """Builder should calculate overall health correctly."""
        # All PASS with high scores -> HEALTHY
        diagnosis = (DiagnosisBuilder()
            .with_skill("skill-001")
            .add_category(CategoryName.CODE_QUALITY, CategoryStatus.PASS, 90)
            .add_category(CategoryName.TEST_COVERAGE, CategoryStatus.PASS, 85)
            .build())
        assert diagnosis.overall_health == HealthStatus.HEALTHY

        # WARN status -> DEGRADED
        diagnosis = (DiagnosisBuilder()
            .with_skill("skill-001")
            .add_category(CategoryName.CODE_QUALITY, CategoryStatus.PASS, 90)
            .add_category(CategoryName.PERFORMANCE, CategoryStatus.WARN, 70)
            .build())
        assert diagnosis.overall_health == HealthStatus.DEGRADED

        # FAIL status -> CRITICAL
        diagnosis = (DiagnosisBuilder()
            .with_skill("skill-001")
            .add_category(CategoryName.SECURITY, CategoryStatus.FAIL, 40)
            .build())
        assert diagnosis.overall_health == HealthStatus.CRITICAL


# =============================================================================
# Test DiagnosisOutput
# =============================================================================
class TestDiagnosisOutput:
    """Tests for DiagnosisOutput class."""

    def test_diagnosis_to_json(self):
        """DiagnosisOutput.to_json() should produce valid JSON."""
        diagnosis = (DiagnosisBuilder()
            .with_skill("skill-001")
            .add_category(CategoryName.CODE_QUALITY, CategoryStatus.PASS, 85)
            .build())

        json_str = diagnosis.to_json()
        parsed = json.loads(json_str)

        assert parsed["skill_id"] == "skill-001"
        assert parsed["overall_health"] == "HEALTHY"

    def test_diagnosis_from_dict(self):
        """DiagnosisOutput should deserialize from dict."""
        data = {
            "diagnosis_id": "DX-L4-001-ABC12345",
            "skill_id": "skill-001",
            "skill_name": "Test Skill",
            "overall_health": "HEALTHY",
            "health_score": 85.0,
            "categories": [
                {
                    "name": "code_quality",
                    "status": "PASS",
                    "score": 90,
                    "findings": [],
                    "weight": 1.0
                }
            ],
            "evidence_refs": [],
            "recommendations": [],
            "generated_at": "2026-02-26T12:00:00Z",
            "metadata": {}
        }

        diagnosis = DiagnosisOutput.from_dict(data)

        assert diagnosis.diagnosis_id == "DX-L4-001-ABC12345"
        assert diagnosis.skill_id == "skill-001"
        assert len(diagnosis.categories) == 1


# =============================================================================
# Test Validation
# =============================================================================
class TestValidateDiagnosis:
    """Tests for validate_diagnosis function."""

    def test_validate_valid_diagnosis(self):
        """Valid diagnosis should pass validation."""
        data = {
            "diagnosis_id": "DX-L4-001-ABC12345",
            "skill_id": "skill-001",
            "overall_health": "HEALTHY",
            "health_score": 85.0,
            "categories": [
                {
                    "name": "code_quality",
                    "status": "PASS",
                    "score": 90,
                    "findings": []
                }
            ],
            "evidence_refs": [
                {
                    "id": "EV-DX-001-ABC12345",
                    "kind": "FILE",
                    "locator": "test.py",
                    "description": "Test"
                }
            ]
        }

        errors = validate_diagnosis(data)
        assert len(errors) == 0

    def test_validate_missing_required_fields(self):
        """Missing required fields should fail validation."""
        data = {
            "diagnosis_id": "DX-L4-001-ABC12345"
        }

        errors = validate_diagnosis(data)
        assert len(errors) > 0
        assert any("skill_id" in e for e in errors)

    def test_validate_invalid_health_score(self):
        """Invalid health_score should fail validation."""
        data = {
            "diagnosis_id": "DX-L4-001-ABC12345",
            "skill_id": "skill-001",
            "overall_health": "HEALTHY",
            "health_score": 150,  # Invalid: > 100
            "categories": [],
            "evidence_refs": []
        }

        errors = validate_diagnosis(data)
        assert any("health_score" in e for e in errors)

    def test_validate_invalid_diagnosis_id(self):
        """Invalid diagnosis_id format should fail validation."""
        data = {
            "diagnosis_id": "INVALID-ID",
            "skill_id": "skill-001",
            "overall_health": "HEALTHY",
            "health_score": 85,
            "categories": [],
            "evidence_refs": []
        }

        errors = validate_diagnosis(data)
        assert any("diagnosis_id" in e for e in errors)


# =============================================================================
# Test Sample Diagnosis
# =============================================================================
class TestSampleDiagnosis:
    """Tests for sample diagnosis file."""

    def test_sample_diagnosis_valid(self):
        """Sample diagnosis.json should be valid."""
        import pathlib
        sample_path = pathlib.Path(__file__).parent.parent / "src" / "diagnosis" / "sample_diagnosis.json"

        if not sample_path.exists():
            pytest.skip("sample_diagnosis.json not found")

        with open(sample_path) as f:
            data = json.load(f)

        errors = validate_diagnosis(data)
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_sample_diagnosis_has_evidence_refs(self):
        """Sample diagnosis should have evidence_refs."""
        import pathlib
        sample_path = pathlib.Path(__file__).parent.parent / "src" / "diagnosis" / "sample_diagnosis.json"

        if not sample_path.exists():
            pytest.skip("sample_diagnosis.json not found")

        with open(sample_path) as f:
            data = json.load(f)

        assert "evidence_refs" in data
        assert len(data["evidence_refs"]) > 0

        # Each finding should have evidence_ref
        for cat in data.get("categories", []):
            for finding in cat.get("findings", []):
                assert "evidence_ref" in finding
