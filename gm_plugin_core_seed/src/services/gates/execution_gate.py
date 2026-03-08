"""Execution Gate - fail-closed execution guard for application layer."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GateResult:
    allow_execute: bool
    error_code: Optional[str] = None
    message: str = ""
    remediation: str = ""
    triggered_rule_ids: List[str] = field(default_factory=list)


def _deny(
    error_code: str,
    message: str,
    remediation: str,
    triggered_rule_ids: Optional[List[str]] = None,
) -> GateResult:
    return GateResult(
        allow_execute=False,
        error_code=error_code,
        message=message,
        remediation=remediation,
        triggered_rule_ids=triggered_rule_ids or [],
    )


def evaluate(
    decision: Optional[str],
    tier: Optional[int],
    policy_pack_version: Optional[str],
    evidence_ref: Optional[str],
    approval_ref: Optional[str] = None,
    autodeploy_allowed: Optional[bool] = None,
) -> GateResult:
    """Fail-closed execution gate evaluation.

    Required: decision, tier, policy_pack_version, evidence_ref.
    """
    missing_fields = []
    if not decision:
        missing_fields.append("decision")
    if tier is None:
        missing_fields.append("tier")
    if not policy_pack_version:
        missing_fields.append("policy_pack_version")
    if not evidence_ref:
        missing_fields.append("evidence_ref")

    if missing_fields:
        return _deny(
            error_code="GATE.EXECUTION.MISSING_FIELDS",
            message=f"Missing required fields: {', '.join(missing_fields)}",
            remediation="Provide decision, tier, policy_pack_version, and evidence_ref.",
            triggered_rule_ids=[f"EXEC.GATE.MISSING_FIELD.{field}" for field in missing_fields],
        )

    if policy_pack_version in ["unknown", "unavailable"]:
        return _deny(
            error_code="GATE.EXECUTION.POLICY_UNAVAILABLE",
            message="Policy pack unavailable or unbound.",
            remediation="Provide a valid policy_pack_version.",
            triggered_rule_ids=["EXEC.GATE.POLICY_UNAVAILABLE"],
        )

    if tier not in [0, 1, 2, 3]:
        return _deny(
            error_code="GATE.EXECUTION.TIER_RANGE",
            message="Tier must be 0, 1, 2, or 3.",
            remediation="Set tier to 0/1/2/3.",
            triggered_rule_ids=["EXEC.GATE.TIER_RANGE"],
        )

    if autodeploy_allowed:
        return _deny(
            error_code="GATE.EXECUTION.AUTODEPLOY_FORBIDDEN",
            message="Autodeploy is forbidden in execution gate.",
            remediation="Route through manual approval and explicit execution.",
            triggered_rule_ids=["EXEC.GATE.AUTODEPLOY_FORBIDDEN"],
        )

    decision_norm = decision.upper()
    if decision_norm == "DENY":
        return _deny(
            error_code="GATE.EXECUTION.DENY",
            message="Decision is DENY.",
            remediation="Resolve policy failures before execution.",
            triggered_rule_ids=["EXEC.GATE.DENY"],
        )

    if decision_norm == "REQUIRE_HITL":
        if not approval_ref:
            return _deny(
                error_code="HITL_REQUIRED",
                message="HITL approval is required before execution.",
                remediation="Provide approval_ref from human review.",
                triggered_rule_ids=["EXEC.GATE.HITL_REQUIRED"],
            )
        return GateResult(allow_execute=True)

    if decision_norm == "ALLOW":
        if tier in [2, 3]:
            return _deny(
                error_code="GATE.EXECUTION.TIER_HIGH",
                message="Tier2/3 execution requires HITL approval.",
                remediation="Provide approval_ref or downgrade to Tier0/1.",
                triggered_rule_ids=["EXEC.GATE.TIER_HIGH"],
            )
        return GateResult(allow_execute=True)

    return _deny(
        error_code="GATE.EXECUTION.DECISION_UNKNOWN",
        message=f"Unknown decision: {decision}",
        remediation="Use decision ALLOW/DENY/REQUIRE_HITL.",
        triggered_rule_ids=["EXEC.GATE.DECISION_UNKNOWN"],
    )
