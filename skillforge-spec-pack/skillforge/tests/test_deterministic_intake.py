"""
test_deterministic_intake.py — T-V0-A: Deterministic Intake tests.

Tests for commit_sha enforcement and constitution compliance rules.

Run: python -m pytest skillforge/tests/test_deterministic_intake.py -v
"""
from __future__ import annotations

import pytest


# ==============================================================================
# TestCommitShaRequired: commit_sha is MUST for github mode
# ==============================================================================
class TestCommitShaRequired:
    """commit_sha is required for github mode and propagated through pipeline."""

    def test_missing_commit_sha_denied(self):
        """Intake without commit_sha should be denied."""
        from skillforge.src.nodes.intake_repo import IntakeRepo

        handler = IntakeRepo()
        input_data = {
            "input": {
                "repo_url": "https://github.com/test/repo",
                "branch": "main",
            }
        }
        errors = handler.validate_input(input_data)
        assert len(errors) > 0
        assert any("commit_sha" in e for e in errors), "Expected commit_sha error"

    def test_commit_sha_present_allowed(self):
        """Intake with commit_sha should pass validation."""
        from skillforge.src.nodes.intake_repo import IntakeRepo

        handler = IntakeRepo()
        input_data = {
            "input": {
                "repo_url": "https://github.com/test/repo",
                "branch": "main",
                "commit_sha": "abc123def456",
            }
        }
        errors = handler.validate_input(input_data)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_commit_sha_propagated_to_output(self):
        """commit_sha should be present in intake output."""
        from skillforge.src.nodes.intake_repo import IntakeRepo

        handler = IntakeRepo()
        input_data = {
            "input": {
                "repo_url": "https://github.com/test/repo",
                "branch": "main",
                "commit_sha": "abc123def456",
            }
        }
        result = handler.execute(input_data)
        assert "commit_sha" in result, "commit_sha missing from output"
        assert result["commit_sha"] == "abc123def456"

    def test_commit_sha_in_validate_output(self):
        """validate_output should check for commit_sha."""
        from skillforge.src.nodes.intake_repo import IntakeRepo

        handler = IntakeRepo()
        # Output without commit_sha
        output_no_sha = {
            "schema_version": "0.1.0",
            "repo_info": {"name": "test", "owner": "test", "default_branch": "main"},
            "fetch_status": "ok",
        }
        errors = handler.validate_output(output_no_sha)
        assert any("commit_sha" in e for e in errors), "Expected commit_sha error in output"

        # Output with commit_sha
        output_with_sha = {
            "schema_version": "0.1.0",
            "repo_info": {"name": "test", "owner": "test", "default_branch": "main"},
            "commit_sha": "abc123",
            "fetch_status": "ok",
        }
        errors = handler.validate_output(output_with_sha)
        assert not any("commit_sha" in e for e in errors), "Unexpected commit_sha error"

    def test_commit_sha_propagated_to_audit_pack(self):
        """commit_sha should be present in original_repo_snapshot of audit pack."""
        from skillforge.src.nodes.pack_publish import PackPublish

        handler = PackPublish()
        artifacts = {
            "input": {
                "repo_url": "https://github.com/test/repo",
                "commit_sha": "abc123def456",
            },
            "intake_repo": {
                "commit_sha": "abc123def456",
            },
            "scaffold_skill_impl": {},
            "sandbox_test_and_trace": {"test_report": {}, "trace_events": []},
            "skill_compose": {"skill_spec": {"name": "test-skill", "version": "1.0.0"}},
        }
        result = handler.execute(artifacts)
        snapshot = result.get("audit_pack", {}).get("files", {}).get("original_repo_snapshot", {})
        assert "commit_sha" in snapshot, "commit_sha missing from original_repo_snapshot"
        assert snapshot["commit_sha"] == "abc123def456"

    def test_commit_sha_in_snapshot_fallback_to_input(self):
        """commit_sha should fallback to input if not in intake_repo."""
        from skillforge.src.nodes.pack_publish import PackPublish

        handler = PackPublish()
        artifacts = {
            "input": {
                "repo_url": "https://github.com/test/repo",
                "commit_sha": "fallback-sha",
            },
            "intake_repo": {},  # No commit_sha here
            "scaffold_skill_impl": {},
            "sandbox_test_and_trace": {"test_report": {}, "trace_events": []},
            "skill_compose": {"skill_spec": {"name": "test-skill", "version": "1.0.0"}},
        }
        result = handler.execute(artifacts)
        snapshot = result.get("audit_pack", {}).get("files", {}).get("original_repo_snapshot", {})
        assert snapshot.get("commit_sha") == "fallback-sha"


