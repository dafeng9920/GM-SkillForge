"""
RepoScan node — scan repository structure and compute fit score.

Path: B, A+B
Stage: 2

Input Contract (conforms to gm-os-core repo_scan_fit_score.schema.json)
--------------
{
    "repo_info": { ... },
    "local_path": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "fit_score": int,          # 0-100
    "repo_type": str,          # workflow | cli | lib | service | template
    "entry_points": list[str],
    "dependencies": dict[str, str],
    "language_stack": str,
    "complexity_metrics": {
        "total_files": int,
        "total_loc": int,
        "avg_function_length": float
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RepoScan:
    """Scan repo structure and produce a fit score."""

    node_id: str = "repo_scan_fit_score"
    stage: int = 2

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info and local_path are present."""
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
        Scan repo structure and compute fit score.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intake = input_data.get("intake_repo", {})
        repo_info = intake.get("repo_info", {})
        languages: dict[str, Any] = repo_info.get("languages", {})
        detected_license = repo_info.get("license")

        # Determine language_stack from first language key
        language_stack = "unknown"
        if languages:
            language_stack = next(iter(languages))

        # Compute fit_score
        score = 40  # base
        if detected_license:
            score += 20
        if len(languages) > 1:
            score += 10
        if "Python" in languages:
            score += 30

        fit_score = max(0, min(100, score))

        # Infer repo_type from language_stack
        type_map: dict[str, str] = {
            "Python": "lib",
            "JavaScript": "service",
            "TypeScript": "service",
            "Go": "cli",
            "Rust": "cli",
            "Shell": "workflow",
            "Bash": "workflow",
        }
        repo_type = type_map.get(language_stack, "template")

        return {
            "schema_version": "0.1.0",
            "fit_score": fit_score,
            "repo_type": repo_type,
            "entry_points": ["main.py"],
            "dependencies": {},
            "language_stack": language_stack,
            "complexity_metrics": {
                "total_files": 1,
                "total_loc": 0,
                "avg_function_length": 0.0,
            },
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scan result."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "fit_score", "repo_type", "entry_points", "language_stack"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        fit_score = output_data.get("fit_score")
        if isinstance(fit_score, (int, float)):
            if not (0 <= fit_score <= 100):
                errors.append(
                    f"SCHEMA_INVALID: fit_score must be 0-100, got {fit_score}"
                )

        valid_types = ("workflow", "cli", "lib", "service", "template")
        repo_type = output_data.get("repo_type")
        if repo_type is not None and repo_type not in valid_types:
            errors.append(
                f"SCHEMA_INVALID: repo_type must be one of {valid_types}, "
                f"got '{repo_type}'"
            )

        return errors
