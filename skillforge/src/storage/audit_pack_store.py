"""
AuditPack Store - AuditPack 存储读取接口

提供 run_id/evidence_ref 索引读取能力，支持一致性校验。

Contract: T8 (L45-D2-ORCH-MINCAP-20260220-002)
Schema: n8n_execution_receipt.schema.json
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ============================================================================
# Constants
# ============================================================================

DEFAULT_STORAGE_PATH = Path(__file__).parent.parent.parent.parent / "data" / "audit_packs"

# Error codes
ERROR_CODES = {
    "STORE_NOT_FOUND": "AuditPack storage path not found",
    "PACK_NOT_FOUND": "AuditPack not found for given identifier",
    "CONSISTENCY_ERROR": "run_id and evidence_ref point to different packs",
    "INVALID_IDENTIFIER": "Invalid identifier format",
    "READ_ERROR": "Error reading AuditPack from storage",
    "CORRUPT_PACK": "AuditPack content is corrupted or invalid",
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ReplayPointer:
    """Replay pointer for at-time replay capability."""
    snapshot_ref: Optional[str] = None
    at_time: Optional[str] = None
    revision: Optional[str] = None
    evidence_bundle_ref: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary with all fields present (nullable allowed)."""
        return {
            "snapshot_ref": self.snapshot_ref,
            "at_time": self.at_time,
            "revision": self.revision,
            "evidence_bundle_ref": self.evidence_bundle_ref,
        }


@dataclass
class EvidenceRef:
    """Evidence reference in an AuditPack."""
    ref_id: str
    type: str
    source_locator: str
    content_hash: str
    timestamp: str
    tool_revision: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "ref_id": self.ref_id,
            "type": self.type,
            "source_locator": self.source_locator,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
        }
        if self.tool_revision:
            result["tool_revision"] = self.tool_revision
        return result


