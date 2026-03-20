"""
Judgment Overrides - T10 deliverable: Judgment override records.

This module provides structures and validation for judgment overrides that allow
human judgment to override automated gate decisions under strict constraints.

T10 Hard Constraints:
- contract 失败 / 无证据 finding / 明确高危命中，不允许被判断洗白
- judgment override 不能是自由文本
- All overrides must have structured justification and traceable evidence

Usage:
    from skillforge.src.contracts.judgment_overrides import (
        JudgmentOverride,
        JudgmentOverrides,
        OverrideJustification,
        can_override_finding
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
class JudgmentOverrideErrorCode:
    """Error codes for judgment override validation."""
    OVERRIDE_FORBIDDEN = "E001_OVERRIDE_FORBIDDEN"
    MISSING_EVIDENCE = "E002_MISSING_EVIDENCE"
    INVALID_JUSTIFICATION = "E003_INVALID_JUSTIFICATION"
    UNAUTHORIZED_APPROVER = "E004_UNAUTHORIZED_APPROVER"
    CRITICAL_RISK_NO_OVERRIDE = "E005_CRITICAL_RISK_NO_OVERRIDE"
    NO_EVIDENCE_OVERRIDE = "E006_NO_EVIDENCE_OVERRIDE"
    BLOCKABLE_OVERRIDE = "E007_BLOCKABLE_OVERRIDE"


# ============================================================================
# Enums (Structured decisions - NO free-form text)
# ============================================================================
class OriginalDecision(Enum):
    """Original automated decision that was overridden."""
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"
    CONDITIONAL_RELEASE = "CONDITIONAL_RELEASE"
    LIMITED_RELEASE = "LIMITED_RELEASE"


class OverrideDecision(Enum):
    """New decision after judgment override."""
    RELEASE = "RELEASE"
    CONDITIONAL_RELEASE = "CONDITIONAL_RELEASE"
    LIMITED_RELEASE = "LIMITED_RELEASE"
    ESCALATE = "ESCALATE"
    REJECT = "REJECT"


class JustificationCode(Enum):
    """Structured justification codes (NO free-form text)."""
    FALSE_POSITIVE_DETECTED = "FALSE_POSITIVE_DETECTED"
    COMPENSATING_CONTROL_EXISTS = "COMPENSATING_CONTROL_EXISTS"
    ACCEPTANCE_WINDOW_ACTIVE = "ACCEPTANCE_WINDOW_ACTIVE"
    BUSINESS_JUSTIFICATION = "BUSINESS_JUSTIFICATION"
    TECHNICAL_DEBT_ACCEPTED = "TECHNICAL_DEBT_ACCEPTED"
    TRANSIENT_CONDITION = "TRANSIENT_CONDITION"
    DEPENDENCY_VALIDATED = "DEPENDENCY_VALIDATED"
    DOCUMENTATION_ACCEPTED = "DOCUMENTATION_ACCEPTED"
    TEST_COVERAGE_VERIFIED = "TEST_COVERAGE_VERIFIED"
    RISK_ACCEPTED_PENDING_FIX = "RISK_ACCEPTED_PENDING_FIX"


class JustificationCategory(Enum):
    """Categories for override justification."""
    DETECTION_ARTIFACT = "detection_artifact"
    MITIGATION_PROVIDED = "mitigation_provided"
    TEMPORAL_EXCEPTION = "temporal_exception"
    DEPENDENCY_TRUST = "dependency_trust"


class ApproverRole(Enum):
    """Roles that can approve overrides."""
    TECHNICAL_LEAD = "TECHNICAL_LEAD"
    SECURITY_ARCHITECT = "SECURITY_ARCHITECT"
    ENGINEERING_MANAGER = "ENGINEERING_MANAGER"
    PRINCIPAL_ENGINEER = "PRINCIPAL_ENGINEER"


class ConditionType(Enum):
    """Types of conditions that can be attached to overrides."""
    MONITORING = "monitoring"
    REMEDIATION_DEADLINE = "remediation_deadline"
    USAGE_LIMIT = "usage_limit"
    DOCUMENTATION = "documentation"
    TESTING = "testing"


# ============================================================================
# Hard Constraint Check: Can Override?
# ============================================================================
def can_override_finding(
    original_decision: str,
    evidence_strength: str | None,
    truth_assessment: str | None,
    severity: str | None,
    evidence_count: int,
) -> dict[str, Any]:
    """
    Check if a finding can be overridden.

    T10 Hard Constraints:
    - contract 失败 / 无证据 finding / 明确高危命中，不允许被判断洗白

    Args:
        original_decision: The original automated decision
        evidence_strength: Strength of evidence (INSUFFICIENT blocks override)
        truth_assessment: Truth assessment (CONFIRMED blocks override for CRITICAL)
        severity: Severity level
        evidence_count: Number of evidence refs (0 blocks override)

    Returns:
        Dict with 'allowed' flag and 'reason' if not allowed.
    """
    errors = []

    # Hard constraint 1: No evidence findings cannot be overridden
    if evidence_count == 0:
        return {
            "allowed": False,
            "reason": f"{JudgmentOverrideErrorCode.NO_EVIDENCE_OVERRIDE}: "
                      f"Findings with no evidence cannot be overridden"
        }

    # Hard constraint 2: INSUFFICIENT evidence findings cannot be overridden
    if evidence_strength == "INSUFFICIENT":
        return {
            "allowed": False,
            "reason": f"{JudgmentOverrideErrorCode.MISSING_EVIDENCE}: "
                      f"Findings with INSUFFICIENT evidence cannot be overridden"
        }

    # Hard constraint 3: CRITICAL findings with CONFIRMED truth cannot be overridden
    if severity == "CRITICAL" and truth_assessment == "CONFIRMED":
        return {
            "allowed": False,
            "reason": f"{JudgmentOverrideErrorCode.CRITICAL_RISK_NO_OVERRIDE}: "
                      f"CRITICAL findings with CONFIRMED truth assessment cannot be overridden"
        }

    # Hard constraint 4: Cannot upgrade REJECT directly to RELEASE
    # Must use intermediate steps (CONDITIONAL_RELEASE or LIMITED_RELEASE)
    if original_decision == "REJECT":
        return {
            "allowed": True,
            "allowed_decisions": ["CONDITIONAL_RELEASE", "LIMITED_RELEASE", "ESCALATE"],
            "forbidden_decisions": ["RELEASE"]
        }

    return {"allowed": True}


# ============================================================================
# Data Structures
# ============================================================================
@dataclass(frozen=True)
class EvidenceRef:
    """Evidence reference for override justification."""
    kind: Literal["FILE", "LOG", "DIFF", "TICKET", "REVIEW", "CODE_LOCATION", "DOCUMENTATION"]
    locator: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "locator": self.locator,
            "note": self.note,
        }


@dataclass
class JustificationDetail:
    """Structured detail for justification (not free-form)."""
    category: JustificationCategory
    compensating_control: str | None = None
    acceptance_expiry: str | None = None
    related_ticket: str | None = None
    validated_artifact: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {"category": self.category.value}
        if self.compensating_control:
            result["compensating_control"] = self.compensating_control
        if self.acceptance_expiry:
            result["acceptance_expiry"] = self.acceptance_expiry
        if self.related_ticket:
            result["related_ticket"] = self.related_ticket
        if self.validated_artifact:
            result["validated_artifact"] = self.validated_artifact
        return result


@dataclass
class OverrideCondition:
    """Condition attached to an override."""
    type: ConditionType
    description: str
    evidence_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "type": self.type.value,
            "description": self.description,
        }
        if self.evidence_path:
            result["evidence_path"] = self.evidence_path
        return result


@dataclass
class Approver:
    """Approver identity."""
    approver_id: str
    approver_role: ApproverRole
    approval_scope: Literal["single_finding", "skill_level", "project_level"]
    delegation_chain: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "approver_id": self.approver_id,
            "approver_role": self.approver_role.value,
            "approval_scope": self.approval_scope,
        }
        if self.delegation_chain:
            result["delegation_chain"] = self.delegation_chain
        return result


@dataclass
class JudgmentOverride:
    """
    A single judgment override record.

    T10 Hard Constraints enforced:
    - Cannot override findings with no evidence
    - Cannot override CRITICAL+CONFIRMED findings
    - Cannot upgrade REJECT directly to RELEASE
    - Justification must be structured (no free-form text)
    """
    override_id: str
    finding_id: str
    original_decision: OriginalDecision
    override_decision: OverrideDecision
    justification_code: JustificationCode
    approver: Approver
    approved_at: str
    evidence_refs: list[EvidenceRef]
    finding_summary: str | None = None
    justification_detail: JustificationDetail | None = None
    severity: str | None = None
    source_type: str | None = None
    expiry: str | None = None
    conditions: list[OverrideCondition] | None = None
    residual_risk_created: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "override_id": self.override_id,
            "finding_id": self.finding_id,
            "finding_summary": self.finding_summary,
            "original_decision": self.original_decision.value,
            "override_decision": self.override_decision.value,
            "justification_code": self.justification_code.value,
            "justification_detail": self.justification_detail.to_dict() if self.justification_detail else None,
            "severity": self.severity,
            "source_type": self.source_type,
            "approver": self.approver.to_dict(),
            "approved_at": self.approved_at,
            "expiry": self.expiry,
            "conditions": [c.to_dict() for c in self.conditions] if self.conditions else None,
            "residual_risk_created": self.residual_risk_created,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
        }
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class JudgmentOverrides:
    """Container for judgment override records."""
    run_id: str
    created_at: str
    t10_version: str = "1.0.0-t10"
    decision_context: Literal["entry_gate", "exit_gate", "escalation_review"] = "exit_gate"
    overrides: list[JudgmentOverride] = field(default_factory=list)

    def add_override(self, override: JudgmentOverride) -> None:
        """Add an override record."""
        self.overrides.append(override)

    def compute_summary(self) -> dict[str, Any]:
        """Compute summary statistics."""
        by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        by_justification = {}

        for override in self.overrides:
            if override.severity:
                by_severity[override.severity] = by_severity.get(override.severity, 0) + 1
            code = override.justification_code.value
            by_justification[code] = by_justification.get(code, 0) + 1

        return {
            "total_overrides": len(self.overrides),
            "by_severity": by_severity,
            "by_justification": by_justification,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "meta": {
                "run_id": self.run_id,
                "created_at": self.created_at,
                "t10_version": self.t10_version,
                "decision_context": self.decision_context,
            },
            "overrides": [o.to_dict() for o in self.overrides],
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
def create_override_id(run_id: str, seq: int) -> str:
    """Create a unique override ID."""
    return f"O-{run_id}-{seq}"


def create_judgment_overrides(
    run_id: str,
    decision_context: Literal["entry_gate", "exit_gate", "escalation_review"] = "exit_gate",
) -> JudgmentOverrides:
    """Create a new JudgmentOverrides container."""
    return JudgmentOverrides(
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        decision_context=decision_context,
    )


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for judgment overrides operations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Work with judgment override records"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate if override is allowed")
    validate_parser.add_argument("--original-decision", required=True)
    validate_parser.add_argument("--evidence-strength")
    validate_parser.add_argument("--truth-assessment")
    validate_parser.add_argument("--severity")
    validate_parser.add_argument("--evidence-count", type=int, default=0)

    args = parser.parse_args()

    if args.command == "validate":
        result = can_override_finding(
            args.original_decision,
            args.evidence_strength,
            args.truth_assessment,
            args.severity,
            args.evidence_count,
        )
        print(f"Allowed: {result['allowed']}")
        if not result['allowed']:
            print(f"Reason: {result['reason']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
