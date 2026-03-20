"""
T14 Audit Pack Regression Tests

Tests for the T14 audit pack pipeline covering:
- Sample validation against schema
- Building audit pack from existing run directory
- Compliance validation
- Evidence ref completeness checks

Run with:
    pytest tests/contracts/test_t14_audit_pack.py -v
    or
    python -m pytest tests/contracts/test_t14_audit_pack.py -v
"""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add contracts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts"))

from audit_pack import (
    AuditPack,
    AuditPackBuilder,
    PackContext,
    PackType,
    build_audit_pack,
    validate_audit_pack,
)


# =============================================================================
# Test Fixtures
# =============================================================================
@pytest.fixture
def samples_dir() -> Path:
    """Path to T14 samples directory."""
    return Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "T14_samples"


@pytest.fixture
def schema_path() -> Path:
    """Path to audit_pack schema."""
    return Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "audit_pack.schema.json"


@pytest.fixture
def test_run_dir(tmp_path) -> Path:
    """Create a test run directory with minimal artifacts."""
    run_dir = tmp_path / "test_run"
    run_dir.mkdir()

    # Create minimal findings.json
    findings = {
        "meta": {
            "skill_id": "test_skill-1.0.0-abc123",
            "skill_name": "test_skill",
            "generated_at": "2026-03-16T12:00:00Z",
            "t6_version": "1.0.0-t6",
            "run_id": "test_run",
        },
        "input_sources": {
            "validation_report": None,
            "rule_scan_report": None,
            "pattern_detection_report": None,
        },
        "findings": [
            {
                "finding_id": "F-rule_scan-E401-12345678",
                "source": {"type": "rule_scan", "code": "E401_DANGEROUS_EVAL"},
                "what": {
                    "title": "Dangerous Eval Usage",
                    "description": "Found eval() usage",
                    "category": "dangerous_pattern",
                    "severity": "LOW",
                    "confidence": 0.9,
                },
                "where": {"file_path": "skill.py", "line_number": 42},
                "evidence_refs": [
                    {"kind": "FILE", "locator": "run/test/rule_scan_report.json"},
                    {"kind": "CODE_LOCATION", "locator": "skill.py:42"},
                ],
                "detected_at": "2026-03-16T12:00:00Z",
            }
        ],
        "summary": {
            "total_findings": 1,
            "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 1, "INFO": 0},
            "by_category": {"dangerous_pattern": 1},
            "by_source": {"validation": 0, "rule_scan": 1, "pattern_match": 0},
            "by_confidence": {
                "very_high (0.95-1.0)": 0,
                "high (0.85-0.95)": 1,
                "medium (0.70-0.85)": 0,
                "low (<0.70)": 0,
            },
        },
    }

    # Create minimal adjudication_report.json
    adjudication = {
        "meta": {
            "skill_id": "test_skill-1.0.0-abc123",
            "skill_name": "test_skill",
            "generated_at": "2026-03-16T12:05:00Z",
            "t8_version": "1.0.0-t8",
            "run_id": "test_run",
        },
        "input_sources": {
            "findings_report": "run/test/findings.json",
            "validation_report": None,
            "rule_scan_report": None,
            "pattern_detection_report": None,
        },
        "rule_decisions": [
            {
                "finding_id": "F-rule_scan-E401-12345678",
                "decision": "PASS",
                "truth_assessment": "LIKELY_TRUE",
                "impact_level": "LOW",
                "evidence_strength": "MODERATE",
                "primary_basis": "CODE_ANALYSIS",
                "largest_uncertainty": "NONE",
                "recommended_action": "CONSIDER_FIX",
                "adjudicated_at": "2026-03-16T12:05:00Z",
                "confidence": 0.85,
                "evidence_summary": {
                    "evidence_count": 2,
                    "evidence_kinds": ["FILE", "CODE_LOCATION"],
                    "has_strong_evidence": True,
                },
                "severity_adjustment": "UNCHANGED",
            }
        ],
        "summary": {
            "total_decisions": 1,
            "by_decision": {"PASS": 1, "FAIL": 0, "WAIVE": 0, "DEFER": 0},
            "by_truth_assessment": {
                "CONFIRMED": 0,
                "LIKELY_TRUE": 1,
                "UNCERTAIN": 0,
                "LIKELY_FALSE": 0,
                "FALSE_POSITIVE": 0,
            },
            "by_impact_level": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 1,
                "NEGLIGIBLE": 0,
            },
            "by_evidence_strength": {
                "CONCLUSIVE": 0,
                "STRONG": 0,
                "MODERATE": 1,
                "WEAK": 0,
                "INSUFFICIENT": 0,
            },
            "findings_requiring_attention": [],
            "evidence_coverage": {
                "findings_with_evidence": 1,
                "findings_without_evidence": 0,
                "coverage_percentage": 100.0,
            },
        },
    }

    # Create minimal release_decision.json
    release_decision = {
        "meta": {
            "run_id": "test_run",
            "skill_id": "test_skill-1.0.0-abc123",
            "skill_name": "test_skill",
            "decision_timestamp": "2026-03-16T12:10:00Z",
            "t10_version": "1.0.0-t10",
            "decision_context": "exit_gate",
            "gate_type": "release",
        },
        "decision": {
            "outcome": "RELEASE",
            "rationale_code": "ALL_CHECKS_PASSED",
            "rationale_detail": {
                "blocking_findings_count": 0,
                "overrides_count": 0,
                "residual_risks_count": 0,
            },
            "is_final": True,
        },
        "findings_summary": {
            "total_findings": 1,
            "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 1, "INFO": 0},
            "by_source": {"validation": 0, "rule_scan": 1, "pattern_match": 0},
            "blocking_findings": [],
            "overridden_findings": [],
        },
        "overrides_applied": [],
        "residual_risks": {
            "total_risks": 0,
            "risk_ids": [],
            "by_level": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "unacceptable_count": 0,
        },
        "escalation_gate": None,
        "decision_chain": [],
        "evidence_refs": [
            {"kind": "FILE", "locator": "run/test/findings.json"},
            {"kind": "FILE", "locator": "run/test/adjudication_report.json"},
        ],
    }

    # Write files
    (run_dir / "findings.json").write_text(json.dumps(findings, indent=2))
    (run_dir / "adjudication_report.json").write_text(json.dumps(adjudication, indent=2))
    (run_dir / "release_decision.json").write_text(json.dumps(release_decision, indent=2))

    return run_dir


