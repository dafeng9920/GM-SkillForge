"""
IntentParser node — parses natural language into structured intent.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "natural_language": str,
    "options": { ... }   # pipeline options
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "intent": {
        "goal": str,
        "domain": str,
        "actions": list[str],
        "constraints": list[str],
        "target_environment": str,
        "intended_use": str
    },
    "confidence": float,   # 0.0 - 1.0
    "raw_input": str
}
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class IntentParser:
    """Parse natural-language skill descriptions into structured intent."""

    node_id: str = "intent_parse"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that natural_language is present and non-empty."""
        errors: list[str] = []

        pipeline_input = input_data.get("input")
        if not isinstance(pipeline_input, dict):
            errors.append("EXEC_VALIDATION_FAILED: 'input' key is required in pipeline artifacts")
            return errors

        nl = pipeline_input.get("natural_language")
        if not nl or not isinstance(nl, str) or not nl.strip():
            errors.append("EXEC_VALIDATION_FAILED: natural_language is required and cannot be empty")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the natural language description into a structured intent dict.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        pipeline_input = input_data.get("input", {})
        natural_language: str = pipeline_input.get("natural_language", "")
        nl_lower = natural_language.lower()

        # goal: first 100 characters
        goal = natural_language[:100]

        # domain: keyword-based inference
        if "data" in nl_lower:
            domain = "data_processing"
        elif "web" in nl_lower:
            domain = "web_service"
        elif "ml" in nl_lower or "ai" in nl_lower:
            domain = "machine_learning"
        else:
            domain = "general"

        # actions: extract matching verb keywords
        action_keywords = ["analyze", "process", "generate", "transform", "compute"]
        actions = [kw for kw in action_keywords if re.search(r'\b' + kw + r'\b', nl_lower)]

        return {
            "schema_version": "0.1.0",
            "intent": {
                "goal": goal,
                "domain": domain,
                "actions": actions,
                "constraints": [],
                "target_environment": "python",
                "intended_use": "automation",
            },
            "confidence": 0.75,
            "raw_input": natural_language,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate output against intent schema."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "intent", "confidence", "raw_input"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        intent = output_data.get("intent")
        if isinstance(intent, dict):
            for field in ("goal", "domain"):
                if field not in intent:
                    errors.append(f"SCHEMA_INVALID: intent.{field} is required")
        elif intent is not None:
            errors.append("SCHEMA_INVALID: intent must be a dict")

        confidence = output_data.get("confidence")
        if isinstance(confidence, (int, float)):
            if not (0.0 <= confidence <= 1.0):
                errors.append(f"SCHEMA_INVALID: confidence must be 0.0-1.0, got {confidence}")

        return errors
