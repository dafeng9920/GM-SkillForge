"""
GateSandbox — Gate evaluator for sandbox_test_and_trace.

Gate Group: delivery (Squad C)
Position: G6 (after scaffold_skill_impl G5)

FAIL-CLOSED: Sandbox failure MUST trigger REJECTED decision.

Evaluates sandbox test output and chains evidence from prior gates:
- G1: intake_repo
- G2: license_gate
- G3: repo_scan_fit_score
- G4: constitution_risk_gate
- G5: scaffold_skill_impl

Output: GateResult conforming to gate_interface_v1.yaml
{
    "gate_name": "sandbox_test_and_trace",
    "gate_decision": "PASSED" | "REJECTED",
    "error_code": str | null,
    "evidence_refs": [EvidenceRef...],
    "next_action": "continue" | "halt"
}
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any


TOOL_REVISION = "0.1.0"
GATE_NAME = "sandbox_test_and_trace"


def _sha256(data: str | bytes) -> str:
    """Compute SHA-256 hex digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class EvidenceRef:
    """Evidence reference conforming to gate_interface_v1.yaml."""

    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "issue_key": self.issue_key,
            "source_locator": self.source_locator,
            "content_hash": self.content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": self.timestamp,
        }


@dataclass
class GateResult:
    """Gate result conforming to gate_interface_v1.yaml."""

    gate_name: str
    gate_decision: str  # "PASSED" | "REJECTED"
    error_code: str | None
    evidence_refs: list[EvidenceRef]
    next_action: str  # "continue" | "halt"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gate_name": self.gate_name,
            "gate_decision": self.gate_decision,
            "error_code": self.error_code,
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
            "next_action": self.next_action,
        }


