"""
LicenseGate node — gate that checks repository license compatibility.

Path: B, A+B
Stage: 1

Input Contract (conforms to gm-os-core license_gate.schema.json)
--------------
{
    "repo_info": { ... },    # from IntakeRepo
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "license_gate",
    "node_id": "license_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "license_detected": str | None,
        "compatible": bool,
        "allowed_licenses": list[str]
    },
    "timestamp": str
}
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

ALLOWED_LICENSES: list[str] = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "0BSD",
    "Unlicense",
]


@dataclass
class LicenseGate:
    """Evaluate license compatibility for an ingested repo."""

    node_id: str = "license_gate"
    stage: int = 1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info is present."""
        errors: list[str] = []

        intake = input_data.get("intake_repo")
        if not isinstance(intake, dict):
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo output is required"
            )
            return errors

        if "repo_info" not in intake:
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo.repo_info is required"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Check repository license and produce GateDecision.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        intake = input_data.get("intake_repo", {})
        repo_info = intake.get("repo_info", {})
        detected_license = repo_info.get("license")

        if not detected_license:
            decision = "DENY"
            reason = "No license detected"
            compatible = False
        elif detected_license not in ALLOWED_LICENSES:
            decision = "DENY"
            reason = f"License '{detected_license}' is not approved"
            compatible = False
        else:
            decision = "ALLOW"
            reason = f"License '{detected_license}' is approved"
            compatible = True

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return {
            "schema_version": "0.1.0",
            "gate_id": "license_gate",
            "node_id": self.node_id,
            "decision": decision,
            "reason": reason,
            "details": {
                "license_detected": detected_license,
                "compatible": compatible,
                "allowed_licenses": list(ALLOWED_LICENSES),
            },
            "timestamp": timestamp,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "gate_id", "node_id", "decision", "reason", "timestamp"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        decision = output_data.get("decision")
        if decision is not None and decision not in ("ALLOW", "DENY", "REQUIRES_CHANGES"):
            errors.append(
                f"GATE_INVALID_DECISION: decision must be ALLOW, DENY, or "
                f"REQUIRES_CHANGES, got '{decision}'"
            )

        return errors
