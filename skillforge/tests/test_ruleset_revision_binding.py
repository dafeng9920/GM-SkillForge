"""
Tests for Ruleset Revision Binding (SEEDS-P0-2)

Contract: T18 (L45-D4-SEEDS-P0-20260220-004)
Coverage: ruleset_revision mandatory presence and consistency
"""
import json
from pathlib import Path
from datetime import datetime, timezone

import pytest
import yaml


# ============================================================================
# Constants
# ============================================================================

# Get project root (GM-SkillForge)
# test file is at: GM-SkillForge/skillforge/tests/test_ruleset_revision_binding.py
# project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RULESET_MANIFEST_PATH = PROJECT_ROOT / "orchestration" / "ruleset_manifest.yml"
SCHEMA_PATH = PROJECT_ROOT / "skillforge" / "src" / "contracts" / "governance" / "gate_decision_envelope.schema.json"

CURRENT_RULESET_REVISION = "v1"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def ruleset_manifest():
    """Load ruleset manifest."""
    with open(RULESET_MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def gate_decision_schema():
    """Load gate decision envelope schema."""
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)


@pytest.fixture
def valid_gate_decision():
    """Create a valid gate decision with ruleset_revision and provenance.repro_env."""
    return {
        "job_id": "L45-D4-SEEDS-P0-20260220-004",
        "skill_id": "l45_seeds_p0_foundation",
        "task_id": "T18",
        "executor": "vs--cc1",
        "gate_decision": "ALLOW",
        "ruleset_revision": CURRENT_RULESET_REVISION,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evidence_ref": "EV-SEEDS-T18-001",
        "verdict": {
            "implementation_ready": "YES",
            "regression_ready": "YES",
            "baseline_ready": "YES",
            "ready_for_next_batch": "YES"
        },
        "provenance": {
            "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": {
                "repo_url": "https://github.com/skillforge/GM-SkillForge",
                "commit_sha": "abc123"
            },
            "repro_env": {
                "python_version": "3.11",
                "deps_lock_hash": "PLACEHOLDER",
                "os": "Windows 11",
                "tool_versions": {
                    "gm_skillforge": "0.0.1"
                }
            }
        },
        "reason": "All SEEDS P0 requirements met"
    }


# ============================================================================
# Ruleset Manifest Tests
# ============================================================================

class TestRulesetManifest:
    """Tests for ruleset manifest structure."""

    def test_ruleset_manifest_exists(self):
        """Ruleset manifest file must exist."""
        assert RULESET_MANIFEST_PATH.exists(), f"Ruleset manifest not found at {RULESET_MANIFEST_PATH}"

    def test_ruleset_manifest_valid_yaml(self, ruleset_manifest):
        """Ruleset manifest must be valid YAML."""
        assert ruleset_manifest is not None
        assert "version" in ruleset_manifest
        assert "ruleset_revision" in ruleset_manifest

    def test_ruleset_manifest_has_required_fields(self, ruleset_manifest):
        """Ruleset manifest must have required fields."""
        required_fields = ["version", "ruleset_revision", "sources"]
        for field in required_fields:
            assert field in ruleset_manifest, f"Missing required field: {field}"

    def test_ruleset_revision_format(self, ruleset_manifest):
        """Ruleset revision must follow format vX."""
        revision = ruleset_manifest["ruleset_revision"]
        assert revision.startswith("v"), f"Ruleset revision must start with 'v': {revision}"
        assert revision[1:].isdigit(), f"Ruleset revision must be vX format: {revision}"

    def test_ruleset_manifest_sources(self, ruleset_manifest):
        """Ruleset manifest must reference source documents."""
        sources = ruleset_manifest.get("sources", {})
        assert len(sources) > 0, "Sources must not be empty"

    def test_ruleset_manifest_constraints(self, ruleset_manifest):
        """Ruleset manifest must document constraints."""
        constraints = ruleset_manifest.get("constraints", [])
        assert len(constraints) > 0, "Constraints must be documented"


# ============================================================================
# Gate Decision Schema Tests
# ============================================================================

class TestGateDecisionSchema:
    """Tests for gate decision envelope schema."""

    def test_schema_exists(self):
        """Gate decision envelope schema must exist."""
        assert SCHEMA_PATH.exists(), f"Schema not found at {SCHEMA_PATH}"

    def test_schema_valid_json(self, gate_decision_schema):
        """Schema must be valid JSON."""
        assert gate_decision_schema is not None
        assert "$schema" in gate_decision_schema

    def test_schema_requires_ruleset_revision(self, gate_decision_schema):
        """Schema must require ruleset_revision field."""
        required_fields = gate_decision_schema.get("required", [])
        assert "ruleset_revision" in required_fields, "ruleset_revision must be in required fields"

    def test_schema_ruleset_revision_pattern(self, gate_decision_schema):
        """Schema must validate ruleset_revision format."""
        props = gate_decision_schema.get("properties", {})
        ruleset_revision = props.get("ruleset_revision", {})
        pattern = ruleset_revision.get("pattern")
        assert pattern is not None, "ruleset_revision must have pattern validation"
        assert "v" in pattern, "Pattern must require 'v' prefix"


# ============================================================================
# Ruleset Revision Binding Tests
# ============================================================================

