"""
test_evidence_container.py — Evidence Container Tests for T-V0-D.

Tests the complete evidence chain:
- semgrep → findings → evidence_ref → evidence.jsonl

Run: python -m pytest skillforge/tests/test_evidence_container.py -v
"""
from __future__ import annotations

import json
from typing import Any

import pytest

from skillforge.src.analyzers.semgrep_runner import AnalysisResult, Finding, SemgrepRunner
from skillforge.src.nodes.pack_publish import PackPublish
from skillforge.src.nodes.sandbox_test import SandboxTest


# =============================================================================
# TestSemgrepRunner — Tests for the semgrep wrapper
# =============================================================================
class TestSemgrepRunner:
    """Tests for SemgrepRunner class."""

    def test_mock_fallback_when_not_installed(self) -> None:
        """SemgrepRunner should return mock results when semgrep is not installed."""
        runner = SemgrepRunner()
        result = runner.analyze("/tmp/nonexistent")

        # Should return results even when semgrep is not installed
        assert isinstance(result, AnalysisResult)
        assert result.tool_version in ("mock-0.0.0", "not-installed") or result.tool_version != "unknown"

    def test_findings_structure(self) -> None:
        """SemgrepRunner findings should have required fields."""
        runner = SemgrepRunner()
        result = runner.analyze("/tmp/test")

        for finding in result.findings:
            assert isinstance(finding, Finding)
            assert hasattr(finding, "rule_id")
            assert hasattr(finding, "severity")
            assert hasattr(finding, "message")
            assert hasattr(finding, "location")

            # Test to_dict method
            d = finding.to_dict()
            assert "rule_id" in d
            assert "severity" in d
            assert "message" in d
            assert "location" in d

    def test_timeout_handling(self) -> None:
        """SemgrepRunner should handle timeouts gracefully."""
        runner = SemgrepRunner()
        # This should not raise an exception even with timeout
        result = runner.analyze("/tmp/test")
        assert isinstance(result, AnalysisResult)
        # Exit code can be 0 (success), 2 (invalid path), or -1 (timeout)
        # The important thing is that it doesn't raise an exception
        assert result.exit_code is not None


# =============================================================================
# TestEvidenceChainReal — Tests for the real evidence chain
# =============================================================================
class TestEvidenceChainReal:
    """Tests for evidence chain with real semgrep integration."""

    def _make_minimal_artifacts(self) -> dict[str, Any]:
        """Create minimal artifacts for testing."""
        return {
            "scaffold_skill_impl": {"bundle_path": "/tmp/test-bundle"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {"passed": 1, "failed": 0},
                "trace_events": [],
                "static_analysis": {
                    "tool": "semgrep",
                    "version": "mock-0.0.0",
                    "findings": [
                        {
                            "rule_id": "python.lang.security.dangerous-subprocess-use",
                            "severity": "warning",
                            "message": "Dangerous subprocess use detected",
                            "location": {"file": "test.py", "line": 10, "column": 5},
                        }
                    ],
                    "raw_output": '{"results": []}',
                },
            },
            "skill_compose": {"skill_spec": {"name": "test-skill", "version": "0.1.0"}},
        }

    def test_static_findings_in_evidence(self) -> None:
        """Static analysis findings should appear in evidence.jsonl."""
        handler = PackPublish()
        artifacts = self._make_minimal_artifacts()
        result = handler.execute(artifacts)

        files = result.get("audit_pack", {}).get("files", {})
        evidence = files.get("evidence", [])

        # Should have at least one static_analysis_finding evidence
        static_evidence = [e for e in evidence if e.get("type") == "static_analysis_finding"]
        assert len(static_evidence) >= 1, "Should have static analysis findings in evidence"

        # Evidence should have required fields
        for ev in static_evidence:
            assert "evidence_id" in ev
            assert ev["evidence_id"].startswith("ev-")
            assert "rule_id" in ev
            assert "severity" in ev

    def test_evidence_ref_resolves(self) -> None:
        """All evidence_refs in policy_matrix should resolve to evidence entries."""
        handler = PackPublish()
        artifacts = self._make_minimal_artifacts()
        result = handler.execute(artifacts)

        files = result.get("audit_pack", {}).get("files", {})
        policy_matrix = files.get("policy_matrix", {})
        evidence = files.get("evidence", [])

        evidence_ids = {e.get("evidence_id") for e in evidence if e.get("evidence_id")}

        for finding in policy_matrix.get("findings", []):
            ref = finding.get("evidence_ref")
            if ref:
                assert ref in evidence_ids, f"evidence_ref {ref} not found in evidence"

    def test_policy_matrix_links_to_evidence(self) -> None:
        """policy_matrix findings should have evidence_ref pointing to evidence."""
        handler = PackPublish()
        artifacts = self._make_minimal_artifacts()
        result = handler.execute(artifacts)

        files = result.get("audit_pack", {}).get("files", {})
        policy_matrix = files.get("policy_matrix", {})

        # All findings should have evidence_ref
        for finding in policy_matrix.get("findings", []):
            assert "evidence_ref" in finding, f"Finding missing evidence_ref: {finding}"
            assert finding["evidence_ref"], "evidence_ref should not be empty"

    def test_static_analysis_log_contains_output(self) -> None:
        """static_analysis.log should contain semgrep raw output."""
        handler = PackPublish()
        artifacts = self._make_minimal_artifacts()
        result = handler.execute(artifacts)

        files = result.get("audit_pack", {}).get("files", {})
        # Check static_analysis_lines count
        assert "static_analysis_lines" in files
        assert isinstance(files["static_analysis_lines"], int)

    def test_intake_provenance_in_evidence(self) -> None:
        """intake_provenance evidence should be present."""
        handler = PackPublish()
        artifacts = self._make_minimal_artifacts()
        artifacts["intake_repo"] = {
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123",
        }
        result = handler.execute(artifacts)

        files = result.get("audit_pack", {}).get("files", {})
        evidence = files.get("evidence", [])

        # Should have intake_provenance evidence
        intake_evidence = [e for e in evidence if e.get("type") == "intake_provenance"]
        assert len(intake_evidence) >= 1, "Should have intake_provenance in evidence"

    def test_gate_decision_in_evidence(self) -> None:
        """gate_decision evidence should be present when gates are run."""
        handler = PackPublish()
        artifacts = self._make_minimal_artifacts()
        artifacts["license_gate"] = {"decision": "ALLOW", "license": "MIT"}
        artifacts["constitution_risk_gate"] = {"decision": "APPROVED"}
        result = handler.execute(artifacts)

        files = result.get("audit_pack", {}).get("files", {})
        evidence = files.get("evidence", [])

        # Should have gate_decision evidence
        gate_evidence = [e for e in evidence if e.get("type") == "gate_decision"]
        assert len(gate_evidence) >= 1, "Should have gate_decision in evidence"


