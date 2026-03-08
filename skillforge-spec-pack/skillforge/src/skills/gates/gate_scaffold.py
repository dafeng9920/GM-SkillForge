"""
GateScaffoldSkill — Gate evaluator for scaffold_skill_impl.

Gate Group: delivery (Squad C)
Position: G5 (after constitution_risk_gate G4)

Implements the experience_capture.py pattern:
- validate_input(input_data) -> list[str]
- execute(input_data) -> dict
- validate_output(output) -> list[str]

Contract: skillforge/src/contracts/gates/scaffold.yaml
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOOL_REVISION = "0.1.0"
GATE_NAME = "scaffold_skill_impl"
CONTRACT_PATH = Path(__file__).parent.parent.parent / "contracts" / "gates" / "scaffold.yaml"


def _sha256(data: str | bytes) -> str:
    """Compute SHA-256 hex digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class GateScaffoldSkill:
    """
    Gate evaluator for scaffold_skill_impl.

    Validates scaffold output and chains evidence from G1-G4.
    Produces GateResult with evidence_refs for downstream gates.

    Follows the experience_capture.py pattern for consistency.
    """

    node_id: str = "scaffold_skill_impl"
    stage: int = 5
    gate_name: str = GATE_NAME
    tool_revision: str = TOOL_REVISION

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate scaffold input against contract requirements.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # SCAFFOLD-001: scaffold_skill_impl output must be present
        scaffold = input_data.get("scaffold_skill_impl")
        if not isinstance(scaffold, dict):
            errors.append("SCAFFOLD-001: scaffold_skill_impl output is required")
            return errors  # Cannot continue validation without scaffold

        # SCAFFOLD-002: files_generated must not be empty
        files_generated = scaffold.get("files_generated")
        if not files_generated:
            errors.append("SCAFFOLD-002: files_generated must not be empty")
        elif not isinstance(files_generated, list):
            errors.append("SCHEMA_INVALID: files_generated must be an array")

        # SCAFFOLD-003: manifest must be present
        manifest = scaffold.get("manifest")
        if not manifest:
            errors.append("SCAFFOLD-003: manifest is required")
        elif not isinstance(manifest, dict):
            errors.append("SCHEMA_INVALID: manifest must be an object")
        else:
            # SCAFFOLD-004: manifest must include skill_id, version, checksum
            required_fields = ["skill_id", "version", "checksum"]
            for field in required_fields:
                if field not in manifest:
                    errors.append(f"SCAFFOLD-004: manifest.{field} is required")

        # Check constitution gate (G4 prerequisite) - optional but recommended
        constitution_gate = input_data.get("constitution_risk_gate")
        if isinstance(constitution_gate, dict):
            decision = constitution_gate.get("decision")
            if decision not in ("ALLOW", "PASSED", None):
                errors.append(f"PREREQUISITE_FAILED: constitution_risk_gate decision is '{decision}'")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute scaffold gate evaluation.

        Chains evidence from G1-G4 and produces GateResult.
        Validates input first and returns REJECTED if validation fails.
        """
        # Validate input first (fail-closed)
        validation_errors = self.validate_input(input_data)
        if validation_errors:
            return {
                "gate_name": self.gate_name,
                "gate_decision": "REJECTED",
                "error_code": "VALIDATION_FAILED",
                "evidence_refs": [],
                "next_action": "halt",
                "validation_errors": validation_errors,
            }

        timestamp = _now_iso()
        scaffold = input_data.get("scaffold_skill_impl", {})
        manifest = scaffold.get("manifest", {})
        evidence_refs: list[dict[str, str]] = []

        # Chain evidence from prior gates G1-G4
        prior_gates = [
            ("intake_repo", "G1"),
            ("license_gate", "G2"),
            ("repo_scan_fit_score", "G3"),
            ("constitution_risk_gate", "G4"),
        ]

        for gate_name, gate_id in prior_gates:
            gate_output = input_data.get(gate_name)
            if isinstance(gate_output, dict) and "evidence_refs" in gate_output:
                for ref in gate_output.get("evidence_refs", []):
                    if isinstance(ref, dict):
                        evidence_refs.append({
                            "issue_key": ref.get("issue_key", f"CHAIN-{gate_id}-{uuid.uuid4().hex[:8]}"),
                            "source_locator": ref.get("source_locator", gate_name),
                            "content_hash": ref.get("content_hash", ""),
                            "tool_revision": ref.get("tool_revision", "unknown"),
                            "timestamp": ref.get("timestamp", timestamp),
                        })

        # Create evidence for scaffold output
        skill_id = manifest.get("skill_id", "unknown-skill")
        scaffold_content_hash = _sha256(json.dumps(scaffold, default=str, sort_keys=True))
        evidence_refs.append({
            "issue_key": f"SCAFFOLD-{skill_id}",
            "source_locator": f"file:///scaffold/{skill_id}/manifest.json",
            "content_hash": scaffold_content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
        })

        # Build PASSED result
        return {
            "gate_name": self.gate_name,
            "gate_decision": "PASSED",
            "error_code": None,
            "evidence_refs": evidence_refs,
            "next_action": "continue",
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """
        Validate output against GateResult schema.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        # Required fields per GateResult schema
        required_fields = ["gate_name", "gate_decision", "evidence_refs", "next_action"]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # Validate gate_decision
        decision = output_data.get("gate_decision")
        if decision not in ("PASSED", "REJECTED"):
            errors.append(f"SCHEMA_INVALID: gate_decision must be 'PASSED' or 'REJECTED', got '{decision}'")

        # Validate next_action
        next_action = output_data.get("next_action")
        if next_action not in ("continue", "halt"):
            errors.append(f"SCHEMA_INVALID: next_action must be 'continue' or 'halt', got '{next_action}'")

        # Validate evidence_refs
        evidence_refs = output_data.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append("SCHEMA_INVALID: evidence_refs must be an array")
        else:
            for i, ref in enumerate(evidence_refs):
                if not isinstance(ref, dict):
                    errors.append(f"SCHEMA_INVALID: evidence_refs[{i}] must be an object")
                    continue
                for field in ["issue_key", "source_locator", "content_hash", "timestamp"]:
                    if field not in ref:
                        errors.append(f"SCHEMA_INVALID: evidence_refs[{i}].{field} is required")

        return errors


def main():
    """CLI entry point for GateScaffoldSkill."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="GateScaffoldSkill - Scaffold gate evaluator")
    parser.add_argument("--input-file", help="Input JSON file with gate request")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    gate = GateScaffoldSkill()

    # Load input
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        print("Error: --input-file is required", file=sys.stderr)
        sys.exit(1)

    # Validate input
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

    # Execute
    output = gate.execute(input_data)

    # Validate output
    output_errors = gate.validate_output(output)
    if output_errors:
        print(f"WARNING: Output validation errors: {output_errors}", file=sys.stderr)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if output["gate_decision"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
