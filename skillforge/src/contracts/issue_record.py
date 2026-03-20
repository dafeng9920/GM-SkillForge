"""
IssueRecord - T12 deliverable: Issue records derived from adjudicated findings.

This module converts RuleDecisions (from T8) into tracked IssueRecords.
Only RuleDecisions with PASS or FAIL decisions become issues - WAIVE and DEFER
decisions do NOT create issues.

Usage:
    from skillforge.src.contracts.issue_record import (
        IssueRecord,
        create_issue_from_decision,
        create_issues_from_adjudication_report
    )

    # Create from RuleDecision
    issue = create_issue_from_decision(
        rule_decision=rule_decision,
        finding=finding,
        created_by="T12-Antigravity-2"
    )

    # Bulk create from AdjudicationReport
    issues = create_issues_from_adjudication_report(
        adjudication_report=adjudication_report,
        findings_report=findings_report
    )

Evidence paths:
    - run/<run_id>/issue_records.json
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
class IssueRecordErrorCode:
    """Error codes for issue record operations."""

    INVALID_DECISION = "E1201_INVALID_DECISION"
    MISSING_FINDING_REF = "E1202_MISSING_FINDING_REF"
    INVALID_RULE_DECISION = "E1203_INVALID_RULE_DECISION"
    ISSUE_ALREADY_EXISTS = "E1204_ISSUE_ALREADY_EXISTS"
    INVALID_STATUS_TRANSITION = "E1205_INVALID_STATUS_TRANSITION"


# ============================================================================
# Issue Status
# ============================================================================
IssueStatus = Literal["OPEN", "IN_PROGRESS", "FIXED", "VERIFIED", "CLOSED", "DEFERRED"]
IssuePriority = Literal["P0", "P1", "P2", "P3", "P4"]


# ============================================================================
# Evidence Ref
# ============================================================================
@dataclass(frozen=True)
class EvidenceRef:
    """Evidence reference from the original finding."""

    kind: Literal["FILE", "LOG", "DIFF", "SNIPPET", "URL", "CODE_LOCATION"]
    locator: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "kind": self.kind,
            "locator": self.locator,
            "note": self.note,
        }


# ============================================================================
# Rule Decision Reference
# ============================================================================
@dataclass(frozen=True)
class RuleDecisionRef:
    """Reference to the originating RuleDecision from T8."""

    decision: Literal["PASS", "FAIL"]
    adjudicated_at: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision": self.decision,
            "adjudicated_at": self.adjudicated_at,
        }


# ============================================================================
# Where Location
# ============================================================================
@dataclass
class WhereLocation:
    """Location information from the original finding."""

    file_path: str
    line_number: int | None = None
    column_number: int | None = None
    function_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "function_name": self.function_name,
        }


# ============================================================================
# Issue Record
# ============================================================================
@dataclass
class IssueRecord:
    """
    T12 Deliverable: Issue record derived from a RuleDecision.

    Only RuleDecisions with PASS or FAIL decisions become issues.
    WAIVE and DEFER decisions do NOT create issues.
    """

    issue_id: str
    finding_id: str
    rule_decision_ref: RuleDecisionRef
    title: str
    description: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    impact_level: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEGLIGIBLE"]
    truth_assessment: Literal["CONFIRMED", "LIKELY_TRUE", "UNCERTAIN", "LIKELY_FALSE"]
    evidence_strength: Literal["CONCLUSIVE", "STRONG", "MODERATE", "WEAK", "INSUFFICIENT"]
    category: Literal[
        "schema_validation",
        "contract_validation",
        "consistency_check",
        "sensitive_permission",
        "external_action",
        "dangerous_pattern",
        "boundary_gap",
        "governance_gap",
        "anti_pattern",
    ]
    status: IssueStatus = "OPEN"
    priority: IssuePriority = "P3"
    where: WhereLocation | None = None
    tags: list[str] = field(default_factory=list)
    related_issues: list[str] = field(default_factory=list)
    security_reference: dict[str, Any] | None = None
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    created_at: str | None = None
    created_by: str = "T12-Antigravity-2"
    updated_at: str | None = None
    updated_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if not self.created_at:
            object.__setattr__(
                self, "created_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            )

    def update_status(
        self,
        new_status: IssueStatus,
        updated_by: str,
    ) -> None:
        """
        Update issue status.

        Args:
            new_status: New status
            updated_by: Who is making the update

        Raises:
            ValueError: If status transition is invalid
        """
        # Define valid transitions
        valid_transitions = {
            "OPEN": ["IN_PROGRESS", "DEFERRED", "CLOSED"],
            "IN_PROGRESS": ["FIXED", "OPEN", "DEFERRED"],
            "FIXED": ["VERIFIED", "OPEN"],
            "VERIFIED": ["CLOSED", "OPEN"],
            "CLOSED": ["OPEN"],  # Can reopen
            "DEFERRED": ["OPEN", "CLOSED"],
        }

        current = self.status
        if new_status not in valid_transitions.get(current, []):
            raise ValueError(
                f"{IssueRecordErrorCode.INVALID_STATUS_TRANSITION}: "
                f"Cannot transition from {current} to {new_status}"
            )

        object.__setattr__(self, "status", new_status)
        object.__setattr__(self, "updated_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        object.__setattr__(self, "updated_by", updated_by)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "issue_id": self.issue_id,
            "finding_id": self.finding_id,
            "rule_decision_ref": self.rule_decision_ref.to_dict(),
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "impact_level": self.impact_level,
            "truth_assessment": self.truth_assessment,
            "evidence_strength": self.evidence_strength,
            "category": self.category,
            "where": self.where.to_dict() if self.where else None,
            "status": self.status,
            "priority": self.priority,
            "tags": self.tags,
            "related_issues": self.related_issues,
            "security_reference": self.security_reference,
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = output_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            temp_path.replace(output_path)
        except OSError as e:
            raise IOError(f"Failed to save issue record to {output_path}: {e}")


# ============================================================================
# Factory Functions
# ============================================================================
def generate_issue_id(task_id: str, finding_id: str) -> str:
    """
    Generate a unique issue ID.

    Args:
        task_id: Task identifier (e.g., 'quant-1.0.0')
        finding_id: Original finding ID

    Returns:
        Issue ID in format ISS-{task_id}-{short_hash}
    """
    hash_input = f"{finding_id}:{task_id}"
    short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    # Sanitize task_id for ID
    safe_task_id = task_id.replace("-", "").replace(".", "")[:12]
    return f"ISS-{safe_task_id}-{short_hash}"


def create_issue_from_decision(
    rule_decision: dict[str, Any],
    finding: dict[str, Any],
    created_by: str = "T12-Antigravity-2",
) -> IssueRecord:
    """
    Create an IssueRecord from a RuleDecision and Finding.

    Args:
        rule_decision: RuleDecision from T8 adjudication report
        finding: Original Finding from T6 findings report
        created_by: Entity creating this issue

    Returns:
        IssueRecord instance

    Raises:
        ValueError: If rule_decision has invalid decision type
    """
    decision = rule_decision.get("decision")
    finding_id = rule_decision.get("finding_id", finding.get("finding_id"))

    # T12 Hard Constraint: Only PASS and FAIL create issues
    if decision not in ("PASS", "FAIL"):
        raise ValueError(
            f"{IssueRecordErrorCode.INVALID_DECISION}: "
            f"Cannot create issue from decision '{decision}'. "
            f"Only PASS and FAIL decisions create issues."
        )

    # Extract finding data
    what = finding.get("what", {})
    where_data = finding.get("where", {})
    fix_data = finding.get("fix", {})
    security_data = finding.get("security", {})

    # Generate issue ID
    task_id = finding.get("source", {}).get("type", "UNKNOWN")
    issue_id = generate_issue_id(task_id, finding_id)

    # Create rule decision ref
    rule_decision_ref = RuleDecisionRef(
        decision=decision,
        adjudicated_at=rule_decision.get("adjudicated_at", ""),
    )

    # Create where location
    where = WhereLocation(
        file_path=where_data.get("file_path", ""),
        line_number=where_data.get("line_number"),
        column_number=where_data.get("column_number"),
        function_name=where_data.get("function_name"),
    )

    # Create evidence refs
    evidence_refs = []
    for ref in finding.get("evidence_refs", []):
        evidence_refs.append(
            EvidenceRef(
                kind=ref.get("kind"),
                locator=ref.get("locator"),
                note=ref.get("note"),
            )
        )

    # Determine priority from severity and impact
    severity = rule_decision.get("impact_level", what.get("severity", "MEDIUM"))
    priority_map = {
        "CRITICAL": "P0",
        "HIGH": "P1",
        "MEDIUM": "P2",
        "LOW": "P3",
        "NEGLIGIBLE": "P4",
        "INFO": "P4",
    }
    priority = priority_map.get(severity, "P3")

    return IssueRecord(
        issue_id=issue_id,
        finding_id=finding_id,
        rule_decision_ref=rule_decision_ref,
        title=what.get("title", "Issue from finding"),
        description=what.get("description", "") + "\n\n" + (fix_data.get("suggested_fix") or fix_data.get("remediation") or ""),
        severity=what.get("severity", "MEDIUM"),
        impact_level=rule_decision.get("impact_level", "MEDIUM"),
        truth_assessment=rule_decision.get("truth_assessment", "UNCERTAIN"),
        evidence_strength=rule_decision.get("evidence_strength", "MODERATE"),
        category=what.get("category", "boundary_gap"),
        where=where,
        priority=priority,
        security_reference=security_data if security_data else None,
        evidence_refs=evidence_refs,
        created_by=created_by,
        metadata={
            "source_task": f"T{3 + ['validation', 'rule_scan', 'pattern_match'].index(finding.get('source', {}).get('type', 'validation'))}"
            if finding.get("source", {}).get("type") in ["validation", "rule_scan", "pattern_match"]
            else "UNKNOWN",
            "original_source_code": finding.get("source", {}).get("code", ""),
            "is_security_issue": bool(security_data),
            "is_governance_issue": what.get("category") in ["governance_gap", "boundary_gap"],
        },
    )


def create_issues_from_adjudication_report(
    adjudication_report: dict[str, Any],
    findings_report: dict[str, Any],
    created_by: str = "T12-Antigravity-2",
) -> list[IssueRecord]:
    """
    Create IssueRecords from an AdjudicationReport.

    Args:
        adjudication_report: T8 adjudication report
        findings_report: T6 findings report (for finding details)
        created_by: Entity creating these issues

    Returns:
        List of IssueRecords (only for PASS/FAIL decisions)
    """
    # Create finding lookup
    findings_map = {f["finding_id"]: f for f in findings_report.get("findings", [])}

    issues = []
    for rule_decision in adjudication_report.get("rule_decisions", []):
        decision = rule_decision.get("decision")

        # Only PASS and FAIL create issues
        if decision not in ("PASS", "FAIL"):
            continue

        finding_id = rule_decision.get("finding_id")
        finding = findings_map.get(finding_id)

        if not finding:
            # Skip if we can't find the original finding
            continue

        try:
            issue = create_issue_from_decision(
                rule_decision=rule_decision,
                finding=finding,
                created_by=created_by,
            )
            issues.append(issue)
        except ValueError:
            # Skip if creation fails
            continue

    return issues


def save_issue_records(
    issues: list[IssueRecord],
    output_path: str | Path,
    run_id: str,
) -> None:
    """
    Save multiple issue records to a JSON file.

    Args:
        issues: List of issue records
        output_path: Path to save the JSON file
        run_id: Run identifier for metadata
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "t12_version": "1.0.0-t12",
        "total_issues": len(issues),
        "by_status": {},
        "by_severity": {},
        "by_priority": {},
        "issues": [issue.to_dict() for issue in issues],
    }

    # Compute summary stats
    for issue in issues:
        # Count by status
        status = issue.status
        data["by_status"][status] = data["by_status"].get(status, 0) + 1

        # Count by severity
        severity = issue.severity
        data["by_severity"][severity] = data["by_severity"].get(severity, 0) + 1

        # Count by priority
        priority = issue.priority
        data["by_priority"][priority] = data["by_priority"].get(priority, 0) + 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for issue record operations."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Generate issue_records.json from adjudication report"
    )
    parser.add_argument(
        "--adjudication-report",
        required=True,
        help="Path to T8 adjudication_report.json",
    )
    parser.add_argument(
        "--findings-report",
        required=True,
        help="Path to T6 findings_report.json",
    )
    parser.add_argument(
        "--output",
        default="run/latest/issue_records.json",
        help="Output path for issue_records.json",
    )
    parser.add_argument(
        "--run-id",
        help="Run identifier (defaults to current timestamp)",
    )
    args = parser.parse_args()

    # Load reports
    with open(args.adjudication_report) as f:
        adjudication_report = json.load(f)

    with open(args.findings_report) as f:
        findings_report = json.load(f)

    # Generate run_id if not provided
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Create issues
    issues = create_issues_from_adjudication_report(
        adjudication_report=adjudication_report,
        findings_report=findings_report,
    )

    # Save
    save_issue_records(issues, args.output, run_id)
    print(f"Issue records saved to: {args.output}")
    print(f"  Total issues: {len(issues)}")


if __name__ == "__main__":
    main()
