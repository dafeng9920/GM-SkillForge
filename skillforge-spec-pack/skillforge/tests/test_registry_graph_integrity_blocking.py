"""
T2: Registry/Graph Integrity Blocking Tests

Tests that verify:
1. Pre-publish integrity verification is performed
2. Tampering detection returns DENY with conflict evidence
3. Publishing is blocked when tampering is detected
4. Integrity gate decisions are recorded in gate_decisions
5. Conflict results are capturable by test_registry_graph_integrity.py
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

import pytest

from skillforge.src.storage.repository import SkillRepository
from skillforge.src.storage.schema import init_db


class TestIntegrityVerification:
    """Test integrity verification functionality in repository."""

    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Path:
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_integrity.sqlite"
        return db_path

    @pytest.fixture
    def repo(self, temp_db: Path) -> SkillRepository:
        """Create a repository with a temporary database."""
        return SkillRepository(db_path=temp_db)

    def test_compute_registry_hash_deterministic(self, repo: SkillRepository):
        """Test that registry hash is deterministic for same state."""
        skill_id = "test-skill-001"
        repo.ensure_skill(skill_id, "Test Skill")
        repo.append_revision(skill_id, "rev-001", manifest_sha256="hash1")

        hash1 = repo.compute_registry_hash(skill_id)
        hash2 = repo.compute_registry_hash(skill_id)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

    def test_compute_registry_hash_changes_on_modification(self, repo: SkillRepository):
        """Test that registry hash changes when state is modified."""
        skill_id = "test-skill-002"
        repo.ensure_skill(skill_id, "Test Skill")
        repo.append_revision(skill_id, "rev-001", manifest_sha256="hash1")

        hash_before = repo.compute_registry_hash(skill_id)

        # Modify state
        repo.append_revision(skill_id, "rev-002", manifest_sha256="hash2")

        hash_after = repo.compute_registry_hash(skill_id)

        assert hash_before != hash_after

    def test_record_integrity_chain(self, repo: SkillRepository):
        """Test recording integrity chain entries."""
        skill_id = "test-skill-003"
        repo.ensure_skill(skill_id, "Test Skill")
        computed_hash = repo.compute_registry_hash(skill_id)

        entry = repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=computed_hash,
            recorded_by="test_node",
            metadata={"test": True},
        )

        assert entry["chain_id"].startswith("ichain-")
        assert entry["chain_type"] == "registry"
        assert entry["entity_id"] == skill_id
        assert entry["computed_hash"] == computed_hash
        assert entry["recorded_by"] == "test_node"

    def test_integrity_chain_append_only(self, repo: SkillRepository):
        """Test that integrity chain is append-only (prev_hash linked)."""
        skill_id = "test-skill-004"
        repo.ensure_skill(skill_id, "Test Skill")

        # Record first entry
        hash1 = repo.compute_registry_hash(skill_id)
        entry1 = repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=hash1,
        )

        # Modify and record second entry
        repo.append_revision(skill_id, "rev-001", manifest_sha256="newhash")
        hash2 = repo.compute_registry_hash(skill_id)
        entry2 = repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=hash2,
        )

        # Second entry should link to first
        assert entry2["prev_hash"] == entry1["computed_hash"]

    def test_verify_integrity_no_prior_state(self, repo: SkillRepository):
        """Test integrity verification with no prior state (first publish)."""
        skill_id = "test-skill-005"
        repo.ensure_skill(skill_id, "Test Skill")

        result = repo.verify_integrity("registry", skill_id)

        assert result["verified"] is True
        assert result["stored_hash"] is None
        assert result["mismatch"] is False
        assert result["evidence"]["first_publish"] is True

    def test_verify_integrity_match(self, repo: SkillRepository):
        """Test integrity verification when state matches."""
        skill_id = "test-skill-006"
        repo.ensure_skill(skill_id, "Test Skill")

        # Record integrity
        hash1 = repo.compute_registry_hash(skill_id)
        repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=hash1,
        )

        # Verify (no changes)
        result = repo.verify_integrity("registry", skill_id)

        assert result["verified"] is True
        assert result["mismatch"] is False

    def test_verify_integrity_mismatch_detects_tampering(self, repo: SkillRepository):
        """Test that integrity verification detects tampering."""
        skill_id = "test-skill-007"
        repo.ensure_skill(skill_id, "Test Skill")

        # Record initial integrity
        hash1 = repo.compute_registry_hash(skill_id)
        repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=hash1,
        )

        # Simulate tampering by directly modifying manifest_sha256
        conn = repo.conn
        conn.execute(
            "INSERT INTO revisions (revision_id, skill_id, effective_at, status, manifest_sha256) "
            "VALUES (?, ?, datetime('now'), 'ACTIVE', ?)",
            ("rev-tampered", skill_id, "tampered-manifest-sha256"),
        )
        conn.commit()

        # Verify should detect mismatch
        result = repo.verify_integrity("registry", skill_id)

        assert result["verified"] is False
        assert result["mismatch"] is True
        assert result["evidence"]["tampering_detected"] is True
        assert result["evidence"]["stored_hash"] == hash1
        assert result["evidence"]["computed_hash"] != hash1

    def test_detect_tampering_returns_allow_when_clean(self, repo: SkillRepository):
        """Test detect_tampering returns ALLOW when no tampering."""
        skill_id = "test-skill-008"
        repo.ensure_skill(skill_id, "Test Skill")

        # Record initial integrity
        hash1 = repo.compute_registry_hash(skill_id)
        repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=hash1,
        )

        result = repo.detect_tampering(skill_id)

        assert result["tampering_detected"] is False
        assert result["decision"] == "ALLOW"
        assert result["ruling"] is None

    def test_detect_tampering_returns_deny_when_tampered(self, repo: SkillRepository):
        """Test detect_tampering returns DENY with ruling when tampering detected."""
        skill_id = "test-skill-009"
        repo.ensure_skill(skill_id, "Test Skill")

        # Record initial integrity
        hash1 = repo.compute_registry_hash(skill_id)
        repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=hash1,
        )

        # Simulate tampering
        conn = repo.conn
        conn.execute(
            "INSERT INTO revisions (revision_id, skill_id, effective_at, status, manifest_sha256) "
            "VALUES (?, ?, datetime('now'), 'ACTIVE', ?)",
            ("rev-tampered", skill_id, "tampered-manifest-sha256-for-l3-test"),
        )
        conn.commit()

        result = repo.detect_tampering(skill_id)

        assert result["tampering_detected"] is True
        assert result["decision"] == "DENY"
        assert result["ruling"]["verdict"] == "DENY"
        assert result["ruling"]["rule_id"] == "INTEGRITY_TAMPER_DETECTED"
        assert result["ruling"]["blocked"] is True


class TestPackPublishIntegrityGate:
    """Test integrity gate integration in PackPublish node."""

    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Path:
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_publish_integrity.sqlite"
        return db_path

    @pytest.fixture
    def repo(self, temp_db: Path) -> SkillRepository:
        """Create a repository with a temporary database."""
        return SkillRepository(db_path=temp_db)

    @pytest.fixture
    def basic_input(self) -> dict[str, Any]:
        """Create basic input data for PackPublish."""
        return {
            "scaffold_skill_impl": {
                "diff": "# No modifications",
            },
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {"passed": 5, "failed": 0},
                "trace_events": [],
                "static_analysis": {
                    "findings": [],
                    "raw_output": "[INFO] Static analysis complete.",
                },
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "test-integrity-skill",
                    "version": "0.1.0",
                    "title": "Test Integrity Skill",
                },
            },
            "intake_repo": {
                "repo_url": "https://github.com/test/repo",
                "commit_sha": "abc123",
                "source": "github",
            },
            "license_gate": {
                "decision": "ALLOW",
                "license": "MIT",
                "license_spdx": "MIT",
            },
            "constitution_risk_gate": {
                "decision": "ALLOW",
                "risk_score": 0.1,
            },
            "repo_scan_fit_score": {
                "findings": [],
                "scan_result": {},
            },
        }

    def test_first_publish_records_integrity(
        self, repo: SkillRepository, basic_input: dict[str, Any], tmp_path: Path, monkeypatch
    ):
        """Test that first publish records integrity hash."""
        import os
        monkeypatch.setenv("SKILLFORGE_DB_PATH", str(tmp_path / "test.sqlite"))

        from skillforge.src.nodes.pack_publish import PackPublish

        node = PackPublish()
        result = node.execute(basic_input)

        assert result["publish_result"]["status"] == "published"
        assert "gate_decisions" in result["audit_pack"]

        # Check that integrity was recorded (no DENY means integrity passed)
        gate_decisions = result["audit_pack"]["gate_decisions"]
        deny_gates = [g for g in gate_decisions if g.get("decision") == "DENY"]
        assert len(deny_gates) == 0

    def test_tampering_blocks_publish(
        self, repo: SkillRepository, basic_input: dict[str, Any], tmp_path: Path, monkeypatch
    ):
        """Test that tampering detection blocks publishing."""
        db_path = tmp_path / "test.sqlite"
        monkeypatch.setenv("SKILLFORGE_DB_PATH", str(db_path))

        from skillforge.src.nodes.pack_publish import PackPublish

        skill_id = basic_input["skill_compose"]["skill_spec"]["name"]

        # Simulate first publish to establish integrity baseline
        repo.ensure_skill(skill_id, "Test Integrity Skill")
        initial_hash = repo.compute_registry_hash(skill_id)
        repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=initial_hash,
            recorded_by="first_publish",
        )

        # Simulate tampering - modify manifest_sha256
        conn = repo.conn
        conn.execute(
            "INSERT INTO revisions (revision_id, skill_id, effective_at, status, manifest_sha256) "
            "VALUES (?, ?, datetime('now'), 'ACTIVE', ?)",
            ("rev-tampered", skill_id, "tampered-manifest-sha256-for-l3-test"),
        )
        conn.commit()

        # Now attempt to publish - should be blocked
        node = PackPublish()
        result = node.execute(basic_input)

        assert result["publish_result"]["status"] == "rejected"

        # Check that integrity gate DENY is in gate_decisions
        gate_decisions = result["audit_pack"]["gate_decisions"]
        integrity_gates = [g for g in gate_decisions if "integrity" in str(g.get("gate", "")).lower()]
        assert len(integrity_gates) > 0

        integrity_gate = integrity_gates[0]
        assert integrity_gate["decision"] == "DENY"
        assert integrity_gate["ruling"]["rule_id"] == "INTEGRITY_TAMPER_DETECTED"

    def test_integrity_gate_in_gate_decisions(
        self, repo: SkillRepository, basic_input: dict[str, Any], tmp_path: Path, monkeypatch
    ):
        """Test that integrity gate decision is recorded in gate_decisions."""
        db_path = tmp_path / "test.sqlite"
        monkeypatch.setenv("SKILLFORGE_DB_PATH", str(db_path))

        from skillforge.src.nodes.pack_publish import PackPublish

        skill_id = basic_input["skill_compose"]["skill_spec"]["name"]

        # Simulate existing skill with tampering
        repo.ensure_skill(skill_id, "Test Integrity Skill")
        initial_hash = repo.compute_registry_hash(skill_id)
        repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=initial_hash,
            recorded_by="first_publish",
        )

        # Tamper
        conn = repo.conn
        conn.execute(
            "INSERT INTO revisions (revision_id, skill_id, effective_at, status, manifest_sha256) "
            "VALUES (?, ?, datetime('now'), 'ACTIVE', ?)",
            ("rev-tampered", skill_id, "tampered-manifest-sha256-for-l3-test"),
        )
        conn.commit()

        node = PackPublish()
        result = node.execute(basic_input)

        gate_decisions = result["audit_pack"]["gate_decisions"]

        # Find integrity gate
        integrity_gate = None
        for g in gate_decisions:
            if "integrity" in str(g.get("gate", "")).lower() or "integrity" in str(g.get("node_id", "")).lower():
                integrity_gate = g
                break

        assert integrity_gate is not None
        assert "timestamp" in integrity_gate
        assert "evidence" in integrity_gate

    def test_conflict_result_capturable_by_test_script(
        self, repo: SkillRepository, basic_input: dict[str, Any], tmp_path: Path, monkeypatch
    ):
        """Test that conflict results are in format capturable by test_registry_graph_integrity.py."""
        db_path = tmp_path / "test.sqlite"
        monkeypatch.setenv("SKILLFORGE_DB_PATH", str(db_path))

        from skillforge.src.nodes.pack_publish import PackPublish

        skill_id = basic_input["skill_compose"]["skill_spec"]["name"]

        # Setup tampered state
        repo.ensure_skill(skill_id, "Test Integrity Skill")
        initial_hash = repo.compute_registry_hash(skill_id)
        repo.record_integrity_chain(
            chain_type="registry",
            entity_id=skill_id,
            computed_hash=initial_hash,
            recorded_by="first_publish",
        )

        conn = repo.conn
        conn.execute(
            "INSERT INTO revisions (revision_id, skill_id, effective_at, status, manifest_sha256) "
            "VALUES (?, ?, datetime('now'), 'ACTIVE', ?)",
            ("rev-tampered", skill_id, "tampered-manifest-sha256-for-l3-test"),
        )
        conn.commit()

        node = PackPublish()
        result = node.execute(basic_input)

        # Verify format matches what test_registry_graph_integrity.py expects
        # The test script checks:
        # 1. status in {"failed", "gate_denied"}
        # 2. error with conflict/integrity/hash/mismatch/tamper keywords
        # 3. gate_decisions with DENY/BLOCK/REQUIRES_CHANGES
        # 4. publish_result.status != "published"

        gate_decisions = result["audit_pack"]["gate_decisions"]
        has_deny = any(
            g.get("decision") in ("DENY", "BLOCK", "REQUIRES_CHANGES")
            for g in gate_decisions
        )

        # The conflict_detected function in test script should return True
        assert result["publish_result"]["status"] != "published"
        assert has_deny


class TestIntegrityHashFormat:
    """Test that integrity hashes match expected format."""

    def test_hash_is_sha256_hex(self):
        """Test that computed hashes are valid SHA256 hex strings."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.sqlite"
            repo = SkillRepository(db_path=db_path)

            skill_id = "hash-format-test"
            repo.ensure_skill(skill_id, "Hash Format Test")

            hash_value = repo.compute_registry_hash(skill_id)

            # SHA256 produces 64 hex characters
            assert len(hash_value) == 64
            assert all(c in "0123456789abcdef" for c in hash_value)

            repo.close()

    def test_integrity_chain_hash_stored_correctly(self):
        """Test that hashes are stored correctly in integrity_chains table."""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.sqlite"
            repo = SkillRepository(db_path=db_path)

            skill_id = "chain-hash-test"
            repo.ensure_skill(skill_id, "Chain Hash Test")

            computed_hash = repo.compute_registry_hash(skill_id)
            entry = repo.record_integrity_chain(
                chain_type="registry",
                entity_id=skill_id,
                computed_hash=computed_hash,
            )

            assert entry["computed_hash"] == computed_hash
            assert entry["hash_algorithm"] == "sha256"  # default

            repo.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
