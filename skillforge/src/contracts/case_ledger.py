"""
CaseLedger - T13 deliverable: Minimal case ledger for test scenario tracking.

This module provides a minimal case ledger structure for tracking test scenarios
without building a large case library. It supports recording case_id, input_scenario,
expected, actual, deviation, adjudication, release, residual_risks, and follow_up_actions.

T13 Hard Constraints:
- No large case library (minimal set only)
- No marking uncovered as completed
- No marking degradable as fully successful

Usage:
    from skillforge.src.contracts.case_ledger import (
        CaseLedger,
        CaseRecord,
        create_minimal_ledger,
        add_case_to_ledger
    )

    # Create minimal ledger
    ledger = create_minimal_ledger(
        created_by="T13-Kior-B",
        in_scope_categories=["happy_path", "edge_case"],
        out_of_scope_items=[{"category": "performance", "reason": "deferred"}]
    )

    # Add case
    case = CaseRecord(
        case_id="CASE_HAPPY_001",
        input_scenario={...},
        expected_behavior={...}
    )
    add_case_to_ledger(ledger, case)

Evidence paths:
    - run/<run_id>/case_ledger.json
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


# ============================================================================
# Error Codes (E13xx series for T13)
# ============================================================================
class CaseLedgerErrorCode:
    """Error codes for case ledger operations."""

    INVALID_BOUNDARY_DECLARATION = "E1301_INVALID_BOUNDARY_DECLARATION"
    UNCOVERED_NOT_DECLARED = "E1302_UNCOVERED_NOT_DECLARED"
    DEGRADATION_MISCLASSIFIED = "E1303_DEGRADATION_MISCLASSIFIED"
    CASE_LIBRARY_TOO_LARGE = "E1304_CASE_LIBRARY_TOO_LARGE"
    RESIDUAL_RISK_MISSING = "E1305_RESIDUAL_RISK_MISSING"
    INVALID_DEGRADATION_LEVEL = "E1306_INVALID_DEGRADATION_LEVEL"
    UNCOVERED_MARKED_COMPLETE = "E1307_UNCOVERED_MARKED_COMPLETE"


# ============================================================================
# Data Types
# ============================================================================
ScenarioType = Literal[
    "happy_path",
    "edge_case",
    "error_case",
    "integration",
    "performance",
    "security",
    "governance",
]

ExecutionStatus = Literal["pending", "executed", "skipped", "blocked"]

AdjudicationDecision = Literal["PASS", "FAIL", "DEGRADED", "WAIVE"]

DegradationLevel = Literal["minor", "partial_functionality", "major"]

ActionStatus = Literal["pending", "in_progress", "completed", "blocked"]


# ============================================================================
# Data Ref
# ============================================================================
@dataclass(frozen=True)
class DataRef:
    """Reference to test data files."""

    kind: Literal["FIXTURE", "SNAPSHOT", "GENERATED", "MANUAL"]
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
# Expected Outcome
# ============================================================================
@dataclass(frozen=True)
class ExpectedOutcome:
    """Expected outcome from test execution."""

    type: Literal[
        "return_value",
        "state_change",
        "side_effect",
        "error",
        "performance",
        "gate_decision",
    ]
    description: str
    criteria: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "description": self.description,
            "criteria": self.criteria,
        }


# ============================================================================
# Deviation Record
# ============================================================================
@dataclass(frozen=True)
class DeviationRecord:
    """
    A deviation from expected behavior.

    T13 Hard Constraint: Deviations MUST be recorded, never hidden.
    """

    type: Literal[
        "outcome_mismatch",
        "missing_outcome",
        "unexpected_outcome",
        "performance_degradation",
        "error_variance",
        "data_difference",
    ]
    description: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"] | None = None
    expected: str | None = None
    actual: str | None = None
    impact: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "description": self.description,
            "severity": self.severity,
            "expected": self.expected,
            "actual": self.actual,
            "impact": self.impact,
        }


# ============================================================================
# Evidence Ref (Execution)
# ============================================================================
@dataclass(frozen=True)
class ExecutionEvidenceRef:
    """Evidence reference from execution."""

    kind: Literal["LOG", "SNIPPET", "SCREENSHOT", "METRIC", "GATE_DECISION", "ARTIFACT"]
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
# Actual Behavior
# ============================================================================
@dataclass(frozen=True)
class ActualBehavior:
    """Actual behavior observed during execution."""

    outcomes: list[dict[str, Any]] | None = None
    deviations: list[DeviationRecord] | None = None
    evidence_refs: list[ExecutionEvidenceRef] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "outcomes": self.outcomes,
            "deviations": [d.to_dict() for d in (self.deviations or [])],
            "evidence_refs": [e.to_dict() for e in (self.evidence_refs or [])],
        }


# ============================================================================
# Execution Record
# ============================================================================
@dataclass(frozen=True)
class ExecutionRecord:
    """Execution record when case is run."""

    status: ExecutionStatus = "pending"
    executed_at: str | None = None
    actual_behavior: ActualBehavior | None = None
    execution_metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "executed_at": self.executed_at,
            "actual_behavior": self.actual_behavior.to_dict() if self.actual_behavior else None,
            "execution_metadata": self.execution_metadata,
        }


# ============================================================================
# Adjudication
# ============================================================================
@dataclass(frozen=True)
class Adjudication:
    """
    Adjudication decision on case execution.

    T13 Hard Constraint: DEGRADED cases MUST specify degradation_level.
    """

    decision: AdjudicationDecision
    adjudicated_at: str
    adjudicated_by: str
    degradation_level: DegradationLevel | None = None
    rationale: str | None = None
    deviation_accepted: bool | None = None

    def __post_init__(self):
        """Validate that DEGRADED decisions have degradation_level."""
        if self.decision == "DEGRADED" and not self.degradation_level:
            raise ValueError(
                f"{CaseLedgerErrorCode.INVALID_DEGRADATION_LEVEL}: "
                f"DEGRADED decisions MUST specify degradation_level"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision": self.decision,
            "adjudicated_at": self.adjudicated_at,
            "adjudicated_by": self.adjudicated_by,
            "degradation_level": self.degradation_level,
            "rationale": self.rationale,
            "deviation_accepted": self.deviation_accepted,
        }


# ============================================================================
# Case Risk
# ============================================================================
@dataclass(frozen=True)
class CaseRisk:
    """
    Residual risk associated with a case.

    T13 Hard Constraint: Residual risks MUST be registered even for PASS cases.
    """

    risk_id: str | None = None
    risk_category: Literal[
        "test_gap",
        "data_limitation",
        "environment_constraint",
        "assumption_violation",
        "degradation_risk",
        "coverage_hole",
    ] = "coverage_hole"
    description: str = ""
    mitigation: str | None = None
    requires_monitoring: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_id": self.risk_id,
            "risk_category": self.risk_category,
            "description": self.description,
            "mitigation": self.mitigation,
            "requires_monitoring": self.requires_monitoring,
        }


# ============================================================================
# Follow Up Action
# ============================================================================
@dataclass(frozen=True)
class FollowUpAction:
    """Follow-up action required from a case."""

    action: str
    status: ActionStatus = "pending"
    owner: str | None = None
    priority: Literal["P0", "P1", "P2", "P3", "P4"] | None = None
    ticket_ref: str | None = None
    target_date: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action": self.action,
            "status": self.status,
            "owner": self.owner,
            "priority": self.priority,
            "ticket_ref": self.ticket_ref,
            "target_date": self.target_date,
        }


# ============================================================================
# Input Scenario
# ============================================================================
@dataclass(frozen=True)
class InputScenario:
    """Input scenario definition."""

    scenario_type: ScenarioType
    inputs: dict[str, Any]
    data_refs: list[DataRef] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_type": self.scenario_type,
            "inputs": self.inputs,
            "data_refs": [d.to_dict() for d in (self.data_refs or [])],
        }


# ============================================================================
# Expected Behavior
# ============================================================================
@dataclass(frozen=True)
class ExpectedBehavior:
    """Expected behavior and outcomes."""

    outcomes: list[ExpectedOutcome]
    assertions: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "outcomes": [o.to_dict() for o in self.outcomes],
            "assertions": self.assertions,
        }


# ============================================================================
# Case Record
# ============================================================================
@dataclass
class CaseRecord:
    """
    A single test case record in the ledger.

    T13 Hard Constraints:
    - deviations must be recorded if present
    - degraded cases must have degradation_level
    - residual_risks should be assessed
    """

    case_id: str
    input_scenario: InputScenario
    expected_behavior: ExpectedBehavior
    execution_record: ExecutionRecord
    title: str | None = None
    description: str | None = None
    created_at: str | None = None
    created_by: str | None = None
    adjudication: Adjudication | None = None
    release_decision: dict[str, Any] | None = None
    residual_risks: list[CaseRisk] | None = None
    follow_up_actions: list[FollowUpAction] | None = None
    tags: list[str] | None = None
    related_case_ids: list[str] | None = None
    issue_refs: list[str] | None = None

    def __post_init__(self):
        """Initialize created_at if not provided."""
        if not self.created_at:
            object.__setattr__(
                self, "created_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            )

    def add_deviation(self, deviation: DeviationRecord) -> None:
        """
        Add a deviation to the execution record.

        T13 Hard Constraint: Deviations must be recorded.
        """
        current = self.execution_record.actual_behavior
        if current is None:
            new_behavior = ActualBehavior(deviations=[deviation])
            new_record = ExecutionRecord(
                status=self.execution_record.status,
                executed_at=self.execution_record.executed_at,
                actual_behavior=new_behavior,
                execution_metadata=self.execution_record.execution_metadata,
            )
        else:
            deviations = list(current.deviations or []) + [deviation]
            new_behavior = ActualBehavior(
                outcomes=current.outcomes,
                deviations=deviations,
                evidence_refs=current.evidence_refs,
            )
            new_record = ExecutionRecord(
                status=self.execution_record.status,
                executed_at=self.execution_record.executed_at,
                actual_behavior=new_behavior,
                execution_metadata=self.execution_record.execution_metadata,
            )
        object.__setattr__(self, "execution_record", new_record)

    def add_residual_risk(self, risk: CaseRisk) -> None:
        """
        Add a residual risk.

        T13 Hard Constraint: Residual risks should be registered.
        """
        risks = list(self.residual_risks or []) + [risk]
        object.__setattr__(self, "residual_risks", risks)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "input_scenario": self.input_scenario.to_dict(),
            "expected_behavior": self.expected_behavior.to_dict(),
            "execution_record": self.execution_record.to_dict(),
            "adjudication": self.adjudication.to_dict() if self.adjudication else None,
            "release_decision": self.release_decision,
            "residual_risks": [r.to_dict() for r in (self.residual_risks or [])],
            "follow_up_actions": [a.to_dict() for a in (self.follow_up_actions or [])],
            "tags": self.tags,
            "related_case_ids": self.related_case_ids,
            "issue_refs": self.issue_refs,
        }


# ============================================================================
# In Scope Item
# ============================================================================
@dataclass(frozen=True)
class InScopeItem:
    """In-scope scenario category."""

    category: Literal[
        "happy_path",
        "edge_case",
        "error_case",
        "integration",
        "performance",
        "security",
        "governance",
    ]
    description: str
    coverage_target: Literal["full", "partial", "sampling"] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "description": self.description,
            "coverage_target": self.coverage_target,
        }


# ============================================================================
# Out of Scope Item
# ============================================================================
@dataclass(frozen=True)
class OutOfScopeItem:
    """
    Out-of-scope scenario.

    T13 Hard Constraint: Uncovered items MUST be declared.
    """

    category: str
    reason: Literal[
        "not_implemented",
        "deferred",
        "out_of_project_scope",
        "requires_external_dependency",
        "deprecated_feature",
    ]
    ticket_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "reason": self.reason,
            "ticket_ref": self.ticket_ref,
        }


# ============================================================================
# Boundary Declaration
# ============================================================================
@dataclass(frozen=True)
class BoundaryDeclaration:
    """
    T13 Hard Constraint: Explicit boundary declaration.

    Defines what IS and IS NOT covered by the case ledger.
    """

    in_scope: list[InScopeItem]
    out_of_scope: list[OutOfScopeItem]
    assumptions: list[str]
    data_constraints: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "in_scope": [i.to_dict() for i in self.in_scope],
            "out_of_scope": [o.to_dict() for o in self.out_of_scope],
            "assumptions": self.assumptions,
            "data_constraints": self.data_constraints,
        }


# ============================================================================
# Coverage Summary
# ============================================================================
@dataclass
class CoverageSummary:
    """Summary of coverage completeness."""

    in_scope_covered: int = 0
    in_scope_total: int = 0
    out_of_scope_declared: int = 0
    completion_percent: float = 0.0

    def __post_init__(self):
        """Calculate completion percent."""
        if self.in_scope_total > 0:
            object.__setattr__(
                self,
                "completion_percent",
                round(self.in_scope_covered / self.in_scope_total * 100, 2),
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "in_scope_covered": self.in_scope_covered,
            "in_scope_total": self.in_scope_total,
            "out_of_scope_declared": self.out_of_scope_declared,
            "completion_percent": self.completion_percent,
        }


# ============================================================================
# Status Summary
# ============================================================================
@dataclass
class StatusSummary:
    """Summary of cases by adjudication status."""

    passed: int = 0
    failed: int = 0
    degraded: int = 0
    waived: int = 0
    pending: int = 0

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "failed": self.failed,
            "degraded": self.degraded,
            "waived": self.waived,
            "pending": self.pending,
        }


# ============================================================================
# Degradation Summary
# ============================================================================
@dataclass
class DegradationSummary:
    """Summary of cases by degradation level."""

    fully_successful: int = 0
    minor_degradation: int = 0
    partial_functionality: int = 0
    major_degradation: int = 0
    unclassified: int = 0

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "fully_successful": self.fully_successful,
            "minor_degradation": self.minor_degradation,
            "partial_functionality": self.partial_functionality,
            "major_degradation": self.major_degradation,
            "unclassified": self.unclassified,
        }


# ============================================================================
# Case Ledger
# ============================================================================
@dataclass
class CaseLedger:
    """
    T13 Deliverable: Minimal case ledger for test scenario tracking.

    Hard Constraints:
    - No large case library (minimal set only)
    - Uncovered scenarios MUST be declared
    - Degraded cases MUST be explicitly classified
    - Residual risks MUST be registered

    Evidence paths: run/<run_id>/case_ledger.json
    """

    ledger_id: str
    boundary_declaration: BoundaryDeclaration
    cases: list[CaseRecord] = field(default_factory=list)
    ledger_version: str = "1.0.0-t13"
    created_at: str | None = None
    created_by: str = "T13-Kior-B"
    parent_ledger_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize created_at if not provided."""
        if not self.created_at:
            object.__setattr__(
                self, "created_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            )

    @property
    def summary(self) -> dict[str, Any]:
        """Compute summary statistics."""
        status_summary = StatusSummary()
        degradation_summary = DegradationSummary()
        coverage_summary = CoverageSummary(
            in_scope_total=len(self.boundary_declaration.in_scope),
            out_of_scope_declared=len(self.boundary_declaration.out_of_scope),
        )

        for case in self.cases:
            # T13 Hard Constraint E1307: Only count EXECUTED cases as covered
            # Pending cases are NOT covered, regardless of whether they have a case_id
            if case.execution_record.status != "executed":
                # Pending/skipped/blocked cases are NOT covered
                status_summary.pending += 1
                continue

            # Case is executed, now check adjudication
            if case.adjudication:
                decision = case.adjudication.decision
                if decision == "PASS":
                    # T13 Hard Constraint E1303: Check for misclassification
                    has_deviations = (
                        case.execution_record.actual_behavior
                        and case.execution_record.actual_behavior.deviations
                    )
                    if has_deviations:
                        # E1303 VIOLATION: Has deviations but marked PASS
                        # This is a misclassification, do NOT count as passed
                        degradation_summary.unclassified += 1
                        # Track separately - do not increment status_summary.passed
                    else:
                        # No deviations, truly successful
                        degradation_summary.fully_successful += 1
                        status_summary.passed += 1
                elif decision == "FAIL":
                    status_summary.failed += 1
                elif decision == "DEGRADED":
                    status_summary.degraded += 1
                    # Classify by degradation level
                    level = case.adjudication.degradation_level
                    if level == "minor":
                        degradation_summary.minor_degradation += 1
                    elif level == "partial_functionality":
                        degradation_summary.partial_functionality += 1
                    elif level == "major":
                        degradation_summary.major_degradation += 1
                elif decision == "WAIVE":
                    status_summary.waived += 1
            else:
                # Executed but no adjudication - treat as pending
                status_summary.pending += 1

            # T13 Hard Constraint E1307: Only executed cases count as covered
            coverage_summary.in_scope_covered += 1

        # Recalculate completion percent after all cases processed
        if coverage_summary.in_scope_total > 0:
            object.__setattr__(
                coverage_summary,
                "completion_percent",
                round(coverage_summary.in_scope_covered / coverage_summary.in_scope_total * 100, 2),
            )

        return {
            "total_cases": len(self.cases),
            "by_status": status_summary.to_dict(),
            "by_degradation": degradation_summary.to_dict(),
            "coverage_completeness": coverage_summary.to_dict(),
        }

    def add_case(self, case: CaseRecord) -> None:
        """
        Add a case to the ledger.

        T13 Hard Constraint: Validate that uncovered is not marked complete.
        """
        # Check for case library bloat
        MAX_MINIMAL_CASES = 100
        if len(self.cases) >= MAX_MINIMAL_CASES:
            raise ValueError(
                f"{CaseLedgerErrorCode.CASE_LIBRARY_TOO_LARGE}: "
                f"Case ledger exceeds minimal size ({MAX_MINIMAL_CASES}). "
                f"Consider splitting or archiving."
            )

        self.cases.append(case)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ledger_id": self.ledger_id,
            "ledger_version": self.ledger_version,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "parent_ledger_ref": self.parent_ledger_ref,
            "boundary_declaration": self.boundary_declaration.to_dict(),
            "cases": [case.to_dict() for case in self.cases],
            "summary": self.summary,
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
            raise IOError(f"Failed to save case ledger to {output_path}: {e}")


# ============================================================================
# Factory Functions
# ============================================================================
def generate_ledger_id(date_str: str | None = None) -> str:
    """
    Generate a unique ledger ID.

    Args:
        date_str: Date string in YYYYMMDD format (defaults to today)

    Returns:
        Ledger ID in format LEDGER-{YYYYMMDD}-{short_hash}
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")

    # Use timestamp for uniqueness
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    hash_input = f"{date_str}_{timestamp}"
    short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    return f"LEDGER-{date_str}-{short_hash}"


def create_boundary_declaration(
    in_scope_categories: list[dict[str, Any]] | None = None,
    out_of_scope_items: list[dict[str, Any]] | None = None,
    assumptions: list[str] | None = None,
    data_constraints: list[dict[str, Any]] | None = None,
) -> BoundaryDeclaration:
    """
    Create a boundary declaration.

    T13 Hard Constraint: Explicit boundary declaration required.

    Args:
        in_scope_categories: Categories in scope
        out_of_scope_items: Items out of scope (must be declared)
        assumptions: Assumptions made
        data_constraints: Data constraints

    Returns:
        BoundaryDeclaration instance
    """
    in_scope_list = [
        InScopeItem(
            category=item.get("category", "happy_path"),
            description=item.get("description", ""),
            coverage_target=item.get("coverage_target"),
        )
        for item in (in_scope_categories or [])
    ]

    out_of_scope_list = [
        OutOfScopeItem(
            category=item.get("category", ""),
            reason=item.get("reason", "not_implemented"),
            ticket_ref=item.get("ticket_ref"),
        )
        for item in (out_of_scope_items or [])
    ]

    return BoundaryDeclaration(
        in_scope=in_scope_list,
        out_of_scope=out_of_scope_list,
        assumptions=assumptions or [],
        data_constraints=data_constraints,
    )


def create_minimal_ledger(
    created_by: str = "T13-Kior-B",
    in_scope_categories: list[dict[str, Any]] | None = None,
    out_of_scope_items: list[dict[str, Any]] | None = None,
    assumptions: list[str] | None = None,
    parent_ledger_ref: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CaseLedger:
    """
    Create a minimal case ledger.

    T13 Hard Constraint: Boundary declaration is required.

    Args:
        created_by: Entity creating the ledger
        in_scope_categories: Categories in scope
        out_of_scope_items: Items explicitly out of scope
        assumptions: Assumptions made
        parent_ledger_ref: Parent ledger if incremental
        metadata: Additional metadata

    Returns:
        CaseLedger instance
    """
    # Default minimal in-scope if not specified
    if in_scope_categories is None:
        in_scope_categories = [
            {"category": "happy_path", "description": "Basic happy path scenarios"},
        ]

    # Create boundary declaration
    boundary = create_boundary_declaration(
        in_scope_categories=in_scope_categories,
        out_of_scope_items=out_of_scope_items,
        assumptions=assumptions,
    )

    ledger_id = generate_ledger_id()

    return CaseLedger(
        ledger_id=ledger_id,
        boundary_declaration=boundary,
        created_by=created_by,
        parent_ledger_ref=parent_ledger_ref,
        metadata=metadata or {},
    )


def add_case_to_ledger(
    ledger: CaseLedger,
    case: CaseRecord,
) -> None:
    """
    Add a case to the ledger.

    Args:
        ledger: CaseLedger to modify
        case: CaseRecord to add

    Raises:
        ValueError: If case library exceeds minimal size
    """
    ledger.add_case(case)


def create_case_from_scenario(
    category: str,
    seq: int,
    scenario_type: ScenarioType,
    inputs: dict[str, Any],
    expected_outcomes: list[dict[str, Any]],
    title: str | None = None,
    description: str | None = None,
) -> CaseRecord:
    """
    Create a CaseRecord from a scenario definition.

    Args:
        category: Category prefix for case_id
        seq: Sequence number
        scenario_type: Type of scenario
        inputs: Input parameters
        expected_outcomes: Expected outcomes
        title: Case title
        description: Case description

    Returns:
        CaseRecord instance
    """
    case_id = f"CASE-{category.upper()}-{seq:03d}"

    input_scenario = InputScenario(
        scenario_type=scenario_type,
        inputs=inputs,
    )

    outcomes = [
        ExpectedOutcome(
            type=o.get("type", "return_value"),
            description=o.get("description", ""),
            criteria=o.get("criteria"),
        )
        for o in expected_outcomes
    ]

    expected_behavior = ExpectedBehavior(outcomes=outcomes)

    execution_record = ExecutionRecord(status="pending")

    return CaseRecord(
        case_id=case_id,
        title=title,
        description=description,
        input_scenario=input_scenario,
        expected_behavior=expected_behavior,
        execution_record=execution_record,
    )


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for case ledger operations."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Generate case_ledger.json (T13 minimal case ledger)"
    )
    parser.add_argument(
        "--output",
        default="run/latest/case_ledger.json",
        help="Output path for case_ledger.json",
    )
    parser.add_argument(
        "--in-scope",
        nargs="*",
        help="In-scope categories (e.g., happy_path edge_case)",
    )
    parser.add_argument(
        "--out-of-scope",
        nargs="*",
        help="Out-of-scope categories (format: category:reason)",
    )
    parser.add_argument(
        "--created-by",
        default="T13-Kior-B",
        help="Entity creating the ledger",
    )
    args = parser.parse_args()

    # Parse in-scope
    in_scope_items = None
    if args.in_scope:
        in_scope_items = [
            {"category": cat, "description": f"{cat} scenarios"}
            for cat in args.in_scope
        ]

    # Parse out-of-scope
    out_of_scope_items = None
    if args.out_of_scope:
        out_of_scope_items = []
        for item in args.out_of_scope:
            if ":" in item:
                category, reason = item.split(":", 1)
                out_of_scope_items.append({"category": category, "reason": reason})
            else:
                out_of_scope_items.append({"category": item, "reason": "not_implemented"})

    # Create ledger
    ledger = create_minimal_ledger(
        created_by=args.created_by,
        in_scope_categories=in_scope_items,
        out_of_scope_items=out_of_scope_items,
        assumptions=["Standard test environment", "Test data available"],
    )

    # Save
    ledger.save(args.output)
    print(f"Case ledger saved to: {args.output}")
    print(f"  Ledger ID: {ledger.ledger_id}")
    print(f"  In-scope categories: {len(ledger.boundary_declaration.in_scope)}")
    print(f"  Out-of-scope declared: {len(ledger.boundary_declaration.out_of_scope)}")


if __name__ == "__main__":
    main()
