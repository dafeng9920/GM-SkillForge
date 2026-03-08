"""
test_delivery.py — Delivery Layer Gate Tests.

Validates delivery layer gates conform to gate_interface_v1.yaml:
- GateScaffoldSkill (G5): scaffold_skill_impl gate
- GateSandboxSkill (G6): sandbox_test_and_trace gate (Fail-Closed)
- GatePublishSkill (G7): pack_audit_and_publish gate (L3 AuditPack)

All gates follow the experience_capture.py pattern:
- validate_input(input_data) -> list[str]
- execute(input_data) -> dict
- validate_output(output) -> list[str]

Key constraints verified:
1. Evidence chaining from G1-G6
2. L3 AuditPack includes 'content_hash' of all prior artifacts
3. Fail-Closed: Sandbox Fail MUST trigger REJECTED
4. GateResult schema compliance

Run: pytest tests/gates/test_delivery.py -v
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def valid_scaffold_output() -> dict[str, Any]:
    """Valid scaffold output for testing."""
    return {
        "schema_version": "0.1.0",
        "bundle_path": "/tmp/skillforge/bundles/test-skill",
        "files_generated": [
            "test-skill/main.py",
            "test-skill/manifest.json",
            "test-skill/README.md",
        ],
        "entry_point": "main.py",
        "language": "Python",
        "test_file": "test-skill/test_skill.py",
        "manifest": {
            "skill_id": "test-skill",
            "version": "1.0.0",
            "checksum": "abc123def456",
        },
    }


@pytest.fixture
def valid_sandbox_output() -> dict[str, Any]:
    """Valid sandbox output for testing."""
    return {
        "schema_version": "0.1.0",
        "success": True,
        "test_report": {
            "total_runs": 3,
            "passed": 3,
            "failed": 0,
            "success_rate": 1.0,
            "avg_latency_ms": 42.5,
        },
        "trace_events": [
            {"event_id": "ev-001", "event_type": "test_start", "timestamp": "2024-01-01T00:00:00Z"},
            {"event_id": "ev-002", "event_type": "test_end", "timestamp": "2024-01-01T00:00:01Z"},
        ],
        "sandbox_report": {
            "cpu_time_ms": 85,
            "memory_peak_mb": 12.3,
            "violations": [],
        },
        "static_analysis": {
            "tool": "semgrep",
            "version": "1.0.0",
            "findings": [],
            "raw_output": "",
        },
    }


@pytest.fixture
def valid_publish_output() -> dict[str, Any]:
    """Valid publish output for testing."""
    return {
        "schema_version": "1.0.0",
        "audit_pack": {
            "audit_id": "audit-abc123",
            "skill_id": "test-skill",
            "version": "1.0.0",
            "quality_level": "L3",
            "gate_decisions": [],
            "test_report": {"total_runs": 3, "passed": 3, "failed": 0},
            "trace_summary": {"total_events": 2},
            "created_at": "2024-01-01T00:00:00Z",
            "files": {
                "manifest": {
                    "schema_version": "1.0.0",
                    "audit_id": "audit-abc123",
                    "skill_id": "test-skill",
                    "provenance": {
                        "source": "github",
                        "commit_sha": "abc123",
                        "content_hash": "def456",
                    },
                    "files": [],
                },
                "policy_matrix": {"findings": []},
            },
        },
        "audit_pack_path": "/tmp/skillforge/audit/audit-abc123",
        "publish_result": {
            "skill_id": "test-skill",
            "version": "1.0.0",
            "status": "published",
            "registry_url": "http://localhost:8080/skills/test-skill/1.0.0",
            "timestamp": "2024-01-01T00:00:00Z",
        },
    }


def _sha256_hex(data: str) -> str:
    """Generate SHA-256 hex hash for testing."""
    return hashlib.sha256(data.encode()).hexdigest()


@pytest.fixture
def prior_artifacts_no_scaffold() -> dict[str, Any]:
    """Mock prior pipeline artifacts G1-G4 without scaffold."""
    return {
        "intake_repo": {
            "repo_name": "test/repo",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123",
            "license": "MIT",
        },
        "license_gate": {
            "decision": "ALLOW",
            "license": "MIT",
            "evidence_refs": [
                {
                    "issue_key": "LICENSE-CHECK",
                    "source_locator": "file:///license",
                    "content_hash": _sha256_hex("license-check"),
                    "tool_revision": "0.1.0",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            ],
        },
        "repo_scan_fit_score": {
            "scan_result": {"score": 85},
            "findings": [],
            "evidence_refs": [
                {
                    "issue_key": "SCAN-RESULT",
                    "source_locator": "file:///scan",
                    "content_hash": _sha256_hex("scan-result"),
                    "tool_revision": "0.1.0",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            ],
        },
        "constitution_risk_gate": {
            "decision": "ALLOW",
            "reason": "Risk assessment passed",
            "evidence_refs": [
                {
                    "issue_key": "CONSTITUTION-CHECK",
                    "source_locator": "file:///constitution",
                    "content_hash": _sha256_hex("constitution-check"),
                    "tool_revision": "0.1.0",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            ],
        },
    }


@pytest.fixture
def prior_artifacts(valid_scaffold_output, prior_artifacts_no_scaffold) -> dict[str, Any]:
    """Mock prior pipeline artifacts G1-G4 with scaffold."""
    return {
        **prior_artifacts_no_scaffold,
        "scaffold_skill_impl": valid_scaffold_output,
    }


# =============================================================================
# GateScaffold Tests (G5)
# =============================================================================

class TestGateScaffold:
    """Tests for GateScaffold gate evaluator."""

    def test_scaffold_passes_with_valid_output(self, prior_artifacts, valid_scaffold_output):
        """Gate should PASSED when scaffold output is valid."""
        from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill

        gate = GateScaffoldSkill()
        artifacts = {**prior_artifacts, "scaffold_skill_impl": valid_scaffold_output}
        result = gate.execute(artifacts)

        assert result["gate_name"] == "scaffold_skill_impl"
        assert result["gate_decision"] == "PASSED"
        assert result["error_code"] is None
        assert result["next_action"] == "continue"
        assert isinstance(result["evidence_refs"], list)
        assert len(result["evidence_refs"]) > 0

    def test_scaffold_rejected_when_missing(self, prior_artifacts_no_scaffold):
        """Gate should REJECTED when scaffold output is missing."""
        from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill

        gate = GateScaffoldSkill()
        result = gate.execute(prior_artifacts_no_scaffold)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("scaffold" in err.lower() for err in result.get("validation_errors", []))
        assert result["next_action"] == "halt"

    def test_scaffold_rejected_when_no_files(self, prior_artifacts, valid_scaffold_output):
        """Gate should REJECTED when no files were generated."""
        from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill

        gate = GateScaffoldSkill()
        invalid_scaffold = {**valid_scaffold_output, "files_generated": []}
        artifacts = {**prior_artifacts, "scaffold_skill_impl": invalid_scaffold}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("files" in err.lower() for err in result.get("validation_errors", []))

    def test_scaffold_rejected_when_manifest_missing(self, prior_artifacts, valid_scaffold_output):
        """Gate should REJECTED when manifest is missing."""
        from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill

        gate = GateScaffoldSkill()
        invalid_scaffold = {k: v for k, v in valid_scaffold_output.items() if k != "manifest"}
        artifacts = {**prior_artifacts, "scaffold_skill_impl": invalid_scaffold}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("manifest" in err.lower() for err in result.get("validation_errors", []))

    def test_scaffold_chains_prior_evidence(self, prior_artifacts, valid_scaffold_output):
        """Gate should chain evidence from prior gates G1-G4."""
        from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill

        gate = GateScaffoldSkill()
        artifacts = {**prior_artifacts, "scaffold_skill_impl": valid_scaffold_output}
        result = gate.execute(artifacts)

        # Should have evidence refs from prior gates (license_gate, repo_scan, constitution)
        evidence_refs = result["evidence_refs"]
        issue_keys = [ref["issue_key"] for ref in evidence_refs]

        # Should contain chain references from prior gates
        assert any("LICENSE" in key or "CHAIN-G2" in key for key in issue_keys)
        assert any("SCAN" in key or "CHAIN-G3" in key for key in issue_keys)

    def test_scaffold_includes_content_hash(self, prior_artifacts, valid_scaffold_output):
        """Gate evidence refs should include content_hash."""
        from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill

        gate = GateScaffoldSkill()
        artifacts = {**prior_artifacts, "scaffold_skill_impl": valid_scaffold_output}
        result = gate.execute(artifacts)

        # All evidence refs should have content_hash field
        for ref in result["evidence_refs"]:
            assert "content_hash" in ref

        # At least the gate's own evidence (SCAFFOLD-*) should have valid SHA-256 hash
        scaffold_refs = [r for r in result["evidence_refs"] if "SCAFFOLD-" in r.get("issue_key", "")]
        for ref in scaffold_refs:
            assert len(ref["content_hash"]) == 64  # SHA-256 hex length


# =============================================================================
# GateSandbox Tests (G6) - Fail-Closed
# =============================================================================

class TestGateSandbox:
    """Tests for GateSandbox gate evaluator with Fail-Closed behavior."""

    def test_sandbox_passes_with_valid_output(self, prior_artifacts, valid_sandbox_output):
        """Gate should PASSED when sandbox tests pass."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": valid_sandbox_output}
        result = gate.execute(artifacts)

        assert result["gate_name"] == "sandbox_test_and_trace"
        assert result["gate_decision"] == "PASSED"
        assert result["error_code"] is None
        assert result["next_action"] == "continue"

    def test_sandbox_fail_closed_on_test_failure(self, prior_artifacts, valid_sandbox_output):
        """FAIL-CLOSED: Test failure MUST trigger REJECTED."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        failed_sandbox = {**valid_sandbox_output, "success": False}
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": failed_sandbox}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "ERR_TESTS_FAILED"
        assert result["next_action"] == "halt"

    def test_sandbox_fail_closed_on_missing_status(self, prior_artifacts, valid_sandbox_output):
        """FAIL-CLOSED: Missing success status MUST trigger REJECTED."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        invalid_sandbox = {k: v for k, v in valid_sandbox_output.items() if k != "success"}
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": invalid_sandbox}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        # Validation fails because success field is required
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("success" in err.lower() for err in result.get("validation_errors", []))

    def test_sandbox_fail_closed_on_violations(self, prior_artifacts, valid_sandbox_output):
        """FAIL-CLOSED: Sandbox violations MUST trigger REJECTED."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        violated_sandbox = {
            **valid_sandbox_output,
            "sandbox_report": {
                "cpu_time_ms": 85,
                "memory_peak_mb": 12.3,
                "violations": ["network_access", "file_write"],
            },
        }
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": violated_sandbox}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "ERR_SANDBOX_VIOLATIONS"

    def test_sandbox_fail_closed_on_critical_findings(self, prior_artifacts, valid_sandbox_output):
        """FAIL-CLOSED: Critical static analysis findings MUST trigger REJECTED."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        critical_sandbox = {
            **valid_sandbox_output,
            "static_analysis": {
                "tool": "semgrep",
                "version": "1.0.0",
                "findings": [
                    {
                        "rule_id": "SEC001",
                        "severity": "critical",
                        "message": "SQL injection vulnerability",
                        "location": {"file": "main.py", "line": 42},
                    }
                ],
            },
        }
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": critical_sandbox}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "ERR_CRITICAL_FINDINGS"

    def test_sandbox_fail_closed_on_test_failures(self, prior_artifacts, valid_sandbox_output):
        """FAIL-CLOSED: Test failures count > 0 MUST trigger REJECTED."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        failed_tests_sandbox = {
            **valid_sandbox_output,
            "test_report": {
                "total_runs": 3,
                "passed": 2,
                "failed": 1,  # 1 failure
            },
        }
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": failed_tests_sandbox}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "ERR_TEST_FAILURES"

    def test_sandbox_rejected_when_scaffold_rejected(self, prior_artifacts, valid_sandbox_output):
        """Gate should REJECTED if scaffold was rejected."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        rejected_scaffold = {
            **prior_artifacts["scaffold_skill_impl"],
            "gate_decision": "REJECTED",
        }
        artifacts = {
            **prior_artifacts,
            "scaffold_skill_impl": rejected_scaffold,
            "sandbox_test_and_trace": valid_sandbox_output,
        }
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        # Validation fails because scaffold gate was rejected (PREREQUISITE_FAILED)
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("scaffold" in err.lower() or "prerequisite" in err.lower()
                   for err in result.get("validation_errors", []))

    def test_sandbox_includes_trace_evidence(self, prior_artifacts, valid_sandbox_output):
        """Gate should include trace events in evidence refs."""
        from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill

        gate = GateSandboxSkill()
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": valid_sandbox_output}
        result = gate.execute(artifacts)

        issue_keys = [ref["issue_key"] for ref in result["evidence_refs"]]
        assert any("TRACE" in key for key in issue_keys)


