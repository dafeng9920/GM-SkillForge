#!/usr/bin/env python3
"""
Pack and Permit - L3 AuditPack Assembly and Permit Issuance Entry Point (v0)

Unified facade for assembling L3 AuditPack and issuing Permit.
This is the designated single entry point for:
- L3 AuditPack assembly (manifest/decisions/policy_matrix/checksums)
- Permit issuance (binding three hashes + audit_pack_hash + revision)
- Delivery completeness validation

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
Implementation components:
- skillforge/src/skills/gates/permit_issuer.py
- skillforge/src/skills/gates/gate_permit.py
- scripts/validate_permit_binding.py
- scripts/validate_delivery_completeness.py
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Add paths for imports
_skillforge_path = Path(__file__).parent.parent / "skillforge"
_scripts_path = Path(__file__).parent.parent / "scripts"

if str(_skillforge_path) not in sys.path:
    sys.path.insert(0, str(_skillforge_path))
if str(_scripts_path) not in sys.path:
    sys.path.insert(0, str(_scripts_path))


class PermitStatus(str, Enum):
    """Permit issuance status."""
    ISSUED = "ISSUED"
    DENIED = "DENIED"
    REQUIRES_CHANGES = "REQUIRES_CHANGES"


@dataclass
class AuditPack:
    """L3 AuditPack - complete execution audit record."""
    pack_id: str
    schema_version: str
    manifest: dict[str, Any]
    gate_decisions: list[dict[str, Any]]
    policy_matrix: dict[str, Any]
    checksums: dict[str, str]
    created_at: str
    revision: str | None = None
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pack_id": self.pack_id,
            "schema_version": self.schema_version,
            "manifest": self.manifest,
            "gate_decisions": self.gate_decisions,
            "policy_matrix": self.policy_matrix,
            "checksums": self.checksums,
            "created_at": self.created_at,
            "revision": self.revision,
            "evidence_refs": self.evidence_refs,
        }

    def calculate_pack_hash(self) -> str:
        """Calculate the audit pack hash."""
        pack_dict = self.to_dict()
        canonical = json.dumps(pack_dict, sort_keys=True, ensure_ascii=False)
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class Permit:
    """Permit - authorization for skill publication."""
    permit_id: str
    schema_version: str
    skill_id: str
    revision: str
    status: PermitStatus
    demand_hash: str
    contract_hash: str
    decision_hash: str
    audit_pack_hash: str
    issued_at: str
    expires_at: str | None = None
    issuer: str = "gm-skillforge-v0"
    restrictions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "permit_id": self.permit_id,
            "schema_version": self.schema_version,
            "skill_id": self.skill_id,
            "revision": self.revision,
            "status": self.status.value,
            "demand_hash": self.demand_hash,
            "contract_hash": self.contract_hash,
            "decision_hash": self.decision_hash,
            "audit_pack_hash": self.audit_pack_hash,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "issuer": self.issuer,
            "restrictions": self.restrictions,
        }


@dataclass
class PackAndPermitResult:
    """Result of pack assembly and permit issuance."""
    success: bool
    audit_pack: AuditPack | None = None
    permit: Permit | None = None
    error_code: str | None = None
    error_message: str | None = None
    validation_results: dict[str, Any] = field(default_factory=dict)


class PackAndPermitAssembler:
    """
    Unified facade for L3 AuditPack assembly and Permit issuance.

    This is the designated single entry point for:
    - Assembling L3 AuditPack from gate decisions
    - Issuing Permit with three-hash binding
    - Validating delivery completeness
    """

    SCHEMA_VERSION = "pack_and_permit_v0"
    _logger = logging.getLogger(__name__)  # FIX-006: module-level logger

    # Required delivery items per PR2
    REQUIRED_DELIVERY_ITEMS = [
        "Blueprint",  # contracts/dsl/*.yml
        "Skill",      # skills/*/
        "n8n",        # workflows/*/
        "Evidence",   # artifacts/*/
        "AuditPack",  # audit_pack/*.json
        "Permit",     # permits/*/*.json
    ]

    def __init__(self, validate_delivery: bool = True):
        """
        Initialize the assembler.

        Args:
            validate_delivery: If True, validate delivery completeness before issuance
        """
        self.validate_delivery = validate_delivery

    def assemble_pack_and_issue_permit(
        self,
        skill_id: str,
        manifest: dict[str, Any],
        gate_decisions: list[dict[str, Any]],
        three_hashes: dict[str, str],
        revision: str | None = None,
        base_path: Path | None = None
    ) -> PackAndPermitResult:
        """
        Assemble L3 AuditPack and issue Permit.

        Args:
            skill_id: Skill identifier
            manifest: Skill manifest
            gate_decisions: List of gate decisions from 8 Gate execution
            three_hashes: Dict with demand_hash, contract_hash, decision_hash
            revision: Optional revision identifier
            base_path: Base path for delivery validation

        Returns:
            PackAndPermitResult with audit pack and permit, or error details
        """
        validation_results = {}

        # 1) Validate three hashes are present
        hash_validation = self._validate_three_hashes(three_hashes)
        validation_results["three_hash_binding"] = hash_validation
        if not hash_validation["valid"]:
            return PackAndPermitResult(
                success=False,
                error_code="SF_THREE_HASH_INCOMPLETE",
                error_message="Permit requires all three hashes (demand/contract/decision)",
                validation_results=validation_results,
            )

        # 2) Validate delivery completeness if enabled
        if self.validate_delivery:
            delivery_validation = self._validate_delivery_completeness(base_path or Path.cwd())
            validation_results["delivery_completeness"] = delivery_validation
            if not delivery_validation["valid"]:
                return PackAndPermitResult(
                    success=False,
                    error_code="SF_DELIVERY_INCOMPLETE",
                    error_message="Delivery completeness check failed",
                    validation_results=validation_results,
                )

        # 3) Check gate decisions for BLOCKER issues
        final_decision = self._get_final_gate_decision(gate_decisions)
        validation_results["gate_decision"] = final_decision

        if final_decision["status"] == "DENY":
            return PackAndPermitResult(
                success=False,
                error_code="SF_GATE_DENIED",
                error_message="Gate decisions contain DENY status",
                audit_pack=self._build_audit_pack(
                    skill_id, manifest, gate_decisions, three_hashes, revision
                ),
                validation_results=validation_results,
            )

        # 4) Determine permit status
        permit_status = PermitStatus.ISSUED
        if final_decision["status"] == "REQUIRES_CHANGES":
            permit_status = PermitStatus.REQUIRES_CHANGES

        # 5) Assemble AuditPack
        audit_pack = self._build_audit_pack(
            skill_id, manifest, gate_decisions, three_hashes, revision
        )

        # 6) Issue Permit
        permit = self._issue_permit(
            skill_id=skill_id,
            revision=revision or audit_pack.pack_id,
            three_hashes=three_hashes,
            audit_pack_hash=audit_pack.calculate_pack_hash(),
            status=permit_status,
        )

        return PackAndPermitResult(
            success=permit_status == PermitStatus.ISSUED,
            audit_pack=audit_pack,
            permit=permit,
            validation_results=validation_results,
        )

    def _validate_three_hashes(self, hashes: dict[str, str]) -> dict[str, Any]:
        """Validate three hashes are present and valid."""
        required = ["demand_hash", "contract_hash", "decision_hash"]
        missing = [h for h in required if h not in hashes or not hashes[h]]

        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "present": [h for h in required if h in hashes and hashes[h]],
        }

    def _validate_delivery_completeness(self, base_path: Path) -> dict[str, Any]:
        """Validate delivery completeness using the validation script."""
        try:
            # Import and run the delivery completeness validator
            from validate_delivery_completeness import validate_delivery_completeness

            result = validate_delivery_completeness(base_path)
            return {
                "valid": result["status"] == "PASS",
                "error_code": result.get("error_code"),
                "missing_items": result.get("missing_items", []),
                "present_items": result.get("present_items", []),
            }
        except Exception as e:
            # FIX-006: Log crash with full traceback so ops can diagnose.
            # Behavior stays fail-closed (valid=False), but now it's observable.
            self._logger.error(
                "delivery_validation_module_crashed",
                extra={"base_path": str(base_path), "error": str(e)},
                exc_info=True,
            )
            return {
                "valid": False,
                "error": f"Delivery validation module crashed: {e}",
            }

    def _get_final_gate_decision(self, gate_decisions: list[dict[str, Any]]) -> dict[str, Any]:
        """Determine final gate decision status."""
        if not gate_decisions:
            return {"status": "ALLOW"}

        # Check for DENY
        for decision in gate_decisions:
            if decision.get("decision") == "DENY":
                return {"status": "DENY", "gate": decision.get("gate_name")}

        # Check for REQUIRES_CHANGES
        for decision in gate_decisions:
            if decision.get("decision") == "REQUIRES_CHANGES":
                return {"status": "REQUIRES_CHANGES", "gate": decision.get("gate_name")}

        return {"status": "ALLOW"}

    def _build_audit_pack(
        self,
        skill_id: str,
        manifest: dict[str, Any],
        gate_decisions: list[dict[str, Any]],
        three_hashes: dict[str, str],
        revision: str | None
    ) -> AuditPack:
        """Build L3 AuditPack."""
        now = datetime.now(UTC).isoformat()

        # Calculate checksums
        manifest_json = json.dumps(manifest, sort_keys=True)
        decisions_json = json.dumps(gate_decisions, sort_keys=True)

        checksums = {
            "manifest_hash": "sha256:" + hashlib.sha256(manifest_json.encode()).hexdigest(),
            "decisions_hash": "sha256:" + hashlib.sha256(decisions_json.encode()).hexdigest(),
            "demand_hash": three_hashes.get("demand_hash", ""),
            "contract_hash": three_hashes.get("contract_hash", ""),
            "decision_hash": three_hashes.get("decision_hash", ""),
        }

        # Build policy matrix from gate decisions
        policy_matrix = self._build_policy_matrix(gate_decisions)

        return AuditPack(
            pack_id=f"AP-{skill_id}-{uuid.uuid4().hex[:8].upper()}",
            schema_version=self.SCHEMA_VERSION,
            manifest=manifest,
            gate_decisions=gate_decisions,
            policy_matrix=policy_matrix,
            checksums=checksums,
            created_at=now,
            revision=revision,
        )

    def _build_policy_matrix(self, gate_decisions: list[dict[str, Any]]) -> dict[str, Any]:
        """Build policy matrix from gate decisions."""
        return {
            "gates_evaluated": len(gate_decisions),
            "gates_passed": sum(1 for d in gate_decisions if d.get("decision") == "ALLOW"),
            "gates_denied": sum(1 for d in gate_decisions if d.get("decision") == "DENY"),
            "gates_requires_changes": sum(1 for d in gate_decisions if d.get("decision") == "REQUIRES_CHANGES"),
            "final_decision": self._get_final_gate_decision(gate_decisions)["status"],
        }

    def _issue_permit(
        self,
        skill_id: str,
        revision: str,
        three_hashes: dict[str, str],
        audit_pack_hash: str,
        status: PermitStatus
    ) -> Permit:
        """Issue a Permit."""
        now = datetime.now(UTC).isoformat()

        return Permit(
            permit_id=f"PERMIT-{skill_id}-{uuid.uuid4().hex[:8].upper()}",
            schema_version=self.SCHEMA_VERSION,
            skill_id=skill_id,
            revision=revision,
            status=status,
            demand_hash=three_hashes["demand_hash"],
            contract_hash=three_hashes["contract_hash"],
            decision_hash=three_hashes["decision_hash"],
            audit_pack_hash=audit_pack_hash,
            issued_at=now,
        )


def main() -> int:
    """CLI entry point for pack and permit operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Assemble L3 AuditPack and issue Permit (v0)")
    parser.add_argument("--skill-id", required=True, help="Skill identifier")
    parser.add_argument("--manifest", type=Path, required=True, help="Skill manifest JSON")
    parser.add_argument("--decisions", type=Path, required=True, help="Gate decisions JSON")
    parser.add_argument("--hashes", type=Path, required=True, help="Three hashes JSON")
    parser.add_argument("--revision", help="Revision identifier")
    parser.add_argument("--output-dir", type=Path, default=Path("permits"), help="Output directory")
    parser.add_argument("--skip-delivery-check", action="store_true", help="Skip delivery completeness check")
    args = parser.parse_args()

    # Load inputs
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        gate_decisions = json.loads(args.decisions.read_text(encoding="utf-8"))
        three_hashes = json.loads(args.hashes.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load inputs: {e}", file=sys.stderr)
        return 1

    # Extract gate_decisions array if wrapped
    if isinstance(gate_decisions, dict) and "gate_decisions" in gate_decisions:
        gate_decisions = gate_decisions["gate_decisions"]

    # Assemble and issue
    assembler = PackAndPermitAssembler(validate_delivery=not args.skip_delivery_check)
    result = assembler.assemble_pack_and_issue_permit(
        skill_id=args.skill_id,
        manifest=manifest,
        gate_decisions=gate_decisions,
        three_hashes=three_hashes,
        revision=args.revision,
    )

    # Write outputs
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if result.audit_pack:
        pack_file = args.output_dir / f"{result.audit_pack.pack_id}.json"
        pack_file.write_text(
            json.dumps(result.audit_pack.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"OK: Wrote AuditPack to {pack_file}")

    if result.permit:
        permit_file = args.output_dir / f"{result.permit.permit_id}.json"
        permit_file.write_text(
            json.dumps(result.permit.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"OK: Wrote Permit to {permit_file}")
        print(f"  Status: {result.permit.status.value}")

    if not result.success:
        if result.error_code:
            print(f"ERROR: {result.error_code} - {result.error_message}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
