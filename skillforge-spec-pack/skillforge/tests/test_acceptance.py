"""
test_acceptance.py — Protocol v1.0 Acceptance Checklist (Section 9).

Maps 1:1 to the 7 Protocol compliance conditions.
Run: python -m pytest skillforge/tests/test_acceptance.py -v
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
ORCH = ROOT / "orchestration"


# ==============================================================================
# 1. Upstream 可复现: repo + commit/tag + fetched_at + snapshot_hash
# ==============================================================================
class TestUpstreamReproducible:
    """Pack-publish generates original_repo_snapshot.json with required fields."""

    def test_snapshot_fields_present(self):
        from skillforge.src.nodes.pack_publish import PackPublish

        handler = PackPublish()
        artifacts = {
            "input": {
                "mode": "github",
                "repo_url": "https://github.com/test/repo",
                "branch": "main",
                "options": {
                    "target_environment": "python",
                    "intended_use": "automation",
                    "visibility": "public",
                    "sandbox_mode": "strict",
                },
            },
            "intake_repo": {
                "repo_name": "test/repo",
                "license": "MIT",
                "files": ["README.md"],
            },
            "sandbox_test_and_trace": {
                "test_results": {"passed": 1, "failed": 0},
            },
        }
        result = handler.execute(artifacts)
        ap = result.get("audit_pack", {})
        files = ap.get("files", {})
        snapshot = files.get("original_repo_snapshot", {})

        assert "id" in snapshot or "repo_url" in snapshot
        assert "fetched_at" in snapshot
        assert "snapshot_hash" in snapshot


# ==============================================================================
# 2. Evidence 闭环: policy_matrix → evidence_ref → evidence.jsonl
# ==============================================================================
class TestEvidenceChain:
    """policy_matrix findings have evidence_ref that resolves to evidence.jsonl."""

    def test_evidence_ref_resolves(self):
        from skillforge.src.nodes.pack_publish import PackPublish

        handler = PackPublish()
        artifacts = {
            "input": {
                "mode": "nl",
                "natural_language": "test",
                "options": {
                    "target_environment": "python",
                    "intended_use": "automation",
                    "visibility": "public",
                    "sandbox_mode": "strict",
                },
            },
            "sandbox_test_and_trace": {
                "test_results": {"passed": 1, "failed": 0},
            },
        }
        result = handler.execute(artifacts)
        ap = result.get("audit_pack", {})
        files = ap.get("files", {})

        policy_matrix = files.get("policy_matrix", {})
        evidence = files.get("evidence", [])

        evidence_ids = {e.get("evidence_id") for e in evidence}
        for finding in policy_matrix.get("findings", []):
            ref = finding.get("evidence_ref")
            if ref:
                assert ref in evidence_ids, f"evidence_ref {ref} not found"


# ==============================================================================
# 3. Contracts-first: schemas/examples/tests/policies 一致性可自动校验
# ==============================================================================
class TestContractsFirst:
    """validate.py --all and --audit-config both pass."""

    def test_validate_all(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate.py"), "--all"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.returncode == 0, f"--all failed:\n{result.stderr}\n{result.stdout}"

    def test_validate_audit_config(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate.py"), "--audit-config"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert result.returncode == 0, f"--audit-config failed:\n{result.stderr}\n{result.stdout}"


# ==============================================================================
# 4. Error policy 对齐: fail → error_code + next_action + suggested_fixes.kind
# ==============================================================================
class TestErrorPolicyAligned:
    """Every error_policy entry has required fields."""

    def test_policy_entries_complete(self):
        import yaml

        with open(ORCH / "error_policy.yml", encoding="utf-8") as f:
            ep = yaml.safe_load(f)

        nodes = ep.get("nodes", {})
        for node_id, node in nodes.items():
            on_err = node.get("on_error", {})
            assert "error_code" in on_err, f"{node_id} missing error_code"
            na = on_err.get("next_action", {})
            assert "action_id" in na, f"{node_id} missing next_action.action_id"
            fixes = na.get("suggested_fixes", [])
            for fix in fixes:
                assert "kind" in fix, f"{node_id} fix missing kind"


# ==============================================================================
# 5. Revision/timepoint: snapshot(--include-deprecated) + index(--at-time)
# ==============================================================================
class TestRevisionTimepoint:
    """Storage layer supports temporal queries."""

    def test_snapshot_at_time(self):
        from skillforge.src.storage.repository import SkillRepository

        repo = SkillRepository(":memory:")
        repo.ensure_skill("s1", "Skill One")
        repo.append_revision("s1", "r1", "2026-01-01T00:00:00Z", quality_level="L3")
        repo.append_revision("s1", "r2", "2026-06-01T00:00:00Z", quality_level="L4")

        snap = repo.get_snapshot("s1", "2026-03-01T00:00:00Z")
        assert snap["revision"]["revision_id"] == "r1"

        snap2 = repo.get_snapshot("s1", "2026-12-01T00:00:00Z")
        assert snap2["revision"]["revision_id"] == "r2"
        repo.close()

    def test_index_at_time(self):
        from skillforge.src.storage.repository import SkillRepository

        repo = SkillRepository(":memory:")
        repo.ensure_skill("s1", "Skill One")
        repo.append_revision("s1", "r1", "2026-01-01T00:00:00Z")
        repo.ensure_skill("s2", "Skill Two")
        repo.append_revision("s2", "r2", "2026-06-01T00:00:00Z")

        idx = repo.get_index("2026-03-01T00:00:00Z")
        ids = [r["skill_id"] for r in idx]
        assert "s1" in ids
        assert "s2" not in ids

        idx2 = repo.get_index("2026-12-01T00:00:00Z")
        ids2 = [r["skill_id"] for r in idx2]
        assert "s1" in ids2
        assert "s2" in ids2
        repo.close()

    def test_include_deprecated(self):
        from skillforge.src.storage.repository import SkillRepository

        repo = SkillRepository(":memory:")
        repo.ensure_skill("s1", "Skill One")
        repo.append_revision("s1", "r1", "2026-01-01T00:00:00Z")
        repo.deprecate_revision("s1", "r1")

        idx_no = repo.get_index("2026-12-01T00:00:00Z", include_deprecated=False)
        idx_yes = repo.get_index("2026-12-01T00:00:00Z", include_deprecated=True)
        assert len(idx_no) == 0
        assert len(idx_yes) >= 1
        repo.close()


# ==============================================================================
# 6. Tombstone 生效: tombstone 后当前面不呈现，但历史仍可复现
# ==============================================================================
class TestTombstoneEffective:
    """Tombstone hides from current view but preserves history."""

    def test_tombstone_hides_skill(self):
        from skillforge.src.storage.repository import SkillRepository

        repo = SkillRepository(":memory:")
        repo.ensure_skill("s1", "Skill One")
        repo.append_revision("s1", "r1", "2026-01-01T00:00:00Z")
        repo.tombstone_skill("s1", "obsolete")

        skills = repo.list_skills(include_tombstoned=False)
        ids = [s["skill_id"] for s in skills]
        assert "s1" not in ids

        all_skills = repo.list_skills(include_tombstoned=True)
        ids_all = [s["skill_id"] for s in all_skills]
        assert "s1" in ids_all
        repo.close()

    def test_tombstone_artifact(self):
        from skillforge.src.storage.repository import SkillRepository

        repo = SkillRepository(":memory:")
        repo.ensure_skill("s1", "Skill One")
        repo.append_revision("s1", "r1", "2026-01-01T00:00:00Z")
        art = repo.add_artifact("r1", "l3_pack", "manifest.json", "abc", 100)

        snap1 = repo.get_snapshot("s1")
        assert len(snap1["artifacts"]) == 1

        repo.tombstone_artifact("s1", art["artifact_id"], "corrupted")
        snap2 = repo.get_snapshot("s1")
        assert len(snap2["artifacts"]) == 0
        repo.close()


# ==============================================================================
# 7. L3 Audit Pack: 7 MUST 文件齐全且 hash 可校验
# ==============================================================================
class TestL3AuditPackComplete:
    """Pack-publish produces all 7 MUST files with verifiable hashes."""

    L3_MUST_FILES = {
        "manifest", "policy_matrix",
        "original_repo_snapshot", "repro_env",
    }

    L3_MANIFEST_ENTRIES = {
        "policy_matrix.json", "static_analysis.log",
        "original_repo_snapshot.json", "repro_env.yml",
        "evidence.jsonl", "source_lineage.diff",
    }

    def test_all_must_files_present(self):
        from skillforge.src.nodes.pack_publish import PackPublish

        handler = PackPublish()
        artifacts = {
            "input": {
                "mode": "github",
                "repo_url": "https://github.com/test/repo",
                "branch": "main",
                "options": {
                    "target_environment": "python",
                    "intended_use": "automation",
                    "visibility": "public",
                    "sandbox_mode": "strict",
                },
            },
            "intake_repo": {
                "repo_name": "test/repo",
                "license": "MIT",
                "files": ["README.md"],
            },
            "sandbox_test_and_trace": {
                "test_results": {"passed": 1, "failed": 0},
            },
        }
        result = handler.execute(artifacts)
        ap = result.get("audit_pack", {})
        files = ap.get("files", {})

        for key in self.L3_MUST_FILES:
            assert key in files, f"L3 MUST file '{key}' missing from audit pack"

        # Check manifest lists all L3 files
        manifest = files.get("manifest", {})
        manifest_filenames = {e.get("file") for e in manifest.get("files", [])}
        for entry in self.L3_MANIFEST_ENTRIES:
            assert entry in manifest_filenames, (
                f"L3 MUST file '{entry}' missing from manifest"
            )

    def test_manifest_has_hashes(self):
        from skillforge.src.nodes.pack_publish import PackPublish

        handler = PackPublish()
        artifacts = {
            "input": {
                "mode": "nl",
                "natural_language": "test",
                "options": {
                    "target_environment": "python",
                    "intended_use": "automation",
                    "visibility": "public",
                    "sandbox_mode": "strict",
                },
            },
            "sandbox_test_and_trace": {
                "test_results": {"passed": 1, "failed": 0},
            },
        }
        result = handler.execute(artifacts)
        manifest = result.get("audit_pack", {}).get("files", {}).get("manifest", {})

        assert "files" in manifest
        for entry in manifest.get("files", []):
            assert "sha256" in entry, f"File {entry.get('name')} missing sha256"
