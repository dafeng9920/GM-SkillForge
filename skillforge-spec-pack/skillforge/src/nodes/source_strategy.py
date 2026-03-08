"""
SourceStrategy node — decides whether to generate from scratch or search GitHub.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "intent": { ... },       # from IntentParser
    "mode": "nl" | "auto",
    "confidence": float
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "strategy": "generate" | "search_github" | "hybrid",
    "search_query": str | None,      # set when strategy includes github search
    "generation_hints": dict | None,  # set when strategy includes generation
    "reason": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SourceStrategy:
    """Decide source strategy based on parsed intent and mode."""

    node_id: str = "source_strategy"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that intent and mode are present."""
        errors: list[str] = []

        intent_parse = input_data.get("intent_parse")
        if not isinstance(intent_parse, dict):
            errors.append("EXEC_VALIDATION_FAILED: intent_parse output is required")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Determine source strategy.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        confidence: float = intent_parse.get("confidence", 0.0)

        pipeline_input = input_data.get("input", {})
        mode: str = pipeline_input.get("mode", "nl")

        # Strategy decision rules
        if mode == "github":
            strategy = "search_github"
            reason = "Mode is 'github'; searching GitHub for matching repos"
        elif mode == "nl" and confidence > 0.8:
            strategy = "generate"
            reason = f"Mode is 'nl' with high confidence ({confidence}); generating from scratch"
        elif mode == "auto":
            strategy = "hybrid"
            reason = "Mode is 'auto'; using hybrid strategy (search + generate)"
        else:
            strategy = "generate"
            reason = f"Mode is '{mode}' with confidence {confidence}; defaulting to generation"

        # search_query
        search_query = None
        if strategy in ("search_github", "hybrid"):
            goal = intent.get("goal", "")
            search_query = goal[:50] if goal else None

        # generation_hints
        generation_hints = None
        if strategy in ("generate", "hybrid"):
            generation_hints = {
                "domain": intent.get("domain", "general"),
                "actions": intent.get("actions", []),
            }

        return {
            "schema_version": "0.1.0",
            "strategy": strategy,
            "search_query": search_query,
            "generation_hints": generation_hints,
            "reason": reason,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate strategy output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "strategy", "reason"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        strategy = output_data.get("strategy")
        if strategy is not None and strategy not in ("generate", "search_github", "hybrid"):
            errors.append(
                f"SCHEMA_INVALID: strategy must be generate, search_github, or hybrid, got '{strategy}'"
            )

        return errors
