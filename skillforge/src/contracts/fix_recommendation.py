"""
FixRecommendation - T12 deliverable: Fix recommendations for issues.

This module provides actionable remediation guidance for issues.
Each FixRecommendation MUST reference a valid issue_id.

Usage:
    from skillforge.src.contracts.fix_recommendation import (
        FixRecommendation,
        FixOption,
        create_recommendation_for_issue,
        generate_recommendations_for_issues
    )

    # Create for a single issue
    recommendation = create_recommendation_for_issue(
        issue=issue,
        recommendation_type="CODE_FIX",
        options=[...]
    )

    # Generate for multiple issues
    recommendations = generate_recommendations_for_issues(
        issues=issues,
        created_by="T12-Antigravity-2"
    )

Evidence paths:
    - run/<run_id>/fix_recommendations.json
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


# ============================================================================
# Error Codes (E12xx series for T12)
# ============================================================================
class FixRecommendationErrorCode:
    """Error codes for fix recommendation operations."""

    INVALID_ISSUE_ID = "E1210_INVALID_ISSUE_ID"
    ISSUE_NOT_FOUND = "E1211_ISSUE_NOT_FOUND"
    MISSING_REQUIRED_OPTION = "E1212_MISSING_REQUIRED_OPTION"
    INVALID_RECOMMENDATION_TYPE = "E1213_INVALID_RECOMMENDATION_TYPE"


# ============================================================================
# Recommendation Types
# ============================================================================
RecommendationType = Literal[
    "CODE_FIX",
    "CONFIGURATION_CHANGE",
    "SCHEMA_UPDATE",
    "DEPENDENCY_UPDATE",
    "PERMISSION_REDUCTION",
    "GOVERNANCE_CONTROL",
    "DOCUMENTATION_UPDATE",
    "ARCHITECTURAL_CHANGE",
    "REFACTORING",
    "MULTI_STEP",
]

FixPriority = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "OPTIONAL"]

FixTier = Literal["RECOMMENDED", "ALTERNATIVE", "LAST_RESORT"]


# ============================================================================
# Fix Option
# ============================================================================
@dataclass
class CodeChange:
    """Specific code change needed."""

    file_path: str
    change_type: Literal["ADD", "MODIFY", "DELETE", "REPLACE"]
    line_number: int | None = None
    old_code: str | None = None
    new_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "change_type": self.change_type,
            "line_number": self.line_number,
            "old_code": self.old_code,
            "new_code": self.new_code,
        }


@dataclass
class Implementation:
    """Implementation guidance for a fix option."""

    code_changes: list[CodeChange] | None = None
    steps: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code_changes": [c.to_dict() for c in self.code_changes] if self.code_changes else None,
            "steps": self.steps,
        }


@dataclass
class FixOption:
    """A fix option with specific implementation details."""

    option_id: str
    name: str
    tier: FixTier
    description: str
    implementation: Implementation | None = None
    pros: list[str] | None = None
    cons: list[str] | None = None
    trade_offs: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "option_id": self.option_id,
            "name": self.name,
            "tier": self.tier,
            "description": self.description,
            "implementation": self.implementation.to_dict() if self.implementation else None,
            "pros": self.pros,
            "cons": self.cons,
            "trade_offs": self.trade_offs,
        }


# ============================================================================
# Verification Criterion
# ============================================================================
@dataclass
class VerificationCriterion:
    """Criterion to verify the fix was successful."""

    criterion: str
    verification_method: Literal["AUTOMATED_TEST", "MANUAL_TEST", "CODE_REVIEW", "SCAN_RE-RUN", "GATE_CHECK"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "criterion": self.criterion,
            "verification_method": self.verification_method,
        }


# ============================================================================
# Fix Recommendation
# ============================================================================
@dataclass
class FixRecommendation:
    """
    T12 Deliverable: Fix recommendation for an issue.

    T12 Hard Constraint: Every FixRecommendation MUST reference a valid issue_id.
    """

    recommendation_id: str
    issue_id: str
    recommendation_type: RecommendationType
    priority: FixPriority
    options: list[FixOption]
    summary: str = ""
    description: str = ""
    prerequisites: list[dict[str, Any]] = field(default_factory=list)
    side_effects: list[dict[str, Any]] = field(default_factory=list)
    testing_recommendations: list[str] = field(default_factory=list)
    verification_criteria: list[VerificationCriterion] = field(default_factory=list)
    related_recommendations: list[str] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)
    created_at: str | None = None
    created_by: str = "T12-Antigravity-2"
    updated_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps and validate."""
        if not self.created_at:
            object.__setattr__(
                self, "created_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            )

        # T12 Hard Constraint: Must have at least one option
        if not self.options:
            raise ValueError(
                f"{FixRecommendationErrorCode.MISSING_REQUIRED_OPTION}: "
                f"FixRecommendation must have at least one option"
            )

        # T12 Hard Constraint: Must have at least one verification criterion
        if not self.verification_criteria:
            # Add default verification criterion
            self.verification_criteria = [
                VerificationCriterion(
                    criterion="Issue no longer detected in follow-up scan",
                    verification_method="SCAN_RE-RUN",
                )
            ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "recommendation_id": self.recommendation_id,
            "issue_id": self.issue_id,
            "recommendation_type": self.recommendation_type,
            "priority": self.priority,
            "summary": self.summary,
            "description": self.description,
            "options": [opt.to_dict() for opt in self.options],
            "prerequisites": self.prerequisites,
            "side_effects": self.side_effects,
            "testing_recommendations": self.testing_recommendations,
            "verification_criteria": [vc.to_dict() for vc in self.verification_criteria],
            "related_recommendations": self.related_recommendations,
            "references": self.references,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ============================================================================
# Factory Functions
# ============================================================================
def generate_recommendation_id(issue_id: str, option_count: int) -> str:
    """
    Generate a unique recommendation ID.

    Args:
        issue_id: Issue ID this recommendation is for
        option_count: Number of options in this recommendation

    Returns:
        Recommendation ID in format REC-{short_hash}-{option_count}
    """
    # Extract short hash from issue_id
    # Format: ISS-{task_id}-{short_hash}
    parts = issue_id.split("-")
    short_hash = parts[-1] if len(parts) > 1 else hashlib.sha256(issue_id.encode()).hexdigest()[:8]
    return f"REC-{short_hash}-{option_count}"


def create_recommendation_for_issue(
    issue: Any,  # IssueRecord or dict with issue_id
    recommendation_type: RecommendationType,
    options: list[FixOption],
    priority: FixPriority | None = None,
    created_by: str = "T12-Antigravity-2",
) -> FixRecommendation:
    """
    Create a FixRecommendation for an issue.

    Args:
        issue: IssueRecord (or dict with issue_id)
        recommendation_type: Type of fix recommended
        options: List of fix options
        priority: Priority level (defaults to derived from issue)
        created_by: Entity creating this recommendation

    Returns:
        FixRecommendation instance
    """
    # Extract issue_id
    if hasattr(issue, "issue_id"):
        issue_id = issue.issue_id
        issue_severity = issue.severity
        issue_category = issue.category
    else:
        issue_id = issue.get("issue_id")
        issue_severity = issue.get("severity", "MEDIUM")
        issue_category = issue.get("category", "boundary_gap")

    # Derive priority from issue severity if not provided
    if priority is None:
        priority_map = {
            "CRITICAL": "CRITICAL",
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "LOW": "LOW",
            "INFO": "OPTIONAL",
        }
        priority = priority_map.get(issue_severity, "MEDIUM")

    recommendation_id = generate_recommendation_id(issue_id, len(options))

    return FixRecommendation(
        recommendation_id=recommendation_id,
        issue_id=issue_id,
        recommendation_type=recommendation_type,
        priority=priority,
        options=options,
        summary=f"Fix for {issue_category} issue",
        description=f"Recommended fix for issue {issue_id}",
        created_by=created_by,
        metadata={
            "auto_generated": True,
            "derived_from_severity": issue_severity,
        },
    )


def generate_recommendations_for_issues(
    issues: list[Any],
    created_by: str = "T12-Antigravity-2",
) -> list[FixRecommendation]:
    """
    Generate fix recommendations for multiple issues.

    Args:
        issues: List of IssueRecords (or dicts with issue data)
        created_by: Entity creating these recommendations

    Returns:
        List of FixRecommendations
    """
    recommendations = []

    for issue in issues:
        # Extract issue data
        if hasattr(issue, "issue_id"):
            issue_id = issue.issue_id
            category = issue.category
            severity = issue.severity
            where = issue.where
            title = issue.title
        else:
            issue_id = issue.get("issue_id")
            category = issue.get("category", "boundary_gap")
            severity = issue.get("severity", "MEDIUM")
            where_data = issue.get("where", {})
            where = WhereLocation(
                file_path=where_data.get("file_path", ""),
                line_number=where_data.get("line_number"),
            ) if where_data else None
            title = issue.get("title", "Issue")

        # Skip INFO/LOW severity issues (optional fixes)
        if severity in ("INFO", "LOW"):
            continue

        # Generate recommendation based on category
        recommendation_type, options = _generate_options_for_category(category, where, title)

        try:
            rec = create_recommendation_for_issue(
                issue=issue,
                recommendation_type=recommendation_type,
                options=options,
                created_by=created_by,
            )
            recommendations.append(rec)
        except ValueError:
            # Skip if creation fails
            continue

    return recommendations


def _generate_options_for_category(
    category: str,
    where: Any | None,
    title: str,
) -> tuple[RecommendationType, list[FixOption]]:
    """
    Generate fix options based on issue category.

    Args:
        category: Issue category
        where: Location information
        title: Issue title

    Returns:
        Tuple of (recommendation_type, options)
    """
    file_path = where.file_path if where else "unknown"
    line_num = where.line_number if where else 0

    if category == "schema_validation":
        return (
            "SCHEMA_UPDATE",
            [
                FixOption(
                    option_id="OPT-1",
                    name="Update schema to match contract",
                    tier="RECOMMENDED",
                    description=f"Update the schema definition to resolve: {title}",
                    implementation=Implementation(
                        steps=[
                            f"1. Open {file_path}",
                            f"2. Locate the schema definition around line {line_num}",
                            "3. Update the schema to match the actual data structure",
                            "4. Re-run validation to confirm",
                        ]
                    ),
                    pros=["Resolves the validation error", "Improves data integrity"],
                    cons=["May require updating data migration scripts"],
                ),
            ]
        )

    elif category == "sensitive_permission":
        return (
            "PERMISSION_REDUCTION",
            [
                FixOption(
                    option_id="OPT-1",
                    name="Remove or reduce permission",
                    tier="RECOMMENDED",
                    description=f"Remove sensitive permission or implement least-privilege: {title}",
                    implementation=Implementation(
                        steps=[
                            "1. Review why this permission is needed",
                            "2. Remove if unused",
                            "3. Or implement proper scope and access controls",
                            "4. Add runtime permission checks",
                        ]
                    ),
                    pros=["Reduces security risk", "Follows principle of least privilege"],
                    cons=["May break existing functionality if permission is actually needed"],
                ),
                FixOption(
                    option_id="OPT-2",
                    name="Document and add guardrails",
                    tier="ALTERNATIVE",
                    description="Keep permission but add strict guardrails and documentation",
                    implementation=Implementation(
                        steps=[
                            "1. Add comprehensive documentation for permission usage",
                            "2. Implement runtime permission checks",
                            "3. Add audit logging for permission usage",
                            "4. Create security review process for usage",
                        ]
                    ),
                    pros=["Maintains functionality", "Adds visibility"],
                    cons=["Higher implementation effort", "Ongoing maintenance burden"],
                ),
            ]
        )

    elif category == "external_action":
        return (
            "CODE_FIX",
            [
                FixOption(
                    option_id="OPT-1",
                    name="Remove external action or sandbox",
                    tier="RECOMMENDED",
                    description=f"Remove external action call or implement sandboxing: {title}",
                    implementation=Implementation(
                        steps=[
                            "1. Review the external action and its purpose",
                            "2. Remove if unnecessary",
                            "3. Or implement sandboxing/containment",
                            "4. Add input validation and sanitization",
                        ]
                    ),
                    pros=["Reduces attack surface", "Prevents code execution risks"],
                    cons=["May impact functionality"],
                ),
            ]
        )

    elif category == "governance_gap":
        return (
            "GOVERNANCE_CONTROL",
            [
                FixOption(
                    option_id="OPT-1",
                    name="Implement missing control",
                    tier="RECOMMENDED",
                    description=f"Add the missing governance control: {title}",
                    implementation=Implementation(
                        steps=[
                            "1. Identify the specific control gap",
                            "2. Design the control implementation",
                            "3. Add automated enforcement",
                            "4. Add monitoring and alerting",
                        ]
                    ),
                    pros=["Addresses governance requirement", "Improves compliance"],
                    cons=["Implementation effort required"],
                ),
            ]
        )

    else:
        # Generic fallback
        return (
            "CODE_FIX",
            [
                FixOption(
                    option_id="OPT-1",
                    name="Fix the identified issue",
                    tier="RECOMMENDED",
                    description=f"Address the issue: {title}",
                    implementation=Implementation(
                        steps=[
                            f"1. Review {file_path}:{line_num}",
                            "2. Implement the fix",
                            "3. Add test coverage",
                            "4. Verify the fix resolves the issue",
                        ]
                    ),
                    pros=["Resolves the issue", "Improves code quality"],
                    cons=["Requires development effort"],
                ),
            ]
        )


def save_fix_recommendations(
    recommendations: list[FixRecommendation],
    output_path: str | Path,
    run_id: str,
) -> None:
    """
    Save fix recommendations to a JSON file.

    Args:
        recommendations: List of fix recommendations
        output_path: Path to save the JSON file
        run_id: Run identifier for metadata
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "t12_version": "1.0.0-t12",
        "total_recommendations": len(recommendations),
        "by_type": {},
        "by_priority": {},
        "recommendations": [rec.to_dict() for rec in recommendations],
    }

    # Compute summary stats
    for rec in recommendations:
        # Count by type
        rec_type = rec.recommendation_type
        data["by_type"][rec_type] = data["by_type"].get(rec_type, 0) + 1

        # Count by priority
        priority = rec.priority
        data["by_priority"][priority] = data["by_priority"].get(priority, 0) + 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================================
# Import WhereLocation for type compatibility
# ============================================================================
from skillforge.src.contracts.issue_record import WhereLocation


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for fix recommendation operations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate fix_recommendations.json from issue records"
    )
    parser.add_argument(
        "--issue-records",
        required=True,
        help="Path to issue_records.json",
    )
    parser.add_argument(
        "--output",
        default="run/latest/fix_recommendations.json",
        help="Output path for fix_recommendations.json",
    )
    parser.add_argument(
        "--run-id",
        help="Run identifier (defaults to current timestamp)",
    )
    args = parser.parse_args()

    # Load issue records
    with open(args.issue_records) as f:
        data = json.load(f)

    issues = data.get("issues", [])

    # Generate recommendations
    recommendations = generate_recommendations_for_issues(issues)

    # Generate run_id if not provided
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Save
    save_fix_recommendations(recommendations, args.output, run_id)
    print(f"Fix recommendations saved to: {args.output}")
    print(f"  Total recommendations: {len(recommendations)}")


if __name__ == "__main__":
    main()