# ==============================================================================
# TestComplianceBoundaries: Constitution gate enforces robots.txt + no-auth rules
# ==============================================================================
class TestComplianceBoundaries:
    """Constitution gate enforces robots.txt + no-auth rules."""

    def test_web_crawl_without_robots_denied(self):
        """web_crawl without robots.txt compliance should be denied."""
        from skillforge.src.nodes.constitution_gate import ConstitutionGate

        handler = ConstitutionGate()
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "capabilities": {
                        "web_crawl": True,
                        "respect_robots_txt": False,  # Violation!
                    },
                }
            },
            "input": {"options": {}},
        }
        result = handler.execute(input_data)
        assert result["decision"] == "DENY"
        assert "robots.txt" in result["reason"].lower()

    def test_web_crawl_with_robots_allowed(self):
        """web_crawl with robots.txt compliance should be allowed."""
        from skillforge.src.nodes.constitution_gate import ConstitutionGate

        handler = ConstitutionGate()
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "capabilities": {
                        "web_crawl": True,
                        "respect_robots_txt": True,  # Compliant
                    },
                }
            },
            "input": {"options": {}},
        }
        result = handler.execute(input_data)
        assert result["decision"] == "ALLOW"

    def test_web_crawl_default_respect_robots_allowed(self):
        """web_crawl without explicit respect_robots_txt defaults to True (allowed)."""
        from skillforge.src.nodes.constitution_gate import ConstitutionGate

        handler = ConstitutionGate()
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "capabilities": {
                        "web_crawl": True,
                        # respect_robots_txt not specified, defaults to True
                    },
                }
            },
            "input": {"options": {}},
        }
        result = handler.execute(input_data)
        assert result["decision"] == "ALLOW"

    def test_authenticated_access_denied(self):
        """authenticated_access capability should be denied in v0."""
        from skillforge.src.nodes.constitution_gate import ConstitutionGate

        handler = ConstitutionGate()
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "capabilities": {
                        "authenticated_access": True,  # Violation!
                    },
                }
            },
            "input": {"options": {}},
        }
        result = handler.execute(input_data)
        assert result["decision"] == "DENY"
        assert "authenticated" in result["reason"].lower() or "restricted" in result["reason"].lower()

    def test_normal_skill_allowed(self):
        """Normal skill without violations should be allowed."""
        from skillforge.src.nodes.constitution_gate import ConstitutionGate

        handler = ConstitutionGate()
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "capabilities": {
                        "file_read": True,
                        "file_write": True,
                    },
                }
            },
            "input": {"options": {}},
        }
        result = handler.execute(input_data)
        assert result["decision"] == "ALLOW"


# ==============================================================================
# TestGateEngineCompliance: GateEngine enforces same rules
# ==============================================================================
class TestGateEngineCompliance:
    """GateEngine._evaluate_constitution_gate enforces robots.txt + no-auth rules."""

    def test_gate_engine_web_crawl_without_robots_denied(self):
        """GateEngine should deny web_crawl without robots.txt compliance."""
        from skillforge.src.orchestration.gate_engine import GateEngine

        engine = GateEngine()
        artifacts = {
            "draft_skill_spec": {
                "capabilities": {
                    "web_crawl": True,
                    "respect_robots_txt": False,
                }
            },
            "input": {"options": {}},
        }
        result = engine.evaluate("constitution_risk_gate", artifacts)
        assert result["decision"] == "DENY"
        assert "robots.txt" in result["reason"].lower()

    def test_gate_engine_authenticated_access_denied(self):
        """GateEngine should deny authenticated_access."""
        from skillforge.src.orchestration.gate_engine import GateEngine

        engine = GateEngine()
        artifacts = {
            "draft_skill_spec": {
                "capabilities": {
                    "authenticated_access": True,
                }
            },
            "input": {"options": {}},
        }
        result = engine.evaluate("constitution_risk_gate", artifacts)
        assert result["decision"] == "DENY"
        assert "authenticated" in result["reason"].lower() or "restricted" in result["reason"].lower()

    def test_gate_engine_normal_skill_allowed(self):
        """GateEngine should allow normal skill."""
        from skillforge.src.orchestration.gate_engine import GateEngine

        engine = GateEngine()
        artifacts = {
            "draft_skill_spec": {
                "capabilities": {
                    "file_read": True,
                }
            },
            "input": {"options": {}},
        }
        result = engine.evaluate("constitution_risk_gate", artifacts)
        assert result["decision"] == "ALLOW"
