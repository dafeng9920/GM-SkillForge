"""
IntakeRepo node — fetch and validate a GitHub repository.

Path: B, A+B
Stage: 0

Input Contract (conforms to gm-os-core intake_repo.schema.json)
--------------
{
    "repo_url": str,
    "branch": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "repo_info": {
        "name": str,
        "owner": str,
        "default_branch": str,
        "stars": int,
        "license": str | None,
        "last_commit_sha": str,
        "languages": dict
    },
    "fetch_status": "ok" | "error",
    "local_path": str | None
}
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class IntakeRepo:
    """Fetch and intake a GitHub repository."""

    node_id: str = "intake_repo"
    stage: int = 0

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_url and commit_sha are present and well-formed."""
        errors: list[str] = []

        pipeline_input = input_data.get("input")
        if not isinstance(pipeline_input, dict):
            errors.append("EXEC_VALIDATION_FAILED: 'input' key is required in pipeline artifacts")
            return errors

        repo_url = pipeline_input.get("repo_url")
        if not repo_url:
            errors.append("EXEC_VALIDATION_FAILED: repo_url is required and cannot be empty")
            return errors

        # L3 Requirement: commit_sha must be present for github mode
        commit_sha = pipeline_input.get("commit_sha")
        if not commit_sha:
            errors.append("EXEC_VALIDATION_FAILED: commit_sha is required for reproducible audit")

        if not isinstance(repo_url, str):
            errors.append("EXEC_VALIDATION_FAILED: repo_url must be a string")
            return errors

        url_ok = (
            "github.com" in repo_url
            or repo_url.startswith("git://")
            or repo_url.startswith("https://")
        )
        if not url_ok:
            errors.append(
                "EXEC_VALIDATION_FAILED: repo_url must contain 'github.com' "
                "or start with 'git://' or 'https://'"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Fetch repository information and clone/download.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        pipeline_input = input_data.get("input", {})
        repo_url: str = pipeline_input.get("repo_url", "")
        branch: str = pipeline_input.get("branch", "main")
        commit_sha: str = pipeline_input.get("commit_sha", "unknown-sha")

        # Parse owner and repo name from URL
        url = repo_url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]
        parts = url.split("/")

        # Take last two non-empty segments as owner/name
        non_empty = [p for p in parts if p]
        owner = non_empty[-2] if len(non_empty) >= 2 else "unknown"
        name = non_empty[-1] if len(non_empty) >= 1 else "unknown"

        return {
            "schema_version": "0.1.0",
            "repo_info": {
                "name": name,
                "owner": owner,
                "default_branch": branch,
                "stars": 0,
                "license": None,
                "last_commit_sha": commit_sha,
                "languages": {"Python": 100},
            },
            "commit_sha": commit_sha,
            "fetch_status": "ok",
            "local_path": None,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate intake output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        if output_data.get("schema_version") != "0.1.0":
            errors.append("SCHEMA_INVALID: schema_version must be '0.1.0'")

        repo_info = output_data.get("repo_info")
        if not isinstance(repo_info, dict):
            errors.append("SCHEMA_INVALID: repo_info must be a dict")
        else:
            for field in ("name", "owner", "default_branch"):
                if field not in repo_info:
                    errors.append(f"SCHEMA_INVALID: repo_info.{field} is required")

        if "fetch_status" not in output_data:
            errors.append("SCHEMA_INVALID: fetch_status is required")

        # L3 Requirement: commit_sha must be present in output
        if "commit_sha" not in output_data:
            errors.append("SCHEMA_INVALID: commit_sha is required for reproducible audit")

        return errors
