"""
EvidenceLevel - T9 deliverable: Evidence level definitions (E1-E5).

This module defines the stable, minimal-bore evidence levels used throughout
SkillForge for declaring test coverage strength. Enforces "no default strength"
principle - evidence level must be explicitly declared.

Evidence Levels (E1-E5):
- E1 (Declaration): Weakest - only a claim/assertion, no supporting artifact
- E2 (Log): Weak - structured log output showing test execution
- E3 (Artifact): Medium - structured output file (JSON, report, etc.)
- E4 (Replayable): Strong - executable test that can be rerun
- E5 (Gate): Strongest - gate_decision.json with entry/exit挂载

Usage:
    from skillforge.src.contracts.evidence_level import (
        get_evidence_level,
        validate_evidence_level,
        EVIDENCE_LEVELS
    )

    # Get level definition
    level = get_evidence_level("E4")
    print(level["level_name"])  # "Replayable Test"

    # Validate level
    is_valid = validate_evidence_level("E5")  # True

Evidence paths:
    - run/<run_id>/evidence_level.json (canonical definitions)
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


# ============================================================================
# Error Codes (E9xx series for T9)
# ============================================================================
class EvidenceLevelErrorCode:
    """Error codes for evidence level validation."""

    LEVEL_ID_INVALID = "E911_LEVEL_ID_INVALID"
    LEVEL_NOT_DECLARED = "E912_LEVEL_NOT_DECLARED"
    EVIDENCE_KIND_MISMATCH = "E913_EVIDENCE_KIND_MISMATCH"
    GATE_DECISION_MISSING = "E914_GATE_DECISION_MISSING"
    ENTRY_GATE_MISSING = "E915_ENTRY_GATE_MISSING"
    EXIT_GATE_MISSING = "E916_EXIT_GATE_MISSING"
    RECEIPT_MISSING = "E917_RECEIPT_MISSING"


# ============================================================================
# Evidence Level IDs
# ============================================================================
EVIDENCE_LEVELS = Literal["E1", "E2", "E3", "E4", "E5"]


# ============================================================================
# Canonical Evidence Level Definitions
# ============================================================================
# E1: Declaration - Weakest evidence level
E1_DECLARATION = {
    "level_id": "E1",
    "level_name": "Declaration (Weakest)",
    "strength": 1,
    "requirements": {
        "description": "A claim or assertion that something exists or works, "
                       "with no supporting artifact. The weakest form of evidence.",
        "minimum_artifacts": "claim only (assertion in code or comment)",
        "replayable": False,
        "automated": False,
        "gate_required": False,
    },
    "acceptable_kinds": ["SNIPPET", "CODE_LOCATION"],
    "validation_criteria": {
        "must_have": ["item_id", "claim"],
        "must_not_have": ["test_file", "log", "gate_decision"],
    },
    "examples": [
        {
            "description": "Comment in code claiming function works",
            "evidence_refs": [
                {"kind": "CODE_LOCATION", "locator": "skill.py:42"}
            ]
        }
    ]
}

# E2: Log - Weak evidence level
E2_LOG = {
    "level_id": "E2",
    "level_name": "Log Output",
    "strength": 2,
    "requirements": {
        "description": "Structured log output showing test execution occurred. "
                       "Provides timestamp and execution trace but no structured output.",
        "minimum_artifacts": "log file with timestamp",
        "replayable": False,
        "automated": True,
        "gate_required": False,
    },
    "acceptable_kinds": ["LOG", "SNIPPET"],
    "validation_criteria": {
        "must_have": ["log_file", "timestamp", "execution_trace"],
        "must_not_have": ["structured_output", "gate_decision"],
    },
    "examples": [
        {
            "description": "Console output from test run",
            "evidence_refs": [
                {"kind": "LOG", "locator": "run/20260316_120000/test.log"}
            ]
        }
    ]
}

# E3: Artifact - Medium evidence level
E3_ARTIFACT = {
    "level_id": "E3",
    "level_name": "Structured Artifact",
    "strength": 3,
    "requirements": {
        "description": "Structured output file (JSON, report, etc.) that can be "
                       "parsed and validated. Provides machine-readable evidence.",
        "minimum_artifacts": "structured file (JSON, YAML, etc.)",
        "replayable": False,
        "automated": True,
        "gate_required": False,
    },
    "acceptable_kinds": ["TEST_FILE", "LOG", "SNIPPET", "RUN_ID"],
    "validation_criteria": {
        "must_have": ["structured_file", "schema_validation"],
        "must_not_have": ["executable_test", "gate_decision"],
    },
    "examples": [
        {
            "description": "validation_report.json from T3",
            "evidence_refs": [
                {"kind": "TEST_FILE", "locator": "run/T3_evidence/validation_report.json"}
            ]
        },
        {
            "description": "rule_scan_report.json from T4",
            "evidence_refs": [
                {"kind": "TEST_FILE", "locator": "run/T4_evidence/rule_scan_report.json"}
            ]
        }
    ]
}

# E4: Replayable - Strong evidence level
E4_REPLAYABLE = {
    "level_id": "E4",
    "level_name": "Replayable Test",
    "strength": 4,
    "requirements": {
        "description": "Executable test that can be rerun with the same inputs "
                       "to produce the same outputs. Provides verifiable evidence.",
        "minimum_artifacts": "test file + assertion + execution capability",
        "replayable": True,
        "automated": True,
        "gate_required": False,
    },
    "acceptable_kinds": ["TEST_FILE", "CODE_LOCATION", "RUN_ID"],
    "validation_criteria": {
        "must_have": ["test_file", "assertion", "can_replay"],
        "must_not_have": ["gate_decision"],
    },
    "examples": [
        {
            "description": "Unit test that can be rerun",
            "evidence_refs": [
                {"kind": "TEST_FILE", "locator": "tests/test_intake.py::test_validate_intent_id"},
                {"kind": "CODE_LOCATION", "locator": "tests/test_intake.py:42"}
            ]
        }
    ]
}

# E5: Gate - Strongest evidence level
E5_GATE = {
    "level_id": "E5",
    "level_name": "Gate Decision (Strongest)",
    "strength": 5,
    "requirements": {
        "description": "Gate decision with entry/exit挂载 per Antigravity-1 standards. "
                       "Provides strongest evidence with closed-loop contract compliance.",
        "minimum_artifacts": "entry_gate_decision.json + exit_gate_decision.json + receipt",
        "replayable": True,
        "automated": True,
        "gate_required": True,
    },
    "acceptable_kinds": ["GATE_DECISION", "RUN_ID", "TEST_FILE"],
    "validation_criteria": {
        "must_have": ["entry_gate_decision", "exit_gate_decision", "receipt"],
        "must_not_have": [],
    },
    "examples": [
        {
            "description": "Gate decision with dual-gate compliance",
            "evidence_refs": [
                {"kind": "GATE_DECISION", "locator": "run/20260316_120000/entry_gate_decision.json"},
                {"kind": "GATE_DECISION", "locator": "run/20260316_120000/exit_gate_decision.json"}
            ]
        }
    ]
}

# All levels indexed by ID
EVIDENCE_LEVEL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "E1": E1_DECLARATION,
    "E2": E2_LOG,
    "E3": E3_ARTIFACT,
    "E4": E4_REPLAYABLE,
    "E5": E5_GATE,
}


# ============================================================================
# Functions
# ============================================================================
def get_evidence_level(level_id: str) -> dict[str, Any]:
    """
    Get evidence level definition by ID.

    Args:
        level_id: Evidence level ID (E1-E5)

    Returns:
        Dictionary containing level definition.

    Raises:
        ValueError: If level_id is invalid.
    """
    if level_id not in EVIDENCE_LEVEL_DEFINITIONS:
        raise ValueError(
            f"{EvidenceLevelErrorCode.LEVEL_ID_INVALID}: "
            f"invalid level_id '{level_id}'. Must be one of: {list(EVIDENCE_LEVEL_DEFINITIONS.keys())}"
        )
    return EVIDENCE_LEVEL_DEFINITIONS[level_id]


def validate_evidence_level(level_id: str) -> bool:
    """
    Validate an evidence level ID.

    Args:
        level_id: Evidence level ID to validate

    Returns:
        True if valid, False otherwise.
    """
    return level_id in EVIDENCE_LEVEL_DEFINITIONS


def get_all_evidence_levels() -> list[dict[str, Any]]:
    """
    Get all evidence level definitions.

    Returns:
        List of all evidence level definitions sorted by strength.
    """
    return [
        EVIDENCE_LEVEL_DEFINITIONS[lid]
        for lid in ["E1", "E2", "E3", "E4", "E5"]
    ]


def compare_levels(level_a: str, level_b: str) -> int:
    """
    Compare two evidence levels by strength.

    Args:
        level_a: First level ID
        level_b: Second level ID

    Returns:
        -1 if level_a < level_b
         0 if level_a == level_b
         1 if level_a > level_b

    Raises:
        ValueError: If either level_id is invalid.
    """
    strength_a = get_evidence_level(level_a)["strength"]
    strength_b = get_evidence_level(level_b)["strength"]

    if strength_a < strength_b:
        return -1
    elif strength_a > strength_b:
        return 1
    else:
        return 0


def validate_evidence_refs(level_id: str, evidence_refs: list[Any]) -> dict[str, Any]:
    """
    Validate that evidence refs match the required level.

    For E5 (Gate Decision), enforces dual-gate compliance:
    - Must have entry_gate_decision evidence
    - Must have exit_gate_decision evidence
    - Must have receipt evidence

    Args:
        level_id: Required evidence level
        evidence_refs: List of evidence refs to validate

    Returns:
        Dict with 'valid' flag and any 'errors'/'warnings'.
    """
    errors: list[str] = []
    warnings: list[str] = []

    level = get_evidence_level(level_id)
    acceptable_kinds = set(level["acceptable_kinds"])
    must_have = set(level["validation_criteria"]["must_have"])

    # Check each ref
    actual_kinds = set()
    locators = []
    for ref in evidence_refs:
        kind = ref.get("kind")
        if not kind:
            errors.append(f"Evidence ref missing 'kind': {ref}")
            continue

        actual_kinds.add(kind)
        locators.append(ref.get("locator", ""))

        # Check if kind is acceptable
        if kind not in acceptable_kinds:
            errors.append(
                f"{EvidenceLevelErrorCode.EVIDENCE_KIND_MISMATCH}: "
                f"kind '{kind}' not acceptable for level {level_id}. "
                f"Acceptable: {sorted(acceptable_kinds)}"
            )

    # E5 specific: enforce dual-gate + receipt
    if level_id == "E5":
        has_entry_gate = any("entry_gate" in loc.lower() for loc in locators)
        has_exit_gate = any("exit_gate" in loc.lower() for loc in locators)
        has_receipt = any(
            "receipt" in loc.lower() or kind == "RUN_ID"
            for loc, kind in zip(locators, [r.get("kind", "") for r in evidence_refs])
        )

        if not has_entry_gate:
            errors.append(
                f"{EvidenceLevelErrorCode.ENTRY_GATE_MISSING}: "
                f"E5 requires entry_gate_decision evidence. "
                f"Expected locator containing 'entry_gate_decision'"
            )

        if not has_exit_gate:
            errors.append(
                f"{EvidenceLevelErrorCode.EXIT_GATE_MISSING}: "
                f"E5 requires exit_gate_decision evidence. "
                f"Expected locator containing 'exit_gate_decision'"
            )

        if not has_receipt:
            errors.append(
                f"{EvidenceLevelErrorCode.RECEIPT_MISSING}: "
                f"E5 requires receipt evidence per Antigravity-1 closed-loop standards. "
                f"Expected evidence with 'receipt' in locator or RUN_ID kind"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def save_evidence_levels(output_path: str | Path) -> None:
    """
    Save all evidence level definitions to a JSON file.

    Args:
        output_path: Path to save evidence_level.json.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": "1.0.0-t9",
        "levels": get_all_evidence_levels(),
        "metadata": {
            "description": "Evidence level definitions for SkillForge T9",
            "generated_at": "2026-03-16T00:00:00Z",
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for evidence level operations."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Work with evidence level definitions"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    subparsers.add_parser("list", help="List all evidence levels")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an evidence level")
    validate_parser.add_argument("level_id", help="Level ID to validate (E1-E5)")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export definitions to JSON")
    export_parser.add_argument(
        "--output",
        default="run/latest/evidence_level.json",
        help="Output path for evidence_level.json",
    )

    args = parser.parse_args()

    if args.command == "list":
        for level in get_all_evidence_levels():
            print(f"{level['level_id']}: {level['level_name']} (strength={level['strength']})")

    elif args.command == "validate":
        is_valid = validate_evidence_level(args.level_id)
        if is_valid:
            level = get_evidence_level(args.level_id)
            print(f"Valid: {level['level_name']}")
        else:
            print(f"Invalid level ID: {args.level_id}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "export":
        save_evidence_levels(args.output)
        print(f"Evidence levels exported to: {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
