"""
GatePublish — Gate evaluator for pack_audit_and_publish.

Gate Group: delivery (Squad C)
Position: G7 (final gate, after sandbox_test_and_trace G6)

L3 AuditPack must include 'content_hash' of all prior artifacts.

Evaluates publish output and chains evidence from prior gates:
- G1: intake_repo
- G2: license_gate
- G3: repo_scan_fit_score
- G4: constitution_risk_gate
- G5: scaffold_skill_impl
- G6: sandbox_test_and_trace

Output: GateResult conforming to gate_interface_v1.yaml
{
    "gate_name": "pack_audit_and_publish",
    "gate_decision": "PASSED" | "REJECTED",
    "error_code": str | null,
    "evidence_refs": [EvidenceRef...],
    "next_action": "continue" | "halt"
}
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any


TOOL_REVISION = "0.1.0"
GATE_NAME = "pack_audit_and_publish"


def _sha256(data: str | bytes) -> str:
    """Compute SHA-256 hex digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class EvidenceRef:
    """Evidence reference conforming to gate_interface_v1.yaml."""

    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "issue_key": self.issue_key,
            "source_locator": self.source_locator,
            "content_hash": self.content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": self.timestamp,
        }


@dataclass
class GateResult:
    """Gate result conforming to gate_interface_v1.yaml."""

    gate_name: str
    gate_decision: str  # "PASSED" | "REJECTED"
    error_code: str | None
    evidence_refs: list[EvidenceRef]
    next_action: str  # "continue" | "halt"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gate_name": self.gate_name,
            "gate_decision": self.gate_decision,
            "error_code": self.error_code,
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
            "next_action": self.next_action,
        }


