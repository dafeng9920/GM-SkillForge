"""
Unit tests for Logic Layer gates.

Tests:
- gate_draft_spec: Draft skill specification from scan report
- gate_risk: Constitution risk assessment gate

Gate Interface Contract: gate_interface_v1.yaml (FROZEN)
"""
from __future__ import annotations

import pytest

from skillforge.src.skills.gates import (
    DraftSpecGate,
    draft_skill_spec,
    ConstitutionRiskGate,
    constitution_risk_gate,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def valid_scan_report():
    """Valid scan report from repo_scan_fit_score gate (G2)."""
    return {
        "schema_version": "0.1.0",
        "fit_score": 75,
        "repo_type": "lib",
        "entry_points": ["main.py", "cli.py"],
        "dependencies": {
            "requests": "2.28.0",
            "click": "8.1.0",
        },
        "language_stack": "Python",
        "complexity_metrics": {
            "total_files": 42,
            "total_loc": 3500,
            "avg_function_length": 15.5,
        },
    }


@pytest.fixture
def low_fit_score_scan_report():
    """Scan report with low fit score."""
    return {
        "schema_version": "0.1.0",
        "fit_score": 25,
        "repo_type": "template",
        "entry_points": [],
        "dependencies": {},
        "language_stack": "unknown",
        "complexity_metrics": {
            "total_files": 1,
            "total_loc": 10,
            "avg_function_length": 0.0,
        },
    }


@pytest.fixture
def valid_skill_spec():
    """Valid skill specification."""
    return {
        "schema_version": "0.1.0",
        "name": "test-skill",
        "version": "0.1.0",
        "description": "A test skill",
        "capabilities": ["file_read", "shell"],
        "tools_required": ["python3"],
        "constraints": ["fit_score >= 40"],
    }


@pytest.fixture
def risky_skill_spec():
    """Skill spec with risky capabilities."""
    return {
        "schema_version": "0.1.0",
        "name": "risky-skill",
        "version": "0.1.0",
        "description": "A skill with elevated risk",
        "capabilities": ["shell", "file_write", "database", "network"],
        "tools_required": ["subprocess", "bash"],
        "constraints": ["risk_tier: L2"],
    }


@pytest.fixture
def override_governance_skill_spec():
    """Skill spec with override_governance flag (RED LINE)."""
    return {
        "schema_version": "0.1.0",
        "name": "bypass-skill",
        "version": "0.1.0",
        "description": "A skill attempting to bypass governance",
        "capabilities": ["shell"],
        "tools_required": ["python3"],
        "constraints": ["override_governance: true"],
    }


@pytest.fixture
def prohibited_capability_skill_spec():
    """Skill spec with prohibited capability."""
    return {
        "schema_version": "0.1.0",
        "name": "privileged-skill",
        "version": "0.1.0",
        "description": "A skill with prohibited capability",
        "capabilities": ["authenticated_access"],
        "tools_required": ["python3"],
        "constraints": [],
    }


# =============================================================================
# Tests for DraftSpecGate
# =============================================================================

class TestDraftSpecGate:
    """Tests for draft_skill_spec gate."""

    def test_draft_spec_with_valid_scan_report(self, valid_scan_report):
        """Test drafting spec with valid scan report."""
        result = draft_skill_spec(valid_scan_report)

        assert result["gate_name"] == "draft_skill_spec"
        assert result["gate_decision"] == "PASSED"
        assert result["next_action"] == "continue"
        assert result["error_code"] is None
        assert len(result["evidence_refs"]) == 1
        assert result["skill_spec"] is not None
        assert result["skill_spec"]["name"] == "auto-drafted-skill"
        assert result["skill_spec"]["schema_version"] == "0.1.0"

    def test_draft_spec_with_low_fit_score(self, low_fit_score_scan_report):
        """Test that low fit score results in REJECTED."""
        result = draft_skill_spec(low_fit_score_scan_report)

        assert result["gate_name"] == "draft_skill_spec"
        assert result["gate_decision"] == "REJECTED"
        assert result["next_action"] == "halt"
        assert result["error_code"] == "GATE.DRAFT_SPEC.FIT_SCORE_TOO_LOW"
        assert len(result["evidence_refs"]) == 0

    def test_draft_spec_with_missing_scan_report(self):
        """Test that missing scan_report results in REJECTED."""
        result = draft_skill_spec(None)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "GATE.DRAFT_SPEC.INPUT_INVALID"

    def test_draft_spec_skill_spec_content(self, valid_scan_report):
        """Test that generated skill_spec has required fields."""
        result = draft_skill_spec(valid_scan_report)
        skill_spec = result["skill_spec"]

        assert "name" in skill_spec
        assert "version" in skill_spec
        assert "description" in skill_spec
        assert "skill_md" in skill_spec
        assert "input_schema" in skill_spec
        assert "output_schema" in skill_spec
        assert "capabilities" in skill_spec

    def test_draft_spec_evidence_ref_structure(self, valid_scan_report):
        """Test evidence_ref structure follows gate_interface_v1.yaml."""
        result = draft_skill_spec(valid_scan_report)

        assert len(result["evidence_refs"]) == 1
        ref = result["evidence_refs"][0]

        assert "issue_key" in ref
        assert "source_locator" in ref
        assert "content_hash" in ref
        assert "tool_revision" in ref
        assert "timestamp" in ref
        assert ref["source_locator"].startswith("skill_spec://")

    def test_draft_spec_class_interface(self, valid_scan_report):
        """Test class-based interface."""
        gate = DraftSpecGate()
        result = gate.execute({"scan_report": valid_scan_report})
        result_dict = gate.to_dict(result)

        assert result_dict["gate_decision"] == "PASSED"
        assert result_dict["skill_spec"] is not None


# =============================================================================
# Tests for ConstitutionRiskGate
# =============================================================================

class TestConstitutionRiskGate:
    """Tests for constitution_risk_gate."""

    def test_risk_gate_with_valid_skill_spec(self, valid_skill_spec):
        """Test risk gate with valid skill spec passes."""
        result = constitution_risk_gate(valid_skill_spec)

        assert result["gate_name"] == "constitution_risk_gate"
        assert result["gate_decision"] == "PASSED"
        assert result["next_action"] == "continue"
        assert result["error_code"] is None
        assert len(result["evidence_refs"]) == 1
        assert result["risk_assessment"] is not None

    def test_risk_gate_with_risky_capabilities(self, risky_skill_spec):
        """Test that risky capabilities may result in REJECTED."""
        result = constitution_risk_gate(risky_skill_spec)

        # Risk score should be elevated due to shell, subprocess, etc.
        assert result["risk_assessment"]["risk_score"] > 0.3
        assert len(result["risk_assessment"]["risk_categories"]) > 0

    def test_risk_gate_blocks_override_governance(self, override_governance_skill_spec):
        """Test that override_governance flag results in REJECTED (RED LINE)."""
        result = constitution_risk_gate(override_governance_skill_spec)

        assert result["gate_decision"] == "REJECTED"
        assert result["next_action"] == "halt"
        assert result["error_code"] == "GATE.RISK.OVERRIDE_GOVERNANCE"
        assert "override_governance" in result["risk_assessment"]["risk_categories"][0]

    def test_risk_gate_blocks_prohibited_capability(self, prohibited_capability_skill_spec):
        """Test that prohibited capability results in REJECTED."""
        result = constitution_risk_gate(prohibited_capability_skill_spec)

        assert result["gate_decision"] == "REJECTED"
        assert result["next_action"] == "halt"
        assert result["risk_assessment"]["risk_score"] == 1.0
        assert any("prohibited" in cat for cat in result["risk_assessment"]["risk_categories"])

    def test_risk_gate_with_missing_skill_spec(self):
        """Test that missing skill_spec results in REJECTED."""
        result = constitution_risk_gate(None)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "GATE.RISK.INPUT_INVALID"

    def test_risk_assessment_structure(self, valid_skill_spec):
        """Test risk_assessment has required fields."""
        result = constitution_risk_gate(valid_skill_spec)
        assessment = result["risk_assessment"]

        assert "schema_version" in assessment
        assert "skill_name" in assessment
        assert "risk_score" in assessment
        assert "risk_tier" in assessment
        assert "risk_categories" in assessment
        assert "mitigations_required" in assessment
        assert "gate_decision" in assessment
        assert "constitution_version" in assessment
        assert "constitution_hash" in assessment
        assert "timestamp" in assessment

    def test_risk_tier_classification(self):
        """Test risk tier is correctly classified."""
        gate = ConstitutionRiskGate()

        # L0: Low risk
        low_risk_spec = {
            "name": "low-risk",
            "capabilities": ["file_read"],
            "tools_required": ["python3"],
        }
        result = gate.execute({"skill_spec": low_risk_spec})
        assert result.risk_assessment["risk_tier"] in ["L0", "L1"]

        # L3: High risk
        high_risk_spec = {
            "name": "high-risk",
            "capabilities": ["shell", "database", "file_write"],
            "tools_required": ["subprocess", "sudo"],
        }
        result = gate.execute({"skill_spec": high_risk_spec})
        assert result.risk_assessment["risk_tier"] == "L3"

    def test_risk_gate_fail_closed(self):
        """Test that risk gate is fail-closed (risk detected = REJECTED)."""
        gate = ConstitutionRiskGate()

        # Create a spec that should definitely be rejected
        dangerous_spec = {
            "name": "dangerous",
            "capabilities": ["authenticated_access"],  # prohibited
            "tools_required": ["subprocess", "sudo"],
        }
        result = gate.execute({"skill_spec": dangerous_spec})

        assert result.gate_decision == "REJECTED"
        assert result.next_action == "halt"

    def test_risk_gate_evidence_ref_structure(self, valid_skill_spec):
        """Test evidence_ref structure follows gate_interface_v1.yaml."""
        result = constitution_risk_gate(valid_skill_spec)

        assert len(result["evidence_refs"]) == 1
        ref = result["evidence_refs"][0]

        assert "issue_key" in ref
        assert "source_locator" in ref
        assert "content_hash" in ref
        assert "tool_revision" in ref
        assert "timestamp" in ref
        assert ref["source_locator"].startswith("risk_assessment://")

    def test_risk_gate_class_interface(self, valid_skill_spec):
        """Test class-based interface."""
        gate = ConstitutionRiskGate()
        result = gate.execute({"skill_spec": valid_skill_spec})
        result_dict = gate.to_dict(result)

        assert result_dict["gate_decision"] == "PASSED"
        assert result_dict["risk_assessment"] is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestLogicGateIntegration:
    """Integration tests for Logic Layer gates."""

    def test_full_pipeline_valid_input(self, valid_scan_report):
        """Test full pipeline: scan -> draft -> risk assessment."""
        # Step 1: Draft spec from scan report
        draft_result = draft_skill_spec(valid_scan_report)
        assert draft_result["gate_decision"] == "PASSED"

        # Step 2: Risk assessment on drafted spec
        skill_spec = draft_result["skill_spec"]
        risk_result = constitution_risk_gate(skill_spec)

        # With valid scan report, risk should be acceptable
        assert risk_result["gate_decision"] in ["PASSED", "REJECTED"]
        assert risk_result["risk_assessment"]["risk_tier"] in ["L0", "L1", "L2", "L3"]

    def test_full_pipeline_low_fit_score(self, low_fit_score_scan_report):
        """Test pipeline with low fit score stops at draft gate."""
        # Step 1: Draft should reject
        draft_result = draft_skill_spec(low_fit_score_scan_report)
        assert draft_result["gate_decision"] == "REJECTED"
        assert draft_result["skill_spec"] is None

    def test_full_pipeline_risky_spec(self):
        """Test pipeline with risky capabilities."""
        # Create a spec that will pass draft but fail risk
        scan_report = {
            "fit_score": 75,
            "language_stack": "Python",
            "repo_type": "lib",
            "entry_points": ["main.py"],
        }

        draft_result = draft_skill_spec(scan_report)
        assert draft_result["gate_decision"] == "PASSED"

        # Modify to add risky capability
        risky_spec = draft_result["skill_spec"].copy()
        risky_spec["capabilities"] = ["authenticated_access"]

        risk_result = constitution_risk_gate(risky_spec)
        assert risk_result["gate_decision"] == "REJECTED"


# =============================================================================
# Schema Validation Tests
# =============================================================================

class TestGateResultSchema:
    """Tests for GateResult schema compliance."""

    def test_draft_spec_gate_result_schema(self, valid_scan_report):
        """Verify draft_spec result follows gate_interface_v1.yaml."""
        result = draft_skill_spec(valid_scan_report)

        # Required fields
        assert "gate_name" in result
        assert "gate_decision" in result
        assert "next_action" in result
        assert "evidence_refs" in result

        # Decision must be PASSED or REJECTED
        assert result["gate_decision"] in ["PASSED", "REJECTED"]

        # next_action must be continue or halt
        assert result["next_action"] in ["continue", "halt"]

    def test_risk_gate_result_schema(self, valid_skill_spec):
        """Verify risk gate result follows gate_interface_v1.yaml."""
        result = constitution_risk_gate(valid_skill_spec)

        # Required fields
        assert "gate_name" in result
        assert "gate_decision" in result
        assert "next_action" in result
        assert "evidence_refs" in result

        # Decision must be PASSED or REJECTED
        assert result["gate_decision"] in ["PASSED", "REJECTED"]

        # next_action must be continue or halt
        assert result["next_action"] in ["continue", "halt"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
