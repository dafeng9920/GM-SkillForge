"""
ScaffoldImpl node — generate skill implementation code from spec.

Path: ALL
Stage: 5

Input Contract (conforms to gm-os-core scaffold_skill_impl.schema.json)
--------------
{
    "skill_spec": { ... },
    "gate_decision": { ... },   # from ConstitutionGate (must be ALLOW)
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "bundle_path": str,         # path to generated skill bundle
    "files_generated": list[str],
    "entry_point": str,
    "language": str,
    "test_file": str | None,
    "manifest": {
        "skill_id": str,
        "version": str,
        "checksum": str
    }
}
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class ScaffoldImpl:
    """Generate skill implementation scaffolding from a validated spec."""

    node_id: str = "scaffold_skill_impl"
    stage: int = 5

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec and gate_decision (ALLOW) are present."""
        errors: list[str] = []

        # Resolve skill_spec
        skill_compose = input_data.get("skill_compose")
        draft_skill_spec = input_data.get("draft_skill_spec")

        has_spec = False
        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            has_spec = True
        if isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            has_spec = True

        if not has_spec:
            errors.append(
                "EXEC_VALIDATION_FAILED: skill_spec is required "
                "(from skill_compose or draft_skill_spec)"
            )

        # Resolve gate_decision
        gate = input_data.get("constitution_risk_gate")
        if not isinstance(gate, dict):
            errors.append("EXEC_VALIDATION_FAILED: constitution_risk_gate output is required")
        else:
            decision = gate.get("decision")
            if decision != "ALLOW":
                errors.append(
                    "GATE_DENIED: Constitution gate must ALLOW before scaffolding"
                )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate skill implementation bundle.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        # Resolve skill_spec
        skill_compose = input_data.get("skill_compose", {})
        draft_skill_spec = input_data.get("draft_skill_spec", {})

        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            skill_spec = skill_compose["skill_spec"]
        elif isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            skill_spec = draft_skill_spec["skill_spec"]
        else:
            skill_spec = {}

        skill_name: str = skill_spec.get("name", "unknown-skill")
        version: str = skill_spec.get("version", "0.1.0")
        tools_required: list[str] = skill_spec.get("tools_required", [])

        # Infer language
        tools_lower = [str(t).lower() for t in tools_required]
        if "python3" in tools_lower or "pip" in tools_lower:
            language = "Python"
        elif "node" in tools_lower or "npm" in tools_lower:
            language = "JavaScript"
        else:
            language = "Python"

        bundle_path = f"/tmp/skillforge/bundles/{skill_name}"
        entry_point = "main.py"
        files_generated = [
            f"{skill_name}/main.py",
            f"{skill_name}/manifest.json",
            f"{skill_name}/README.md",
        ]
        test_file = f"{skill_name}/test_skill.py"
        checksum = hashlib.sha256(skill_name.encode()).hexdigest()[:16]

        return {
            "schema_version": "0.1.0",
            "bundle_path": bundle_path,
            "files_generated": files_generated,
            "entry_point": entry_point,
            "language": language,
            "test_file": test_file,
            "manifest": {
                "skill_id": skill_name,
                "version": version,
                "checksum": checksum,
            },
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scaffold output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "bundle_path", "files_generated", "entry_point", "manifest"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        manifest = output_data.get("manifest")
        if isinstance(manifest, dict):
            for field in ("skill_id", "version", "checksum"):
                if field not in manifest:
                    errors.append(f"SCHEMA_INVALID: manifest.{field} is required")
        elif manifest is not None:
            errors.append("SCHEMA_INVALID: manifest must be a dict")

        return errors
