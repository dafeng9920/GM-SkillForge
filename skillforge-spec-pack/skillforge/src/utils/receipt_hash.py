"""
Receipt Hash Implementation for GM-SkillForge

This module provides deterministic receipt hash generation for audit packs
following the L6 authenticity protocol.

Task: T08 - ISSUE-07: 审计回执哈希修正
Executor: vs--cc3

Purpose:
- Remove Python built-in hash() (unstable across runs)
- Use SHA-256(canonical payload) for deterministic receipt hashing
- Ensure consistent hash values across different environments

Receipt Hash = SHA-256(canonical_json(receipt_payload))
"""

import hashlib
from typing import Any, Optional
from dataclasses import dataclass, field, asdict

from skillforge.src.utils.canonical_json import canonical_json, canonical_json_hash


@dataclass
class EvidenceRef:
    """
    Reference to an evidence package for audit verification.

    Fields:
    - envelope_id: Unique identifier of the evidence envelope
    - envelope_hash: SHA-256 hash of the canonical envelope
    - storage_location: URI/Path where the envelope is stored
    - received_at: ISO-8601 timestamp when evidence was received
    - verified: Boolean indicating if signature was verified
    """
    envelope_id: str
    envelope_hash: str
    storage_location: str
    received_at: str
    verified: bool = False
    evidence_type: str = "evidence_envelope.v1"
    node_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ReceiptPayload:
    """
    Payload for receipt hash computation.

    This is the canonical structure that gets hashed to create
    the receipt hash. It contains all essential audit information
    in a deterministic format.

    Fields:
    - audit_id: Unique identifier for this audit
    - job_id: Job identifier
    - created_at: ISO-8601 timestamp
    - node_id: Node that performed the audit
    - decision: Audit gate decision (PASSED/FAILED/REJECTED)
    - evidence_refs: List of evidence references
    - manifest_hash: Hash of the skill manifest
    - signature_present: Whether the receipt is signed
    """
    audit_id: str
    job_id: str
    created_at: str
    node_id: str
    decision: str
    evidence_refs: list[EvidenceRef]
    manifest_hash: Optional[str] = None
    signature_present: bool = False
    trace_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for canonicalization."""
        return {
            "audit_id": self.audit_id,
            "job_id": self.job_id,
            "created_at": self.created_at,
            "node_id": self.node_id,
            "decision": self.decision,
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
            "manifest_hash": self.manifest_hash,
            "signature_present": self.signature_present,
            "trace_id": self.trace_id,
        }


def compute_receipt_hash(payload: ReceiptPayload) -> str:
    """
    Compute SHA-256 hash of canonical receipt payload.

    This function ensures deterministic receipt hashing across
    different runs and environments by using canonical JSON
    serialization before SHA-256 hashing.

    Args:
        payload: ReceiptPayload to hash

    Returns:
        Hexadecimal SHA-256 hash string

    Example:
        >>> payload = ReceiptPayload(
        ...     audit_id="audit-001",
        ...     job_id="job-001",
        ...     created_at="2026-02-26T12:00:00Z",
        ...     node_id="node-001",
        ...     decision="PASSED",
        ...     evidence_refs=[]
        ... )
        >>> receipt_hash = compute_receipt_hash(payload)
        >>> assert len(receipt_hash) == 64  # SHA-256 = 64 hex chars
    """
    return canonical_json_hash(payload.to_dict())


def compute_receipt_hash_from_dict(payload_dict: dict[str, Any]) -> str:
    """
    Compute receipt hash directly from a dictionary.

    Convenience function for computing hash when you already
    have a dictionary representation of the receipt payload.

    Args:
        payload_dict: Dictionary containing receipt payload data

    Returns:
        Hexadecimal SHA-256 hash string
    """
    return canonical_json_hash(payload_dict)


def verify_receipt_consistency(
    payload: ReceiptPayload,
    iterations: int = 100
) -> dict[str, Any]:
    """
    Verify that receipt hash is consistent across multiple runs.

    This is critical for audit integrity - the same receipt must
    always produce the same hash.

    Args:
        payload: ReceiptPayload to test
        iterations: Number of times to compute hash

    Returns:
        Dictionary with verification results:
        - consistent: True if all hashes are identical
        - iterations: Number of iterations performed
        - unique_hashes: Number of unique hash values found
        - hash: The consistent hash value (if consistent=True)
    """
    hashes = set()

    for _ in range(iterations):
        h = compute_receipt_hash(payload)
        hashes.add(h)

    return {
        "consistent": len(hashes) == 1,
        "iterations": iterations,
        "unique_hashes": len(hashes),
        "hash": list(hashes)[0] if len(hashes) == 1 else None,
    }


def create_evidence_ref(
    envelope_id: str,
    envelope_hash: str,
    storage_location: str,
    received_at: str,
    verified: bool = False,
    node_id: Optional[str] = None,
) -> EvidenceRef:
    """
    Create an EvidenceRef for receipt payload.

    Args:
        envelope_id: Unique identifier of the evidence envelope
        envelope_hash: SHA-256 hash of the canonical envelope
        storage_location: URI/Path where envelope is stored
        received_at: ISO-8601 timestamp
        verified: Whether signature was verified
        node_id: Optional node identifier

    Returns:
        EvidenceRef instance
    """
    return EvidenceRef(
        envelope_id=envelope_id,
        envelope_hash=envelope_hash,
        storage_location=storage_location,
        received_at=received_at,
        verified=verified,
        node_id=node_id,
    )


def create_receipt_payload(
    audit_id: str,
    job_id: str,
    created_at: str,
    node_id: str,
    decision: str,
    evidence_refs: list[EvidenceRef],
    manifest_hash: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> ReceiptPayload:
    """
    Create a ReceiptPayload for hashing.

    Args:
        audit_id: Unique audit identifier
        job_id: Job identifier
        created_at: ISO-8601 timestamp
        node_id: Node that performed the audit
        decision: Gate decision (PASSED/FAILED/REJECTED)
        evidence_refs: List of evidence references
        manifest_hash: Optional manifest hash
        trace_id: Optional trace ID

    Returns:
        ReceiptPayload instance
    """
    return ReceiptPayload(
        audit_id=audit_id,
        job_id=job_id,
        created_at=created_at,
        node_id=node_id,
        decision=decision,
        evidence_refs=evidence_refs,
        manifest_hash=manifest_hash,
        trace_id=trace_id,
    )


# Convenience exports
__all__ = [
    "EvidenceRef",
    "ReceiptPayload",
    "compute_receipt_hash",
    "compute_receipt_hash_from_dict",
    "verify_receipt_consistency",
    "create_evidence_ref",
    "create_receipt_payload",
]