@dataclass
class AuditPack:
    """AuditPack representing a complete execution audit record."""
    pack_id: str
    run_id: str
    evidence_ref: str
    gate_decision: str
    executed_at: str
    skill_id: str
    workflow_id: str
    job_id: Optional[str] = None
    permit_token: Optional[str] = None
    audit_pack_ref: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    replay_pointer: Optional[ReplayPointer] = None
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    output: Optional[dict] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary matching n8n_execution_receipt schema."""
        result = {
            "receipt_id": self.pack_id,
            "run_id": self.run_id,
            "evidence_ref": self.evidence_ref,
            "gate_decision": self.gate_decision,
            "executed_at": self.executed_at,
            "skill_id": self.skill_id,
            "workflow_id": self.workflow_id,
            "replay_pointer": self.replay_pointer.to_dict() if self.replay_pointer else None,
        }

        # Optional fields
        if self.job_id:
            result["job_id"] = self.job_id
        if self.permit_token:
            result["permit_token"] = self.permit_token
        if self.audit_pack_ref:
            result["audit_pack_ref"] = self.audit_pack_ref
        if self.error_code:
            result["error_code"] = self.error_code
        if self.error_message:
            result["error_message"] = self.error_message
        if self.evidence_refs:
            result["evidence_chain"] = {
                "evidence_refs": [e.to_dict() for e in self.evidence_refs]
            }
        if self.output:
            result["output"] = self.output
        if self.metadata:
            result["metadata"] = self.metadata

        return result


@dataclass
class FetchResult:
    """Result of fetching an AuditPack."""
    success: bool
    pack: Optional[AuditPack] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    evidence_ref: Optional[str] = None
    run_id: Optional[str] = None

    @classmethod
    def ok(cls, pack: AuditPack) -> "FetchResult":
        """Create a successful result."""
        return cls(
            success=True,
            pack=pack,
            evidence_ref=pack.evidence_ref,
            run_id=pack.run_id,
        )

    @classmethod
    def error(
        cls,
        error_code: str,
        error_message: str,
        evidence_ref: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> "FetchResult":
        """Create an error result."""
        return cls(
            success=False,
            error_code=error_code,
            error_message=error_message,
            evidence_ref=evidence_ref,
            run_id=run_id,
        )


# ============================================================================
# AuditPackStore
# ============================================================================

class AuditPackStore:
    """
    AuditPack 存储读取接口。

    提供 run_id/evidence_ref 索引读取能力，支持一致性校验。

    Constraints:
    - run_id 与 evidence_ref 任一给定时必须能做一致性校验
    - 读取失败必须 fail-closed 并返回结构化错误信封
    - 返回体必须包含 replay_pointer（可空但字段存在）
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize the store with optional custom storage path."""
        self.storage_path = storage_path or DEFAULT_STORAGE_PATH
        self._index: dict[str, str] = {}  # run_id/evidence_ref -> pack_file
        self._packs: dict[str, AuditPack] = {}  # pack_id -> AuditPack
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure the store is initialized with default packs if empty."""
        if self._initialized:
            return

        # Create storage directory if not exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load existing packs from storage
        self._load_existing_packs()

        # If no packs exist, only create sample packs for testing if in dev/test env
        env = os.getenv("SKILLFORGE_ENV")
        env_val = env.lower() if env else "prod"
        if env_val in ("dev", "test") and len(self._packs) == 0:
            self._create_sample_packs()

        self._initialized = True

    def _load_existing_packs(self) -> None:
        """Load existing packs from storage."""
        if not self.storage_path.exists():
            return

        for pack_file in self.storage_path.glob("*.json"):
            try:
                with open(pack_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pack = self._dict_to_pack(data)
                self._packs[pack.pack_id] = pack
                self._index[pack.run_id] = pack.pack_id
                self._index[pack.evidence_ref] = pack.pack_id
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip corrupted files
                continue

    def _create_sample_packs(self) -> None:
        """Create sample packs for testing."""
        import time
        import uuid

        ts = int(time.time())

        # Sample successful pack
        pack1 = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-A1B2C3D4",
            evidence_ref=f"EV-EXEC-L4-{ts}-A1B2C3D4",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="l45_n8n_orchestration_boundary",
            workflow_id="wf_001",
            job_id="L45-D2-ORCH-MINCAP-20260220-002",
            permit_token="PERMIT-L4-1739980000-XYZ123",
            audit_pack_ref=f"audit://packs/L45-D2-{ts}",
            replay_pointer=ReplayPointer(
                snapshot_ref=f"snapshot://L45-D2-{ts}/v1",
                at_time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                revision="v1.0.0",
                evidence_bundle_ref=f"evidence://bundles/L45-D2-{ts}",
            ),
            evidence_refs=[
                EvidenceRef(
                    ref_id=f"EV-COG-L4-{ts}-A1B2C3D4",
                    type="cognition",
                    source_locator=f"cognition://dims/{ts}-A1B2C3D4",
                    content_hash="sha256:abc123def456",
                    timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    tool_revision="v1.0.0",
                ),
            ],
            output={
                "status": "success",
                "data": {"dimensions": 10, "processed": True},
            },
        )

        self._save_pack(pack1)

    def _save_pack(self, pack: AuditPack) -> None:
        """Save a pack to storage."""
        pack_file = self.storage_path / f"{pack.pack_id}.json"
        with open(pack_file, "w", encoding="utf-8") as f:
            json.dump(pack.to_dict(), f, indent=2)

        self._packs[pack.pack_id] = pack
        self._index[pack.run_id] = pack.pack_id
        self._index[pack.evidence_ref] = pack.pack_id

    def _dict_to_pack(self, data: dict) -> AuditPack:
        """Convert dictionary to AuditPack."""
        replay_pointer = None
        if data.get("replay_pointer"):
            rp = data["replay_pointer"]
            replay_pointer = ReplayPointer(
                snapshot_ref=rp.get("snapshot_ref"),
                at_time=rp.get("at_time"),
                revision=rp.get("revision"),
                evidence_bundle_ref=rp.get("evidence_bundle_ref"),
            )

        evidence_refs = []
        if data.get("evidence_chain", {}).get("evidence_refs"):
            for e in data["evidence_chain"]["evidence_refs"]:
                evidence_refs.append(EvidenceRef(
                    ref_id=e["ref_id"],
                    type=e["type"],
                    source_locator=e["source_locator"],
                    content_hash=e["content_hash"],
                    timestamp=e["timestamp"],
                    tool_revision=e.get("tool_revision"),
                ))

        return AuditPack(
            pack_id=data["receipt_id"],
            run_id=data["run_id"],
            evidence_ref=data["evidence_ref"],
            gate_decision=data["gate_decision"],
            executed_at=data["executed_at"],
            skill_id=data["skill_id"],
            workflow_id=data["workflow_id"],
            job_id=data.get("job_id"),
            permit_token=data.get("permit_token"),
            audit_pack_ref=data.get("audit_pack_ref"),
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
            replay_pointer=replay_pointer,
            evidence_refs=evidence_refs,
            output=data.get("output"),
            metadata=data.get("metadata"),
        )

    def fetch_by_run_id(self, run_id: str) -> FetchResult:
        """
        Fetch an AuditPack by run_id.

        Args:
            run_id: The run ID to look up

        Returns:
            FetchResult with pack on success or error details on failure
        """
        self._ensure_initialized()

        if not run_id:
            return FetchResult.error(
                error_code="INVALID_IDENTIFIER",
                error_message="run_id cannot be empty",
            )

        pack_id = self._index.get(run_id)
        if not pack_id:
            return FetchResult.error(
                error_code="PACK_NOT_FOUND",
                error_message=f"No AuditPack found for run_id: {run_id}",
                run_id=run_id,
            )

        pack = self._packs.get(pack_id)
        if not pack:
            return FetchResult.error(
                error_code="CORRUPT_PACK",
                error_message=f"AuditPack index corrupt for run_id: {run_id}",
                run_id=run_id,
            )

        return FetchResult.ok(pack)

    def fetch_by_evidence_ref(self, evidence_ref: str) -> FetchResult:
        """
        Fetch an AuditPack by evidence_ref.

        Args:
            evidence_ref: The evidence reference to look up

        Returns:
            FetchResult with pack on success or error details on failure
        """
        self._ensure_initialized()

        if not evidence_ref:
            return FetchResult.error(
                error_code="INVALID_IDENTIFIER",
                error_message="evidence_ref cannot be empty",
            )

        pack_id = self._index.get(evidence_ref)
        if not pack_id:
            return FetchResult.error(
                error_code="PACK_NOT_FOUND",
                error_message=f"No AuditPack found for evidence_ref: {evidence_ref}",
                evidence_ref=evidence_ref,
            )

        pack = self._packs.get(pack_id)
        if not pack:
            return FetchResult.error(
                error_code="CORRUPT_PACK",
                error_message=f"AuditPack index corrupt for evidence_ref: {evidence_ref}",
                evidence_ref=evidence_ref,
            )

        return FetchResult.ok(pack)

    def fetch_with_consistency_check(
        self,
        run_id: Optional[str] = None,
        evidence_ref: Optional[str] = None,
    ) -> FetchResult:
        """
        Fetch an AuditPack with consistency check.

        When both run_id and evidence_ref are provided, verifies they point to
        the same AuditPack.

        Args:
            run_id: Optional run ID to look up
            evidence_ref: Optional evidence reference to look up

        Returns:
            FetchResult with pack on success or error details on failure
        """
        self._ensure_initialized()

        # At least one identifier must be provided
        if not run_id and not evidence_ref:
            return FetchResult.error(
                error_code="INVALID_IDENTIFIER",
                error_message="Either run_id or evidence_ref must be provided",
            )

        # Only run_id provided
        if run_id and not evidence_ref:
            return self.fetch_by_run_id(run_id)

        # Only evidence_ref provided
        if evidence_ref and not run_id:
            return self.fetch_by_evidence_ref(evidence_ref)

        # Both provided - consistency check
        result_by_run = self.fetch_by_run_id(run_id)
        result_by_ref = self.fetch_by_evidence_ref(evidence_ref)

        # If either lookup failed, return the error
        if not result_by_run.success:
            return result_by_run
        if not result_by_ref.success:
            return result_by_ref

        # Consistency check: both must point to the same pack
        if result_by_run.pack.pack_id != result_by_ref.pack.pack_id:
            return FetchResult.error(
                error_code="CONSISTENCY_ERROR",
                error_message=(
                    f"Consistency check failed: run_id {run_id} points to pack "
                    f"{result_by_run.pack.pack_id}, but evidence_ref {evidence_ref} "
                    f"points to pack {result_by_ref.pack.pack_id}"
                ),
                run_id=run_id,
                evidence_ref=evidence_ref,
            )

        return result_by_run

    def store_pack(self, pack: AuditPack) -> bool:
        """
        Store an AuditPack (append-only).

        Args:
            pack: The AuditPack to store

        Returns:
            True if stored successfully
        """
        self._ensure_initialized()
        self._save_pack(pack)
        return True

    def list_packs(self, limit: int = 100) -> list[AuditPack]:
        """
        List all stored AuditPacks.

        Args:
            limit: Maximum number of packs to return

        Returns:
            List of AuditPacks
        """
        self._ensure_initialized()
        return list(self._packs.values())[:limit]


# ============================================================================
# Singleton instance
# ============================================================================

_store_instance: Optional[AuditPackStore] = None


def get_audit_pack_store() -> AuditPackStore:
    """Get the singleton AuditPackStore instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = AuditPackStore()
    return _store_instance
