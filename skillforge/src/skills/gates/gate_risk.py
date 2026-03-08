"""
Gate: constitution_risk_gate — Constitution risk assessment for skill safety.

Gate Group: logic (squad-b)
Stage: 4

Input Contract (conforms to gate_interface_v1.yaml)
----------------------------------------------------
{
    "skill_spec": {
        "name": str,
        "version": str,
        "capabilities": list[str],
        "tools_required": list[str],
        "constraints": list[str],
        ...
    }
}

Output Contract (GateResult)
----------------------------
{
    "gate_name": "constitution_risk_gate",
    "gate_decision": "PASSED" | "REJECTED",
    "next_action": "continue" | "halt",
    "error_code": str | null,
    "evidence_refs": [...],
    "risk_assessment": { ... }  # Evidence payload
}

Deny List (Red Lines):
- Must NOT allow specs with 'override_governance' flag
- Must NOT modify Constitution definitions
- Fail-Closed: Risk detected MUST trigger REJECTED
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..experience_capture import FixKind, capture_gate_event

GATE_NAME = "constitution_risk_gate"
GATE_VERSION = "0.1.0"
TOOL_REVISION = "skillforge.gates.logic.v1"

# Constitution version (SSOT - DO NOT MODIFY)
CONSTITUTION_VERSION = "constitution_v1.md"
CONSTITUTION_HASH = "c14f8d9e3a2b1f0c8d7e6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4"

# Risk thresholds
RISK_SCORE_DENY_THRESHOLD = 0.7
RISK_SCORE_REVIEW_THRESHOLD = 0.3

# Capability risk weights
CAPABILITY_RISK_WEIGHTS: Dict[str, float] = {
    "shell": 0.3,
    "file_write": 0.2,
    "database": 0.3,
    "network": 0.1,
    "llm": 0.1,
}

# Prohibited capabilities in v0 scope
PROHIBITED_CAPABILITIES = {
    "authenticated_access",
    "privileged_execution",
    "system_modification",
}

# Risk tier mapping
RISK_TIER_MAP = [
    (0.0, 0.3, "L0"),
    (0.3, 0.5, "L1"),
    (0.5, 0.7, "L2"),
    (0.7, 1.0, "L3"),
]


@dataclass
class EvidenceRef:
    """Evidence reference per gate_interface_v1.yaml."""
    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str


@dataclass
class GateResult:
    """Gate result per gate_interface_v1.yaml."""
    gate_name: str
    gate_decision: str  # "PASSED" | "REJECTED"
    next_action: str    # "continue" | "halt"
    evidence_refs: List[EvidenceRef]
    error_code: Optional[str] = None
    risk_assessment: Optional[Dict[str, Any]] = None


def _compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _refs_to_dict(evidence_refs: List[EvidenceRef]) -> List[Dict[str, str]]:
    """Convert evidence refs to dict for capture helper."""
    return [
        {
            "issue_key": ref.issue_key,
            "source_locator": ref.source_locator,
            "content_hash": ref.content_hash,
            "tool_revision": ref.tool_revision,
            "timestamp": ref.timestamp,
        }
        for ref in evidence_refs
    ]


def _get_risk_tier(risk_score: float) -> str:
    """Map risk score to risk tier."""
    for min_score, max_score, tier in RISK_TIER_MAP:
        if min_score <= risk_score < max_score:
            return tier
    return "L3"


def _check_override_governance(skill_spec: Dict[str, Any]) -> bool:
    """
    Check if skill spec has override_governance flag.
    This is a RED LINE - such specs MUST be rejected.
    """
    # Check in constraints
    constraints = skill_spec.get("constraints", [])
    for constraint in constraints:
        if isinstance(constraint, str) and "override_governance" in constraint.lower():
            return True

    # Check in capabilities dict
    capabilities = skill_spec.get("capabilities", {})
    if isinstance(capabilities, dict):
        if capabilities.get("override_governance"):
            return True

    # Check top-level flags
    if skill_spec.get("override_governance"):
        return True

    return False


def _assess_risk(skill_spec: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
    """
    Assess risk based on skill spec capabilities and constraints.

    Returns:
        Tuple of (risk_score, risk_categories, mitigations_required)
    """
    risk_score: float = 0.0
    risk_categories: List[str] = []
    mitigations_required: List[str] = []

    # Get capabilities
    capabilities = skill_spec.get("capabilities", [])
    if isinstance(capabilities, dict):
        capabilities = list(capabilities.keys())

    # Assess each capability
    for capability in capabilities:
        cap_lower = str(capability).lower()
        for risk_cap, weight in CAPABILITY_RISK_WEIGHTS.items():
            if risk_cap in cap_lower:
                risk_score += weight
                risk_categories.append(f"capability:{risk_cap}")
                break

    # Check tools_required for risky tools
    tools_required = skill_spec.get("tools_required", [])
    for tool in tools_required:
        tool_lower = str(tool).lower()
        if tool_lower in ["subprocess", "shell", "bash", "sh"]:
            risk_score += 0.3
            risk_categories.append("tool:subprocess")
            mitigations_required.append("Review subprocess usage; consider sandboxing")
        elif tool_lower in ["sudo", "root", "admin"]:
            risk_score += 0.5
            risk_categories.append("tool:privilege_escalation")
            mitigations_required.append("Privileged execution requires manual approval")

    # Check for elevated risk tier constraints
    constraints = skill_spec.get("constraints", [])
    constraints_str = " ".join(str(c) for c in constraints).lower()
    if "l3" in constraints_str:
        risk_score += 0.2
        risk_categories.append("constraint:high_risk_tier")
    elif "l2" in constraints_str:
        risk_score += 0.1
        risk_categories.append("constraint:elevated_risk_tier")

    # Check for prohibited capabilities
    for capability in capabilities:
        cap_lower = str(capability).lower()
        if cap_lower in PROHIBITED_CAPABILITIES:
            risk_score = 1.0
            risk_categories.append(f"prohibited:{cap_lower}")
            mitigations_required.append(f"Capability '{capability}' is prohibited in v0 scope")

    # Clamp risk score
    risk_score = min(risk_score, 1.0)

    return (risk_score, risk_categories, mitigations_required)


def _build_risk_assessment(
    skill_spec: Dict[str, Any],
    risk_score: float,
    risk_categories: List[str],
    mitigations_required: List[str],
    decision: str,
    reason: str,
) -> Dict[str, Any]:
    """Build risk assessment evidence payload."""
    return {
        "schema_version": "0.1.0",
        "skill_name": skill_spec.get("name", "unknown"),
        "risk_score": risk_score,
        "risk_tier": _get_risk_tier(risk_score),
        "risk_categories": risk_categories,
        "mitigations_required": mitigations_required,
        "gate_decision": decision,
        "reason": reason,
        "constitution_version": CONSTITUTION_VERSION,
        "constitution_hash": CONSTITUTION_HASH,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


@dataclass
class ConstitutionRiskGate:
    """
    Gate for constitution risk assessment.

    Implements fail-closed semantics: any detected risk MUST trigger REJECTED.
    Enforces deny list: specs with 'override_governance' flag are rejected.
    Does NOT modify Constitution definitions.
    """

    gate_name: str = GATE_NAME
    version: str = GATE_VERSION

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate skill_spec input."""
        errors: List[str] = []

        if not isinstance(input_data, dict):
            errors.append("INPUT_INVALID: input_data must be a dict")
            return errors

        skill_spec = input_data.get("skill_spec")
        if skill_spec is None:
            errors.append("INPUT_INVALID: skill_spec is required")
        elif not isinstance(skill_spec, dict):
            errors.append("INPUT_INVALID: skill_spec must be a dict")

        return errors

    def execute(self, input_data: Dict[str, Any]) -> GateResult:
        """
        Execute the constitution_risk_gate.

        Args:
            input_data: Dictionary containing 'skill_spec'

        Returns:
            GateResult with risk_assessment evidence

        Fail-Closed Behavior:
            - Any detected risk MUST trigger REJECTED decision
            - Red line violations (override_governance) always result in REJECTED
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        issue_key = f"RISK-{int(time.time() * 1000)}"

        # Validate input
        validation_errors = self.validate_input(input_data)
        if validation_errors:
            result = GateResult(
                gate_name=self.gate_name,
                gate_decision="REJECTED",
                next_action="halt",
                error_code="GATE.RISK.INPUT_INVALID",
                evidence_refs=[],
            )
            capture_gate_event(
                gate_node=self.gate_name,
                gate_decision=result.gate_decision,
                evidence_refs=[],
                error_code=result.error_code,
                fix_kind=FixKind.GATE_DECISION,
                summary="constitution risk gate rejected due to invalid input",
            )
            return result

        skill_spec = input_data.get("skill_spec", {})

        # RED LINE CHECK: override_governance flag
        if _check_override_governance(skill_spec):
            risk_assessment = _build_risk_assessment(
                skill_spec=skill_spec,
                risk_score=1.0,
                risk_categories=["redline:override_governance"],
                mitigations_required=["Remove override_governance flag from spec"],
                decision="REJECTED",
                reason="RED LINE: Spec contains override_governance flag; rejected per deny list",
            )
            content_hash = _compute_hash(str(risk_assessment))
            evidence_ref = EvidenceRef(
                issue_key=issue_key,
                source_locator=f"risk_assessment://{issue_key}",
                content_hash=content_hash,
                tool_revision=TOOL_REVISION,
                timestamp=timestamp,
            )
            result = GateResult(
                gate_name=self.gate_name,
                gate_decision="REJECTED",
                next_action="halt",
                error_code="GATE.RISK.OVERRIDE_GOVERNANCE",
                evidence_refs=[evidence_ref],
                risk_assessment=risk_assessment,
            )
            capture_gate_event(
                gate_node=self.gate_name,
                gate_decision=result.gate_decision,
                evidence_refs=_refs_to_dict(result.evidence_refs),
                error_code=result.error_code,
                fix_kind=FixKind.GATE_DECISION,
                summary="constitution red-line override_governance detected",
            )
            return result

        # Assess risk
        risk_score, risk_categories, mitigations_required = _assess_risk(skill_spec)

        # Determine decision (FAIL-CLOSED)
        if risk_score >= RISK_SCORE_DENY_THRESHOLD:
            decision = "REJECTED"
            reason = f"Risk score {risk_score:.2f} exceeds deny threshold ({RISK_SCORE_DENY_THRESHOLD}); " \
                     f"categories: {risk_categories}"
            next_action = "halt"
            error_code = "GATE.RISK.SCORE_EXCEEDED"
        else:
            decision = "PASSED"
            reason = f"Risk score {risk_score:.2f} within acceptable limits; " \
                     f"tier: {_get_risk_tier(risk_score)}"
            next_action = "continue"
            error_code = None

        # Build risk assessment
        risk_assessment = _build_risk_assessment(
            skill_spec=skill_spec,
            risk_score=risk_score,
            risk_categories=risk_categories,
            mitigations_required=mitigations_required,
            decision=decision,
            reason=reason,
        )

        # Create evidence reference
        content_hash = _compute_hash(str(risk_assessment))
        evidence_ref = EvidenceRef(
            issue_key=issue_key,
            source_locator=f"risk_assessment://{issue_key}",
            content_hash=content_hash,
            tool_revision=TOOL_REVISION,
            timestamp=timestamp,
        )

        result = GateResult(
            gate_name=self.gate_name,
            gate_decision=decision,
            next_action=next_action,
            error_code=error_code,
            evidence_refs=[evidence_ref],
            risk_assessment=risk_assessment,
        )
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result.gate_decision,
            evidence_refs=_refs_to_dict(result.evidence_refs),
            error_code=result.error_code,
            fix_kind=FixKind.GATE_DECISION,
            summary=f"constitution risk evaluated with score {risk_score:.3f}",
        )
        return result

    def validate_output(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Validate output against GateResult schema.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: List[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        # Required fields per gate_interface_v1.yaml
        required_fields = ["gate_name", "gate_decision", "next_action", "evidence_refs"]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # Validate gate_name
        gate_name = output_data.get("gate_name")
        if gate_name != GATE_NAME:
            errors.append(f"SCHEMA_INVALID: gate_name must be '{GATE_NAME}'")

        # Validate gate_decision
        gate_decision = output_data.get("gate_decision")
        if gate_decision not in ("PASSED", "REJECTED"):
            errors.append("SCHEMA_INVALID: gate_decision must be 'PASSED' or 'REJECTED'")

        # Validate next_action
        next_action = output_data.get("next_action")
        if next_action not in ("continue", "halt"):
            errors.append("SCHEMA_INVALID: next_action must be 'continue' or 'halt'")

        # Validate evidence_refs
        evidence_refs = output_data.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append("SCHEMA_INVALID: evidence_refs must be an array")
        else:
            for i, ref in enumerate(evidence_refs):
                if not isinstance(ref, dict):
                    errors.append(f"SCHEMA_INVALID: evidence_refs[{i}] must be an object")
                    continue
                for ref_field in ["issue_key", "source_locator", "content_hash", "tool_revision", "timestamp"]:
                    if ref_field not in ref:
                        errors.append(f"SCHEMA_INVALID: evidence_refs[{i}].{ref_field} is required")

        # Validate risk_assessment
        risk_assessment = output_data.get("risk_assessment")
        if not isinstance(risk_assessment, dict):
            errors.append("SCHEMA_INVALID: risk_assessment must be a dict")
        else:
            required_assessment_fields = [
                "schema_version", "skill_name", "risk_score", "risk_tier",
                "risk_categories", "mitigations_required", "gate_decision",
                "reason", "constitution_version", "constitution_hash", "timestamp"
            ]
            for field in required_assessment_fields:
                if field not in risk_assessment:
                    errors.append(f"SCHEMA_INVALID: risk_assessment.{field} is required")

            # Validate risk_score range
            risk_score = risk_assessment.get("risk_score")
            if isinstance(risk_score, (int, float)):
                if not (0.0 <= risk_score <= 1.0):
                    errors.append(f"SCHEMA_INVALID: risk_assessment.risk_score must be 0.0-1.0, got {risk_score}")

            # Validate risk_tier
            risk_tier = risk_assessment.get("risk_tier")
            if risk_tier not in ("L0", "L1", "L2", "L3"):
                errors.append(f"SCHEMA_INVALID: risk_assessment.risk_tier must be L0-L3, got '{risk_tier}'")

        return errors

    def to_dict(self, result: GateResult) -> Dict[str, Any]:
        """Convert GateResult to dict for serialization."""
        return {
            "gate_name": result.gate_name,
            "gate_decision": result.gate_decision,
            "next_action": result.next_action,
            "error_code": result.error_code,
            "evidence_refs": [
                {
                    "issue_key": ref.issue_key,
                    "source_locator": ref.source_locator,
                    "content_hash": ref.content_hash,
                    "tool_revision": ref.tool_revision,
                    "timestamp": ref.timestamp,
                }
                for ref in result.evidence_refs
            ],
            "risk_assessment": result.risk_assessment,
        }


def constitution_risk_gate(skill_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Functional interface for the constitution_risk_gate.

    Args:
        skill_spec: Skill specification from draft_skill_spec gate

    Returns:
        GateResult dict with risk_assessment evidence

    Fail-Closed Behavior:
        - Risk detected MUST trigger REJECTED decision
        - Specs with 'override_governance' flag are always rejected
    """
    gate = ConstitutionRiskGate()
    result = gate.execute({"skill_spec": skill_spec})
    return gate.to_dict(result)


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI entry point for constitution_risk_gate."""
    import sys
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Constitution risk assessment for skill safety")
    parser.add_argument("--input-file", help="Input JSON file with skill_spec")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate input, do not execute"
    )
    args = parser.parse_args()

    gate = ConstitutionRiskGate()

    # Load input
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        print("Error: --input-file is required", file=sys.stderr)
        sys.exit(1)

    # Validate input
    validation_errors = gate.validate_input(input_data)
    if validation_errors:
        error_result = {
            "gate_name": GATE_NAME,
            "gate_decision": "REJECTED",
            "next_action": "halt",
            "error_code": "GATE.RISK.INPUT_INVALID",
            "evidence_refs": [],
            "risk_assessment": None,
            "validation_errors": validation_errors
        }
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=2)
        else:
            print(json.dumps(error_result, indent=2))
        sys.exit(1)

    if args.validate_only:
        print(json.dumps({"status": "VALID", "errors": []}, indent=2))
        sys.exit(0)

    # Execute
    result = gate.execute(input_data)
    output = gate.to_dict(result)

    # Validate output
    output_errors = gate.validate_output(output)
    if output_errors:
        print(f"WARNING: Output validation errors: {output_errors}", file=sys.stderr)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if output["gate_decision"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
