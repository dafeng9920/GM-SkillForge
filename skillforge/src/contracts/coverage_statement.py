"""
CoverageStatement - T9 deliverable: Explicit coverage declaration for test artifacts.

This module enforces the T9 requirements:
- Explicitly declare what IS covered (no defaults)
- Explicitly declare what is NOT covered (silence = not covered)
- Attach evidence levels to each covered item
- Provide traceable evidence references

Usage:
    from skillforge.src.contracts.coverage_statement import CoverageStatement, CoveredItem

    # Create coverage statement
    statement = CoverageStatement(
        artifact_id="T3_validation",
        artifact_type="task",
        declared_by="vs--cc1"
    )
    statement.add_covered(
        item_id="validate_intent_id",
        item_type="function",
        evidence_level="E4",
        evidence_refs=[...]
    )
    statement.add_uncovered(
        item_id="validate_branch_only",
        item_type="function",
        reason="not_implemented"
    )

Evidence paths:
    - run/<run_id>/coverage_statement.json
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


# ============================================================================
# Error Codes (E9xx series for T9)
# ============================================================================
class CoverageErrorCode:
    """Error codes for coverage statement validation."""

    COV_ID_INVALID = "E901_COV_ID_INVALID"
    ARTIFACT_ID_MISSING = "E902_ARTIFACT_ID_MISSING"
    EVIDENCE_LEVEL_INVALID = "E903_EVIDENCE_LEVEL_INVALID"
    EVIDENCE_REF_MISSING = "E904_EVIDENCE_REF_MISSING"
    UNCOVERED_REASON_INVALID = "E905_UNCOVERED_REASON_INVALID"
    IMPLICIT_COVERAGE = "E906_IMPLICIT_COVERAGE"
    DEFAULT_FULL_COVERAGE = "E907_DEFAULT_FULL_COVERAGE"


# ============================================================================
# Evidence Levels
# ============================================================================
EVIDENCE_LEVELS = Literal["E1", "E2", "E3", "E4", "E5"]


# ============================================================================
# Evidence Reference
# ============================================================================
@dataclass(frozen=True)
class EvidenceRef:
    """Reference to evidence supporting a coverage claim."""

    kind: Literal["TEST_FILE", "LOG", "GATE_DECISION", "SNIPPET", "RUN_ID", "CODE_LOCATION"]
    locator: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "kind": self.kind,
            "locator": self.locator,
            "note": self.note,
        }


# ============================================================================
# Covered Item
# ============================================================================
@dataclass
class CoveredItem:
    """An item that IS covered by tests."""

    item_id: str
    item_type: Literal["function", "method", "class", "schema_field", "rule", "pattern", "path", "endpoint"]
    evidence_level: EVIDENCE_LEVELS
    evidence_refs: list[EvidenceRef]
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "evidence_level": self.evidence_level,
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
            "note": self.note,
        }


# ============================================================================
# Uncovered Item
# ============================================================================
@dataclass
class UncoveredItem:
    """An item that is NOT covered (explicitly declared)."""

    item_id: str
    item_type: Literal["function", "method", "class", "schema_field", "rule", "pattern", "path", "endpoint", "edge_case", "integration"]
    reason: Literal["not_implemented", "out_of_scope", "deferred", "requires_fixture", "unknown", "deprecated"]
    planned: bool | None = None
    ticket_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "reason": self.reason,
            "planned": self.planned,
            "ticket_ref": self.ticket_ref,
        }


# ============================================================================
# Excluded Item
# ============================================================================
@dataclass
class ExcludedItem:
    """An item explicitly excluded from coverage requirements."""

    item_id: str
    exclusion_reason: Literal["internal_only", "generated_code", "third_party", "trivial", "configuration_only"]
    approved_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "exclusion_reason": self.exclusion_reason,
            "approved_by": self.approved_by,
        }


# ============================================================================
# Coverage Summary
# ============================================================================
@dataclass
class CoverageSummary:
    """Summary statistics (computed, not declared)."""

    total_items: int
    covered_count: int
    uncovered_count: int
    coverage_percent: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_items": self.total_items,
            "covered_count": self.covered_count,
            "uncovered_count": self.uncovered_count,
            "coverage_percent": self.coverage_percent,
        }


# ============================================================================
# Coverage Statement
# ============================================================================
@dataclass
class CoverageStatement:
    """
    T9 deliverable: Explicit coverage declaration for test artifacts.

    Enforces:
    - No default full coverage (silence = not covered)
    - Evidence level must be declared for each covered item
    - Evidence refs must be provided for covered items
    - Uncovered items must be explicitly declared
    """

    artifact_id: str
    artifact_type: Literal["task", "contract", "module", "function", "schema", "pipeline"]
    declared_by: str
    declared_at: str
    covered_items: list[CoveredItem] = field(default_factory=list)
    uncovered_items: list[UncoveredItem] = field(default_factory=list)
    exclusions: list[ExcludedItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def statement_id(self) -> str:
        """Generate unique statement ID."""
        hash_input = f"{self.artifact_id}:{self.declared_at}:{self.declared_by}"
        short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        return f"COV-{self.artifact_id}-{short_hash}"

    def add_covered(
        self,
        item_id: str,
        item_type: Literal["function", "method", "class", "schema_field", "rule", "pattern", "path", "endpoint"],
        evidence_level: EVIDENCE_LEVELS,
        evidence_refs: list[EvidenceRef],
        note: str | None = None,
    ) -> None:
        """
        Add a covered item.

        Args:
            item_id: Identifier of the covered item
            item_type: Type of the covered item
            evidence_level: Evidence level (E1-E5)
            evidence_refs: List of evidence references
            note: Optional additional context
        """
        if evidence_level not in ("E1", "E2", "E3", "E4", "E5"):
            raise ValueError(
                f"{CoverageErrorCode.EVIDENCE_LEVEL_INVALID}: "
                f"evidence_level must be E1-E5, got '{evidence_level}'"
            )

        if not evidence_refs:
            raise ValueError(
                f"{CoverageErrorCode.EVIDENCE_REF_MISSING}: "
                f"at least one evidence_ref required for covered item '{item_id}'"
            )

        self.covered_items.append(
            CoveredItem(
                item_id=item_id,
                item_type=item_type,
                evidence_level=evidence_level,
                evidence_refs=evidence_refs,
                note=note,
            )
        )

    def add_uncovered(
        self,
        item_id: str,
        item_type: Literal["function", "method", "class", "schema_field", "rule", "pattern", "path", "endpoint", "edge_case", "integration"],
        reason: Literal["not_implemented", "out_of_scope", "deferred", "requires_fixture", "unknown", "deprecated"],
        planned: bool | None = None,
        ticket_ref: str | None = None,
    ) -> None:
        """
        Add an uncovered item (explicit declaration).

        Args:
            item_id: Identifier of the uncovered item
            item_type: Type of the uncovered item
            reason: Reason why this item is not covered
            planned: Whether coverage is planned for future
            ticket_ref: Reference to tracking ticket if planned
        """
        self.uncovered_items.append(
            UncoveredItem(
                item_id=item_id,
                item_type=item_type,
                reason=reason,
                planned=planned,
                ticket_ref=ticket_ref,
            )
        )

    def add_excluded(
        self,
        item_id: str,
        exclusion_reason: Literal["internal_only", "generated_code", "third_party", "trivial", "configuration_only"],
        approved_by: str | None = None,
    ) -> None:
        """
        Add an excluded item.

        Args:
            item_id: Identifier of the excluded item
            exclusion_reason: Reason for exclusion
            approved_by: Who approved this exclusion
        """
        self.exclusions.append(
            ExcludedItem(
                item_id=item_id,
                exclusion_reason=exclusion_reason,
                approved_by=approved_by,
            )
        )

    def compute_summary(self) -> CoverageSummary:
        """
        Compute coverage summary.

        Returns:
            CoverageSummary with computed statistics.
        """
        covered = len(self.covered_items)
        uncovered = len(self.uncovered_items)
        total = covered + uncovered

        # Note: exclusions are NOT counted in total (they're excluded from requirements)
        percent = (covered / total * 100) if total > 0 else 0.0

        return CoverageSummary(
            total_items=total,
            covered_count=covered,
            uncovered_count=uncovered,
            coverage_percent=round(percent, 2),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        summary = self.compute_summary()

        return {
            "statement_id": self.statement_id,
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "declared_at": self.declared_at,
            "declared_by": self.declared_by,
            "covered_items": [item.to_dict() for item in self.covered_items],
            "uncovered_items": [item.to_dict() for item in self.uncovered_items],
            "exclusions": [item.to_dict() for item in self.exclusions],
            "coverage_summary": summary.to_dict(),
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """
        Save the coverage statement to a JSON file.

        Args:
            output_path: Path to save the coverage statement JSON.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically via temp file
        temp_path = output_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            temp_path.replace(output_path)
        except OSError as e:
            raise IOError(f"Failed to save coverage statement to {output_path}: {e}")


