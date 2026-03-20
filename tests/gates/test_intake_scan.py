"""
Unit tests for Entrance Layer gates.

Tests:
- gate_intake: Intake repo gate (G1)
- gate_scan: Repo scan fit score gate (G2)

Gate Interface Contract: gate_interface_v1.yaml (FROZEN)
"""
from __future__ import annotations

import pytest
import tempfile
import os

from skillforge.src.skills.gates import (
    GateIntakeRepo,
    intake_repo,
    GateRepoScanFitScore,
    repo_scan_fit_score,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def valid_intake_input():
    """Valid input for intake gate (T1 适配: 添加 intent_id)."""
    return {
        "intent_id": "AUDIT_REPO_SKILL",  # T1 新增：必须是白名单中的 intent_id
        "repo_url": "https://github.com/example/repo.git",
        "commit_sha": "abc123def456789012345678901234567890abcd",  # 40-char SHA
        "at_time": "2026-02-18T00:00:00Z",
    }


@pytest.fixture
def valid_repo_path():
    """Create a valid repo structure for scanning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create README.md
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("# Test Project")
        # Create pyproject.toml
        with open(os.path.join(tmpdir, "pyproject.toml"), "w") as f:
            f.write('[project]\nname = "test"\n')
        # Create src directory
        os.makedirs(os.path.join(tmpdir, "src"))
        yield tmpdir


# =============================================================================
# Tests for IntakeGate
# =============================================================================

class TestIntakeGate:
    """Tests for intake_repo gate."""

    def test_intake_with_valid_input(self, valid_intake_input):
        """Test intake gate with valid input passes."""
        result = intake_repo(
            intent_id=valid_intake_input["intent_id"],  # T1 新增
            repo_url=valid_intake_input["repo_url"],
            commit_sha=valid_intake_input["commit_sha"],
            at_time=valid_intake_input["at_time"],
        )

        assert result["gate_name"] == "intake_repo"
        assert result["gate_decision"] == "PASSED"
        assert result["next_action"] == "continue"
        assert result["error_code"] is None
        assert len(result["evidence_refs"]) == 1

    def test_missing_commit_sha_triggers_rejected(self):
        """Fail-Closed: Missing commit_sha MUST trigger REJECTED."""
        result = intake_repo(
            intent_id="AUDIT_REPO_SKILL",  # T1 新增
            repo_url="https://github.com/example/repo.git",
            commit_sha=None,  # Missing
            at_time="2026-02-18T00:00:00Z",
        )

        assert result["gate_decision"] == "REJECTED"
        assert result["next_action"] == "halt"
        assert result["error_code"] == GateIntakeRepo.ERROR_COMMIT_SHA_MISSING
        assert len(result["evidence_refs"]) == 0

    def test_empty_commit_sha_triggers_rejected(self):
        """Fail-Closed: Empty commit_sha MUST trigger REJECTED."""
        result = intake_repo(
            intent_id="AUDIT_REPO_SKILL",  # T1 新增
            repo_url="https://github.com/example/repo.git",
            commit_sha="",  # Empty
            at_time="2026-02-18T00:00:00Z",
        )

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == GateIntakeRepo.ERROR_COMMIT_SHA_MISSING

    def test_missing_repo_url_triggers_rejected(self):
        """Missing repo_url MUST trigger REJECTED."""
        result = intake_repo(
            intent_id="AUDIT_REPO_SKILL",  # T1 新增
            repo_url=None,
            commit_sha="abc123def456789012345678901234567890abcd",
            at_time="2026-02-18T00:00:00Z",
        )

        assert result["gate_decision"] == "REJECTED"
        # T1 实现：repo_url=None 返回 ERROR_REPO_URL_MISSING
        assert result["error_code"] == GateIntakeRepo.ERROR_REPO_URL_MISSING

    def test_intake_produces_evidence_ref(self, valid_intake_input):
        """Valid input MUST produce EvidenceRef."""
        result = intake_repo(
            intent_id=valid_intake_input["intent_id"],  # T1 新增
            repo_url=valid_intake_input["repo_url"],
            commit_sha=valid_intake_input["commit_sha"],
            at_time=valid_intake_input["at_time"],
            issue_key="REQ-TEST001",
        )

        assert len(result["evidence_refs"]) == 1
        evidence = result["evidence_refs"][0]

        assert evidence["issue_key"] == "REQ-TEST001"
        assert evidence["source_locator"].startswith("file://")
        assert len(evidence["content_hash"]) == 64  # SHA-256 hex length
        # T1 实现：tool_revision 是 v1.1.0-t1 而非 v1.0.0
        assert evidence["tool_revision"] == "v1.1.0-t1"
        assert "T" in evidence["timestamp"]  # ISO8601 format

    def test_intake_class_interface(self, valid_intake_input):
        """Test class-based interface with validate_input/execute pattern."""
        gate = GateIntakeRepo()

        input_data = {
            "intent_id": valid_intake_input["intent_id"],  # T1 新增
            "repo_url": valid_intake_input["repo_url"],
            "commit_sha": valid_intake_input["commit_sha"],
            "at_time": valid_intake_input["at_time"],
        }

        # Validate input
        errors = gate.validate_input(input_data)
        assert len(errors) == 0

        # Execute
        result = gate.execute(input_data)
        assert result["gate_decision"] == "PASSED"

        # Validate output
        output_errors = gate.validate_output(result)
        assert len(output_errors) == 0


# =============================================================================
# Tests for ScanGate
# =============================================================================

class TestScanGate:
    """Tests for repo_scan_fit_score gate."""

    def test_scan_missing_repo_path_triggers_rejected(self):
        """Missing repo_path MUST trigger REJECTED."""
        result = repo_scan_fit_score(repo_path=None)

        assert result["gate_decision"] == "REJECTED"
        assert result["next_action"] == "halt"
        assert result["error_code"] == GateRepoScanFitScore.ERROR_REPO_NOT_FOUND

    def test_scan_nonexistent_path_triggers_rejected(self):
        """Non-existent repo_path MUST trigger REJECTED."""
        result = repo_scan_fit_score(repo_path="/nonexistent/path/12345")

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == GateRepoScanFitScore.ERROR_FIT_SCORE_LOW

    def test_low_fit_score_triggers_rejected(self):
        """Fail-Closed: Low fit score MUST trigger REJECTED."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty directory - no README, no pyproject, no src
            gate = GateRepoScanFitScore()
            input_data = {"repo_path": tmpdir, "min_fit_score": 0.6}
            result = gate.execute(input_data)

            assert result["gate_decision"] == "REJECTED"
            assert result["error_code"] == GateRepoScanFitScore.ERROR_FIT_SCORE_LOW

    def test_valid_repo_produces_evidence_ref(self, valid_repo_path):
        """Valid repo MUST produce EvidenceRef."""
        result = repo_scan_fit_score(
            repo_path=valid_repo_path,
            issue_key="SCAN-TEST001",
        )

        assert result["gate_decision"] == "PASSED"
        assert len(result["evidence_refs"]) == 1

        evidence = result["evidence_refs"][0]
        assert evidence["issue_key"] == "SCAN-TEST001"
        assert evidence["source_locator"].startswith("file://")
        assert len(evidence["content_hash"]) == 64

    def test_high_fit_score_repo_passes(self, valid_repo_path):
        """Repo with high fit score MUST pass."""
        result = repo_scan_fit_score(repo_path=valid_repo_path)

        assert result["gate_decision"] == "PASSED"
        assert result["next_action"] == "continue"

    def test_scan_class_interface(self, valid_repo_path):
        """Test class-based interface with validate_input/execute pattern."""
        gate = GateRepoScanFitScore()

        input_data = {"repo_path": valid_repo_path}

        # Validate input
        errors = gate.validate_input(input_data)
        assert len(errors) == 0

        # Execute
        result = gate.execute(input_data)
        assert result["gate_decision"] == "PASSED"

        # Validate output
        output_errors = gate.validate_output(result)
        assert len(output_errors) == 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestEntranceGateIntegration:
    """Integration tests for Entrance Layer gates."""

    def test_full_pipeline_pass(self):
        """Test full pipeline with valid inputs."""
        # Step 1: Intake
        intake_result = intake_repo(
            intent_id="AUDIT_REPO_SKILL",  # T1 新增
            repo_url="https://github.com/example/repo.git",
            commit_sha="abc123def456789012345678901234567890abcd",
            at_time="2026-02-18T00:00:00Z",
            issue_key="REQ-INTEG001",
        )

        assert intake_result["gate_decision"] == "PASSED"
        assert len(intake_result["evidence_refs"]) == 1

        # Step 2: Scan (need enough files to pass fit score threshold)
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "README.md"), "w") as f:
                f.write("# Test")
            with open(os.path.join(tmpdir, "pyproject.toml"), "w") as f:
                f.write('[project]\nname = "test"\n')

            scan_result = repo_scan_fit_score(
                repo_path=tmpdir,
                issue_key="SCAN-INTEG001",
            )

            assert scan_result["gate_decision"] == "PASSED"
            assert len(scan_result["evidence_refs"]) == 1

    def test_pipeline_halt_at_intake(self):
        """Test pipeline halts at intake when commit_sha missing."""
        result = intake_repo(
            intent_id="AUDIT_REPO_SKILL",  # T1 新增
            repo_url="https://github.com/example/repo.git",
            commit_sha=None,  # Missing - Fail-Closed
            at_time="2026-02-18T00:00:00Z",
        )

        assert result["gate_decision"] == "REJECTED"
        assert result["next_action"] == "halt"

    def test_pipeline_halt_at_scan(self):
        """Test pipeline halts at scan when fit score too low."""
        # Intake passes
        intake_result = intake_repo(
            intent_id="AUDIT_REPO_SKILL",  # T1 新增
            repo_url="https://github.com/example/repo.git",
            commit_sha="abc123def456789012345678901234567890abcd",
            at_time="2026-02-18T00:00:00Z",
        )
        assert intake_result["gate_decision"] == "PASSED"

        # Scan fails (empty directory = low score)
        with tempfile.TemporaryDirectory() as tmpdir:
            scan_result = repo_scan_fit_score(repo_path=tmpdir)

            assert scan_result["gate_decision"] == "REJECTED"
            assert scan_result["next_action"] == "halt"