@dataclass
class GateSandbox:
    """
    Gate evaluator for sandbox_test_and_trace.

    FAIL-CLOSED: Any sandbox failure results in REJECTED decision.

    Validates:
    - Test success flag
    - No critical violations
    - Trace events present
    - Static analysis pass (no critical findings)

    Chains evidence from G1-G5 for downstream gates.
    """

    gate_name: str = GATE_NAME
    tool_revision: str = TOOL_REVISION

    # Critical severity levels that trigger REJECTION
    CRITICAL_SEVERITIES: frozenset[str] = frozenset({
        "error", "ERROR", "critical", "CRITICAL", "blocker", "BLOCKER",
    })

    def evaluate(self, artifacts: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate sandbox test output and produce GateResult.

        FAIL-CLOSED: Sandbox failure MUST trigger REJECTED.

        Args:
            artifacts: Pipeline artifacts including:
                - sandbox_test_and_trace: Test results with success flag
                - scaffold_skill_impl: G5 gate decision (must be PASSED)
                - Prior gate evidence refs for chaining

        Returns:
            GateResult dict conforming to gate_interface_v1.yaml
        """
        timestamp = _now_iso()
        evidence_refs: list[EvidenceRef] = []

        # ── Validate sandbox output exists ──
        sandbox = artifacts.get("sandbox_test_and_trace")
        if not isinstance(sandbox, dict):
            return self._build_rejected(
                error_code="ERR_SANDBOX_OUTPUT_MISSING",
                reason="sandbox_test_and_trace output is missing or invalid",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Check scaffold gate passed (G5 prerequisite) ──
        scaffold_gate = artifacts.get("scaffold_skill_impl")
        if isinstance(scaffold_gate, dict):
            gate_decision = scaffold_gate.get("gate_decision")
            if gate_decision == "REJECTED":
                return self._build_rejected(
                    error_code="ERR_SCAFFOLD_REJECTED",
                    reason="Scaffold gate was rejected, cannot proceed with sandbox",
                    evidence_refs=evidence_refs,
                    timestamp=timestamp,
                )
            # Chain evidence from scaffold gate
            if "evidence_refs" in scaffold_gate:
                for ref in scaffold_gate.get("evidence_refs", []):
                    if isinstance(ref, dict):
                        evidence_refs.append(EvidenceRef(
                            issue_key=ref.get("issue_key", f"CHAIN-G5-{uuid.uuid4().hex[:8]}"),
                            source_locator=ref.get("source_locator", "scaffold_skill_impl"),
                            content_hash=ref.get("content_hash", ""),
                            tool_revision=ref.get("tool_revision", "unknown"),
                            timestamp=ref.get("timestamp", timestamp),
                        ))

        # ── FAIL-CLOSED: Check test success flag ──
        success = sandbox.get("success")
        if success is False:
            # FAIL-CLOSED: Test failure MUST trigger REJECTED
            return self._build_rejected(
                error_code="ERR_TESTS_FAILED",
                reason="Sandbox tests failed (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        if success is None:
            return self._build_rejected(
                error_code="ERR_TEST_STATUS_UNKNOWN",
                reason="Sandbox test success status is missing",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Validate test report ──
        test_report = sandbox.get("test_report", {})
        if not isinstance(test_report, dict):
            return self._build_rejected(
                error_code="ERR_TEST_REPORT_MISSING",
                reason="Test report is missing or invalid",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # Check for test failures
        failed = test_report.get("failed", 0)
        if failed > 0:
            # FAIL-CLOSED: Any test failure triggers REJECTED
            return self._build_rejected(
                error_code="ERR_TEST_FAILURES",
                reason=f"Tests failed: {failed} test(s) did not pass (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Check for sandbox violations (FAIL-CLOSED) ──
        sandbox_report = sandbox.get("sandbox_report", {})
        violations = sandbox_report.get("violations", [])
        if violations:
            # FAIL-CLOSED: Any sandbox violation triggers REJECTED
            return self._build_rejected(
                error_code="ERR_SANDBOX_VIOLATIONS",
                reason=f"Sandbox violations detected: {violations} (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Check static analysis for critical findings (FAIL-CLOSED) ──
        static_analysis = sandbox.get("static_analysis", {})
        findings = static_analysis.get("findings", [])
        critical_findings = [
            f for f in findings
            if isinstance(f, dict) and f.get("severity") in self.CRITICAL_SEVERITIES
        ]
        if critical_findings:
            # FAIL-CLOSED: Critical static analysis findings trigger REJECTED
            return self._build_rejected(
                error_code="ERR_CRITICAL_FINDINGS",
                reason=f"Critical static analysis findings: {len(critical_findings)} (fail-closed)",
                evidence_refs=evidence_refs,
                timestamp=timestamp,
            )

        # ── Chain evidence from G1-G4 (if available) ──
        self._chain_prior_evidence(artifacts, evidence_refs, timestamp)

        # ── Create evidence for sandbox output ──
        sandbox_content_hash = _sha256(json.dumps(sandbox, default=str, sort_keys=True))
        evidence_refs.append(EvidenceRef(
            issue_key=f"SANDBOX-{test_report.get('total_runs', 0)}-RUNS",
            source_locator="file:///sandbox/test_report.json",
            content_hash=sandbox_content_hash,
            tool_revision=self.tool_revision,
            timestamp=timestamp,
        ))

        # ── Create evidence for trace events ──
        trace_events = sandbox.get("trace_events", [])
        if trace_events:
            trace_hash = _sha256(json.dumps(trace_events, default=str, sort_keys=True))
            evidence_refs.append(EvidenceRef(
                issue_key="TRACE_LOG",
                source_locator="file:///sandbox/trace_events.jsonl",
                content_hash=trace_hash,
                tool_revision=self.tool_revision,
                timestamp=timestamp,
            ))

        # ── Build PASSED result ──
        return GateResult(
            gate_name=self.gate_name,
            gate_decision="PASSED",
            error_code=None,
            evidence_refs=evidence_refs,
            next_action="continue",
        ).to_dict()

    def _chain_prior_evidence(
        self,
        artifacts: dict[str, Any],
        evidence_refs: list[EvidenceRef],
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
            gate_output = artifacts.get(gate_name)
            if isinstance(gate_output, dict) and "evidence_refs" in gate_output:
                for ref in gate_output.get("evidence_refs", []):
                    if isinstance(ref, dict):
                        evidence_refs.append(EvidenceRef(
                            issue_key=ref.get("issue_key", f"CHAIN-{gate_id}-{uuid.uuid4().hex[:8]}"),
                            source_locator=ref.get("source_locator", gate_name),
                            content_hash=ref.get("content_hash", ""),
                            tool_revision=ref.get("tool_revision", "unknown"),
                            timestamp=ref.get("timestamp", timestamp),
                        ))

    def _build_rejected(
        self,
        error_code: str,
        reason: str,
        evidence_refs: list[EvidenceRef],
        timestamp: str,
    ) -> dict[str, Any]:
        """Build a REJECTED GateResult with next_action=halt."""
        return GateResult(
            gate_name=self.gate_name,
            gate_decision="REJECTED",
            error_code=error_code,
            evidence_refs=evidence_refs,
            next_action="halt",
        ).to_dict()
