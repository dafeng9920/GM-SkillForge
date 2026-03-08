"""
GateEngine — gate decision evaluator.

Produces a GateDecision dict conforming to gm-os-core gate_decision.schema.json:
{
    "schema_version": "0.1.0",
    "gate_id": str,
    "node_id": str,
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": dict,
    "timestamp": str (ISO-8601)
}
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any


# License whitelist — module-level constant (not a dataclass field)
_ALLOWED_LICENSES: frozenset[str] = frozenset({
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
    "ISC", "0BSD", "Unlicense",
})


@dataclass
class GateEngine:
    """
    Gate decision evaluation engine.

    The GateEngine delegates to node-specific evaluator logic and wraps
    results in the standard GateDecision schema.

    Attributes:
        schema_version: Schema version for emitted GateDecision dicts.
    """

    schema_version: str = "0.1.0"

    def evaluate(self, node_id: str, artifacts: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate a gate for the specified node.

        Args:
            node_id: The gate node identifier (e.g. "license_gate").
            artifacts: Accumulated pipeline artifacts up to this stage.

        Returns:
            GateDecision dict.
        """
        gate_id = f"gate-{uuid.uuid4()}"

        try:
            if node_id == "license_gate":
                return self._evaluate_license_gate(gate_id, node_id, artifacts)
            elif node_id == "constitution_risk_gate":
                return self._evaluate_constitution_gate(gate_id, node_id, artifacts)
            else:
                # Unknown gate — default ALLOW with warning
                return self._build_decision(
                    gate_id=gate_id, node_id=node_id,
                    decision="ALLOW",
                    reason=f"No specialized evaluator for '{node_id}'; defaulting to ALLOW",
                    details={"warning": "no_evaluator_registered"},
                )
        except Exception as exc:
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="DENY",
                reason=f"Gate evaluation error: {exc}",
                details={"exception": str(exc)},
            )

    def _evaluate_license_gate(
        self, gate_id: str, node_id: str, artifacts: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate license compliance."""
        # Look for license info in provenance or build_record
        provenance = artifacts.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {}
        build_record = artifacts.get("build_record", {})
        if not isinstance(build_record, dict):
            build_record = {}

        # Try to find license from multiple sources
        license_id = provenance.get("license") or build_record.get("license")
        if not license_id:
            intake = artifacts.get("intake_repo")
            if isinstance(intake, dict):
                license_id = intake.get("license")

        if not license_id:
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="DENY",
                reason="No license information found in artifacts",
                details={"checked_keys": ["provenance.license", "build_record.license", "intake_repo.license"]},
            )

        if license_id not in _ALLOWED_LICENSES:
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="DENY",
                reason=f"License '{license_id}' is not in the approved whitelist",
                details={"license": license_id, "allowed": sorted(_ALLOWED_LICENSES)},
            )

        return self._build_decision(
            gate_id=gate_id, node_id=node_id,
            decision="ALLOW",
            reason=f"License '{license_id}' is approved",
            details={"license": license_id},
        )

    def _evaluate_constitution_gate(
        self, gate_id: str, node_id: str, artifacts: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate constitutional risk constraints."""
        # Look for skill spec in artifacts
        spec = (
            artifacts.get("draft_skill_spec", {})
            or artifacts.get("skill_compose", {})
            or {}
        )
        if not isinstance(spec, dict):
            spec = {}

        # Get input options for sandbox_mode
        input_data = artifacts.get("input", {})
        if not isinstance(input_data, dict):
            input_data = {}
        options = input_data.get("options", {})
        if not isinstance(options, dict):
            options = {}
        sandbox_mode = options.get("sandbox_mode", "strict")

        # Check capabilities
        capabilities = spec.get("capabilities", {})
        if not isinstance(capabilities, dict):
            capabilities = {}

        risk_tier = spec.get("risk_tier", "L0")

        # ── v0 Scope Constitution Rules (Protocol v0 Scope) ──
        # Rule: robots_txt — web_crawl must respect robots.txt
        if capabilities.get("web_crawl") and not capabilities.get("respect_robots_txt", True):
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="DENY",
                reason="web_crawl without robots.txt compliance is prohibited",
                details={"capabilities": capabilities, "violation": "robots_txt"},
            )

        # Rule: auth_content — authenticated/restricted content access is prohibited in v0
        if capabilities.get("authenticated_access"):
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="DENY",
                reason="Authenticated/restricted content access is prohibited in v0",
                details={"capabilities": capabilities, "violation": "authenticated_access"},
            )

        # Rule: network=true + strict sandbox → DENY
        if capabilities.get("network") and sandbox_mode == "strict":
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="DENY",
                reason="Network access requested but sandbox_mode is 'strict'",
                details={"capabilities": capabilities, "sandbox_mode": sandbox_mode},
            )

        # Rule: subprocess=true + risk > L1 → REQUIRES_CHANGES
        if capabilities.get("subprocess") and risk_tier in ("L2", "L3"):
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="REQUIRES_CHANGES",
                reason=f"Subprocess access with risk_tier '{risk_tier}' requires review",
                details={"capabilities": capabilities, "risk_tier": risk_tier},
            )

        # Rule: validate risk_tier
        valid_tiers = {"L0", "L1", "L2", "L3"}
        if risk_tier and risk_tier not in valid_tiers:
            return self._build_decision(
                gate_id=gate_id, node_id=node_id,
                decision="REQUIRES_CHANGES",
                reason=f"Invalid risk_tier '{risk_tier}'",
                details={"risk_tier": risk_tier, "valid_tiers": sorted(valid_tiers)},
            )

        return self._build_decision(
            gate_id=gate_id, node_id=node_id,
            decision="ALLOW",
            reason="Constitution risk assessment passed",
            details={"risk_tier": risk_tier, "capabilities": capabilities},
        )

    def _build_decision(
        self,
        *,
        gate_id: str,
        node_id: str,
        decision: str,
        reason: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Helper to build a well-formed GateDecision."""
        return {
            "schema_version": self.schema_version,
            "gate_id": gate_id,
            "node_id": node_id,
            "decision": decision,
            "reason": reason,
            "details": details or {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
