"""
GatePublishSkill — Gate evaluator for pack_audit_and_publish.

Gate Group: delivery (Squad C)
Position: G7 (final gate, after sandbox_test_and_trace G6)

L3 AuditPack must include 'content_hash' of all prior artifacts.

Implements the experience_capture.py pattern:
- validate_input(input_data) -> list[str]
- execute(input_data) -> dict
- validate_output(output) -> list[str]

Contract: skillforge/src/contracts/gates/publish.yaml
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..experience_capture import FixKind, capture_gate_event

TOOL_REVISION = "0.1.0"
GATE_NAME = "pack_audit_and_publish"
CONTRACT_PATH = Path(__file__).parent.parent.parent / "contracts" / "gates" / "publish.yaml"

# L3 MUST files that must be present in audit pack
L3_MUST_FILES: frozenset[str] = frozenset({
    "manifest.json",
    "policy_matrix.json",
    "static_analysis.log",
    "original_repo_snapshot.json",
    "repro_env.yml",
    "evidence.jsonl",
})


def _sha256(data: str | bytes) -> str:
    """Compute SHA-256 hex digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class GatePublishSkill:
    """
    Gate evaluator for pack_audit_and_publish (L3 AuditPack).

    L3 AuditPack must include 'content_hash' of all prior artifacts.
    This is the final gate in the delivery pipeline.
    """

    node_id: str = "pack_audit_and_publish"
    stage: int = 7
    gate_name: str = GATE_NAME
    tool_revision: str = TOOL_REVISION

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate publish input against contract requirements."""
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # PUBLISH-001: pack_audit_and_publish output must be present
        pack_publish = input_data.get("pack_audit_and_publish")
        if not isinstance(pack_publish, dict):
            errors.append("PUBLISH-001: pack_audit_and_publish output is required")
            return errors

        # PUBLISH-002: audit_pack must be present and valid
        audit_pack = pack_publish.get("audit_pack")
        if not isinstance(audit_pack, dict):
            errors.append("PUBLISH-002: audit_pack is required")
            return errors

        # Validate audit pack required fields
        required_audit_fields = ["audit_id", "skill_id", "version", "quality_level"]
        for field in required_audit_fields:
            if field not in audit_pack:
                errors.append(f"SCHEMA_INVALID: audit_pack.{field} is required")

        # PUBLISH-003: quality_level must be L3
        quality_level = audit_pack.get("quality_level")
        if quality_level and quality_level != "L3":
            errors.append(f"PUBLISH-003: Expected quality_level L3, got '{quality_level}'")

        # PUBLISH-005: manifest must be present in audit_pack.files
        files = audit_pack.get("files")
        if isinstance(files, dict):
            if "manifest" not in files:
                errors.append("PUBLISH-005: manifest missing from audit_pack.files")
        elif files is not None:
            errors.append("SCHEMA_INVALID: audit_pack.files must be an object")

        # Check sandbox gate prerequisite
        sandbox_gate = input_data.get("sandbox_test_and_trace")
        if isinstance(sandbox_gate, dict):
            gate_decision = sandbox_gate.get("gate_decision")
            if gate_decision == "REJECTED":
                errors.append("PREREQUISITE_FAILED: sandbox_test_and_trace gate was REJECTED")
            # Also check success flag
            success = sandbox_gate.get("success")
            if success is False:
                errors.append("PREREQUISITE_FAILED: sandbox_test_and_trace success=false")

        # Check publish_result
        publish_result = pack_publish.get("publish_result")
        if isinstance(publish_result, dict):
            status = publish_result.get("status")
            if status and status not in ("published", "rejected"):
                errors.append(f"SCHEMA_INVALID: publish_result.status must be 'published' or 'rejected'")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute publish gate evaluation.

        L3 AuditPack must include 'content_hash' of all prior artifacts.
        Validates input first and returns REJECTED if validation fails.
        """
        # Validate input first (fail-closed)
        validation_errors = self.validate_input(input_data)
        if validation_errors:
            result = {
                "gate_name": self.gate_name,
                "gate_decision": "REJECTED",
                "error_code": "VALIDATION_FAILED",
                "evidence_refs": [],
                "next_action": "halt",
                "validation_errors": validation_errors,
            }
            capture_gate_event(
                gate_node=self.gate_name,
                gate_decision=result["gate_decision"],
                evidence_refs=result["evidence_refs"],
                error_code=result["error_code"],
                fix_kind=FixKind.GATE_DECISION,
                summary="publish gate rejected due to input validation failure",
            )
            return result

        timestamp = _now_iso()
        pack_publish = input_data.get("pack_audit_and_publish", {})
        audit_pack = pack_publish.get("audit_pack", {})
        evidence_refs: list[dict[str, str]] = []
        content_hashes: dict[str, str] = {}

        # Check sandbox gate
        sandbox_gate = input_data.get("sandbox_test_and_trace")
        if isinstance(sandbox_gate, dict):
            gate_decision = sandbox_gate.get("gate_decision")
            if gate_decision == "REJECTED":
                return self._build_rejected(
                    error_code="ERR_SANDBOX_REJECTED",
                    reason="Sandbox gate was rejected, cannot publish",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )
            success = sandbox_gate.get("success")
            if success is False:
                return self._build_rejected(
                    error_code="ERR_SANDBOX_FAILED",
                    reason="Sandbox tests failed, cannot publish",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )

        # PUBLISH-004: Check publish status
        publish_result = pack_publish.get("publish_result", {})
        status = publish_result.get("status")
        if status == "rejected":
            return self._build_rejected(
                error_code="ERR_PUBLISH_REJECTED",
                reason="Publish result status is 'rejected'",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # Compute and chain content_hash for all prior artifacts (G1-G6)
        prior_artifacts = [
            ("intake_repo", "G1"),
            ("license_gate", "G2"),
            ("repo_scan_fit_score", "G3"),
            ("constitution_risk_gate", "G4"),
            ("scaffold_skill_impl", "G5"),
            ("sandbox_test_and_trace", "G6"),
        ]

        for artifact_name, gate_id in prior_artifacts:
            artifact = input_data.get(artifact_name)
            if isinstance(artifact, dict):
                artifact_hash = _sha256(json.dumps(artifact, default=str, sort_keys=True))
                content_hashes[artifact_name] = artifact_hash

                evidence_refs.append({
                    "issue_key": f"ARTIFACT-{gate_id}",
                    "source_locator": f"artifact://{artifact_name}",
                    "content_hash": artifact_hash,
                    "tool_revision": self.tool_revision,
                    "timestamp": timestamp,
                })

                # Chain evidence_refs from prior gates
                if "evidence_refs" in artifact:
                    for ref in artifact.get("evidence_refs", []):
                        if isinstance(ref, dict):
                            evidence_refs.append({
                                "issue_key": ref.get("issue_key", f"CHAIN-{gate_id}-{uuid.uuid4().hex[:8]}"),
                                "source_locator": ref.get("source_locator", artifact_name),
                                "content_hash": ref.get("content_hash", ""),
                                "tool_revision": ref.get("tool_revision", "unknown"),
                                "timestamp": ref.get("timestamp", timestamp),
                            })

        # Create aggregate content hash for L3 AuditPack
        aggregate_hash = _sha256(json.dumps(content_hashes, sort_keys=True))
        evidence_refs.append({
            "issue_key": "L3_CONTENT_HASH_AGGREGATE",
            "source_locator": "file:///audit/manifest.json/provenance",
            "content_hash": aggregate_hash,
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
        })

        # Create evidence for audit pack
        audit_pack_hash = _sha256(json.dumps(audit_pack, default=str, sort_keys=True))
        evidence_refs.append({
            "issue_key": f"AUDIT-PACK-{audit_pack.get('audit_id', 'unknown')}",
            "source_locator": f"file:///audit/{audit_pack.get('audit_id', 'unknown')}/manifest.json",
            "content_hash": audit_pack_hash,
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
        })

        result = {
            "gate_name": self.gate_name,
            "gate_decision": "PASSED",
            "error_code": None,
            "evidence_refs": evidence_refs,
            "next_action": "continue",
            "content_hashes": content_hashes,
        }
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            fix_kind=FixKind.PUBLISH_PACK,
            summary="L3 audit pack publish gate passed with aggregate content hash",
            metadata={"artifact_count": len(content_hashes)},
        )
        return result

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate output against GateResult schema."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        required_fields = ["gate_name", "gate_decision", "evidence_refs", "next_action"]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        decision = output_data.get("gate_decision")
        if decision not in ("PASSED", "REJECTED"):
            errors.append(f"SCHEMA_INVALID: gate_decision must be 'PASSED' or 'REJECTED'")

        next_action = output_data.get("next_action")
        if next_action not in ("continue", "halt"):
            errors.append(f"SCHEMA_INVALID: next_action must be 'continue' or 'halt'")

        evidence_refs = output_data.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append("SCHEMA_INVALID: evidence_refs must be an array")

        return errors

    def _build_rejected(
        self,
        error_code: str,
        reason: str,
        evidence_refs: list[dict[str, str]],
        timestamp: str,
    ) -> dict[str, Any]:
        """Build a REJECTED GateResult with next_action=halt."""
        result = {
            "gate_name": self.gate_name,
            "gate_decision": "REJECTED",
            "error_code": error_code,
            "evidence_refs": evidence_refs,
            "next_action": "halt",
            "reason": reason,
        }
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            error_code=result["error_code"],
            fix_kind=FixKind.GATE_DECISION,
            summary=reason,
        )
        return result


def main():
    """CLI entry point for GatePublishSkill."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="GatePublishSkill - Publish gate evaluator (L3 AuditPack)")
    parser.add_argument("--input-file", help="Input JSON file with gate request")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    gate = GatePublishSkill()

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        print("Error: --input-file is required", file=sys.stderr)
        sys.exit(1)

    validation_errors = gate.validate_input(input_data)
    if validation_errors:
        error_result = {
            "gate_name": gate.gate_name,
            "gate_decision": "REJECTED",
            "error_code": "VALIDATION_FAILED",
            "evidence_refs": [],
            "next_action": "halt",
            "validation_errors": validation_errors,
        }
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=2)
        else:
            print(json.dumps(error_result, indent=2))
        sys.exit(1)

    output = gate.execute(input_data)

    output_errors = gate.validate_output(output)
    if output_errors:
        print(f"WARNING: Output validation errors: {output_errors}", file=sys.stderr)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if output["gate_decision"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