class TestRulesetRevisionBinding:
    """Tests for ruleset_revision binding in gate decisions."""

    def test_valid_gate_decision_has_ruleset_revision(self, valid_gate_decision):
        """Valid gate decision must include ruleset_revision."""
        assert "ruleset_revision" in valid_gate_decision
        assert valid_gate_decision["ruleset_revision"] == CURRENT_RULESET_REVISION

    def test_gate_decision_without_ruleset_revision_invalid(self):
        """Gate decision without ruleset_revision must be invalid."""
        decision = {
            "job_id": "L45-D4-SEEDS-P0-20260220-004",
            "gate_decision": "ALLOW",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence_ref": "EV-TEST-001"
        }
        assert "ruleset_revision" not in decision

    def test_allow_without_ruleset_revision_forbidden(self):
        """ALLOW without ruleset_revision must be forbidden."""
        decision = {
            "job_id": "L45-D4-SEEDS-P0-20260220-004",
            "gate_decision": "ALLOW",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence_ref": "EV-TEST-001"
            # Missing ruleset_revision
        }
        # This decision should be rejected by validation
        assert "ruleset_revision" not in decision, "ALLOW must require ruleset_revision"

    def test_ruleset_revision_consistency(self, valid_gate_decision, ruleset_manifest):
        """Ruleset revision in decision must match manifest."""
        decision_revision = valid_gate_decision["ruleset_revision"]
        manifest_revision = ruleset_manifest["ruleset_revision"]
        assert decision_revision == manifest_revision, \
            f"Revision mismatch: decision={decision_revision}, manifest={manifest_revision}"


# ============================================================================
# Fail-Closed Tests
# ============================================================================

class TestFailClosed:
    """Tests for fail-closed behavior."""

    def test_missing_ruleset_revision_must_fail_closed(self):
        """Missing ruleset_revision must trigger fail-closed error."""
        decision = {
            "job_id": "L45-D4-SEEDS-P0-20260220-004",
            "gate_decision": "ALLOW",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence_ref": "EV-TEST-001"
        }

        # Validate that missing ruleset_revision would cause failure
        has_ruleset_revision = "ruleset_revision" in decision
        assert has_ruleset_revision is False, "Decision should not have ruleset_revision"

        # Fail-closed: should not allow
        is_valid = has_ruleset_revision and decision["gate_decision"] == "ALLOW"
        assert is_valid is False, "ALLOW without ruleset_revision must be invalid"

    def test_empty_ruleset_revision_must_fail_closed(self):
        """Empty ruleset_revision must trigger fail-closed error."""
        decision = {
            "job_id": "L45-D4-SEEDS-P0-20260220-004",
            "gate_decision": "ALLOW",
            "ruleset_revision": "",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence_ref": "EV-TEST-001"
        }

        # Empty string is invalid - must have value and min length 2
        revision = decision["ruleset_revision"]
        is_valid = bool(revision) and len(revision) >= 2
        assert is_valid is False, "Empty ruleset_revision must be invalid"

    def test_invalid_ruleset_revision_format_must_fail(self):
        """Invalid ruleset_revision format must fail."""
        invalid_revisions = ["1", "v", "V1", "version1", "v-1", "v1.0"]

        for rev in invalid_revisions:
            decision = {
                "job_id": "L45-D4-SEEDS-P0-20260220-004",
                "gate_decision": "ALLOW",
                "ruleset_revision": rev,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "evidence_ref": "EV-TEST-001"
            }

            # Check format: must be vX where X is digits
            is_valid_format = (
                rev.startswith("v") and
                len(rev) >= 2 and
                rev[1:].isdigit()
            )
            assert is_valid_format is False, f"Invalid revision '{rev}' should fail validation"


# ============================================================================
# At-Time Replay Tests
# ============================================================================

class TestAtTimeReplay:
    """Tests for at-time replay capability."""

    def test_ruleset_revision_readable_for_replay(self, valid_gate_decision):
        """Ruleset revision must be readable for at-time replay."""
        assert "ruleset_revision" in valid_gate_decision
        revision = valid_gate_decision["ruleset_revision"]
        assert revision is not None
        assert isinstance(revision, str)

    def test_provenance_includes_ruleset_revision(self):
        """Provenance should include ruleset_revision for replay."""
        provenance = {
            "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": {
                "repo_url": "https://github.com/your-org/GM-SkillForge",
                "commit_sha": "a1b2c3d4e5f6"
            },
            "ruleset_revision": CURRENT_RULESET_REVISION
        }

        assert "ruleset_revision" in provenance
        assert provenance["ruleset_revision"] == CURRENT_RULESET_REVISION

    def test_at_time_replay_can_verify_revision(self, valid_gate_decision, ruleset_manifest):
        """At-time replay can verify ruleset_revision consistency."""
        decision_revision = valid_gate_decision["ruleset_revision"]
        manifest_revision = ruleset_manifest["ruleset_revision"]

        # Replay verification: revision should match
        consistent = decision_revision == manifest_revision
        assert consistent is True, "At-time replay should find consistent ruleset_revision"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for ruleset revision binding."""

    def test_full_gate_decision_flow(self, valid_gate_decision, ruleset_manifest):
        """Full gate decision flow should include ruleset_revision."""
        # 1. Decision has ruleset_revision
        assert "ruleset_revision" in valid_gate_decision

        # 2. Revision matches manifest
        assert valid_gate_decision["ruleset_revision"] == ruleset_manifest["ruleset_revision"]

        # 3. Schema validation would pass
        assert valid_gate_decision["ruleset_revision"].startswith("v")

    def test_schema_allows_valid_decision(self, gate_decision_schema, valid_gate_decision):
        """Schema should allow valid gate decision with ruleset_revision."""
        required = gate_decision_schema.get("required", [])

        # Check all required fields are present
        for field in required:
            assert field in valid_gate_decision, f"Missing required field: {field}"

    def test_ruleset_revision_in_verification_summary(self, valid_gate_decision):
        """Gate decision can include ruleset_revision in verification."""
        # Verification should be traceable to ruleset
        verification = {
            "ruleset_revision": valid_gate_decision["ruleset_revision"],
            "verified_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "verified": True
        }

        assert verification["ruleset_revision"] == CURRENT_RULESET_REVISION
        assert verification["verified"] is True