# ============================================================================
# Convenience Functions
# ============================================================================
def validate_coverage_statement(data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate a coverage statement dictionary.

    Args:
        data: Dictionary containing coverage statement fields.

    Returns:
        Dict with 'valid' flag and any 'errors'/'warnings'.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check required fields
    if "artifact_id" not in data:
        errors.append(f"{CoverageErrorCode.ARTIFACT_ID_MISSING}: artifact_id is required")

    # Validate evidence levels if covered_items present
    for item in data.get("covered_items", []):
        level = item.get("evidence_level")
        if level not in ("E1", "E2", "E3", "E4", "E5"):
            errors.append(
                f"{CoverageErrorCode.EVIDENCE_LEVEL_INVALID}: "
                f"invalid evidence_level '{level}' for item '{item.get('item_id')}'"
            )

        # Check evidence refs
        if not item.get("evidence_refs"):
            errors.append(
                f"{CoverageErrorCode.EVIDENCE_REF_MISSING}: "
                f"no evidence_refs for covered item '{item.get('item_id')}'"
            )

    # Validate uncovered reasons
    valid_reasons = {"not_implemented", "out_of_scope", "deferred", "requires_fixture", "unknown", "deprecated"}
    for item in data.get("uncovered_items", []):
        reason = item.get("reason")
        if reason not in valid_reasons:
            errors.append(
                f"{CoverageErrorCode.UNCOVERED_REASON_INVALID}: "
                f"invalid reason '{reason}' for item '{item.get('item_id')}'"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def create_coverage_statement(
    artifact_id: str,
    artifact_type: Literal["task", "contract", "module", "function", "schema", "pipeline"],
    declared_by: str,
    declared_at: str | None = None,
) -> CoverageStatement:
    """
    Create a coverage statement.

    Args:
        artifact_id: Identifier of the artifact being covered
        artifact_type: Type of artifact
        declared_by: Entity declaring coverage
        declared_at: Optional timestamp (defaults to now)

    Returns:
        CoverageStatement instance.
    """
    if not declared_at:
        declared_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return CoverageStatement(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        declared_by=declared_by,
        declared_at=declared_at,
    )


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for coverage statement generation."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Generate coverage_statement.json"
    )
    parser.add_argument(
        "--artifact-id", required=True, help="Artifact identifier (e.g., T3_validation)"
    )
    parser.add_argument(
        "--artifact-type",
        required=True,
        choices=["task", "contract", "module", "function", "schema", "pipeline"],
        help="Type of artifact"
    )
    parser.add_argument(
        "--declared-by", default="vs--cc1", help="Entity declaring coverage"
    )
    parser.add_argument(
        "--output",
        default="run/latest/coverage_statement.json",
        help="Output path for coverage_statement.json",
    )
    args = parser.parse_args()

    # Create statement
    statement = create_coverage_statement(
        artifact_id=args.artifact_id,
        artifact_type=args.artifact_type,
        declared_by=args.declared_by,
    )

    # Save
    try:
        statement.save(args.output)
        print(f"Coverage statement saved to: {args.output}")
        print(f"  Statement ID: {statement.statement_id}")
    except IOError as e:
        print(f"Failed to save: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
