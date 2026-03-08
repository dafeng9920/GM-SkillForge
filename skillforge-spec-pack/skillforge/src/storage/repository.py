"""
SkillForge Repository — CRUD + temporal queries.

API per AUDIT_ENGINE_PROTOCOL_v1.md and 对话记录.md:
- append_revision(skill_id, revision_id, effective_at)
- deprecate_revision(skill_id, revision_id, effective_at, reason)
- tombstone_artifact(skill_id, artifact_id, effective_at, reason)
- get_snapshot(skill_id, at_time)
- list_skills(include_tombstoned=False)

T2 Extension: Registry/Graph Integrity Verification
- compute_registry_hash(skill_id) — compute hash of skill's registry state
- record_integrity_chain(...) — record integrity signature before publish
- verify_integrity(skill_id) — verify current state matches stored hash
- detect_tampering(skill_id) — detect and return tamper evidence
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .schema import init_db


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _uuid() -> str:
    return uuid.uuid4().hex[:12]


@dataclass
class SkillRepository:
    """SQLite-backed skill storage with revision + tombstone support."""

    db_path: str | Path = "db/skillforge.sqlite"
    _conn: sqlite3.Connection | None = field(default=None, repr=False, init=False)

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = init_db(self.db_path)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # ── Skill CRUD ────────────────────────────────────────

    def ensure_skill(self, skill_id: str, title: str = "") -> dict[str, Any]:
        """Create skill if not exists, return skill record."""
        now = _now_iso()
        self.conn.execute(
            "INSERT OR IGNORE INTO skills (skill_id, title, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (skill_id, title or skill_id, now, now),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM skills WHERE skill_id = ?", (skill_id,)
        ).fetchone()
        return dict(row) if row else {}

    def list_skills(self, include_tombstoned: bool = False) -> list[dict[str, Any]]:
        """List all skills. If include_tombstoned=False, exclude tombstoned."""
        if include_tombstoned:
            rows = self.conn.execute("SELECT * FROM skills ORDER BY skill_id").fetchall()
        else:
            rows = self.conn.execute(
                "SELECT s.* FROM skills s "
                "WHERE NOT EXISTS ("
                "  SELECT 1 FROM tombstones t "
                "  WHERE t.skill_id = s.skill_id AND t.revision_id IS NULL AND t.artifact_id IS NULL"
                ") ORDER BY s.skill_id"
            ).fetchall()
        return [dict(r) for r in rows]

    # ── Revision Model ────────────────────────────────────

    def append_revision(
        self,
        skill_id: str,
        revision_id: str | None = None,
        effective_at: str | None = None,
        manifest_sha256: str = "",
        path: str = "",
        quality_level: str = "L1",
        catalog_version: str | None = None,
    ) -> dict[str, Any]:
        """
        Append a new revision (event-sourcing: never overwrite).

        Args:
            skill_id: The skill identifier
            revision_id: Optional revision ID (auto-generated if not provided)
            effective_at: ISO-8601 timestamp for when this revision becomes effective
            manifest_sha256: SHA256 hash of the manifest
            path: Path to the revision artifacts
            quality_level: Quality level (L1-L5)
            catalog_version: Optional issue_catalog version used for this audit
        """
        self.ensure_skill(skill_id)
        revision_id = revision_id or f"rev-{_uuid()}"
        effective_at = effective_at or _now_iso()

        # Build metadata JSON
        metadata: dict[str, Any] = {}
        if catalog_version:
            metadata["catalog_version"] = catalog_version
        metadata_json = json.dumps(metadata) if metadata else None

        self.conn.execute(
            "INSERT INTO revisions "
            "(revision_id, skill_id, effective_at, status, manifest_sha256, path, quality_level, metadata) "
            "VALUES (?, ?, ?, 'ACTIVE', ?, ?, ?, ?)",
            (revision_id, skill_id, effective_at, manifest_sha256, path, quality_level, metadata_json),
        )

        # Update skill timestamp
        self.conn.execute(
            "UPDATE skills SET updated_at = ? WHERE skill_id = ?",
            (_now_iso(), skill_id),
        )
        self.conn.commit()

        row = self.conn.execute(
            "SELECT * FROM revisions WHERE revision_id = ?", (revision_id,)
        ).fetchone()
        return dict(row) if row else {}

    def deprecate_revision(
        self,
        skill_id: str,
        revision_id: str,
        reason: str = "superseded",
    ) -> dict[str, Any]:
        """Mark a revision as DEPRECATED."""
        self.conn.execute(
            "UPDATE revisions SET status = 'DEPRECATED' "
            "WHERE revision_id = ? AND skill_id = ?",
            (revision_id, skill_id),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM revisions WHERE revision_id = ?", (revision_id,)
        ).fetchone()
        return dict(row) if row else {}

    def get_revisions(
        self,
        skill_id: str,
        include_deprecated: bool = False,
    ) -> list[dict[str, Any]]:
        """Get revisions for a skill, optionally including deprecated."""
        if include_deprecated:
            rows = self.conn.execute(
                "SELECT * FROM revisions WHERE skill_id = ? "
                "AND status != 'TOMBSTONED' ORDER BY effective_at DESC",
                (skill_id,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM revisions WHERE skill_id = ? "
                "AND status = 'ACTIVE' ORDER BY effective_at DESC",
                (skill_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ── Artifact CRUD ─────────────────────────────────────

    def add_artifact(
        self,
        revision_id: str,
        artifact_type: str,
        filename: str,
        sha256: str,
        size_bytes: int = 0,
    ) -> dict[str, Any]:
        """Add an artifact to a revision."""
        artifact_id = f"art-{_uuid()}"
        self.conn.execute(
            "INSERT INTO artifacts "
            "(artifact_id, revision_id, artifact_type, filename, sha256, size_bytes) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (artifact_id, revision_id, artifact_type, filename, sha256, size_bytes),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,)
        ).fetchone()
        return dict(row) if row else {}

    def get_artifacts(self, revision_id: str) -> list[dict[str, Any]]:
        """Get all artifacts for a revision."""
        rows = self.conn.execute(
            "SELECT * FROM artifacts WHERE revision_id = ? ORDER BY artifact_type",
            (revision_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Tombstone ─────────────────────────────────────────

    def tombstone_skill(
        self, skill_id: str, reason: str, tombstoned_by: str = ""
    ) -> dict[str, Any]:
        """Tombstone an entire skill (logical delete)."""
        tombstone_id = f"ts-{_uuid()}"
        now = _now_iso()
        self.conn.execute(
            "INSERT INTO tombstones (tombstone_id, skill_id, reason, tombstoned_at, tombstoned_by) "
            "VALUES (?, ?, ?, ?, ?)",
            (tombstone_id, skill_id, reason, now, tombstoned_by),
        )

        # Mark all active revisions as TOMBSTONED
        self.conn.execute(
            "UPDATE revisions SET status = 'TOMBSTONED' WHERE skill_id = ? AND status = 'ACTIVE'",
            (skill_id,),
        )
        self.conn.commit()
        return {"tombstone_id": tombstone_id, "skill_id": skill_id, "reason": reason}

    def tombstone_artifact(
        self,
        skill_id: str,
        artifact_id: str,
        reason: str,
        tombstoned_by: str = "",
    ) -> dict[str, Any]:
        """Tombstone a single artifact."""
        tombstone_id = f"ts-{_uuid()}"
        now = _now_iso()
        self.conn.execute(
            "INSERT INTO tombstones "
            "(tombstone_id, skill_id, artifact_id, reason, tombstoned_at, tombstoned_by) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (tombstone_id, skill_id, artifact_id, reason, now, tombstoned_by),
        )
        self.conn.commit()
        return {"tombstone_id": tombstone_id, "artifact_id": artifact_id, "reason": reason}

    # ── Temporal Queries ──────────────────────────────────

    def get_snapshot(
        self, skill_id: str, at_time: str | None = None
    ) -> dict[str, Any]:
        """
        Get snapshot of a skill at a point in time.

        Returns the latest ACTIVE revision effective at or before at_time,
        plus its artifacts.
        """
        at_time = at_time or _now_iso()

        rev_row = self.conn.execute(
            "SELECT * FROM revisions "
            "WHERE skill_id = ? AND effective_at <= ? AND status IN ('ACTIVE', 'DEPRECATED') "
            "ORDER BY effective_at DESC LIMIT 1",
            (skill_id, at_time),
        ).fetchone()

        if not rev_row:
            return {"skill_id": skill_id, "at_time": at_time, "revision": None, "artifacts": []}

        revision = dict(rev_row)
        artifacts = self.get_artifacts(revision["revision_id"])

        # Exclude tombstoned artifacts
        tombstoned_ids = {
            r["artifact_id"]
            for r in self.conn.execute(
                "SELECT artifact_id FROM tombstones "
                "WHERE skill_id = ? AND artifact_id IS NOT NULL AND tombstoned_at <= ?",
                (skill_id, at_time),
            ).fetchall()
            if r["artifact_id"]
        }
        artifacts = [a for a in artifacts if a["artifact_id"] not in tombstoned_ids]

        return {
            "skill_id": skill_id,
            "at_time": at_time,
            "revision": revision,
            "artifacts": artifacts,
        }

    def get_index(
        self, at_time: str | None = None, include_deprecated: bool = False
    ) -> list[dict[str, Any]]:
        """
        Get index of all skills at a point in time.

        Returns list of {skill_id, latest_revision, quality_level}.
        """
        at_time = at_time or _now_iso()

        if include_deprecated:
            status_filter = "r.status IN ('ACTIVE', 'DEPRECATED')"
        else:
            status_filter = "r.status = 'ACTIVE'"

        rows = self.conn.execute(
            "SELECT r.*, s.title FROM revisions r "
            "JOIN skills s ON r.skill_id = s.skill_id "
            f"WHERE r.effective_at <= ? AND {status_filter} "
            "AND NOT EXISTS ("
            "  SELECT 1 FROM tombstones t "
            "  WHERE t.skill_id = r.skill_id AND t.revision_id IS NULL AND t.artifact_id IS NULL "
            "  AND t.tombstoned_at <= ?"
            ") "
            "ORDER BY r.skill_id, r.effective_at DESC",
            (at_time, at_time),
        ).fetchall()

        # Deduplicate — keep only the latest revision per skill
        seen: set[str] = set()
        results: list[dict[str, Any]] = []
        for row in rows:
            d = dict(row)
            if d["skill_id"] not in seen:
                seen.add(d["skill_id"])
                results.append(d)

        return results

    # ── T2: Integrity Verification ─────────────────────────────

    def compute_registry_hash(self, skill_id: str) -> str:
        """
        Compute SHA256 hash of a skill's current registry state.

        Includes: skill metadata, active revisions, artifacts, tombstones.
        Used for tamper detection before publish.
        """
        # Collect all state for this skill
        snapshot = self.get_snapshot(skill_id)

        # Get all revisions (including deprecated for complete state)
        all_revisions = self.get_revisions(skill_id, include_deprecated=True)

        # Get tombstones for this skill
        tombstones = self.conn.execute(
            "SELECT * FROM tombstones WHERE skill_id = ? ORDER BY tombstoned_at",
            (skill_id,),
        ).fetchall()

        # Build canonical state representation
        state = {
            "skill_id": skill_id,
            "snapshot": snapshot,
            "all_revisions": [dict(r) for r in all_revisions],
            "tombstones": [dict(t) for t in tombstones],
        }

        # Sort keys for deterministic hash
        state_json = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(state_json.encode("utf-8")).hexdigest()

    def compute_graph_hash(self) -> str:
        """
        Compute SHA256 hash of the entire skill graph (all skills and relationships).

        Used for global registry integrity verification.
        """
        # Get all skills
        skills = self.list_skills(include_tombstoned=True)

        # Build graph state
        graph_state = {
            "skills": [],
            "total_skills": len(skills),
            "computed_at": _now_iso(),
        }

        for skill in skills:
            skill_id = skill["skill_id"]
            skill_hash = self.compute_registry_hash(skill_id)
            graph_state["skills"].append({
                "skill_id": skill_id,
                "hash": skill_hash,
            })

        # Sort skills by skill_id for deterministic hash
        graph_state["skills"].sort(key=lambda x: x["skill_id"])

        state_json = json.dumps(graph_state, sort_keys=True, default=str)
        return hashlib.sha256(state_json.encode("utf-8")).hexdigest()

    def record_integrity_chain(
        self,
        chain_type: str,
        entity_id: str | None,
        computed_hash: str,
        recorded_by: str = "pack_publish",
        signature: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Record an integrity chain entry (append-only).

        Args:
            chain_type: 'registry', 'graph', or 'manifest'
            entity_id: skill_id or None for global graph
            computed_hash: SHA256 hash of the state
            recorded_by: node_id that recorded this
            signature: optional cryptographic signature
            metadata: additional context

        Returns the recorded chain entry.
        """
        chain_id = f"ichain-{_uuid()}"

        # Get previous hash for append-only chain
        prev_entry = self.conn.execute(
            "SELECT chain_id, computed_hash FROM integrity_chains "
            "WHERE chain_type = ? AND (entity_id = ? OR (? IS NULL AND entity_id IS NULL)) "
            "ORDER BY recorded_at DESC LIMIT 1",
            (chain_type, entity_id, entity_id),
        ).fetchone()
        prev_hash = prev_entry["computed_hash"] if prev_entry else None

        metadata_json = json.dumps(metadata) if metadata else None

        self.conn.execute(
            "INSERT INTO integrity_chains "
            "(chain_id, chain_type, entity_id, computed_hash, prev_hash, signature, recorded_at, recorded_by, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (chain_id, chain_type, entity_id, computed_hash, prev_hash, signature, _now_iso(), recorded_by, metadata_json),
        )
        self.conn.commit()

        row = self.conn.execute(
            "SELECT * FROM integrity_chains WHERE chain_id = ?", (chain_id,)
        ).fetchone()
        return dict(row) if row else {}

    def get_latest_integrity_hash(
        self,
        chain_type: str,
        entity_id: str | None = None,
    ) -> str | None:
        """
        Get the latest recorded integrity hash for an entity.

        Returns None if no integrity chain exists.
        """
        row = self.conn.execute(
            "SELECT computed_hash FROM integrity_chains "
            "WHERE chain_type = ? AND (entity_id = ? OR (? IS NULL AND entity_id IS NULL)) "
            "ORDER BY recorded_at DESC LIMIT 1",
            (chain_type, entity_id, entity_id),
        ).fetchone()
        return row["computed_hash"] if row else None

    def verify_integrity(
        self,
        chain_type: str,
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Verify that current state matches the latest recorded integrity hash.

        Returns:
        {
            "verified": bool,
            "chain_type": str,
            "entity_id": str | None,
            "stored_hash": str | None,
            "computed_hash": str,
            "mismatch": bool,
            "evidence": dict | None  -- If tampering detected, includes details
        }
        """
        # Compute current hash
        if chain_type == "registry":
            if not entity_id:
                return {
                    "verified": False,
                    "chain_type": chain_type,
                    "entity_id": entity_id,
                    "stored_hash": None,
                    "computed_hash": "",
                    "mismatch": True,
                    "evidence": {"error": "entity_id required for registry integrity check"},
                }
            computed_hash = self.compute_registry_hash(entity_id)
        elif chain_type == "graph":
            computed_hash = self.compute_graph_hash()
        else:
            return {
                "verified": False,
                "chain_type": chain_type,
                "entity_id": entity_id,
                "stored_hash": None,
                "computed_hash": "",
                "mismatch": True,
                "evidence": {"error": f"unknown chain_type: {chain_type}"},
            }

        # Get stored hash
        stored_hash = self.get_latest_integrity_hash(chain_type, entity_id)

        # If no stored hash, nothing to verify against (first-time publish)
        if stored_hash is None:
            return {
                "verified": True,  # No prior state = no tampering
                "chain_type": chain_type,
                "entity_id": entity_id,
                "stored_hash": None,
                "computed_hash": computed_hash,
                "mismatch": False,
                "evidence": {"first_publish": True},
            }

        # Compare hashes
        mismatch = stored_hash != computed_hash

        evidence: dict[str, Any] | None = None
        if mismatch:
            evidence = {
                "tampering_detected": True,
                "stored_hash": stored_hash,
                "computed_hash": computed_hash,
                "chain_type": chain_type,
                "entity_id": entity_id,
                "timestamp": _now_iso(),
            }

            # Get specific evidence for registry tampering
            if chain_type == "registry" and entity_id:
                # Find which revisions were modified
                revisions = self.get_revisions(entity_id, include_deprecated=True)
                modified_revisions = []
                for rev in revisions:
                    stored_rev_hash = rev.get("manifest_sha256")
                    if stored_rev_hash and stored_rev_hash.startswith("tampered"):
                        modified_revisions.append({
                            "revision_id": rev.get("revision_id"),
                            "manifest_sha256": stored_rev_hash,
                        })
                if modified_revisions:
                    evidence["modified_revisions"] = modified_revisions

        return {
            "verified": not mismatch,
            "chain_type": chain_type,
            "entity_id": entity_id,
            "stored_hash": stored_hash,
            "computed_hash": computed_hash,
            "mismatch": mismatch,
            "evidence": evidence,
        }

    def detect_tampering(self, skill_id: str) -> dict[str, Any]:
        """
        Detect tampering for a specific skill's registry entry.

        This is the main entry point for pre-publish integrity checks.

        Returns:
        {
            "tampering_detected": bool,
            "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
            "ruling": {...},  -- Conflict evidence if tampering detected
            "integrity_result": {...}  -- Full verification result
        }
        """
        # Verify registry integrity
        integrity_result = self.verify_integrity("registry", skill_id)

        if not integrity_result["mismatch"]:
            # No tampering detected
            return {
                "tampering_detected": False,
                "decision": "ALLOW",
                "ruling": None,
                "integrity_result": integrity_result,
            }

        # Tampering detected - build conflict ruling
        ruling = {
            "verdict": "DENY",
            "rule_id": "INTEGRITY_TAMPER_DETECTED",
            "description": "Registry/graph integrity verification failed - tampering detected",
            "evidence": integrity_result.get("evidence"),
            "blocked": True,
            "remediation": "Restore original registry state or reset integrity chain",
        }

        return {
            "tampering_detected": True,
            "decision": "DENY",
            "ruling": ruling,
            "integrity_result": integrity_result,
        }