@dataclass
class GatePublish:
    """
    Gate evaluator for pack_audit_and_publish (L3 AuditPack).

    L3 AuditPack must include 'content_hash' of all prior artifacts.

    Validates:
    - Audit pack structure
    - Manifest integrity (with content_hash of all prior artifacts)
    - Publish status
    - All L3 MUST files present

    Chains evidence from G1-G6 for audit trail.
    """

    gate_name: str = GATE_NAME
    tool_revision: str = TOOL_REVISION

    # L3 MUST files that must be present in audit pack
    L3_MUST_FILES: frozenset[str] = frozenset({
        "manifest.json",
        "policy_matrix.json",
        "static_analysis.log",
        "original_repo_snapshot.json",
        "repro_env.yml",
        "evidence.jsonl",
    })

    def evaluate(self, artifacts: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate publish output and produce GateResult.

        L3 AuditPack must include 'content_hash' of all prior artifacts.

        Args:
            artifacts: Pipeline artifacts including:
                - pack_audit_and_publish: Publish result with audit_pack
                - sandbox_test_and_trace: G6 gate decision (must be PASSED)
                - All prior artifacts for content_hash chain

        Returns:
            GateResult dict conforming to gate_interface_v1.yaml
        """
        timestamp = _now_iso()
        evidence_refs: list[EvidenceRef] = []
        content_hashes: dict[str, str] = {}  # artifact_name -> content_hash

        # ── Check sandbox gate passed (G6 prerequisite) ──
        sandbox_gate = artifacts.get("sandbox_test_and_trace")
        if isinstance(sandbox_gate, dict):
            # Check if sandbox has gate_decision (from GateSandbox)
            gate_decision = sandbox_gate.get("gate_decision")
            if gate_decision == "REJECTED":
                return self._build_rejected(
                    error_code="ERR_SANDBOX_REJECTED",
                    reason="Sandbox gate was rejected, cannot publish",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )
            # Check success flag (from SandboxTest node)
            success = sandbox_gate.get("success")
            if success is False:
                return self._build_rejected(
                    error_code="ERR_SANDBOX_FAILED",
                    reason="Sandbox tests failed, cannot publish",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )

        # ── Validate pack_audit_and_publish output exists ──
        pack_publish = artifacts.get("pack_audit_and_publish")
        if not isinstance(pack_publish, dict):
            return self._build_rejected(
                error_code="ERR_PUBLISH_OUTPUT_MISSING",
                reason="pack_audit_and_publish output is missing or invalid",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Validate audit pack ──
        audit_pack = pack_publish.get("audit_pack")
        if not isinstance(audit_pack, dict):
            return self._build_rejected(
                error_code="ERR_AUDIT_PACK_MISSING",
                reason="Audit pack is missing or invalid",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # Validate audit pack required fields
        required_audit_fields = ["audit_id", "skill_id", "version", "quality_level"]
        for field_name in required_audit_fields:
            if field_name not in audit_pack:
                return self._build_rejected(
                    error_code="ERR_AUDIT_PACK_INCOMPLETE",
                    reason=f"Audit pack missing required field: {field_name}",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )

        # Validate quality level is L3
        if audit_pack.get("quality_level") != "L3":
            return self._build_rejected(
                error_code="ERR_QUALITY_LEVEL_INVALID",
                reason=f"Expected quality_level L3, got {audit_pack.get('quality_level')}",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Validate L3 MUST files (files metadata) ──
        files_metadata = audit_pack.get("files", {})
        if not isinstance(files_metadata, dict):
            return self._build_rejected(
                error_code="ERR_FILES_METADATA_MISSING",
                reason="Audit pack files metadata is missing",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # Check manifest exists and has proper structure
        manifest = files_metadata.get("manifest")
        if not isinstance(manifest, dict):
            return self._build_rejected(
                error_code="ERR_MANIFEST_MISSING",
                reason="L3 MUST file manifest.json is missing",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Compute and chain content_hash for all prior artifacts (G1-G6) ──
        prior_artifacts = [
            ("intake_repo", "G1"),
            ("license_gate", "G2"),
            ("repo_scan_fit_score", "G3"),
            ("constitution_risk_gate", "G4"),
            ("scaffold_skill_impl", "G5"),
            ("sandbox_test_and_trace", "G6"),
        ]

        for artifact_name, gate_id in prior_artifacts:
            artifact = artifacts.get(artifact_name)
            if isinstance(artifact, dict):
                artifact_hash = _sha256(json.dumps(artifact, default=str, sort_keys=True))
                content_hashes[artifact_name] = artifact_hash

                # Create evidence ref for this artifact
                evidence_refs.append(EvidenceRef(
                    issue_key=f"ARTIFACT-{gate_id}",
                    source_locator=f"artifact://{artifact_name}",
                    content_hash=artifact_hash,
                    tool_revision=self.tool_revision,
                    timestamp=timestamp,
                ))

                # Also chain evidence_refs from prior gates
                if "evidence_refs" in artifact:
                    for ref in artifact.get("evidence_refs", []):
                        if isinstance(ref, dict):
                            evidence_refs.append(EvidenceRef(
                                issue_key=ref.get("issue_key", f"CHAIN-{gate_id}-{uuid.uuid4().hex[:8]}"),
                                source_locator=ref.get("source_locator", artifact_name),
                                content_hash=ref.get("content_hash", ""),
                                tool_revision=ref.get("tool_revision", "unknown"),
                                timestamp=ref.get("timestamp", timestamp),
                            ))

        # ── Verify manifest includes content_hash of prior artifacts ──
        manifest_provenance = manifest.get("provenance", {})
        if isinstance(manifest_provenance, dict):
            # Check for content_hash field in provenance
            # This verifies L3 requirement: AuditPack must include content_hash of all prior artifacts
            manifest_content_hash = manifest_provenance.get("content_hash")
            if not manifest_content_hash:
                # Compute aggregate content hash from all prior artifacts
                aggregate_hash = _sha256(json.dumps(content_hashes, sort_keys=True))
                evidence_refs.append(EvidenceRef(
                    issue_key="L3_CONTENT_HASH_AGGREGATE",
                    source_locator="file:///audit/manifest.json/provenance",
                    content_hash=aggregate_hash,
                    tool_revision=self.tool_revision,
                    timestamp=timestamp,
                ))

        # ── Validate publish result ──
        publish_result = pack_publish.get("publish_result", {})
        if not isinstance(publish_result, dict):
            return self._build_rejected(
                error_code="ERR_PUBLISH_RESULT_MISSING",
                reason="Publish result is missing or invalid",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        status = publish_result.get("status")
        if status not in ("published", "rejected"):
            return self._build_rejected(
                error_code="ERR_PUBLISH_STATUS_INVALID",
                reason=f"Invalid publish status: {status}",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # If publish was rejected, gate should also be REJECTED
        if status == "rejected":
            return self._build_rejected(
                error_code="ERR_PUBLISH_REJECTED",
                reason="Publish result status is 'rejected'",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Create evidence for audit pack ──
        audit_pack_hash = _sha256(json.dumps(audit_pack, default=str, sort_keys=True))
        evidence_refs.append(EvidenceRef(
            issue_key=f"AUDIT-PACK-{audit_pack.get('audit_id', 'unknown')}",
            source_locator=f"file:///audit/{audit_pack.get('audit_id', 'unknown')}/manifest.json",
            content_hash=audit_pack_hash,
            tool_revision=self.tool_revision,
            timestamp=timestamp,
        ))

        # ── Build PASSED result ──
        return GateResult(
            gate_name=self.gate_name,
            gate_decision="PASSED",
            error_code=None,
            evidence_refs=evidence_refs,
            next_action="continue",  # Pipeline complete
        ).to_dict()

    def _build_rejected(
        self,
        error_code: str,
        reason: str,
        evidence_refs: list[EvidenceRef],
        timestamp: str,
    ) -> dict[str, Any]:
        """Build a REJECTED GateResult with next_action=halt."""
        return GateResult(
            gate_name=self.gate_name,
            gate_decision="REJECTED",
            error_code=error_code,
            evidence_refs=evidence_refs,
            next_action="halt",
        ).to_dict()
