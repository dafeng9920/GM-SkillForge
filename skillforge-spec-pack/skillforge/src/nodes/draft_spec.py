"""
DraftSpec node — draft a skill specification from scan results.

Path: B, A+B
Stage: 3

Input Contract (conforms to gm-os-core draft_skill_spec.schema.json)
--------------
{
    "repo_info": { ... },
    "scan_result": { ... },     # from RepoScan
    "options": { ... }
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
    "source": "repo",
    "derived_from": {
        "repo_url": str,
        "commit_sha": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DraftSpec:
    """Draft a skill specification from repository scan results."""

    node_id: str = "draft_skill_spec"
    stage: int = 3

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate scan_result and repo_info are present."""
        errors: list[str] = []

        if not isinstance(input_data.get("intake_repo"), dict):
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo output is required"
            )

        if not isinstance(input_data.get("repo_scan_fit_score"), dict):
            errors.append(
                "EXEC_VALIDATION_FAILED: repo_scan_fit_score output is required"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Draft skill specification from scan.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intake = input_data["intake_repo"]
        scan = input_data["repo_scan_fit_score"]
        pipeline_input = input_data.get("input", {})

        repo_info = intake.get("repo_info", {})
        repo_name: str = repo_info.get("name", "unknown")
        repo_owner: str = repo_info.get("owner", "unknown")
        commit_sha: str = repo_info.get("last_commit_sha", "unknown")

        entry_points: list[str] = scan.get("entry_points", ["main.py"])
        language_stack: str = scan.get("language_stack", "unknown")
        fit_score: int = scan.get("fit_score", 0)

        # Infer tools_required from language_stack
        tools_map: dict[str, list[str]] = {
            "Python": ["python3", "pip"],
            "JavaScript": ["node", "npm"],
            "TypeScript": ["node", "npm", "tsc"],
            "Go": ["go"],
            "Rust": ["cargo"],
        }
        tools_required = tools_map.get(language_stack, [])

        # Build steps from entry_points
        first_entry = entry_points[0] if entry_points else "main.py"
        steps: list[dict[str, Any]] = [
            {
                "id": "step_1",
                "action": "execute",
                "description": f"Run {first_entry}",
            }
        ]

        # Build inputs from entry_points
        inputs: list[dict[str, Any]] = [
            {"name": ep, "type": "file", "required": True}
            for ep in entry_points
        ]

        skill_spec: dict[str, Any] = {
            "name": f"skill-{repo_name}",
            "version": "0.1.0",
            "description": f"Auto-drafted skill from {repo_owner}/{repo_name}",
            "inputs": inputs,
            "outputs": [{"name": "result", "type": "object"}],
            "tools_required": tools_required,
            "steps": steps,
            "constraints": [
                "risk_tier: L1",
                f"fit_score >= 40 (actual: {fit_score})",
            ],
        }

        repo_url: str = pipeline_input.get("repo_url", "")
        confidence: float = min(fit_score / 100, 0.95)

        return {
            "schema_version": "0.1.0",
            "skill_spec": skill_spec,
            "source": "repo",
            "derived_from": {
                "repo_url": repo_url,
                "commit_sha": commit_sha,
            },
            "confidence": confidence,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate drafted spec."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        if "schema_version" not in output_data:
            errors.append("SCHEMA_INVALID: schema_version is required")

        if "source" not in output_data:
            errors.append("SCHEMA_INVALID: source is required")
        elif output_data["source"] != "repo":
            errors.append("SCHEMA_INVALID: source must be 'repo'")

        skill_spec = output_data.get("skill_spec")
        if not isinstance(skill_spec, dict):
            errors.append("SCHEMA_INVALID: skill_spec must be a dict")
        else:
            for field in ("name", "version", "description"):
                if field not in skill_spec:
                    errors.append(f"SCHEMA_INVALID: skill_spec.{field} is required")

        return errors
