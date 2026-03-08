"""
SkillComposer node — generate a skill spec from intent (no repo source).

Path: A only
Stage: A-only (stage index 1 within path A context)

Input Contract
--------------
{
    "intent": { ... },
    "generation_hints": dict | None,
    "options": { ... },
    "existing_skill": dict | None,    # T3: Existing skill for incremental updates
    "change_request": dict | None     # T3: Change request for delta updates
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "skill_spec": {
        "name": str,
        "version": str,
        "description": str,
        "inputs": list[dict],
        "outputs": list[dict],
        "tools_required": list[str],
        "steps": list[dict],
        "constraints": list[str]
    },
    "source": "generated",
    "confidence": float,
    "delta_info": {                    # T3: Delta information
        "is_incremental": bool,
        "base_version": str | None,
        "version_bump": "major" | "minor" | "patch" | None,
        "change_type": "new" | "update" | "subskill",
        "parent_skill": str | None
    }
}

T3 Extension: Incremental Delta Enforcement
- Detects if request is incremental (update to existing skill)
- Enforces version bump: major/minor/patch based on change scope
- Supports sub-skill creation for significant divergence
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class SkillComposer:
    """Compose a skill specification directly from parsed intent."""

    node_id: str = "skill_compose"
    stage: int = -1  # A-only pre-shared stage

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate intent presence."""
        errors: list[str] = []

        intent_parse = input_data.get("intent_parse")
        if not isinstance(intent_parse, dict):
            errors.append("EXEC_VALIDATION_FAILED: intent_parse output is required")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate a skill specification from intent.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        confidence: float = intent_parse.get("confidence", 0.5)

        source_strategy = input_data.get("source_strategy", {})
        generation_hints = source_strategy.get("generation_hints")

        goal: str = intent.get("goal", "unknown")
        domain: str = intent.get("domain", "general")
        target_env: str = intent.get("target_environment", "python")
        constraints: list[str] = list(intent.get("constraints", []))

        # ── T3: Incremental Delta Detection ──
        # First check for engine-injected incremental context
        incremental_context = input_data.get("_incremental_context", {})
        is_engine_incremental = incremental_context.get("is_incremental", False)

        # Fallback to direct parameters
        existing_skill = input_data.get("existing_skill")
        change_request = input_data.get("change_request", {})

        # Use engine-injected context if available
        if is_engine_incremental and not existing_skill:
            existing_skill = incremental_context.get("existing_skill")
        if is_engine_incremental and not change_request:
            change_request = incremental_context.get("change_request", {})

        is_incremental = False
        base_version = None
        version_bump = None
        change_type = "new"
        parent_skill = None
        base_skill_spec = None

        if isinstance(existing_skill, dict) and existing_skill.get("skill_spec"):
            is_incremental = True
            base_skill_spec = existing_skill["skill_spec"]
            base_version = base_skill_spec.get("version", "0.1.0")
            parent_skill = base_skill_spec.get("name")

            # Determine change scope and version bump
            change_scope = change_request.get("scope", "minor")

            if change_scope == "major" or self._is_breaking_change(change_request, base_skill_spec):
                version_bump = "major"
                change_type = "update"
            elif change_scope == "subskill" or self._is_divergent_change(change_request, base_skill_spec):
                version_bump = "minor"
                change_type = "subskill"
            else:
                version_bump = "patch"
                change_type = "update"

        # Build name: sanitise goal fragment
        goal_slug = re.sub(r'[^a-z0-9]+', '-', goal[:20].lower()).strip('-')

        if change_type == "subskill" and parent_skill:
            # Create sub-skill name
            name = f"{parent_skill}-{goal_slug}"
        else:
            name = f"skill-{domain}-{goal_slug}"

        # If incremental, use existing skill name for updates
        if is_incremental and change_type == "update":
            name = base_skill_spec.get("name", name)

        # tools_required from target_environment
        tools_map: dict[str, list[str]] = {
            "python": ["python3", "pip"],
            "node": ["node", "npm"],
            "javascript": ["node", "npm"],
            "go": ["go"],
            "rust": ["cargo"],
        }
        tools_required = tools_map.get(target_env, ["python3", "pip"])

        # constraints
        all_constraints = constraints + ["risk_tier: L1"]

        # Compute new version
        if is_incremental and base_version:
            new_version = self._bump_version(base_version, version_bump)
        else:
            new_version = "0.1.0"

        skill_spec: dict[str, Any] = {
            "name": name,
            "version": new_version,
            "description": goal,
            "inputs": [{"name": "input_data", "type": "object", "required": True}],
            "outputs": [{"name": "result", "type": "object"}],
            "tools_required": tools_required,
            "steps": [
                {
                    "id": "step_1",
                    "action": "execute",
                    "description": f"Execute {goal[:50]}",
                }
            ],
            "constraints": all_constraints,
        }

        # T3: Preserve parent reference for sub-skills
        if change_type == "subskill" and parent_skill:
            skill_spec["parent_skill"] = parent_skill
            skill_spec["derived_from_version"] = base_version

        # Build delta_info
        delta_info: dict[str, Any] = {
            "is_incremental": is_incremental,
            "base_version": base_version,
            "version_bump": version_bump,
            "change_type": change_type,
            "parent_skill": parent_skill,
        }

        return {
            "schema_version": "0.1.0",
            "skill_spec": skill_spec,
            "source": "generated",
            "confidence": confidence * 0.9,
            "delta_info": delta_info,
        }

    def _bump_version(self, version: str, bump_type: str | None) -> str:
        """Bump version based on change type."""
        if not bump_type:
            return version

        try:
            parts = version.split(".")
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0

            if bump_type == "major":
                return f"{major + 1}.0.0"
            elif bump_type == "minor":
                return f"{major}.{minor + 1}.0"
            else:  # patch
                return f"{major}.{minor}.{patch + 1}"
        except (ValueError, IndexError):
            return version

    def _is_breaking_change(self, change_request: dict[str, Any], base_spec: dict[str, Any]) -> bool:
        """Determine if change is breaking (requires major version bump)."""
        breaking_keywords = ["remove", "delete", "breaking", "incompatible"]
        description = change_request.get("description", "").lower()
        return any(kw in description for kw in breaking_keywords)

    def _is_divergent_change(self, change_request: dict[str, Any], base_spec: dict[str, Any]) -> bool:
        """Determine if change is divergent enough to warrant sub-skill creation."""
        divergent_keywords = ["fork", "variant", "alternative", "extend"]
        description = change_request.get("description", "").lower()
        return any(kw in description for kw in divergent_keywords)

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate generated skill spec."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "skill_spec", "source", "confidence"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # T3: delta_info is required
        if "delta_info" not in output_data:
            errors.append("SCHEMA_INVALID: delta_info is required (T3)")

        skill_spec = output_data.get("skill_spec")
        if isinstance(skill_spec, dict):
            for field in ("name", "version", "description"):
                if field not in skill_spec:
                    errors.append(f"SCHEMA_INVALID: skill_spec.{field} is required")
        elif skill_spec is not None:
            errors.append("SCHEMA_INVALID: skill_spec must be a dict")

        source = output_data.get("source")
        if source is not None and source != "generated":
            errors.append(f"SCHEMA_INVALID: source must be 'generated', got '{source}'")

        # T3: Validate delta_info structure
        delta_info = output_data.get("delta_info")
        if isinstance(delta_info, dict):
            required_delta_fields = ["is_incremental", "change_type"]
            for field in required_delta_fields:
                if field not in delta_info:
                    errors.append(f"SCHEMA_INVALID: delta_info.{field} is required (T3)")

            # Validate change_type values
            change_type = delta_info.get("change_type")
            valid_change_types = {"new", "update", "subskill"}
            if change_type is not None and change_type not in valid_change_types:
                errors.append(f"SCHEMA_INVALID: delta_info.change_type must be one of {valid_change_types}")

            # If incremental, base_version must be present
            if delta_info.get("is_incremental") and not delta_info.get("base_version"):
                errors.append("SCHEMA_INVALID: delta_info.base_version required when is_incremental=True")
        elif delta_info is not None:
            errors.append("SCHEMA_INVALID: delta_info must be a dict")

        return errors
