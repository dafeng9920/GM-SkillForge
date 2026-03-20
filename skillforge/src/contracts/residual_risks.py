"""
Residual Risks - T10 deliverable: Residual risk records.

This module provides structures for documenting risks that remain after mitigation
or override, with tracking and remediation requirements.

Usage:
    from skillforge.src.contracts.residual_risks import (
        ResidualRisk,
        ResidualRisks,
        MitigationStrategy,
        RiskStatus
    )
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional


# ============================================================================
# Error Codes (E0xx series for T10)
# ============================================================================
class ResidualRiskErrorCode:
    """Error codes for residual risk validation."""
    RISK_WITHOUT_OVERRIDE = "E011_RISK_WITHOUT_OVERRIDE"
    CRITICAL_RISK_UNACCEPTED = "E012_CRITICAL_RISK_UNACCEPTED"
    INVALID_STATUS = "E013_INVALID_STATUS"


# ============================================================================
# Enums (Structured decisions - NO free-form text)
# ============================================================================
class RiskLevel(Enum):
    """Residual risk level after mitigation/override."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskCategory(Enum):
    """Categories of residual risks."""
    SECURITY = "security"
    CORRECTNESS = "correctness"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COMPLIANCE = "compliance"
    DATA_QUALITY = "data_quality"
    ACCESS_CONTROL = "access_control"
    SUPPLY_CHAIN = "supply_chain"


class Likelihood(Enum):
    """Likelihood of the risk materializing."""
    VERY_LIKELY = "VERY_LIKELY"
    LIKELY = "LIKELY"
    POSSIBLE = "POSSIBLE"
    UNLIKELY = "UNLIKELY"
    RARE = "RARE"


class Impact(Enum):
    """Impact if the risk materializes."""
    SEVERE = "SEVERE"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class RiskStatus(Enum):
    """Current status of the risk."""
    OPEN = "open"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class MitigationStrategy(Enum):
    """Strategy for dealing with a risk."""
    AVOID = "avoid"
    TRANSFER = "transfer"
    MITIGATE = "mitigate"
    ACCEPT = "accept"
    MONITOR = "monitor"