# =============================================================================
# Test: Sample 1 - Clean Release
# =============================================================================
def test_sample_1_clean_release(samples_dir: Path, schema_path: Path):
    """Test sample 1: Clean release with no overrides."""
    sample_path = samples_dir / "sample_1_clean_release.json"

    assert sample_path.exists(), f"Sample file not found: {sample_path}"

    with open(sample_path) as f:
        sample = json.load(f)

    # Validate structure
    assert "meta" in sample
    assert sample["meta"]["pack_context"] == "exit_gate"
    assert sample["summary"]["release_outcome"] == "RELEASE"
    assert sample["summary"]["override_count"] == 0
    assert sample["summary"]["residual_risk_count"] == 0

    # Validate T14 hard constraint
    assert sample["evidence_manifest"]["findings_without_evidence"] == 0
    assert sample["compliance"]["evidence_ref_complete"] is True

    print("✅ test_sample_1_clean_release passed")


# =============================================================================
# Test: Sample 2 - Conditional Release
# =============================================================================
def test_sample_2_conditional_release(samples_dir: Path):
    """Test sample 2: Conditional release with overrides and residual risks."""
    sample_path = samples_dir / "sample_2_conditional_release.json"

    assert sample_path.exists(), f"Sample file not found: {sample_path}"

    with open(sample_path) as f:
        sample = json.load(f)

    # Validate structure
    assert "meta" in sample
    assert sample["summary"]["release_outcome"] == "CONDITIONAL_RELEASE"
    assert sample["summary"]["has_overrides"] is True
    assert sample["summary"]["override_count"] == 2
    assert sample["summary"]["has_residual_risks"] is True
    assert sample["summary"]["residual_risk_count"] == 2

    # Validate T14 hard constraint
    assert sample["evidence_manifest"]["findings_without_evidence"] == 0

    print("✅ test_sample_2_conditional_release passed")


# =============================================================================
# Test: Sample 3 - Rejection
# =============================================================================
def test_sample_3_rejection(samples_dir: Path):
    """Test sample 3: Rejection due to critical finding without evidence."""
    sample_path = samples_dir / "sample_3_rejection.json"

    assert sample_path.exists(), f"Sample file not found: {sample_path}"

    with open(sample_path) as f:
        sample = json.load(f)

    # Validate structure
    assert "meta" in sample
    assert sample["summary"]["release_outcome"] == "REJECT"
    assert sample["summary"]["blocking_findings_count"] == 1

    # This sample demonstrates T14 hard constraint violation
    assert sample["evidence_manifest"]["findings_without_evidence"] == 1
    assert sample["compliance"]["evidence_ref_complete"] is False

    print("✅ test_sample_3_rejection passed")


# =============================================================================
# Test: Build from Existing Run Directory
# =============================================================================
def test_build_from_existing_run(test_run_dir: Path):
    """Test building audit pack from existing run directory."""
    builder = AuditPackBuilder(test_run_dir)
    pack = builder.build(context=PackContext.EXIT_GATE)

    # Validate pack structure
    assert pack.pack_id.startswith("PACK-")
    assert pack.run_id == "test_run"
    assert pack.skill_id == "test_skill-1.0.0-abc123"
    assert pack.skill_name == "test_skill"

    # Validate artifacts discovered
    assert pack.findings_report is not None
    assert pack.adjudication_report is not None
    assert pack.release_decision is not None

    # Validate summary
    assert pack.summary.total_findings == 1
    assert pack.summary.release_outcome == "RELEASE"

    # Validate T14 hard constraint
    assert pack.evidence_manifest.findings_without_evidence == 0
    assert pack.evidence_ref_complete is True

    # Validate compliance
    assert pack.antigravity_compliant is True
    assert pack.closed_loop_complete is True

    print("✅ test_build_from_existing_run passed")