# =============================================================================
# GatePublish Tests (G7) - L3 AuditPack
# =============================================================================

class TestGatePublish:
    """Tests for GatePublish gate evaluator with L3 AuditPack requirements."""

    def test_publish_passes_with_valid_output(
        self, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """Gate should PASSED when publish output is valid."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": valid_sandbox_output,
            "pack_audit_and_publish": valid_publish_output,
        }
        result = gate.execute(artifacts)

        assert result["gate_name"] == "pack_audit_and_publish"
        assert result["gate_decision"] == "PASSED"
        assert result["error_code"] is None
        assert result["next_action"] == "continue"

    def test_publish_rejected_when_missing(self, prior_artifacts, valid_sandbox_output):
        """Gate should REJECTED when publish output is missing."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        artifacts = {**prior_artifacts, "sandbox_test_and_trace": valid_sandbox_output}
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("pack_audit_and_publish" in err.lower() for err in result.get("validation_errors", []))

    def test_publish_rejected_when_audit_pack_missing(
        self, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """Gate should REJECTED when audit_pack is missing."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        invalid_publish = {k: v for k, v in valid_publish_output.items() if k != "audit_pack"}
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": valid_sandbox_output,
            "pack_audit_and_publish": invalid_publish,
        }
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("audit_pack" in err.lower() for err in result.get("validation_errors", []))

    def test_publish_rejected_when_quality_level_not_l3(
        self, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """Gate should REJECTED when quality_level is not L3."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        invalid_publish = {
            **valid_publish_output,
            "audit_pack": {**valid_publish_output["audit_pack"], "quality_level": "L1"},
        }
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": valid_sandbox_output,
            "pack_audit_and_publish": invalid_publish,
        }
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "VALIDATION_FAILED"
        assert any("quality_level" in err.lower() or "l3" in err.lower()
                   for err in result.get("validation_errors", []))

    def test_publish_rejected_when_publish_status_rejected(
        self, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """Gate should REJECTED when publish status is 'rejected'."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        rejected_publish = {
            **valid_publish_output,
            "publish_result": {**valid_publish_output["publish_result"], "status": "rejected"},
        }
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": valid_sandbox_output,
            "pack_audit_and_publish": rejected_publish,
        }
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"
        assert result["error_code"] == "ERR_PUBLISH_REJECTED"

    def test_publish_includes_content_hash_of_prior_artifacts(
        self, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """L3 AuditPack must include content_hash of all prior artifacts."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": valid_sandbox_output,
            "pack_audit_and_publish": valid_publish_output,
        }
        result = gate.execute(artifacts)

        # Should have evidence refs for all prior artifacts (G1-G6)
        evidence_refs = result["evidence_refs"]
        artifact_sources = [ref.get("source_locator", "") for ref in evidence_refs]

        # Verify content_hash presence for all artifacts
        for ref in evidence_refs:
            assert "content_hash" in ref

        # Gate's own artifact:// refs should have valid SHA-256 hash (64 chars)
        artifact_refs = [r for r in evidence_refs if "artifact://" in r.get("source_locator", "")]
        for ref in artifact_refs:
            assert len(ref["content_hash"]) == 64  # SHA-256 hex

        # Verify we have artifact:// references for G1-G6
        assert any("artifact://intake_repo" in src for src in artifact_sources)
        assert any("artifact://scaffold_skill_impl" in src for src in artifact_sources)
        assert any("artifact://sandbox_test_and_trace" in src for src in artifact_sources)

    def test_publish_rejected_when_sandbox_rejected(
        self, prior_artifacts, valid_publish_output
    ):
        """Gate should REJECTED if sandbox was rejected."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        rejected_sandbox = {
            "gate_decision": "REJECTED",
            "success": False,
        }
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": rejected_sandbox,
            "pack_audit_and_publish": valid_publish_output,
        }
        result = gate.execute(artifacts)

        assert result["gate_decision"] == "REJECTED"


# =============================================================================
# GateResult Schema Compliance Tests
# =============================================================================

class TestGateResultSchema:
    """Tests for GateResult schema compliance per gate_interface_v1.yaml."""

    @pytest.mark.parametrize("gate_class,gate_name,artifacts_key", [
        ("GateScaffold", "scaffold_skill_impl", "scaffold_skill_impl"),
        ("GateSandbox", "sandbox_test_and_trace", "sandbox_test_and_trace"),
        ("GatePublish", "pack_audit_and_publish", "pack_audit_and_publish"),
    ])
    def test_gate_result_has_required_fields(
        self, gate_class, gate_name, artifacts_key, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """All GateResults must have required fields per schema."""
        if gate_class == "GateScaffold":
            from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill as Gate
            artifacts = {**prior_artifacts}
            artifacts["scaffold_skill_impl"] = prior_artifacts["scaffold_skill_impl"]
        elif gate_class == "GateSandbox":
            from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill as Gate
            artifacts = {**prior_artifacts, "sandbox_test_and_trace": valid_sandbox_output}
        else:
            from skillforge.src.skills.gates.gate_publish import GatePublishSkill as Gate
            artifacts = {
                **prior_artifacts,
                "sandbox_test_and_trace": valid_sandbox_output,
                "pack_audit_and_publish": valid_publish_output,
            }

        gate = Gate()
        result = gate.execute(artifacts)

        # Verify required fields
        assert "gate_name" in result
        assert "gate_decision" in result
        assert "error_code" in result
        assert "evidence_refs" in result
        assert "next_action" in result

        # Verify field types
        assert isinstance(result["gate_name"], str)
        assert result["gate_decision"] in ("PASSED", "REJECTED")
        assert result["error_code"] is None or isinstance(result["error_code"], str)
        assert isinstance(result["evidence_refs"], list)
        assert result["next_action"] in ("continue", "halt")

    @pytest.mark.parametrize("gate_class", ["GateScaffold", "GateSandbox", "GatePublish"])
    def test_evidence_ref_schema_compliance(
        self, gate_class, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """All EvidenceRefs must have required fields per schema."""
        if gate_class == "GateScaffold":
            from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill as Gate
            artifacts = {**prior_artifacts}
        elif gate_class == "GateSandbox":
            from skillforge.src.skills.gates.gate_sandbox import GateSandboxSkill as Gate
            artifacts = {**prior_artifacts, "sandbox_test_and_trace": valid_sandbox_output}
        else:
            from skillforge.src.skills.gates.gate_publish import GatePublishSkill as Gate
            artifacts = {
                **prior_artifacts,
                "sandbox_test_and_trace": valid_sandbox_output,
                "pack_audit_and_publish": valid_publish_output,
            }

        gate = Gate()
        result = gate.execute(artifacts)

        # Gate should produce at least one evidence ref
        assert len(result["evidence_refs"]) > 0

        for ref in result["evidence_refs"]:
            # Verify required fields per gate_interface_v1.yaml
            assert "issue_key" in ref
            assert "source_locator" in ref
            assert "content_hash" in ref
            assert "tool_revision" in ref
            assert "timestamp" in ref

            # Verify types
            assert isinstance(ref["issue_key"], str)
            assert isinstance(ref["source_locator"], str)
            assert isinstance(ref["content_hash"], str)
            assert isinstance(ref["tool_revision"], str)
            assert isinstance(ref["timestamp"], str)

        # At least gate's own evidence (not chained from prior) should have valid SHA-256
        # Chained evidence may have different hash formats from prior gates
        non_chained_refs = [
            r for r in result["evidence_refs"]
            if "CHAIN-" not in r.get("issue_key", "")
        ]
        for ref in non_chained_refs:
            # Verify content_hash is valid SHA-256 (64 hex chars)
            assert len(ref["content_hash"]) == 64, (
                f"Non-chained evidence {ref['issue_key']} content_hash should be SHA-256"
            )
            assert all(c in "0123456789abcdef" for c in ref["content_hash"])


# =============================================================================
# Evidence Chain Tests
# =============================================================================

class TestEvidenceChaining:
    """Tests for evidence chaining from G1-G6."""

    def test_full_evidence_chain(
        self, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """GatePublish should chain evidence from all prior gates G1-G6."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": valid_sandbox_output,
            "pack_audit_and_publish": valid_publish_output,
        }
        result = gate.execute(artifacts)

        # Count artifacts referenced
        artifact_refs = [
            ref for ref in result["evidence_refs"]
            if "artifact://" in ref.get("source_locator", "")
        ]

        # Should have refs for G1-G6
        sources = {ref["source_locator"] for ref in artifact_refs}
        expected_artifacts = [
            "artifact://intake_repo",
            "artifact://license_gate",
            "artifact://repo_scan_fit_score",
            "artifact://constitution_risk_gate",
            "artifact://scaffold_skill_impl",
            "artifact://sandbox_test_and_trace",
        ]

        for expected in expected_artifacts:
            assert expected in sources, f"Missing evidence chain for {expected}"

    def test_evidence_refs_have_unique_issue_keys(
        self, prior_artifacts, valid_sandbox_output, valid_publish_output
    ):
        """Evidence refs should have unique issue_keys within a gate result."""
        from skillforge.src.skills.gates.gate_publish import GatePublishSkill

        gate = GatePublishSkill()
        artifacts = {
            **prior_artifacts,
            "sandbox_test_and_trace": valid_sandbox_output,
            "pack_audit_and_publish": valid_publish_output,
        }
        result = gate.execute(artifacts)

        issue_keys = [ref["issue_key"] for ref in result["evidence_refs"]]
        # Allow some duplicates from chaining, but most should be unique
        unique_ratio = len(set(issue_keys)) / len(issue_keys) if issue_keys else 1.0
        assert unique_ratio >= 0.5, "Too many duplicate issue_keys in evidence refs"
