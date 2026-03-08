"""
Core protocols for SkillForge implementation layer.

All modules MUST program against these protocols, never concrete classes.
Protocols follow gm-os-core schema conventions; every data structure
that leaves the process boundary carries schema_version = "0.1.0".
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class NodeHandler(Protocol):
    """
    A single pipeline node.

    Every node:
    - validates its input against the corresponding gm-os-core schema,
    - executes domain logic,
    - validates its output,
    - emits at least one trace_event.

    Attributes:
        node_id: Unique identifier matching pipeline_v0.yml node names.
        stage: Numeric stage index (pre-0 stages use -1).
    """

    node_id: str
    stage: int

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Return a list of validation error strings. Empty list = valid."""
        ...

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Run the node logic.

        Args:
            input_data: Validated input payload.

        Returns:
            Output payload conforming to this node's output schema.

        Raises:
            RuntimeError: On unrecoverable execution failure.
        """
        ...

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Return a list of validation error strings. Empty list = valid."""
        ...


@runtime_checkable
class GateEvaluator(Protocol):
    """
    Evaluates a gate decision for a given pipeline node.

    Returns a dict conforming to gm-os-core gate_decision.schema.json:
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

    def evaluate(self, node_id: str, artifacts: dict[str, Any]) -> dict[str, Any]:
        """Evaluate gate and return a GateDecision dict."""
        ...


@runtime_checkable
class Adapter(Protocol):
    """
    External service adapter.

    Adapters wrap third-party APIs (GitHub, sandbox runtime, registry)
    behind a stable interface so pipeline nodes never talk to the outside
    world directly.

    Attributes:
        adapter_id: Unique adapter identifier.
    """

    adapter_id: str

    def health_check(self) -> bool:
        """Return True if the backing service is reachable."""
        ...

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic action dispatch.

        Args:
            action: The adapter-specific action name.
            params: Action parameters.

        Returns:
            Action result payload.
        """
        ...
