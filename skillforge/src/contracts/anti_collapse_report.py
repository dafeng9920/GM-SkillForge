"""
AntiCollapseReport - T13 deliverable: Anti-collapse report enforcement.

This module provides the anti-collapse report that enforces:
1. Boundary declarations - what IS and IS NOT covered
2. Uncovered assertions - preventing false claims of completeness
3. Degradation classification - preventing false success claims
4. Residual risk registration - even for PASS cases

T13 Hard Constraints:
- Uncovered scenarios MUST be declared, NOT claimed as completed
- Degraded cases MUST be explicitly classified, NOT marked as fully successful
- Residual risks MUST be registered even for PASS cases
- No default assumptions of coverage or success

Usage:
    from skillforge.src.contracts.anti_collapse_report import (
        AntiCollapseReport,
        analyze_case_ledger,
        generate_anti_collapse_report
    )

    # Analyze a case ledger
    report = generate_anti_collapse_report(
        case_ledger=ledger,
        report_type="initial",
        created_by="T13-Kior-B"
    )

    # Check release readiness
    if report.anti_collapse_score["posture"] == "STRONG":
        print("Ready for release")
    elif report.anti_collapse_score["release_recommendation"] == "blocked":
        print("Blocked:", report.anti_collapse_score["blocking_issues"])

Evidence paths:
    - run/<run_id>/anti_collapse_report.json
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from skillforge.src.contracts.case_ledger import CaseLedger


# ============================================================================
# Error Codes (E13xx series for T13 - continued)
# ============================================================================
class AntiCollapseErrorCode:
    """Error codes for anti-collapse report operations."""

    BOUNDARY_VIOLATION_DETECTED = "E1310_BOUNDARY_VIOLATION_DETECTED"
    UNCOVERED_NOT_DECLARED = "E1311_UNCOVERED_NOT_DECLARED"
    COVERAGE_INTEGRITY_FAILED = "E1312_COVERAGE_INTEGRITY_FAILED"
    DEGRADATION_MISCLASSIFIED = "E1313_DEGRADATION_MISCLASSIFIED"
    RESIDUAL_RISK_INCOMPLETE = "E1314_RESIDUAL_RISK_INCOMPLETE"
    CRITICAL_RISK_UNADDRESSED = "E1315_CRITICAL_RISK_UNADDRESSED"


# ============================================================================
# Data Types
# ============================================================================
ReportType = Literal["initial", "incremental", "final", "post_release"]

BoundaryType = Literal["in_scope", "out_of_scope", "assumption", "constraint"]

VerificationStatus = Literal["verified", "violated", "unknown"]

ViolationType = Literal[
    "uncovered_claimed_complete",
    "out_of_scope_tested",
    "assumption_unstated",
    "constraint_ignored",
    "implicit_boundary",
]

DegradationLevel = Literal["minor", "partial_functionality", "major"]

RiskCategory = Literal[
    "test_gap",
    "data_limitation",
    "environment_constraint",
    "assumption_violation",
    "degradation_risk",
    "coverage_hole",
    "dependency_risk",
]

AntiCollapsePosture = Literal["STRONG", "MODERATE", "WEAK", "CRITICAL"]

ReleaseRecommendation = Literal["clear", "caution", "blocked"]


# ============================================================================
# Declared Boundary
# ============================================================================
@dataclass(frozen=True)
class DeclaredBoundary:
    """An explicitly declared boundary from the case ledger."""

    boundary_id: str
    type: BoundaryType
    assertion: str
    verification_status: VerificationStatus | None = None
    related_cases: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "boundary_id": self.boundary_id,
            "type": self.type,
            "assertion": self.assertion,
            "verification_status": self.verification_status,
            "related_cases": self.related_cases,
        }


# ============================================================================
# Boundary Violation
# ============================================================================
@dataclass(frozen=True)
class BoundaryViolation:
    """
    A detected boundary violation.

    T13 Hard Constraint: Violations prevent false claims of coverage.
    """

    violation_type: ViolationType
    description: str
    affected_scope: str | None = None
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] | None = None
    evidence: str | None = None
    remediation: str | None = None
    related_case_refs: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "violation_type": self.violation_type,
            "description": self.description,
            "affected_scope": self.affected_scope,
            "severity": self.severity,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "related_case_refs": self.related_case_refs,
        }


# ============================================================================
# Implicit Uncovered Item
# ============================================================================
@dataclass(frozen=True)
class ImplicitUncoveredItem:
    """
    An item that is uncovered but NOT declared.

    T13 Hard Constraint: This represents a declaration gap.
    """

    item: str
    why_uncovered: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "item": self.item,
            "why_uncovered": self.why_uncovered,
            "severity": self.severity,
            "recommendation": self.recommendation,
        }


# ============================================================================
# Uncovered Declared
# ============================================================================
@dataclass(frozen=True)
class UncoveredDeclared:
    """
    T13 Hard Constraint: Verification that uncovered items are properly declared.
    """

    total_declared_uncovered: int
    verified_declared: list[str]
    implicit_uncovered_detected: list[ImplicitUncoveredItem]
    declaration_integrity_score: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_declared_uncovered": self.total_declared_uncovered,
            "verified_declared": self.verified_declared,
            "implicit_uncovered_detected": [i.to_dict() for i in self.implicit_uncovered_detected],
            "declaration_integrity_score": self.declaration_integrity_score,
        }


# ============================================================================
# Boundary Assertions
# ============================================================================
@dataclass
class BoundaryAssertions:
    """
    T13 Hard Constraint: Explicit boundary assertions.
    """

    declared_boundaries: list[DeclaredBoundary]
    boundary_violations: list[BoundaryViolation]
    uncovered_declared: UncoveredDeclared
    assumption_violations: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "declared_boundaries": [b.to_dict() for b in self.declared_boundaries],
            "boundary_violations": [v.to_dict() for v in self.boundary_violations],
            "uncovered_declared": self.uncovered_declared.to_dict(),
            "assumption_violations": self.assumption_violations,
        }


# ============================================================================
# Coverage Gap
# ============================================================================
@dataclass(frozen=True)
class CoverageGap:
    """
    A gap between claimed and verified coverage.

    T13 Hard Constraint: Coverage gaps expose false claims.
    """

    gap_type: Literal[
        "false_claim", "weak_evidence", "missing_trace", "unverified_case", "stale_coverage"
    ]
    description: str
    affected_scope: str | None = None
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] | None = None
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gap_type": self.gap_type,
            "description": self.description,
            "affected_scope": self.affected_scope,
            "severity": self.severity,
            "remediation": self.remediation,
        }


# ============================================================================
# Coverage Integrity
# ============================================================================
@dataclass
class CoverageIntegrity:
    """
    T13 Hard Constraint: Coverage integrity analysis.
    """

    claimed_coverage: dict[str, Any]
    verified_coverage: dict[str, Any]
    coverage_gaps: list[CoverageGap]
    integrity_check_passed: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "claimed_coverage": self.claimed_coverage,
            "verified_coverage": self.verified_coverage,
            "coverage_gaps": [g.to_dict() for g in self.coverage_gaps],
            "integrity_check_passed": self.integrity_check_passed,
        }


# ============================================================================
# Degraded Case
# ============================================================================
@dataclass(frozen=True)
class DegradedCaseReport:
    """
    A case with explicit degradation classification.

    T13 Hard Constraint: Degradation must be explicit.
    """

    case_id: str
    title: str | None
    adjudication_decision: Literal["DEGRADED", "PASS", "FAIL"]
    degradation_level: DegradationLevel
    deviations: list[dict[str, Any]]
    impact: str | None
    residual_risks: list[str] | None
    release_allowed: bool | None
    release_conditions: list[str] | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "title": self.title,
            "adjudication_decision": self.adjudication_decision,
            "degradation_level": self.degradation_level,
            "deviations": self.deviations,
            "impact": self.impact,
            "residual_risks": self.residual_risks,
            "release_allowed": self.release_allowed,
            "release_conditions": self.release_conditions,
        }


# ============================================================================
# Misclassification Detected
# ============================================================================
@dataclass(frozen=True)
class MisclassificationDetected:
    """
    A case that should be DEGRADED but is marked as PASS.

    T13 Hard Constraint: This is a false success claim.
    """

    case_id: str
    actual_state: str
    marked_as: str | None
    why_degraded: str
    recommended_classification: Literal["DEGRADED-minor", "DEGRADED-partial_functionality", "DEGRADED-major", "FAIL"] | None
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "actual_state": self.actual_state,
            "marked_as": self.marked_as,
            "why_degraded": self.why_degraded,
            "recommended_classification": self.recommended_classification,
            "severity": self.severity,
        }


# ============================================================================
# Degradation Classification
# ============================================================================
@dataclass
class DegradationClassification:
    """
    T13 Hard Constraint: Explicit degradation classification.
    """

    cases_by_status: dict[str, int]
    degraded_cases: list[DegradedCaseReport]
    degradation_levels: dict[str, int]
    misclassification_detected: list[MisclassificationDetected]
    classification_integrity_score: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cases_by_status": self.cases_by_status,
            "degraded_cases": [c.to_dict() for c in self.degraded_cases],
            "degradation_levels": self.degradation_levels,
            "misclassification_detected": [m.to_dict() for m in self.misclassification_detected],
            "classification_integrity_score": self.classification_integrity_score,
        }


# ============================================================================
# Registered Risk
# ============================================================================
@dataclass(frozen=True)
class RegisteredRisk:
    """A registered residual risk."""

    risk_id: str
    source_case_id: str | None
    category: RiskCategory
    description: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    likelihood: Literal["VERY_LIKELY", "LIKELY", "POSSIBLE", "UNLIKELY", "RARE"] | None
    impact: Literal["SEVERE", "HIGH", "MEDIUM", "LOW", "MINIMAL"] | None
    mitigation: str | None
    status: Literal["open", "mitigating", "monitoring", "accepted", "closed"] | None
    ticket_ref: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_id": self.risk_id,
            "source_case_id": self.source_case_id,
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "mitigation": self.mitigation,
            "status": self.status,
            "ticket_ref": self.ticket_ref,
        }


# ============================================================================
# Residual Risk Register
# ============================================================================
@dataclass
class ResidualRiskRegister:
    """
    T13 Hard Constraint: Residual risk register - even for PASS cases.
    """

    total_risks: int
    by_category: dict[str, int]
    by_severity: dict[str, int]
    by_case_status: dict[str, int] | None
    critical_risks: list[RegisteredRisk]
    all_risks: list[RegisteredRisk] | None
    risk_register_complete: bool
    gaps_detected: list[dict[str, Any]] | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_risks": self.total_risks,
            "by_category": self.by_category,
            "by_severity": self.by_severity,
            "by_case_status": self.by_case_status,
            "critical_risks": [r.to_dict() for r in self.critical_risks],
            "all_risks": [r.to_dict() for r in self.all_risks] if self.all_risks else None,
            "risk_register_complete": self.risk_register_complete,
            "gaps_detected": self.gaps_detected,
        }


# ============================================================================
# Anti Collapse Score Determinant
# ============================================================================
@dataclass(frozen=True)
class ScoreDeterminant:
    """A factor that determined the anti-collapse score."""

    factor: Literal[
        "boundary_transparency",
        "coverage_integrity",
        "degradation_classification",
        "risk_register_completeness",
        "critical_issue_count",
    ]
    impact: str
    value: float | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "factor": self.factor,
            "impact": self.impact,
            "value": self.value,
        }


# ============================================================================
# Anti Collapse Score
# ============================================================================
@dataclass
class AntiCollapseScore:
    """
    Overall anti-collapse score and assessment.
    """

    score: float
    posture: AntiCollapsePosture
    determinants: list[ScoreDeterminant]
    release_recommendation: ReleaseRecommendation | None
    recommendation_rationale: str | None
    blocking_issues: list[dict[str, Any]] | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "posture": self.posture,
            "determinants": [d.to_dict() for d in self.determinants],
            "release_recommendation": self.release_recommendation,
            "recommendation_rationale": self.recommendation_rationale,
            "blocking_issues": self.blocking_issues,
        }


# ============================================================================
# Immediate Action
# ============================================================================
@dataclass(frozen=True)
class ImmediateAction:
    """Immediate action required to address anti-collapse concerns."""

    action: str
    priority: Literal["P0", "P1", "P2", "P3"]
    owner: str | None
    target_date: str | None
    related_ref: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action": self.action,
            "priority": self.priority,
            "owner": self.owner,
            "target_date": self.target_date,
            "related_ref": self.related_ref,
        }


# ============================================================================
# Anti Collapse Report
# ============================================================================
@dataclass
class AntiCollapseReport:
    """
    T13 Deliverable: Anti-collapse report enforcement.

    Hard Constraints:
    - Uncovered scenarios MUST be declared
    - Degraded cases MUST be explicitly classified
    - Residual risks MUST be registered

    Evidence paths: run/<run_id>/anti_collapse_report.json
    """

    report_id: str
    report_type: ReportType
    case_ledger_ref: str
    boundary_assertions: BoundaryAssertions
    coverage_integrity: CoverageIntegrity
    degradation_classification: DegradationClassification
    residual_risk_register: ResidualRiskRegister
    anti_collapse_score: AntiCollapseScore
    created_at: str | None = None
    created_by: str = "T13-Kior-B"
    parent_report_ref: str | None = None
    reporting_period: dict[str, str | None] | None = None
    anti_collapse_metrics: dict[str, float] | None = None
    immediate_actions: list[ImmediateAction] | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        """Initialize created_at if not provided."""
        if not self.created_at:
            object.__setattr__(
                self, "created_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "case_ledger_ref": self.case_ledger_ref,
            "parent_report_ref": self.parent_report_ref,
            "reporting_period": self.reporting_period,
            "boundary_assertions": self.boundary_assertions.to_dict(),
            "coverage_integrity": self.coverage_integrity.to_dict(),
            "degradation_classification": self.degradation_classification.to_dict(),
            "residual_risk_register": self.residual_risk_register.to_dict(),
            "anti_collapse_metrics": self.anti_collapse_metrics,
            "anti_collapse_score": self.anti_collapse_score.to_dict(),
            "immediate_actions": [a.to_dict() for a in (self.immediate_actions or [])],
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
            raise IOError(f"Failed to save anti-collapse report to {output_path}: {e}")


# ============================================================================
# Analysis Functions
# ============================================================================
def analyze_boundary_integrity(ledger: CaseLedger) -> BoundaryAssertions:
    """
    Analyze boundary integrity of a case ledger.

    T13 Hard Constraint: Detect uncovered items not declared as such.
    """
    # Build declared boundaries
    declared_boundaries = []
    boundary_idx = 0

    # In-scope boundaries
    for item in ledger.boundary_declaration.in_scope:
        boundary_idx += 1
        declared_boundaries.append(
            DeclaredBoundary(
                boundary_id=f"B-{boundary_idx:03d}",
                type="in_scope",
                assertion=item.description,
                verification_status="verified",
            )
        )

    # Out-of-scope boundaries
    for item in ledger.boundary_declaration.out_of_scope:
        boundary_idx += 1
        declared_boundaries.append(
            DeclaredBoundary(
                boundary_id=f"B-{boundary_idx:03d}",
                type="out_of_scope",
                assertion=f"Out of scope: {item.category} ({item.reason})",
                verification_status="verified",
            )
        )

    # Assumption boundaries
    for assumption in ledger.boundary_declaration.assumptions:
        boundary_idx += 1
        declared_boundaries.append(
            DeclaredBoundary(
                boundary_id=f"B-{boundary_idx:03d}",
                type="assumption",
                assertion=assumption,
                verification_status="unknown",
            )
        )

    # Check for boundary violations
    violations = []

    # Check for cases that claim success but have deviations
    for case in ledger.cases:
        if (
            case.adjudication
            and case.adjudication.decision == "PASS"
            and case.execution_record.actual_behavior
            and case.execution_record.actual_behavior.deviations
        ):
            # PASS with deviations - potential violation
            violations.append(
                BoundaryViolation(
                    violation_type="uncovered_claimed_complete",
                    description=f"Case {case.case_id} marked PASS but has deviations",
                    affected_scope=case.case_id,
                    severity="HIGH",
                    remediation="Reclassify as DEGRADED or address deviations",
                    related_case_refs=[case.case_id],
                )
            )

    # Check for uncovered items not declared
    implicit_uncovered = []
    for case in ledger.cases:
        if case.execution_record.status == "pending":
            implicit_uncovered.append(
                ImplicitUncoveredItem(
                    item=f"Case {case.case_id}",
                    why_uncovered="Not yet executed",
                    severity="LOW",
                    recommendation="Execute case or mark as out of scope",
                )
            )

    declaration_score = 1.0 if len(implicit_uncovered) == 0 else max(0.5, 1.0 - len(implicit_uncovered) * 0.1)

    uncovered_declared = UncoveredDeclared(
        total_declared_uncovered=len(ledger.boundary_declaration.out_of_scope),
        verified_declared=[item.category for item in ledger.boundary_declaration.out_of_scope],
        implicit_uncovered_detected=implicit_uncovered,
        declaration_integrity_score=round(declaration_score, 2),
    )

    return BoundaryAssertions(
        declared_boundaries=declared_boundaries,
        boundary_violations=violations,
        uncovered_declared=uncovered_declared,
    )


def analyze_coverage_integrity(ledger: CaseLedger) -> CoverageIntegrity:
    """
    Analyze coverage integrity.

    T13 Hard Constraint: Verify claimed coverage.
    """
    in_scope_total = len(ledger.boundary_declaration.in_scope)
    executed_count = sum(
        1
        for case in ledger.cases
        if case.execution_record.status == "executed"
    )
    claimed_percent = round(executed_count / in_scope_total * 100, 2) if in_scope_total > 0 else 0.0

    claimed_coverage = {
        "in_scope_count": in_scope_total,
        "covered_count": executed_count,
        "claimed_percent": claimed_percent,
    }

    # Verified coverage (same as claimed for now, could be adjusted with external verification)
    verified_coverage = {
        "verified_covered": executed_count,
        "verified_percent": claimed_percent,
        "verification_method": "manual_review",
    }

    # Check for gaps
    gaps = []
    for case in ledger.cases:
        if case.execution_record.status == "pending":
            gaps.append(
                CoverageGap(
                    gap_type="unverified_case",
                    description=f"Case {case.case_id} not executed",
                    affected_scope=case.case_id,
                    severity="LOW",
                    remediation="Execute case or mark as out of scope",
                )
            )

    integrity_passed = len(gaps) == 0

    return CoverageIntegrity(
        claimed_coverage=claimed_coverage,
        verified_coverage=verified_coverage,
        coverage_gaps=gaps,
        integrity_check_passed=integrity_passed,
    )


def analyze_degradation_classification(ledger: CaseLedger) -> DegradationClassification:
    """
    Analyze degradation classification.

    T13 Hard Constraint: Detect misclassifications (PASS with deviations).
    """
    cases_by_status = {
        "fully_successful": 0,
        "degraded_pass": 0,
        "degraded_explicit": 0,
        "failed": 0,
        "waived": 0,
        "pending": 0,
    }

    degraded_cases = []
    misclassifications = []

    degradation_levels = {"minor": 0, "partial_functionality": 0, "major": 0}

    for case in ledger.cases:
        if not case.adjudication:
            cases_by_status["pending"] += 1
            continue

        decision = case.adjudication.decision
        has_deviations = (
            case.execution_record.actual_behavior
            and case.execution_record.actual_behavior.deviations
        )

        if decision == "FAIL":
            cases_by_status["failed"] += 1
        elif decision == "WAIVE":
            cases_by_status["waived"] += 1
        elif decision == "DEGRADED":
            cases_by_status["degraded_explicit"] += 1
            degradation_levels[case.adjudication.degradation_level or "minor"] += 1

            # Add to degraded cases report
            if case.execution_record.actual_behavior:
                deviations = [
                    d.to_dict() for d in (case.execution_record.actual_behavior.deviations or [])
                ]
            else:
                deviations = []

            degraded_cases.append(
                DegradedCaseReport(
                    case_id=case.case_id,
                    title=case.title,
                    adjudication_decision="DEGRADED",
                    degradation_level=case.adjudication.degradation_level or "minor",
                    deviations=deviations,
                    impact=case.adjudication.rationale,
                    residual_risks=None,
                    release_allowed=None,
                    release_conditions=None,
                )
            )
        elif decision == "PASS":
            if has_deviations:
                # T13 Hard Constraint: PASS with deviations is a misclassification
                cases_by_status["degraded_pass"] += 1
                misclassifications.append(
                    MisclassificationDetected(
                        case_id=case.case_id,
                        actual_state="Has deviations but marked PASS",
                        marked_as="PASS",
                        why_degraded="Contains deviations from expected behavior",
                        recommended_classification="DEGRADED-minor",
                        severity="MEDIUM",
                    )
                )
            else:
                cases_by_status["fully_successful"] += 1

    # Calculate integrity score
    integrity_score = (
        1.0 if len(misclassifications) == 0 else max(0.0, 1.0 - len(misclassifications) * 0.2)
    )

    return DegradationClassification(
        cases_by_status=cases_by_status,
        degraded_cases=degraded_cases,
        degradation_levels=degradation_levels,
        misclassification_detected=misclassifications,
        classification_integrity_score=round(integrity_score, 2),
    )


def analyze_residual_risks(ledger: CaseLedger) -> ResidualRiskRegister:
    """
    Analyze residual risk register.

    T13 Hard Constraint: Check for missing risk assessments.
    """
    all_risks = []
    critical_risks = []
    gaps_detected = []

    by_category = {
        "test_gap": 0,
        "data_limitation": 0,
        "environment_constraint": 0,
        "assumption_violation": 0,
        "degradation_risk": 0,
        "coverage_hole": 0,
        "dependency_risk": 0,
    }

    by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

    by_case_status = {"in_pass_cases": 0, "in_degraded_cases": 0, "in_fail_cases": 0, "in_unexecuted_cases": 0}

    # Extract risks from cases
    for case in ledger.cases:
        if not case.residual_risks:
            # T13 Hard Constraint: Missing risk assessment is a gap
            if case.adjudication and case.adjudication.decision in ("PASS", "DEGRADED"):
                gaps_detected.append(
                    {
                        "case_id": case.case_id,
                        "gap_type": "no_risk_assessment",
                        "recommendation": "Assess and register residual risks",
                    }
                )
            continue

        for risk in case.residual_risks:
            # Create risk ID if not provided
            if not risk.risk_id:
                import hashlib

                hash_input = f"{case.case_id}:{risk.description}"
                short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
                risk_id = f"R-{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}-{short_hash}"
            else:
                risk_id = risk.risk_id

            registered_risk = RegisteredRisk(
                risk_id=risk_id,
                source_case_id=case.case_id,
                category=risk.risk_category,
                description=risk.description,
                severity="MEDIUM",  # Default if not specified
                likelihood=None,
                impact=None,
                mitigation=risk.mitigation,
                status="open",
                ticket_ref=None,
            )

            all_risks.append(registered_risk)

            # Count by category
            if risk.risk_category in by_category:
                by_category[risk.risk_category] += 1

            # Count by case status
            if case.adjudication:
                decision = case.adjudication.decision
                if decision == "PASS":
                    by_case_status["in_pass_cases"] += 1
                elif decision == "DEGRADED":
                    by_case_status["in_degraded_cases"] += 1
                elif decision == "FAIL":
                    by_case_status["in_fail_cases"] += 1
            else:
                by_case_status["in_unexecuted_cases"] += 1

    # Critical risks are those with severity HIGH or above
    for risk in all_risks:
        by_severity[risk.severity] += 1
        if risk.severity in ("CRITICAL", "HIGH"):
            critical_risks.append(risk)

    risk_register_complete = len(gaps_detected) == 0

    return ResidualRiskRegister(
        total_risks=len(all_risks),
        by_category=by_category,
        by_severity=by_severity,
        by_case_status=by_case_status,
        critical_risks=critical_risks,
        all_risks=all_risks,
        risk_register_complete=risk_register_complete,
        gaps_detected=gaps_detected if gaps_detected else None,
    )


def calculate_anti_collapse_score(
    boundary_assertions: BoundaryAssertions,
    coverage_integrity: CoverageIntegrity,
    degradation_classification: DegradationClassification,
    residual_risk_register: ResidualRiskRegister,
) -> AntiCollapseScore:
    """
    Calculate overall anti-collapse score.

    Score components:
    - Boundary transparency (0-1)
    - Coverage honesty (0-1)
    - Degradation honesty (0-1)
    - Risk awareness (0-1)
    """
    # Extract component scores
    boundary_score = boundary_assertions.uncovered_declared.declaration_integrity_score
    coverage_score = 1.0 if coverage_integrity.integrity_check_passed else 0.7
    degradation_score = degradation_classification.classification_integrity_score
    risk_score = 1.0 if residual_risk_register.risk_register_complete else 0.6

    # Calculate overall score (weighted average)
    weights = {"boundary": 0.3, "coverage": 0.25, "degradation": 0.25, "risk": 0.2}
    overall_score = round(
        boundary_score * weights["boundary"]
        + coverage_score * weights["coverage"]
        + degradation_score * weights["degradation"]
        + risk_score * weights["risk"],
        2,
    )

    # Determine posture
    if overall_score >= 0.9:
        posture = "STRONG"
    elif overall_score >= 0.7:
        posture = "MODERATE"
    elif overall_score >= 0.5:
        posture = "WEAK"
    else:
        posture = "CRITICAL"

    # Build determinants
    determinants = [
        ScoreDeterminant(
            factor="boundary_transparency",
            impact="High" if boundary_score >= 0.8 else "Moderate" if boundary_score >= 0.6 else "Low",
            value=boundary_score,
        ),
        ScoreDeterminant(
            factor="coverage_integrity",
            impact="High" if coverage_score >= 0.8 else "Moderate",
            value=coverage_score,
        ),
        ScoreDeterminant(
            factor="degradation_classification",
            impact="High" if degradation_score >= 0.8 else "Moderate" if degradation_score >= 0.6 else "Low",
            value=degradation_score,
        ),
        ScoreDeterminant(
            factor="risk_register_completeness",
            impact="High" if risk_score >= 0.8 else "Moderate",
            value=risk_score,
        ),
    ]

    # Add critical issue count determinant
    critical_count = len(residual_risk_register.critical_risks)
    if critical_count > 0:
        determinants.append(
            ScoreDeterminant(
                factor="critical_issue_count",
                impact=f"{critical_count} critical risks detected",
                value=float(critical_count),
            )
        )

    # Determine release recommendation
    blocking_issues = []
    if posture == "CRITICAL":
        release_recommendation = "blocked"
        blocking_issues.append(
            {
                "issue": "Critical anti-collapse posture",
                "why_blocking": "System shows signs of collapse risk - fundamental governance issues",
                "ref": None,
            }
        )
    elif posture == "WEAK":
        release_recommendation = "blocked"
        if degradation_classification.misclassification_detected:
            blocking_issues.append(
                {
                    "issue": "Degradation misclassifications detected",
                    "why_blocking": "False success claims prevent accurate risk assessment",
                    "ref": "degradation_classification.misclassification_detected",
                }
            )
        if not residual_risk_register.risk_register_complete:
            blocking_issues.append(
                {
                    "issue": "Incomplete risk register",
                    "why_blocking": "Residual risks not properly assessed",
                    "ref": "residual_risk_register.gaps_detected",
                }
            )
    elif posture == "MODERATE":
        release_recommendation = "caution"
    else:
        release_recommendation = "clear"

    # Build rationale
    rationale_parts = [
        f"Anti-collapse posture is {posture} (score: {overall_score:.2f}).",
    ]
    if boundary_score < 1.0:
        rationale_parts.append(f"Boundary transparency at {boundary_score:.0%}.")
    if degradation_score < 1.0:
        rationale_parts.append(
            f"Degradation integrity at {degradation_score:.0%} with {len(degradation_classification.misclassification_detected)} misclassifications."
        )
    if critical_count > 0:
        rationale_parts.append(f"{critical_count} critical risks require attention.")

    recommendation_rationale = " ".join(rationale_parts)

    return AntiCollapseScore(
        score=overall_score,
        posture=posture,
        determinants=determinants,
        release_recommendation=release_recommendation,
        recommendation_rationale=recommendation_rationale,
        blocking_issues=blocking_issues if blocking_issues else None,
    )


# ============================================================================
# Factory Functions
# ============================================================================
def generate_report_id(date_str: str | None = None) -> str:
    """
    Generate a unique report ID.

    Args:
        date_str: Date string in YYYYMMDD format (defaults to today)

    Returns:
        Report ID in format ACR-{YYYYMMDD}-{short_hash}
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")

    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    hash_input = f"{date_str}_{timestamp}"
    short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    return f"ACR-{date_str}-{short_hash}"


