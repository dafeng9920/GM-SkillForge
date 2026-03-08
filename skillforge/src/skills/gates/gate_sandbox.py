"""
GateSandboxSkill — Gate evaluator for sandbox_test_and_trace.

Gate Group: delivery (Squad C)
Position: G6 (after scaffold_skill_impl G5)

FAIL-CLOSED: Sandbox failure MUST trigger REJECTED decision.

Implements the experience_capture.py pattern:
- validate_input(input_data) -> list[str]
- execute(input_data) -> dict
- validate_output(output) -> list[str]

Contract: skillforge/src/contracts/gates/sandbox.yaml
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..experience_capture import FixKind, capture_gate_event

TOOL_REVISION = "0.1.0"
GATE_NAME = "sandbox_test_and_trace"
CONTRACT_PATH = Path(__file__).parent.parent.parent / "contracts" / "gates" / "sandbox.yaml"

# Critical severity levels that trigger REJECTION (FC-SANDBOX-005)
CRITICAL_SEVERITIES: frozenset[str] = frozenset({
    "error", "ERROR", "critical", "CRITICAL", "blocker", "BLOCKER",
})


def _sha256(data: str | bytes) -> str:
    """Compute SHA-256 hex digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class GateSandboxSkill:
    """
    Gate evaluator for sandbox_test_and_trace.

    FAIL-CLOSED: Any sandbox failure results in REJECTED decision.

    Implements fail-closed rules FC-SANDBOX-001 to FC-SANDBOX-005.
    Chains evidence from G1-G5 for downstream gates.
    """

    node_id: str = "sandbox_test_and_trace"
    stage: int = 6
    gate_name: str = GATE_NAME
    tool_revision: str = TOOL_REVISION

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate sandbox input against fail-closed rules.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # Sandbox output must be present
        sandbox = input_data.get("sandbox_test_and_trace")
        if not isinstance(sandbox, dict):
            errors.append("SCHEMA_INVALID: sandbox_test_and_trace output is required")
            return errors

        # FC-SANDBOX-002: Missing success status
        if "success" not in sandbox:
            errors.append("FC-SANDBOX-002: success field is required")

        # Check test_report structure
        test_report = sandbox.get("test_report")
        if test_report is not None and not isinstance(test_report, dict):
            errors.append("SCHEMA_INVALID: test_report must be an object")

        # Check sandbox_report structure
        sandbox_report = sandbox.get("sandbox_report")
        if sandbox_report is not None and not isinstance(sandbox_report, dict):
            errors.append("SCHEMA_INVALID: sandbox_report must be an object")

        # Check scaffold gate prerequisite
        scaffold_gate = input_data.get("scaffold_skill_impl")
        if isinstance(scaffold_gate, dict):
            gate_decision = scaffold_gate.get("gate_decision")
            if gate_decision == "REJECTED":
                errors.append("PREREQUISITE_FAILED: scaffold_skill_impl gate was REJECTED")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute sandbox gate evaluation with FAIL-CLOSED behavior.

        FC-SANDBOX-001 to FC-SANDBOX-005 are enforced.
        Validates input first and returns REJECTED if validation fails.
        """
        # Validate input first (fail-closed)
        validation_errors = self.validate_input(input_data)
        if validation_errors:
            result = {
                "gate_name": self.gate_name,
                "gate_decision": "REJECTED",
                "error_code": "VALIDATION_FAILED",
                "evidence_refs": [],
                "next_action": "halt",
                "validation_errors": validation_errors,
            }
            capture_gate_event(
                gate_node=self.gate_name,
                gate_decision=result["gate_decision"],
                evidence_refs=result["evidence_refs"],
                error_code=result["error_code"],
                fix_kind=FixKind.GATE_DECISION,
                summary="sandbox gate rejected due to input validation failure",
            )
            return result

        timestamp = _now_iso()
        sandbox = input_data.get("sandbox_test_and_trace", {})
        evidence_refs: list[dict[str, str]] = []

        # Chain evidence from scaffold gate G5
        scaffold_gate = input_data.get("scaffold_skill_impl")
        if isinstance(scaffold_gate, dict) and "evidence_refs" in scaffold_gate:
            for ref in scaffold_gate.get("evidence_refs", []):
                if isinstance(ref, dict):
                    evidence_refs.append({
                        "issue_key": ref.get("issue_key", f"CHAIN-G5-{uuid.uuid4().hex[:8]}"),
                        "source_locator": ref.get("source_locator", "scaffold_skill_impl"),
                        "content_hash": ref.get("content_hash", ""),
                        "tool_revision": ref.get("tool_revision", "unknown"),
                        "timestamp": ref.get("timestamp", timestamp),
                    })

        # Check scaffold gate rejected
        if isinstance(scaffold_gate, dict):
            gate_decision = scaffold_gate.get("gate_decision")
            if gate_decision == "REJECTED":
                return self._build_rejected(
                    error_code="ERR_SCAFFOLD_REJECTED",
                    reason="Scaffold gate was rejected, cannot proceed with sandbox",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )

        # FC-SANDBOX-001: success=false MUST trigger REJECTED
        success = sandbox.get("success")
        if success is False:
            return self._build_rejected(
                error_code="ERR_TESTS_FAILED",
                reason="Sandbox tests failed (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # FC-SANDBOX-002: Missing success status MUST trigger REJECTED
        if success is None:
            return self._build_rejected(
                error_code="ERR_TEST_STATUS_UNKNOWN",
                reason="Sandbox test success status is missing",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # FC-SANDBOX-003: Any test failures (failed > 0) MUST trigger REJECTED
        test_report = sandbox.get("test_report", {})
        failed = test_report.get("failed", 0)
        if failed > 0:
            return self._build_rejected(
                error_code="ERR_TEST_FAILURES",
                reason=f"Tests failed: {failed} test(s) did not pass (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # FC-SANDBOX-004: Any sandbox violations MUST trigger REJECTED
        sandbox_report = sandbox.get("sandbox_report", {})
        violations = sandbox_report.get("violations", [])
        if violations:
            return self._build_rejected(
                error_code="ERR_SANDBOX_VIOLATIONS",
                reason=f"Sandbox violations detected: {violations} (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # FC-SANDBOX-005: Critical static analysis findings MUST trigger REJECTED
        static_analysis = sandbox.get("static_analysis", {})
        findings = static_analysis.get("findings", [])
        critical_findings = [
            f for f in findings
            if isinstance(f, dict) and f.get("severity") in CRITICAL_SEVERITIES
        ]
        if critical_findings:
            return self._build_rejected(
                error_code="ERR_CRITICAL_FINDINGS",
                reason=f"Critical static analysis findings: {len(critical_findings)} (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # Chain evidence from G1-G4
        self._chain_prior_evidence(input_data, evidence_refs, timestamp)

        # Create evidence for sandbox output
        sandbox_content_hash = _sha256(json.dumps(sandbox, default=str, sort_keys=True))
        evidence_refs.append({
            "issue_key": f"SANDBOX-{test_report.get('total_runs', 0)}-RUNS",
            "source_locator": "file:///sandbox/test_report.json",
            "content_hash": sandbox_content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
        })

        # Create evidence for trace events
        trace_events = sandbox.get("trace_events", [])
        if trace_events:
            trace_hash = _sha256(json.dumps(trace_events, default=str, sort_keys=True))
            evidence_refs.append({
                "issue_key": "TRACE_LOG",
                "source_locator": "file:///sandbox/trace_events.jsonl",
                "content_hash": trace_hash,
                "tool_revision": self.tool_revision,
                "timestamp": timestamp,
            })

        result = {
            "gate_name": self.gate_name,
            "gate_decision": "PASSED",
            "error_code": None,
            "evidence_refs": evidence_refs,
            "next_action": "continue",
        }
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            fix_kind=FixKind.ADD_TESTS,
            summary=f"sandbox gate passed with {len(trace_events)} trace event(s)",
            metadata={"trace_event_count": len(trace_events)},
        )
        return result

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate output against GateResult schema."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        required_fields = ["gate_name", "gate_decision", "evidence_refs", "next_action"]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        decision = output_data.get("gate_decision")
        if decision not in ("PASSED", "REJECTED"):
            errors.append(f"SCHEMA_INVALID: gate_decision must be 'PASSED' or 'REJECTED'")

        next_action = output_data.get("next_action")
        if next_action not in ("continue", "halt"):
            errors.append(f"SCHEMA_INVALID: next_action must be 'continue' or 'halt'")

        evidence_refs = output_data.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append("SCHEMA_INVALID: evidence_refs must be an array")

        return errors

    def _chain_prior_evidence(
        self,
        input_data: dict[str, Any],
        evidence_refs: list[dict[str, str]],
        timestamp: str,
    ) -> None:
        """Chain evidence from prior gates G1-G4."""
        prior_gates = [
            ("intake_repo", "G1"),
            ("license_gate", "G2"),
            ("repo_scan_fit_score", "G3"),
            ("constitution_risk_gate", "G4"),
        ]

        for gate_name, gate_id in prior_gates:
            gate_output = input_data.get(gate_name)
            if isinstance(gate_output, dict) and "evidence_refs" in gate_output:
                for ref in gate_output.get("evidence_refs", []):
                    if isinstance(ref, dict):
                        evidence_refs.append({
                            "issue_key": ref.get("issue_key", f"CHAIN-{gate_id}-{uuid.uuid4().hex[:8]}"),
                            "source_locator": ref.get("source_locator", gate_name),
                            "content_hash": ref.get("content_hash", ""),
                            "tool_revision": ref.get("tool_revision", "unknown"),
                            "timestamp": ref.get("timestamp", timestamp),
                        })

    def _build_rejected(
        self,
        error_code: str,
        reason: str,
        evidence_refs: list[dict[str, str]],
        timestamp: str,
    ) -> dict[str, Any]:
        """Build a REJECTED GateResult with next_action=halt."""
        result = {
            "gate_name": self.gate_name,
            "gate_decision": "REJECTED",
            "error_code": error_code,
            "evidence_refs": evidence_refs,
            "next_action": "halt",
            "reason": reason,
        }
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            error_code=result["error_code"],
            fix_kind=FixKind.GATE_DECISION,
            summary=reason,
        )
        return result


def main():
    """CLI entry point for GateSandboxSkill."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="GateSandboxSkill - Sandbox gate evaluator (Fail-Closed)")
    parser.add_argument("--input-file", help="Input JSON file with gate request")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    gate = GateSandboxSkill()

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        print("Error: --input-file is required", file=sys.stderr)
        sys.exit(1)

    validation_errors = gate.validate_input(input_data)
    if validation_errors:
        error_result = {
            "gate_name": gate.gate_name,
            "gate_decision": "REJECTED",
            "error_code": "VALIDATION_FAILED",
            "evidence_refs": [],
            "next_action": "halt",
            "validation_errors": validation_errors,
        }
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=2)
        else:
            print(json.dumps(error_result, indent=2))
        sys.exit(1)

    output = gate.execute(input_data)

    output_errors = gate.validate_output(output)
    if output_errors:
        print(f"WARNING: Output validation errors: {output_errors}", file=sys.stderr)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if output["gate_decision"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
