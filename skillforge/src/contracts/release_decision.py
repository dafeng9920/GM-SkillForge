"""
Release Decision - T10 deliverable: Final release decision with evidence binding.

This module provides structures for the final release decision that integrates
findings, overrides, and residual risks into a gate decision.

Usage:
    from skillforge.src.contracts.release_decision import (
        ReleaseDecision,
        ReleaseOutcome,
        make_release_decision,
        check_blockable_findings
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
class ReleaseDecisionErrorCode:
    """Error codes for release decision validation."""
    NO_EVIDENCE = "E021_NO_EVIDENCE"
    CRITICAL_RISK_UNACCEPTED = "E022_CRITICAL_RISK_UNACCEPTED"
    BLOCKABLE_NOT_OVERRIDDEN = "E023_BLOCKABLE_NOT_OVERRIDDEN"
    EVIDENCE_INCOMPLETE = "E024_EVIDENCE_INCOMPLETE"


# ============================================================================
# Enums (Structured decisions - NO free-form text)
# ============================================================================
class ReleaseOutcome(Enum):
    """Final decision outcomes."""
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"
    CONDITIONAL_RELEASE = "CONDITIONAL_RELEASE"
    LIMITED_RELEASE = "LIMITED_RELEASE"
    RELEASE = "RELEASE"


class RationaleCode(Enum):
    """Structured rationale codes (NO free-form text)."""
    ALL_CHECKS_PASSED = "ALL_CHECKS_PASSED"
    CRITICAL_FINDINGS_UNRESOLVED = "CRITICAL_FINDINGS_UNRESOLVED"
    HIGH_RISK_THRESHOLD_EXCEEDED = "HIGH_RISK_THRESHOLD_EXCEEDED"
    EVIDENCE_INCOMPLETE = "EVIDENCE_INCOMPLETE"
    OVERRIDE_APPROVED = "OVERRIDE_APPROVED"
    CONDITIONAL_ACCEPTANCE = "CONDITIONAL_ACCEPTANCE"
    LIMITED_SCOPE_APPROVED = "LIMITED_SCOPE_APPROVED"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    REMEDIATION_REQUIRED = "REMEDIATION_REQUIRED"
    DEFERRED_DECISION = "DEFERRED_DECISION"


class DecisionContext(Enum):
    """Context of the decision."""
    ENTRY_GATE = "entry_gate"
    EXIT_GATE = "exit_gate"
    ESCALATION_REVIEW = "escalation_review"


class GateType(Enum):
    """Type of gate making this decision."""
    INTAKE = "intake"
    VALIDATION = "validation"
    ADJUDICATION = "adjudication"
    RELEASE = "release"


class ConditionType(Enum):
    """Types of release conditions."""
    MONITORING_REQUIRED = "monitoring_required"
    USAGE_RESTRICTION = "usage_restriction"
    REMEDIATION_DEADLINE = "remediation_deadline"
    ADDITIONAL_TESTING = "additional_testing"
    DOCUMENTATION_REQUIRED = "documentation_required"
    APPROVAL_REQUIRED = "approval_required"
    SCOPE_LIMITATION = "scope_limitation"


class EscalationTarget(Enum):
    """Who escalation goes to."""
    TECHNICAL_LEAD = "TECHNICAL_LEAD"
    ARCHITECTURE_BOARD = "ARCHITECTURE_BOARD"
    SECURITY_COUNCIL = "SECURITY_COUNCIL"
    CTO_OFFICE = "CTO_OFFICE"


class EscalationReason(Enum):
    """Reason for escalation."""
    EXCEEDS_DELEGATED_AUTHORITY = "EXCEEDS_DELEGATED_AUTHORITY"
    NOVEL_ATTACK_VECTOR = "NOVEL_ATTACK_VECTOR"
    SIGNATURE_DISAGREEMENT = "SIGNATURE_DISAGREEMENT"
    BUSINESS_CRITICALITY = "BUSINESS_CRITICALITY"
    REGULATORY_IMPLICATION = "REGULATORY_IMPLICATION"


class EnvironmentType(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    SANDBOX = "sandbox"


# ============================================================================
# Hard Constraint Check: Blockable Findings
# ============================================================================
def check_blockable_findings(
    findings: list[dict[str, Any]],
    overridden_ids: set[str],
) -> dict[str, Any]:
    """
    Check if there are blockable findings that weren't overridden.

    Blockable findings:
    - CRITICAL severity with CONFIRMED truth
    - Evidence strength INSUFFICIENT
    - No evidence (evidence_count == 0)

    Args:
        findings: List of finding dicts from T6
        overridden_ids: Set of finding IDs that were overridden

    Returns:
        Dict with 'has_blockable' flag and list of blocking finding IDs.
    """
    blocking = []

    for finding in findings:
        finding_id = finding.get("finding_id")

        # Skip if overridden
        if finding_id in overridden_ids:
            continue

        # Check CRITICAL + CONFIRMED
        if (
            finding.get("what", {}).get("severity") == "CRITICAL"
            and finding.get("truth_assessment") == "CONFIRMED"
        ):
            blocking.append(finding_id)
            continue

        # Check INSUFFICIENT evidence
        if finding.get("evidence_strength") == "INSUFFICIENT":
            blocking.append(finding_id)
            continue

        # Check no evidence
        if len(finding.get("evidence_refs", [])) == 0:
            blocking.append(finding_id)

    return {
        "has_blockable": len(blocking) > 0,
        "blocking_findings": blocking,
    }


# ============================================================================
# Data Structures
# ============================================================================
@dataclass(frozen=True)
class EvidenceRef:
    """Evidence reference for release decision."""
    kind: Literal["FILE", "LOG", "REPORT", "REVIEW", "TICKET", "DOCUMENTATION"]
    locator: str
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "locator": self.locator,
            "note": self.note,
        }


@dataclass
class ReleaseCondition:
    """Condition for release."""
    type: ConditionType
    description: str
    deadline: str | None = None
    verification_method: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "type": self.type.value,
            "description": self.description,
        }
        if self.deadline:
            result["deadline"] = self.deadline
        if self.verification_method:
            result["verification_method"] = self.verification_method
        return result


@dataclass
class ReleaseScope:
    """Scope limitation for limited releases."""
    allowed_environments: list[EnvironmentType] | None = None
    allowed_users: list[str] | None = None
    usage_limits: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {}
        if self.allowed_environments:
            result["allowed_environments"] = [e.value for e in self.allowed_environments]
        if self.allowed_users:
            result["allowed_users"] = self.allowed_users
        if self.usage_limits:
            result["usage_limits"] = self.usage_limits
        return result


@dataclass
class DecisionRationale:
    """Structured rationale for the decision."""
    code: RationaleCode
    blocking_findings_count: int | None = None
    overrides_count: int | None = None
    residual_risks_count: int | None = None
    escalation_reason: EscalationReason | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {"code": self.code.value}
        if self.blocking_findings_count is not None:
            result["blocking_findings_count"] = self.blocking_findings_count
        if self.overrides_count is not None:
            result["overrides_count"] = self.overrides_count
        if self.residual_risks_count is not None:
            result["residual_risks_count"] = self.residual_risks_count
        if self.escalation_reason:
            result["escalation_reason"] = self.escalation_reason.value
        return result


@dataclass
class EscalationGate:
    """Escalation information."""
    escalated_to: EscalationTarget
    escalation_reason_code: EscalationReason
    escalated_at: str
    response_deadline: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "escalated_to": self.escalated_to.value,
            "escalation_reason_code": self.escalation_reason_code.value,
            "escalated_at": self.escalated_at,
        }
        if self.response_deadline:
            result["response_deadline"] = self.response_deadline
        return result


@dataclass
class DecisionChainEntry:
    """Entry in the decision chain."""
    timestamp: str
    stage: str
    outcome: str
    decision_maker: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "stage": self.stage,
            "outcome": self.outcome,
            "decision_maker": self.decision_maker,
        }


@dataclass
class ReleaseDecision:
    """
    Final release decision with structured evidence binding.

    T10 Hard Constraints enforced:
    - Release decision must have supporting evidence
    - CRITICAL residual risks cannot be accepted for release
    - Blockable findings must be overridden or cause REJECT
    """
    run_id: str
    skill_id: str
    decision_timestamp: str
    t10_version: str = "1.0.0-t10"
    decision_context: DecisionContext = DecisionContext.EXIT_GATE
    gate_type: GateType = GateType.RELEASE
    skill_name: str = ""

    # Decision
    outcome: ReleaseOutcome = ReleaseOutcome.REJECT
    rationale: DecisionRationale | None = None
    is_final: bool = True
    valid_until: str | None = None
    conditions: list[ReleaseCondition] | None = None
    scope: ReleaseScope | None = None

    # Findings summary
    total_findings: int = 0
    by_severity: dict[str, int] = field(default_factory=dict)
    by_source: dict[str, int] = field(default_factory=dict)
    blocking_findings: list[str] = field(default_factory=list)
    overridden_findings: list[str] = field(default_factory=list)

    # References
    overrides_applied: list[dict[str, Any]] = field(default_factory=list)
    residual_risks: dict[str, Any] = field(default_factory=dict)
    escalation_gate: EscalationGate | None = None
    decision_chain: list[DecisionChainEntry] = field(default_factory=list)
    evidence_refs: list[EvidenceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "meta": {
                "run_id": self.run_id,
                "skill_id": self.skill_id,
                "skill_name": self.skill_name,
                "decision_timestamp": self.decision_timestamp,
                "t10_version": self.t10_version,
                "decision_context": self.decision_context.value,
                "gate_type": self.gate_type.value,
            },
            "decision": {
                "outcome": self.outcome.value,
                "rationale_code": self.rationale.code.value if self.rationale else None,
                "rationale_detail": self.rationale.to_dict() if self.rationale else None,
                "is_final": self.is_final,
                "valid_until": self.valid_until,
                "conditions": [c.to_dict() for c in self.conditions] if self.conditions else None,
                "scope": self.scope.to_dict() if self.scope else None,
            },
            "findings_summary": {
                "total_findings": self.total_findings,
                "by_severity": self.by_severity,
                "by_source": self.by_source,
                "blocking_findings": self.blocking_findings,
                "overridden_findings": self.overridden_findings,
            },
            "overrides_applied": self.overrides_applied,
            "residual_risks": self.residual_risks,
            "escalation_gate": self.escalation_gate.to_dict() if self.escalation_gate else None,
            "decision_chain": [e.to_dict() for e in self.decision_chain],
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
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
# Decision Logic
# ============================================================================
def make_release_decision(
    findings: list[dict[str, Any]],
    overrides: list[dict[str, Any]],
    residual_risks: list[dict[str, Any]],
    evidence_refs: list[EvidenceRef],
    run_id: str,
    skill_id: str,
) -> ReleaseDecision:
    """
    Make a release decision based on findings, overrides, and residual risks.

    Decision Logic:
    1. Check for blockable findings (CRITICAL+CONFIRMED, INSUFFICIENT evidence, no evidence)
    2. Check residual risk levels
    3. Check overrides applied
    4. Determine outcome: REJECT / ESCALATE / CONDITIONAL_RELEASE / LIMITED_RELEASE / RELEASE

    T10 Zero Exception Directive:
    - Release decision without supporting evidence → directly FAIL

    Args:
        findings: List of findings from T6/T8
        overrides: List of judgment overrides applied
        residual_risks: List of residual risks
        evidence_refs: Evidence supporting this decision (REQUIRED)
        run_id: Run identifier
        skill_id: Skill identifier

    Returns:
        ReleaseDecision with structured outcome.

    Raises:
        ValueError: If evidence_refs is empty (Zero Exception Directive)
    """
    # Zero Exception Directive: Release decision must have supporting evidence
    if not evidence_refs:
        raise ValueError(
            f"{ReleaseDecisionErrorCode.NO_EVIDENCE}: "
            f"Release decision requires supporting evidence. "
            f"Provided evidence_refs is empty."
        )

    now = datetime.now(timezone.utc).isoformat()

    # Get overridden finding IDs
    overridden_ids = {o.get("finding_id") for o in overrides}

    # Check for blockable findings
    blockable_check = check_blockable_findings(findings, overridden_ids)

    # Count by severity
    by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for f in findings:
        sev = f.get("what", {}).get("severity", "INFO")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    # Count residual risks by level
    risk_by_level = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in residual_risks:
        level = r.get("risk_level", "LOW")
        risk_by_level[level] = risk_by_level.get(level, 0) + 1

    # Decision logic
    outcome = ReleaseOutcome.REJECT
    rationale = RationaleCode.CRITICAL_FINDINGS_UNRESOLVED
    is_final = True

    # Priority 1: Blockable findings without override → REJECT
    # Zero Exception Directive: Blockable findings cannot be washed through override
    if blockable_check["has_blockable"]:
        outcome = ReleaseOutcome.REJECT
        rationale = RationaleCode.CRITICAL_FINDINGS_UNRESOLVED
        is_final = True  # Cannot be overridden - blockable findings are hard rejects

    # Priority 2: CRITICAL residual risks → ESCALATE
    elif risk_by_level.get("CRITICAL", 0) > 0:
        outcome = ReleaseOutcome.ESCALATE
        rationale = RationaleCode.HIGH_RISK_THRESHOLD_EXCEEDED
        is_final = False

    # Priority 3: HIGH residual risks or overrides → CONDITIONAL or LIMITED
    elif risk_by_level.get("HIGH", 0) > 0 or len(overrides) > 0:
        if risk_by_level.get("HIGH", 0) > 2:
            outcome = ReleaseOutcome.CONDITIONAL_RELEASE
            rationale = RationaleCode.OVERRIDE_APPROVED
        else:
            outcome = ReleaseOutcome.LIMITED_RELEASE
            rationale = RationaleCode.LIMITED_SCOPE_APPROVED

    # Priority 4: All clear → RELEASE
    elif (
        blockable_check["blocking_findings"] == []
        and risk_by_level.get("CRITICAL", 0) == 0
        and risk_by_level.get("HIGH", 0) == 0
    ):
        outcome = ReleaseOutcome.RELEASE
        rationale = RationaleCode.ALL_CHECKS_PASSED

    return ReleaseDecision(
        run_id=run_id,
        skill_id=skill_id,
        decision_timestamp=now,
        outcome=outcome,
        rationale=DecisionRationale(
            code=rationale,
            blocking_findings_count=len(blockable_check["blocking_findings"]),
            overrides_count=len(overrides),
            residual_risks_count=len(residual_risks),
        ),
        is_final=is_final,
        total_findings=len(findings),
        by_severity=by_severity,
        blocking_findings=blockable_check["blocking_findings"],
        overridden_findings=list(overridden_ids),
        overrides_applied=overrides,
        residual_risks={
            "total_risks": len(residual_risks),
            "risk_ids": [r.get("risk_id") for r in residual_risks],
            "by_level": risk_by_level,
            "unacceptable_count": risk_by_level.get("CRITICAL", 0) + risk_by_level.get("HIGH", 0),
        },
        evidence_refs=evidence_refs,
    )


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for release decision operations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Make release decision"
    )
    parser.add_argument("--findings", required=True, help="Path to findings JSON")
    parser.add_argument("--overrides", help="Path to overrides JSON")
    parser.add_argument("--risks", help="Path to residual risks JSON")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--output", "-o", default="run/latest/release_decision.json")

    args = parser.parse_args()

    # Load inputs
    with open(args.findings) as f:
        findings = json.load(f).get("findings", [])

    overrides = []
    if args.overrides:
        with open(args.overrides) as f:
            data = json.load(f)
            overrides = data.get("overrides", [])

    risks = []
    if args.risks:
        with open(args.risks) as f:
            data = json.load(f)
            risks = data.get("risks", [])

    # Make decision
    decision = make_release_decision(
        findings=findings,
        overrides=overrides,
        residual_risks=risks,
        evidence_refs=[],
        run_id=args.run_id,
        skill_id=args.skill_id,
    )

    # Save
    decision.save(args.output)
    print(f"Release decision saved to: {args.output}")
    print(f"Outcome: {decision.outcome.value}")


if __name__ == "__main__":
    main()