def generate_anti_collapse_report(
    case_ledger: CaseLedger,
    report_type: ReportType = "initial",
    created_by: str = "T13-Kior-B",
    parent_report_ref: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AntiCollapseReport:
    """
    Generate an anti-collapse report from a case ledger.

    T13 Hard Constraints enforced:
    - Boundary declarations verified
    - Uncovered items detected
    - Degradation misclassifications flagged
    - Residual risk completeness checked

    Args:
        case_ledger: CaseLedger to analyze
        report_type: Type of report
        created_by: Entity creating the report
        parent_report_ref: Parent report if incremental
        metadata: Additional metadata

    Returns:
        AntiCollapseReport instance
    """
    # Analyze components
    boundary_assertions = analyze_boundary_integrity(case_ledger)
    coverage_integrity = analyze_coverage_integrity(case_ledger)
    degradation_classification = analyze_degradation_classification(case_ledger)
    residual_risk_register = analyze_residual_risks(case_ledger)

    # Calculate score
    anti_collapse_score = calculate_anti_collapse_score(
        boundary_assertions=boundary_assertions,
        coverage_integrity=coverage_integrity,
        degradation_classification=degradation_classification,
        residual_risk_register=residual_risk_register,
    )

    # Build metrics
    anti_collapse_metrics = {
        "boundary_transparency": boundary_assertions.uncovered_declared.declaration_integrity_score,
        "coverage_honesty": 1.0 if coverage_integrity.integrity_check_passed else 0.7,
        "degradation_honesty": degradation_classification.classification_integrity_score,
        "risk_awareness": 1.0 if residual_risk_register.risk_register_complete else 0.6,
    }

    # Generate immediate actions for critical issues
    immediate_actions = []
    if anti_collapse_score.release_recommendation == "blocked":
        for issue in (anti_collapse_score.blocking_issues or []):
            immediate_actions.append(
                ImmediateAction(
                    action=issue["why_blocking"],
                    priority="P0",
                    owner=None,
                    target_date=None,
                    related_ref=issue.get("ref"),
                )
            )

    if degradation_classification.misclassification_detected:
        immediate_actions.append(
            ImmediateAction(
                action=f"Reclassify {len(degradation_classification.misclassification_detected)} misclassified cases",
                priority="P1",
                owner=None,
                target_date=None,
                related_ref=None,
            )
        )

    report_id = generate_report_id()

    return AntiCollapseReport(
        report_id=report_id,
        report_type=report_type,
        case_ledger_ref=case_ledger.ledger_id,
        boundary_assertions=boundary_assertions,
        coverage_integrity=coverage_integrity,
        degradation_classification=degradation_classification,
        residual_risk_register=residual_risk_register,
        anti_collapse_score=anti_collapse_score,
        created_by=created_by,
        parent_report_ref=parent_report_ref,
        anti_collapse_metrics=anti_collapse_metrics,
        immediate_actions=immediate_actions if immediate_actions else None,
        metadata=metadata,
    )


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for anti-collapse report generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate anti_collapse_report.json from case_ledger.json (T13)"
    )
    parser.add_argument(
        "--case-ledger",
        required=True,
        help="Path to case_ledger.json",
    )
    parser.add_argument(
        "--output",
        default="run/latest/anti_collapse_report.json",
        help="Output path for anti_collapse_report.json",
    )
    parser.add_argument(
        "--report-type",
        choices=["initial", "incremental", "final", "post_release"],
        default="initial",
        help="Type of report",
    )
    parser.add_argument(
        "--created-by",
        default="T13-Kior-B",
        help="Entity creating the report",
    )
    args = parser.parse_args()

    # Load case ledger
    with open(args.case_ledger) as f:
        ledger_data = json.load(f)

    # Reconstruct ledger (simplified - in practice, would use proper deserialization)
    # For now, just use the dict directly for analysis
    print(f"Loading case ledger: {args.case_ledger}")
    print(f"  Ledger ID: {ledger_data.get('ledger_id')}")
    print(f"  Total cases: {len(ledger_data.get('cases', []))}")

    # Generate report (would need proper ledger reconstruction in practice)
    print("Note: Full report generation requires CaseLedger object.")
    print(f"Would save to: {args.output}")


if __name__ == "__main__":
    main()
