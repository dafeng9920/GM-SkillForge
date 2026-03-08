"""
ConstitutionGate node — risk assessment gate for skill safety and alignment.

Path: ALL
Stage: 4

Input Contract (conforms to gm-os-core constitution_risk_gate.schema.json)
--------------
{
    "skill_spec": { ... },      # from SkillComposer or DraftSpec
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "constitution_risk_gate",
    "node_id": "constitution_risk_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "risk_score": float,        # 0.0 - 1.0
        "risk_categories": list[str],
        "mitigations_required": list[str],
        "constitution_version": str,
        "constitution_hash": str    # SHA256 hex digest
    },
    "ruling": {
        "verdict": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
        "rule_id": str,             # Constitution rule that triggered
        "evidence_ref": str | None, # Reference to evidence supporting ruling
        "blocked": bool             # True if action is blocked
    },
    "timestamp": str
}
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any

from skillforge.src.utils.constitution import load_constitution


# ── Malicious Intent Patterns (T1 Hard Gate) ────────────────────────────────
# Patterns that indicate attempts to bypass safety controls or create harmful skills
MALICIOUS_INTENT_PATTERNS = [
    # Bypass patterns
    r"绕过(风控|安全|限制|检测|验证)",
    r"bypass.*(security|control|safety|limit|check)",
    # Unlimited/unrestricted automation
    r"无限制.*(自动|下单|交易|操作)",
    r"unlimited.*(auto|order|trade|operation)",
    # Automated trading/ordering without limits
    r"自动(下单|交易|购买).*(无|不限)",
    r"auto.*(order|trade|buy).*(unlimited|no.?limit)",
    # Risk evasion
    r"逃避.*风险",
    r"evade.*risk",
    # Fraud/deception
    r"(欺诈|诈骗|钓鱼|欺骗)",
    r"(fraud|phishing|deceive|scam)",
    # Unauthorized access
    r"(未授权|非法).*(访问|获取)",
    r"unauthorized.*(access|obtain)",
    # Data exfiltration
    r"(窃取|盗取|泄露).*(数据|信息)",
    r"(steal|exfiltrate|leak).*(data|info)",
]

# Compile patterns for efficiency
COMPILED_MALICIOUS_PATTERNS = [re.compile(p, re.IGNORECASE) for p in MALICIOUS_INTENT_PATTERNS]


@dataclass
class ConstitutionGate:
    """Evaluate skill spec against the GM OS constitution for safety and alignment."""

    node_id: str = "constitution_risk_gate"
    stage: int = 4

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec is present."""
        errors: list[str] = []

        skill_compose = input_data.get("skill_compose")
        draft_skill_spec = input_data.get("draft_skill_spec")

        has_spec = False
        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            has_spec = True
        if isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            has_spec = True

        if not has_spec:
            errors.append(
                "EXEC_VALIDATION_FAILED: skill_spec source is required "
                "(from skill_compose or draft_skill_spec)"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate skill spec against constitution risk criteria.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        # Load constitution (fail-closed per §2.2)
        constitution_ref, constitution_hash = load_constitution()
        if constitution_ref == "MISSING":
            return {
                "schema_version": "0.1.0",
                "gate_id": "constitution_risk_gate",
                "node_id": self.node_id,
                "decision": "DENY",
                "reason": "Constitution file missing; Fail-Closed per Constitution §2.2",
                "details": {
                    "risk_score": 1.0,
                    "risk_categories": ["constitution_missing"],
                    "mitigations_required": ["Ensure constitution_v1.md exists at docs/2026-02-16/"],
                    "constitution_version": "MISSING",
                    "constitution_hash": "",
                },
                "ruling": {
                    "verdict": "DENY",
                    "rule_id": "CONSTITUTION_MISSING",
                    "evidence_ref": None,
                    "blocked": True,
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

        # ── T1: Malicious Intent Detection (Hard Gate) ────────────────────────
        # Check natural_language input for malicious patterns
        natural_language = input_data.get("input", {}).get("natural_language", "")
        if not natural_language:
            # Also check intent_parse for the original intent
            intent_parse = input_data.get("intent_parse", {})
            if isinstance(intent_parse, dict):
                natural_language = intent_parse.get("original_text", "")
                if not natural_language:
                    intent = intent_parse.get("intent", {})
                    if isinstance(intent, dict):
                        natural_language = intent.get("description", "")

        # Scan for malicious patterns
        matched_pattern = None
        matched_text = ""
        if natural_language:
            for pattern in COMPILED_MALICIOUS_PATTERNS:
                match = pattern.search(natural_language)
                if match:
                    matched_pattern = pattern.pattern
                    matched_text = match.group(0)
                    break

        if matched_pattern:
            return {
                "schema_version": "0.1.0",
                "gate_id": "constitution_risk_gate",
                "node_id": self.node_id,
                "decision": "DENY",
                "reason": f"Malicious intent detected: pattern '{matched_text}' matches prohibited content",
                "details": {
                    "risk_score": 1.0,
                    "risk_categories": ["malicious_intent"],
                    "mitigations_required": ["Remove malicious intent from request"],
                    "constitution_version": constitution_ref,
                    "constitution_hash": constitution_hash,
                    "matched_pattern": matched_pattern,
                },
                "ruling": {
                    "verdict": "DENY",
                    "rule_id": "MALICIOUS_INTENT_DETECTED",
                    "evidence_ref": f"matched_text='{matched_text}', pattern='{matched_pattern}'",
                    "blocked": True,
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

        # Resolve skill_spec: prefer skill_compose, fall back to draft_skill_spec
        skill_compose = input_data.get("skill_compose", {})
        draft_skill_spec = input_data.get("draft_skill_spec", {})

        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            skill_spec = skill_compose["skill_spec"]
        elif isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            skill_spec = draft_skill_spec["skill_spec"]
        else:
            skill_spec = {}

        # Options
        options = input_data.get("input", {}).get("options", {})
        sandbox_mode: str = options.get("sandbox_mode", "strict")

        # Risk assessment
        risk_categories: list[str] = []
        risk_score: float = 0.0

        # Check constraints for elevated risk tiers
        constraints = skill_spec.get("constraints", [])
        constraints_str = " ".join(str(c) for c in constraints).lower()
        if "l2" in constraints_str or "l3" in constraints_str:
            risk_score += 0.3
            risk_categories.append("elevated_risk_tier")

        # Check tools_required for subprocess / shell access
        tools_required = skill_spec.get("tools_required", [])
        for tool in tools_required:
            tool_lower = str(tool).lower()
            if tool_lower == "subprocess" or "shell" in tool_lower:
                risk_score += 0.3
                risk_categories.append("subprocess_access")
                break

        # Check intent domain for ML compute
        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        if intent.get("domain") == "machine_learning":
            risk_score += 0.1
            risk_categories.append("ml_compute")

        # ── v0 Scope Constitution Rules (Protocol v0 Scope) ──
        capabilities = skill_spec.get("capabilities", {})
        if not isinstance(capabilities, dict):
            capabilities = {}

        # Rule: robots_txt — web_crawl must respect robots.txt
        if capabilities.get("web_crawl") and not capabilities.get("respect_robots_txt", True):
            return {
                "schema_version": "0.1.0",
                "gate_id": "constitution_risk_gate",
                "node_id": self.node_id,
                "decision": "DENY",
                "reason": "web_crawl without robots.txt compliance is prohibited",
                "details": {
                    "risk_score": 1.0,
                    "risk_categories": ["robots_txt_violation"],
                    "mitigations_required": ["Set respect_robots_txt=true in capabilities"],
                    "constitution_version": constitution_ref,
                    "constitution_hash": constitution_hash,
                },
                "ruling": {
                    "verdict": "DENY",
                    "rule_id": "ROBOTS_TXT_VIOLATION",
                    "evidence_ref": "capabilities.web_crawl=true, capabilities.respect_robots_txt=false",
                    "blocked": True,
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

        # Rule: auth_content — authenticated/restricted content access is prohibited in v0
        if capabilities.get("authenticated_access"):
            return {
                "schema_version": "0.1.0",
                "gate_id": "constitution_risk_gate",
                "node_id": self.node_id,
                "decision": "DENY",
                "reason": "Authenticated/restricted content access is prohibited in v0",
                "details": {
                    "risk_score": 1.0,
                    "risk_categories": ["authenticated_access_violation"],
                    "mitigations_required": ["Remove authenticated_access capability"],
                    "constitution_version": constitution_ref,
                    "constitution_hash": constitution_hash,
                },
                "ruling": {
                    "verdict": "DENY",
                    "rule_id": "AUTHENTICATED_ACCESS_VIOLATION",
                    "evidence_ref": "capabilities.authenticated_access=true",
                    "blocked": True,
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

        # Clamp
        risk_score = min(risk_score, 1.0)

        # Decision rules
        mitigations_required: list[str] = []
        if risk_score >= 0.7:
            decision = "DENY"
            reason = f"Risk score {risk_score:.2f} exceeds threshold (0.7); categories: {risk_categories}"
            rule_id = "RISK_SCORE_THRESHOLD_EXCEEDED"
            blocked = True
        elif risk_score >= 0.3:
            decision = "REQUIRES_CHANGES"
            reason = f"Risk score {risk_score:.2f} requires review; categories: {risk_categories}"
            mitigations_required = ["Review subprocess usage", "Add resource limits"]
            rule_id = "RISK_SCORE_REQUIRES_REVIEW"
            blocked = False
        else:
            decision = "ALLOW"
            reason = f"Risk score {risk_score:.2f} is within acceptable limits"
            rule_id = "RISK_SCORE_ACCEPTABLE"
            blocked = False

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return {
            "schema_version": "0.1.0",
            "gate_id": "constitution_risk_gate",
            "node_id": self.node_id,
            "decision": decision,
            "reason": reason,
            "details": {
                "risk_score": risk_score,
                "risk_categories": risk_categories,
                "mitigations_required": mitigations_required,
                "constitution_version": constitution_ref,
                "constitution_hash": constitution_hash,
            },
            "ruling": {
                "verdict": decision,
                "rule_id": rule_id,
                "evidence_ref": f"risk_score={risk_score:.2f}, categories={risk_categories}",
                "blocked": blocked,
            },
            "timestamp": timestamp,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "gate_id", "node_id", "decision", "reason", "timestamp", "ruling"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        decision = output_data.get("decision")
        if decision is not None and decision not in ("ALLOW", "DENY", "REQUIRES_CHANGES"):
            errors.append(
                f"GATE_INVALID_DECISION: decision must be ALLOW, DENY, or "
                f"REQUIRES_CHANGES, got '{decision}'"
            )

        details = output_data.get("details")
        if isinstance(details, dict):
            for field in ("risk_score", "risk_categories", "constitution_version", "constitution_hash"):
                if field not in details:
                    errors.append(f"SCHEMA_INVALID: details.{field} is required")
        else:
            errors.append("SCHEMA_INVALID: details must be a dict")

        # Validate ruling structure
        ruling = output_data.get("ruling")
        if isinstance(ruling, dict):
            for field in ("verdict", "rule_id", "blocked"):
                if field not in ruling:
                    errors.append(f"SCHEMA_INVALID: ruling.{field} is required")
            verdict = ruling.get("verdict")
            if verdict is not None and verdict not in ("ALLOW", "DENY", "REQUIRES_CHANGES"):
                errors.append(
                    f"GATE_INVALID_RULING_VERDICT: ruling.verdict must be ALLOW, DENY, or "
                    f"REQUIRES_CHANGES, got '{verdict}'"
                )
        else:
            errors.append("SCHEMA_INVALID: ruling must be a dict")

        return errors