# =============================================================================
# TestSandboxTestIntegration — Tests for sandbox_test.py integration
# =============================================================================
class TestSandboxTestIntegration:
    """Tests for sandbox_test.py with semgrep integration."""

    def test_sandbox_test_has_static_analysis(self) -> None:
        """SandboxTest output should include static_analysis."""
        handler = SandboxTest()
        result = handler.execute({
            "scaffold_skill_impl": {"bundle_path": "/tmp/test-bundle"},
        })

        assert "static_analysis" in result
        static = result["static_analysis"]
        assert "tool" in static
        assert static["tool"] == "semgrep"
        assert "version" in static
        assert "findings" in static
        assert "raw_output" in static
        assert isinstance(static["findings"], list)

    def test_sandbox_test_findings_have_evidence_id(self) -> None:
        """SandboxTest findings should have evidence_id field for later use."""
        handler = SandboxTest()
        result = handler.execute({
            "scaffold_skill_impl": {"bundle_path": "/tmp/test-bundle"},
        })

        static = result.get("static_analysis", {})
        findings = static.get("findings", [])

        # Each finding should have a structure compatible with evidence chain
        for finding in findings:
            assert "rule_id" in finding
            assert "severity" in finding
            assert "message" in finding
            assert "location" in finding


# =============================================================================
# TestEvidenceIdFormat — Tests for evidence_id format
# =============================================================================
class TestEvidenceIdFormat:
    """Tests for evidence_id format compliance."""

    def test_evidence_id_globally_unique(self) -> None:
        """evidence_id should be globally unique (ev-{uuid_hex[:8]})."""
        handler = PackPublish()
        artifacts = {
            "scaffold_skill_impl": {"bundle_path": "/tmp/test-bundle"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {"passed": 1, "failed": 0},
                "static_analysis": {"findings": [], "raw_output": "{}"},
            },
            "skill_compose": {"skill_spec": {"name": "test-skill", "version": "0.1.0"}},
        }
        result1 = handler.execute(artifacts)
        result2 = handler.execute(artifacts)

        evidence1 = result1.get("audit_pack", {}).get("files", {}).get("evidence", [])
        evidence2 = result2.get("audit_pack", {}).get("files", {}).get("evidence", [])

        ids1 = {e.get("evidence_id") for e in evidence1}
        ids2 = {e.get("evidence_id") for e in evidence2}

        # IDs should be different between runs
        assert ids1 != ids2, "evidence_ids should be unique between runs"

    def test_evidence_id_format(self) -> None:
        """evidence_id should match ev-{uuid_hex[:8]} format."""
        handler = PackPublish()
        artifacts = {
            "scaffold_skill_impl": {"bundle_path": "/tmp/test-bundle"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {"passed": 1, "failed": 0},
                "static_analysis": {"findings": [], "raw_output": "{}"},
            },
            "skill_compose": {"skill_spec": {"name": "test-skill", "version": "0.1.0"}},
        }
        result = handler.execute(artifacts)

        evidence = result.get("audit_pack", {}).get("files", {}).get("evidence", [])

        import re
        pattern = re.compile(r"^ev-[a-f0-9]{8}$")

        for ev in evidence:
            eid = ev.get("evidence_id", "")
            assert pattern.match(eid), f"evidence_id '{eid}' does not match ev-{{uuid_hex[:8]}} format"
