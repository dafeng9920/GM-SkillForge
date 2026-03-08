"""
GitHubDiscovery node — search GitHub for candidate repos matching intent.

Path: A+B only
Stage: pre-0 (-1)

Input Contract
--------------
{
    "search_query": str,
    "intent": { ... },
    "max_results": int       # default 5
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "candidates": [
        {
            "repo_url": str,
            "stars": int,
            "license": str | None,
            "fit_score_estimate": int,
            "match_reason": str
        }
    ],
    "selected": {
        "repo_url": str,
        "reason": str
    } | None,
    "fallback_to_generate": bool
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GitHubDiscovery:
    """Search GitHub for repos that match the parsed intent."""

    node_id: str = "github_discover"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate search_query and intent are present."""
        errors: list[str] = []

        source_strategy = input_data.get("source_strategy")
        if not isinstance(source_strategy, dict):
            errors.append("EXEC_VALIDATION_FAILED: source_strategy output is required")
            return errors

        if not source_strategy.get("search_query"):
            errors.append("EXEC_VALIDATION_FAILED: source_strategy.search_query is required")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Search GitHub and rank candidate repos.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        source_strategy = input_data.get("source_strategy", {})
        search_query: str = source_strategy.get("search_query", "")

        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        domain: str = intent.get("domain", "general")

        # Generate mock candidates
        candidates: list[dict[str, Any]] = []
        for i in range(3):
            candidates.append({
                "repo_url": f"https://github.com/mock-org/mock-{i}",
                "stars": 100 * (i + 1),
                "license": "MIT",
                "fit_score_estimate": 70 - i * 10,
                "match_reason": f"Matches intent domain: {domain}",
            })

        # Select the best candidate (first)
        selected = {
            "repo_url": candidates[0]["repo_url"],
            "reason": f"Highest fit_score_estimate ({candidates[0]['fit_score_estimate']}) for query: {search_query}",
        }

        return {
            "schema_version": "0.1.0",
            "candidates": candidates,
            "selected": selected,
            "fallback_to_generate": False,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate discovery output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "candidates", "fallback_to_generate"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        candidates = output_data.get("candidates")
        if candidates is not None and not isinstance(candidates, list):
            errors.append("SCHEMA_INVALID: candidates must be a list")

        return errors