class ReviewFrequency(Enum):
    """How often to review an accepted risk."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


# ============================================================================
# Data Structures
# ============================================================================
@dataclass(frozen=True)
class EvidenceRef:
    """Evidence reference for risk assessment."""
    kind: Literal["FILE", "LOG", "ANALYSIS", "TICKET", "DOCUMENTATION", "METRIC"]
    locator: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "locator": self.locator,
            "note": self.note,
        }


@dataclass
class MitigationAction:
    """A mitigation action."""
    action: str
    owner: str
    target_date: str | None = None
    status: Literal["pending", "in_progress", "completed", "blocked"] = "pending"

    def to_dict(self) -> dict[str, Any]:
        result = {
            "action": self.action,
            "owner": self.owner,
            "status": self.status,
        }
        if self.target_date:
            result["target_date"] = self.target_date
        return result


@dataclass
class MitigationPlan:
    """Mitigation plan details."""
    actions: list[MitigationAction] = field(default_factory=list)
    estimated_completion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "actions": [a.to_dict() for a in self.actions],
        }
        if self.estimated_completion:
            result["estimated_completion"] = self.estimated_completion
        return result


@dataclass
class MonitoringPlan:
    """Monitoring plan for accepted risks."""
    metrics: list[str] = field(default_factory=list)
    review_frequency: ReviewFrequency = ReviewFrequency.WEEKLY
    escalation_threshold: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "metrics": self.metrics,
            "review_frequency": self.review_frequency.value,
        }
        if self.escalation_threshold:
            result["escalation_threshold"] = self.escalation_threshold
        return result


@dataclass
class AcceptanceDetails:
    """Details for accepted risks."""
    accepted_by: str
    accepted_at: str
    review_date: str | None = None
    justification: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = {
            "accepted_by": self.accepted_by,
            "accepted_at": self.accepted_at,
            "justification": self.justification,
        }
        if self.review_date:
            result["review_date"] = self.review_date
        return result


@dataclass
class ResidualRisk:
    """
    A single residual risk record.

    Created when a judgment override leaves residual risk that must be tracked.
    """
    risk_id: str
    source_finding_id: str
    source_override_id: str
    risk_level: RiskLevel
    risk_category: RiskCategory
    likelihood: Likelihood
    impact: Impact
    status: RiskStatus
    created_at: str
    title: str | None = None
    description: str = ""
    original_severity: str | None = None
    calculated_score: float | None = None
    mitigation_strategy: MitigationStrategy | None = None
    mitigation_plan: MitigationPlan | None = None
    monitoring_plan: MonitoringPlan | None = None
    acceptance_details: AcceptanceDetails | None = None
    related_ticket: str | None = None
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    updated_at: str | None = None
    closed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "risk_id": self.risk_id,
            "source_finding_id": self.source_finding_id,
            "source_override_id": self.source_override_id,
            "title": self.title,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "original_severity": self.original_severity,
            "risk_category": self.risk_category.value,
            "likelihood": self.likelihood.value,
            "impact": self.impact.value,
            "calculated_score": self.calculated_score,
            "status": self.status.value,
            "mitigation_strategy": self.mitigation_strategy.value if self.mitigation_strategy else None,
            "mitigation_plan": self.mitigation_plan.to_dict() if self.mitigation_plan else None,
            "monitoring_plan": self.monitoring_plan.to_dict() if self.monitoring_plan else None,
            "acceptance_details": self.acceptance_details.to_dict() if self.acceptance_details else None,
            "related_ticket": self.related_ticket,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "closed_at": self.closed_at,
        }
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class ResidualRisks:
    """Container for residual risk records."""
    run_id: str
    created_at: str
    t10_version: str = "1.0.0-t10"
    assessment_methodology: Literal["qualitative", "semi_quantitative", "quantitative"] = "semi_quantitative"
    risks: list[ResidualRisk] = field(default_factory=list)

    def add_risk(self, risk: ResidualRisk) -> None:
        """Add a risk record."""
        self.risks.append(risk)

    def compute_summary(self) -> dict[str, Any]:
        """Compute summary statistics."""
        by_level = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        by_status = {"open": 0, "mitigating": 0, "monitoring": 0, "accepted": 0, "closed": 0}
        with_mitigation = 0
        with_monitoring = 0
        accepted_without_mitigation = 0

        for risk in self.risks:
            by_level[risk.risk_level.value] = by_level.get(risk.risk_level.value, 0) + 1
            by_status[risk.status.value] = by_status.get(risk.status.value, 0) + 1

            if risk.mitigation_plan and risk.mitigation_plan.actions:
                with_mitigation += 1
            if risk.monitoring_plan:
                with_monitoring += 1
            if risk.status == RiskStatus.ACCEPTED and not risk.mitigation_plan:
                accepted_without_mitigation += 1

        return {
            "total_risks": len(self.risks),
            "by_level": by_level,
            "by_status": by_status,
            "mitigation_coverage": {
                "with_mitigation": with_mitigation,
                "with_monitoring": with_monitoring,
                "accepted_without_mitigation": accepted_without_mitigation,
            },
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "meta": {
                "run_id": self.run_id,
                "created_at": self.created_at,
                "t10_version": self.t10_version,
                "assessment_methodology": self.assessment_methodology,
            },
            "risks": [r.to_dict() for r in self.risks],
            "summary": self.compute_summary(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


# ============================================================================
# Factory Functions
# ============================================================================
def create_risk_id(run_id: str, seq: int) -> str:
    """Create a unique risk ID."""
    return f"R-{run_id}-{seq}"


def calculate_risk_score(likelihood: Likelihood, impact: Impact) -> float:
    """Calculate risk score (1-5 scale for likelihood x impact)."""
    likelihood_score = {
        Likelihood.VERY_LIKELY: 5,
        Likelihood.LIKELY: 4,
        Likelihood.POSSIBLE: 3,
        Likelihood.UNLIKELY: 2,
        Likelihood.RARE: 1,
    }
    impact_score = {
        Impact.SEVERE: 5,
        Impact.HIGH: 4,
        Impact.MEDIUM: 3,
        Impact.LOW: 2,
        Impact.MINIMAL: 1,
    }
    return likelihood_score[likelihood] * impact_score[impact]


def create_residual_risks(
    run_id: str,
    assessment_methodology: Literal["qualitative", "semi_quantitative", "quantitative"] = "semi_quantitative",
) -> ResidualRisks:
    """Create a new ResidualRisks container."""
    return ResidualRisks(
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        assessment_methodology=assessment_methodology,
    )


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for residual risk operations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Work with residual risk records"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Calculate score command
    score_parser = subparsers.add_parser("score", help="Calculate risk score")
    score_parser.add_argument("--likelihood", required=True, choices=[l.value for l in Likelihood])
    score_parser.add_argument("--impact", required=True, choices=[i.value for i in Impact])

    args = parser.parse_args()

    if args.command == "score":
        likelihood = Likelihood(args.likelihood)
        impact = Impact(args.impact)
        score = calculate_risk_score(likelihood, impact)
        print(f"Risk Score: {score}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
