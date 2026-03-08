"""
Gate evaluators for the Delivery Layer (Squad C).

These gates evaluate pipeline artifacts and produce GateResult decisions
conforming to gate_interface_v1.yaml:

- gate_scaffold: Evaluates scaffold_skill_impl output
- gate_sandbox: Evaluates sandbox_test_and_trace output (Fail-Closed)
- gate_publish: Evaluates pack_audit_and_publish output

GateResult Schema:
{
    "gate_name": str,
    "gate_decision": "PASSED" | "REJECTED",
    "error_code": str | null,
    "evidence_refs": [EvidenceRef...],
    "next_action": "continue" | "halt"
}

EvidenceRef Schema:
{
    "issue_key": str,
    "source_locator": str,
    "content_hash": str (SHA-256),
    "tool_revision": str,
    "timestamp": str (ISO-8601)
}
"""
from __future__ import annotations

__all__ = [
    "GateScaffold",
    "GateSandbox",
    "GatePublish",
]

from skillforge.src.gates.gate_scaffold import GateScaffold
from skillforge.src.gates.gate_sandbox import GateSandbox
from skillforge.src.gates.gate_publish import GatePublish
