#!/usr/bin/env python3
"""
Demand Parser Lite - Restricted NL to Demand DSL Parser (v0)

Performs minimal parsing of natural language into Demand DSL v0 format.
Supports 4 modes with blocking clarification (max 3 questions).

Modes supported:
- generate_skill: Generate a new skill from NL
- modify_skill: Modify an existing skill
- audit_skill: Audit an existing skill
- compose_workflow: Compose multiple skills into workflow

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
"""

from __future__ import annotations

import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class Mode(str, Enum):
    """Supported execution modes in v0."""
    GENERATE_SKILL = "generate_skill"
    MODIFY_SKILL = "modify_skill"
    AUDIT_SKILL = "audit_skill"
    COMPOSE_WORKFLOW = "compose_workflow"


class ClarificationRequest(str, Enum):
    """Types of clarification requests."""
    MISSING_MODE = "missing_mode"
    MISSING_TARGET = "missing_target"
    MISSING_SOURCE = "missing_source"
    AMBIGUOUS_OPERATION = "ambiguous_operation"
    INSUFFICIENT_CONTEXT = "insufficient_context"


@dataclass
class ClarificationQuestion:
    """A clarification question to ask the user."""
    question_id: str
    question_type: str
    question_text: str
    options: list[str] | None = None
    required: bool = True


@dataclass
class ParseResult:
    """Result of parsing NL to Demand DSL."""
    success: bool
    demand_dsl: dict[str, Any] | None = None
    clarifications_needed: list[ClarificationQuestion] = field(default_factory=list)
    error_message: str | None = None
    parse_metadata: dict[str, Any] = field(default_factory=dict)