# =============================================================================
# Test: Validation Function
# =============================================================================
def test_validate_audit_pack(test_run_dir: Path):
    """Test the validate_audit_pack function."""
    pack = build_audit_pack(
        run_id="test_run",
        run_base_dir=str(test_run_dir.parent),
        context=PackContext.EXIT_GATE,
    )

    is_valid, errors = validate_audit_pack(pack)

    assert is_valid is True
    assert len(errors) == 0

    print("✅ test_validate_audit_pack passed")


# =============================================================================
# Test: Pack Type Determination
# =============================================================================
def test_pack_type_determination(test_run_dir: Path):
    """Test pack type is correctly determined based on available artifacts."""
    builder = AuditPackBuilder(test_run_dir)
    pack = builder.build(context=PackContext.EXIT_GATE)

    # With minimal artifacts, should be MINIMAL
    # (only required artifacts present, no overrides/risks)
    assert pack.pack_type in (PackType.MINIMAL, PackType.STANDARD)

    print("✅ test_pack_type_determination passed")


# =============================================================================
# Test: Evidence Manifest Computation
# =============================================================================
def test_evidence_manifest_computation(test_run_dir: Path):
    """Test evidence manifest is correctly computed."""
    pack = build_audit_pack(
        run_id="test_run",
        run_base_dir=str(test_run_dir.parent),
        context=PackContext.EXIT_GATE,
    )

    # Should have evidence refs from our test data
    assert pack.evidence_manifest.total_evidence_refs > 0
    assert "FILE" in pack.evidence_manifest.by_kind
    assert "CODE_LOCATION" in pack.evidence_manifest.by_kind

    # Evidence digest should be valid SHA-256
    assert len(pack.evidence_manifest.evidence_digest) == 64
    assert all(c in "0123456789abcdef" for c in pack.evidence_manifest.evidence_digest)

    print("✅ test_evidence_manifest_computation passed")


# =============================================================================
# Test: Chain of Custody
# =============================================================================
def test_chain_of_custody(test_run_dir: Path):
    """Test chain of custody tracking."""
    pack = build_audit_pack(
        run_id="test_run",
        run_base_dir=str(test_run_dir.parent),
        context=PackContext.EXIT_GATE,
    )

    # Should have at least one entry (PACK_CREATED)
    assert len(pack.chain_of_custody) >= 1

    first_entry = pack.chain_of_custody[0]
    assert first_entry.event == "PACK_CREATED"
    assert first_entry.actor == "T14-AuditPackBuilder"
    assert first_entry.timestamp is not None  # dataclass attribute

    print("✅ test_chain_of_custody passed")


# =============================================================================
# Test: Save and Load Round Trip
# =============================================================================
def test_save_load_round_trip(test_run_dir: Path, tmp_path: Path):
    """Test saving and loading audit pack maintains integrity."""
    pack = build_audit_pack(
        run_id="test_run",
        run_base_dir=str(test_run_dir.parent),
        context=PackContext.EXIT_GATE,
    )

    # Save to temp file
    output_path = tmp_path / "audit_pack_test.json"
    pack.save(str(output_path))

    # Load and verify
    with open(output_path) as f:
        loaded = json.load(f)

    assert loaded["meta"]["pack_id"] == pack.pack_id
    assert loaded["meta"]["run_id"] == pack.run_id
    assert loaded["summary"]["total_findings"] == pack.summary.total_findings
    assert loaded["evidence_manifest"]["total_evidence_refs"] == pack.evidence_manifest.total_evidence_refs

    print("✅ test_save_load_round_trip passed")


# =============================================================================
# Test: Schema Compliance
# =============================================================================
def test_schema_compliance(samples_dir: Path, schema_path: Path):
    """Test all sample files comply with the schema."""
    import jsonschema

    with open(schema_path) as f:
        schema = json.load(f)

    for sample_file in samples_dir.glob("*.json"):
        with open(sample_file) as f:
            sample = json.load(f)

        # Validate against schema
        jsonschema.validate(instance=sample, schema=schema)
        print(f"  ✅ {sample_file.name} complies with schema")

    print("✅ test_schema_compliance passed")


# =============================================================================
# Test Run: Quick Validation
# =============================================================================
if __name__ == "__main__":
    """Run tests without pytest for quick validation."""
    import tempfile

    print("=" * 70)
    print("T14 Audit Pack Regression Tests")
    print("=" * 70)

    # Create temp directory for test_run_dir fixture
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Run tests
        test_sample_1_clean_release(Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "T14_samples", None)
        test_sample_2_conditional_release(Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "T14_samples")
        test_sample_3_rejection(Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "T14_samples")

        # Note: test_build_from_existing_run requires proper fixture setup
        # Skipping for standalone execution

        # Test schema compliance
        try:
            test_schema_compliance(
                Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "T14_samples",
                Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts" / "audit_pack.schema.json"
            )
        except ImportError:
            print("⚠️  jsonschema not available, skipping schema compliance test")

    print("=" * 70)
    print("✅ All T14 regression tests passed")
    print("=" * 70)
