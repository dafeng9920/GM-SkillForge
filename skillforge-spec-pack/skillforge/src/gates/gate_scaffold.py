"""
GateScaffold — Gate evaluator for scaffold_skill_impl.

Gate Group: delivery (Squad C)
Position: G5 (after constitution_risk_gate G4)

Evaluates scaffold output and chains evidence from prior gates:
- G1: intake_repo
- G2: license_gate
- G3: repo_scan_fit_score
- G4: constitution_risk_gate

Output: GateResult conforming to gate_interface_v1.yaml
{
    "gate_name": "scaffold_skill_impl",
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
from dataclasses import dataclass, field
from typing import Any


TOOL_REVISION = "0.1.0"
GATE_NAME = "scaffold_skill_impl"


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
class GateScaffold:
    """
    Gate evaluator for scaffold_skill_impl.

    Validates scaffold output and chains evidence from G1-G4.
    Produces GateResult with evidence_refs for downstream gates.
    """

    gate_name: str = GATE_NAME
    tool_revision: str = TOOL_REVISION

    def evaluate(self, artifacts: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate scaffold output and produce GateResult.

        Args:
            artifacts: Pipeline artifacts including:
                - scaffold_skill_impl: Scaffold output with files_generated
                - constitution_risk_gate: G4 gate decision (must be PASSED)
                - Prior gate evidence refs for chaining

        Returns:
            GateResult dict conforming to gate_interface_v1.yaml
        """
        timestamp = _now_iso()
        evidence_refs: list[EvidenceRef] = []

        # ── Validate scaffold output exists ──
        scaffold = artifacts.get("scaffold_skill_impl")
        if not isinstance(scaffold, dict):
            return self._build_rejected(
                error_code="ERR_SCAFFOLD_MISSING",
                reason="scaffold_skill_impl output is missing or invalid",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Check constitution gate passed (G4 prerequisite) ──
        constitution_gate = artifacts.get("constitution_risk_gate")
        if isinstance(constitution_gate, dict):
            decision = constitution_gate.get("decision")
            if decision not in ("ALLOW", "PASSED", None):
                return self._build_rejected(
                    error_code="ERR_CONSTITUTION_DENIED",
                    reason=f"Constitution gate denied with decision: {decision}",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )
            # Chain evidence from constitution gate
            if "evidence_refs" in constitution_gate:
                for ref in constitution_gate.get("evidence_refs", []):
                    if isinstance(ref, dict):
                        evidence_refs.append(EvidenceRef(
                            issue_key=ref.get("issue_key", f"CHAIN-G4-{uuid.uuid4().hex[:8]}"),
                            source_locator=ref.get("source_locator", "constitution_risk_gate"),
                            content_hash=ref.get("content_hash", ""),
                            tool_revision=ref.get("tool_revision", "unknown"),
                            timestamp=ref.get("timestamp", timestamp),
                        ))

        # ── Validate scaffold content ──
        files_generated = scaffold.get("files_generated", [])
        if not files_generated:
            return self._build_rejected(
                error_code="ERR_NO_FILES_GENERATED",
                reason="Scaffold produced no files",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        manifest = scaffold.get("manifest", {})
        if not manifest:
            return self._build_rejected(
                error_code="ERR_MANIFEST_MISSING",
                reason="Scaffold manifest is missing",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # Validate manifest fields
        required_manifest_fields = ["skill_id", "version", "checksum"]
        for field_name in required_manifest_fields:
            if field_name not in manifest:
                return self._build_rejected(
                    error_code="ERR_MANIFEST_INCOMPLETE",
                    reason=f"Scaffold manifest missing required field: {field_name}",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )

        # ── Chain evidence from G1-G3 (if available) ──
        self._chain_prior_evidence(artifacts, evidence_refs, timestamp)

        # ── Create evidence for scaffold output ──
        scaffold_content_hash = _sha256(json.dumps(scaffold, default=str, sort_keys=True))
        evidence_refs.append(EvidenceRef(
            issue_key=f"SCAFFOLD-{manifest.get('skill_id', 'unknown')}",
            source_locator=f"file:///scaffold/{manifest.get('skill_id', 'unknown')}/manifest.json",
            content_hash=scaffold_content_hash,
            tool_revision=self.tool_revision,
            timestamp=timestamp,
        ))

        # ── Build PASSED result ──
        return GateResult(
            gate_name=self.gate_name,
            gate_decision="PASSED",
            error_code=None,
            evidence_refs=evidence_refs,
            next_action="continue",
        ).to_dict()

    def _chain_prior_evidence(
        self,
        artifacts: dict[str, Any],
        evidence_refs: list[EvidenceRef],
        timestamp: str,
    ) -> None:
        """Chain evidence from prior gates G1-G3."""
        prior_gates = [
            ("intake_repo", "G1"),
            ("license_gate", "G2"),
            ("repo_scan_fit_score", "G3"),
        ]

        for gate_name, gate_id in prior_gates:
            gate_output = artifacts.get(gate_name)
            if isinstance(gate_output, dict) and "evidence_refs" in gate_output:
                for ref in gate_output.get("evidence_refs", []):
                    if isinstance(ref, dict):
                        evidence_refs.append(EvidenceRef(
                            issue_key=ref.get("issue_key", f"CHAIN-{gate_id}-{uuid.uuid4().hex[:8]}"),
                            source_locator=ref.get("source_locator", gate_name),
                            content_hash=ref.get("content_hash", ""),
                            tool_revision=ref.get("tool_revision", "unknown"),
                            timestamp=ref.get("timestamp", timestamp),
                        ))

    def _build_rejected(
        self,
        error_code: str,
        reason: str,
        evidence_refs: list[EvidenceRef],
        timestamp: str,
    ) -> dict[str, Any]:
        """Build a REJECTED GateResult."""
        return GateResult(
            gate_name=self.gate_name,
            gate_decision="REJECTED",
            error_code=error_code,
            evidence_refs=evidence_refs,
            next_action="halt",
        ).to_dict()