class DemandParserLite:
    """
    Lightweight NL to Demand DSL parser.

    v0 Constraints:
    - Only 4 supported modes
    - Max 3 clarification questions
    - Missing required fields => clarifications, not guessing
    - Does not do full DDD deconstruction
    - Does not do autonomous planning
    """

    SCHEMA_VERSION = "demand_dsl_v0"
    MAX_CLARIFICATIONS = 3

    # Mode detection patterns
    MODE_PATTERNS = {
        Mode.GENERATE_SKILL: [
            r"\bgenerate\b.*\bskill\b",
            r"\bcreate\b.*\bskill\b",
            r"\bbuild\b.*\bskill\b",
            r"\bmake\b.*\bskill\b",
            r"\bnew\b.*\bskill\b",
        ],
        Mode.MODIFY_SKILL: [
            r"\bmodify\b.*\bskill\b",
            r"\bupdate\b.*\bskill\b",
            r"\bchange\b.*\bskill\b",
            r"\bedit\b.*\bskill\b",
            r"\bfix\b.*\bskill\b",
        ],
        Mode.AUDIT_SKILL: [
            r"\baudit\b.*\bskill\b",
            r"\bcheck\b.*\bskill\b",
            r"\breview\b.*\bskill\b",
            r"\bvalidate\b.*\bskill\b",
            r"\binspect\b.*\bskill\b",
        ],
        Mode.COMPOSE_WORKFLOW: [
            r"\bcompose\b.*\bworkflow\b",
            r"\bcombine\b.*\bskills\b",
            r"\bworkflow\b.*\bcompose\b",
            r"\borchestrate\b",
        ],
    }

    # Source detection patterns
    SOURCE_PATTERNS = {
        "repo_url": r"https?://github\.com/[\w-]+/[\w-]+",
        "skill_id": r"skill:[\w-]+",
        "local_path": r"^[\w~/].*",
    }

    def __init__(self):
        """Initialize the parser."""
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        self._compiled_mode_patterns = {}
        for mode, patterns in self.MODE_PATTERNS.items():
            self._compiled_mode_patterns[mode] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
        self._compiled_source_patterns = {
            kind: re.compile(pattern) for kind, pattern in self.SOURCE_PATTERNS.items()
        }

    def parse(
        self,
        nl_input: str,
        user_id: str | None = None,
        source_type: str = "nl_prompt"
    ) -> ParseResult:
        """
        Parse natural language input into Demand DSL.

        Args:
            nl_input: Natural language input text
            user_id: Optional user identifier
            source_type: Type of input source

        Returns:
            ParseResult with Demand DSL or clarifications needed
        """
        clarifications: list[ClarificationQuestion] = []
        dsl: dict[str, Any] = {
            "schema_version": self.SCHEMA_VERSION,
            "intent_id": f"{uuid.uuid4().hex}",
            "trigger": {
                "type": source_type,
                "source": user_id or "unknown",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        # Detect mode
        mode = self._detect_mode(nl_input)
        if mode is None:
            clarifications.append(ClarificationQuestion(
                question_id="q_mode",
                question_type=ClarificationRequest.MISSING_MODE,
                question_text="What would you like to do?",
                options=[m.value for m in Mode],
                required=True,
            ))
            return ParseResult(
                success=False,
                clarifications_needed=clarifications,
                error_message="Could not determine execution mode",
            )
        dsl["mode"] = mode.value

        # Extract sources
        sources = self._extract_sources(nl_input)
        if not sources:
            clarifications.append(ClarificationQuestion(
                question_id="q_source",
                question_type=ClarificationRequest.MISSING_SOURCE,
                question_text="What is the source or input for this operation?",
                required=True,
            ))
        dsl["sources"] = sources

        # Extract destinations
        destinations = self._extract_destinations(nl_input, mode)
        if not destinations:
            clarifications.append(ClarificationQuestion(
                question_id="q_destination",
                question_type=ClarificationRequest.MISSING_TARGET,
                question_text="Where should the output be written?",
                required=True,
            ))
        dsl["destinations"] = destinations

        # Set defaults for transforms
        dsl["transforms"] = []

        # Set defaults for constraints
        dsl["constraints"] = self._default_constraints()

        # Set defaults for acceptance
        dsl["acceptance"] = self._default_acceptance()

        # Check if we have too many clarifications
        if len(clarifications) > self.MAX_CLARIFICATIONS:
            return ParseResult(
                success=False,
                clarifications_needed=clarifications[:self.MAX_CLARIFICATIONS],
                error_message=f"Too many clarifications needed (max {self.MAX_CLARIFICATIONS})",
            )

        # If we have clarifications, return incomplete result
        if clarifications:
            return ParseResult(
                success=False,
                demand_dsl=dsl,
                clarifications_needed=clarifications,
                parse_metadata={"clarification_count": len(clarifications)},
            )

        return ParseResult(
            success=True,
            demand_dsl=dsl,
            parse_metadata={"mode": mode.value},
        )

    def _detect_mode(self, text: str) -> Mode | None:
        """Detect execution mode from text."""
        text_lower = text.lower()
        for mode, patterns in self._compiled_mode_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return mode
        return None

    def _extract_sources(self, text: str) -> list[dict[str, Any]]:
        """Extract source references from text."""
        sources = []

        # Check for repo URLs
        for match in re.finditer(r"https?://github\.com/[\w-]+/[\w-]+", text):
            sources.append({
                "kind": "repo_url",
                "locator": match.group(0),
                "version": "main",  # Default version
            })

        # Check for skill IDs
        for match in re.finditer(r"skill:[\w-]+", text):
            sources.append({
                "kind": "skill_id",
                "locator": match.group(0),
            })

        # If no structured sources found, use the text itself
        if not sources:
            sources.append({
                "kind": "nl_text",
                "locator": text.strip(),
                "format": "text",
            })

        return sources

    def _extract_destinations(self, text: str, mode: Mode) -> list[dict[str, Any]]:
        """Extract destination from text based on mode."""
        destinations = []

        if mode == Mode.GENERATE_SKILL:
            # Try to extract skill name from text
            # Look for patterns like "create X skill" or "generate Y"
            skill_name_match = re.search(
                r"(?:generate|create|build|make)\s+(?:a\s+)?(?:new\s+)?(\w+(?:\s+\w+)?)?\s*skill",
                text,
                re.IGNORECASE
            )
            if skill_name_match:
                name = skill_name_match.group(1) or "generated_skill"
                skill_name = name.replace(" ", "_").lower()
                destinations.append({
                    "kind": "skill",
                    "locator": f"skills/{skill_name}",
                    "write_mode": "create",
                    "format": "python",
                })
            else:
                # Default skill name
                destinations.append({
                    "kind": "skill",
                    "locator": "skills/generated_skill",
                    "write_mode": "create",
                    "format": "python",
                })

        elif mode == Mode.MODIFY_SKILL:
            destinations.append({
                "kind": "skill",
                "locator": "skills/modified_skill",
                "write_mode": "update",
                "format": "python",
            })

        elif mode == Mode.AUDIT_SKILL:
            destinations.append({
                "kind": "audit_report",
                "locator": "reports/audit_result.json",
                "write_mode": "create",
                "format": "json",
            })

        elif mode == Mode.COMPOSE_WORKFLOW:
            destinations.append({
                "kind": "workflow",
                "locator": "workflows/composed_workflow.json",
                "write_mode": "create",
                "format": "json",
            })

        return destinations

    def _default_constraints(self) -> dict[str, Any]:
        """Get default constraints for v0."""
        return {
            "network_policy": "deny_by_default",
            "execution_mode": "dry_run",
            "secrets": [],
            "resource_limits": {
                "max_duration_seconds": 300,
                "max_memory_mb": 512,
            },
            "human_approval_points": [
                "constitution_risk_gate",
                "pack_audit_and_publish",
            ],
        }

    def _default_acceptance(self) -> dict[str, Any]:
        """Get default acceptance criteria for v0."""
        return {
            "success_criteria": [
                {
                    "criterion": "Manifest is valid per demand_dsl_v0.schema.yml",
                    "check_type": "static_check",
                },
                {
                    "criterion": "Dry-run execution completes without errors",
                    "check_type": "automated_test",
                },
            ],
            "quality_gates": {
                "min_test_pass_rate": 1.0,
                "security_scan_required": True,
            },
        }


def main() -> int:
    """CLI entry point for testing."""
    import json

    parser = DemandParserLite()

    if len(sys.argv) > 1:
        nl_input = " ".join(sys.argv[1:])
    else:
        nl_input = "Generate a skill that emails PDFs to Notion"

    result = parser.parse(nl_input, user_id="test_user")

    if result.success:
        print("SUCCESS - Generated Demand DSL:")
        print(json.dumps(result.demand_dsl, indent=2))
    else:
        print("CLARIFICATIONS NEEDED:")
        for q in result.clarifications_needed:
            print(f"  [{q.question_id}] {q.question_text}")
            if q.options:
                print(f"    Options: {', '.join(q.options)}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
        if result.demand_dsl:
            print("\nPartial DSL:")
            print(json.dumps(result.demand_dsl, indent=2))

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