# =============================================================================
# Schema Validation Tests
# =============================================================================

class TestGateResultSchema:
    """Tests for GateResult schema compliance."""

    def test_intake_gate_result_schema(self, valid_intake_input):
        """Verify intake result follows gate_interface_v1.yaml."""
        result = intake_repo(
            intent_id=valid_intake_input["intent_id"],  # T1 新增
            repo_url=valid_intake_input["repo_url"],
            commit_sha=valid_intake_input["commit_sha"],
            at_time=valid_intake_input["at_time"],
        )

        # Check required fields
        assert "gate_name" in result
        assert "gate_decision" in result
        assert "next_action" in result
        assert "evidence_refs" in result

        # Decision must be PASSED or REJECTED
        assert result["gate_decision"] in ["PASSED", "REJECTED"]

        # next_action must be continue or halt
        assert result["next_action"] in ["continue", "halt"]

    def test_scan_gate_result_schema(self, valid_repo_path):
        """Verify scan result follows gate_interface_v1.yaml."""
        result = repo_scan_fit_score(repo_path=valid_repo_path)

        # Check required fields
        assert "gate_name" in result
        assert "gate_decision" in result
        assert "next_action" in result
        assert "evidence_refs" in result

        # Decision must be PASSED or REJECTED
        assert result["gate_decision"] in ["PASSED", "REJECTED"]

        # next_action must be continue or halt
        assert result["next_action"] in ["continue", "halt"]

    def test_evidence_ref_schema(self, valid_intake_input):
        """Verify EvidenceRef follows gate_interface_v1.yaml."""
        result = intake_repo(
            intent_id=valid_intake_input["intent_id"],  # T1 新增
            repo_url=valid_intake_input["repo_url"],
            commit_sha=valid_intake_input["commit_sha"],
            at_time=valid_intake_input["at_time"],
        )

        evidence = result["evidence_refs"][0]

        # Required fields per gate_interface_v1.yaml
        assert "issue_key" in evidence
        assert "source_locator" in evidence
        assert "content_hash" in evidence
        assert "tool_revision" in evidence
        assert "timestamp" in evidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
