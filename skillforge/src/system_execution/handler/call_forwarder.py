"""
Call Forwarder Module

Forwards calls from handler to service/orchestrator layers.
Does NOT execute business logic or trigger side effects.
"""

from __future__ import annotations

from typing import Any, Dict, List
from .handler_interface import HandlerInput, ForwardTarget, HandlerInterface
from .input_acceptance import InputAcceptance


class CallForwarder(HandlerInterface):
    """
    Call forwarding between handler and downstream layers.

    CONSTRAINTS:
    - Forwards ONLY based on input type and action
    - Does NOT evaluate business rules
    - Does NOT execute side effects

    Forwarding strategy:
    1. Validate input acceptance
    2. Determine forwarding target
    3. Prepare context for downstream
    4. Return forwarding info (no actual call)
    """

    # Forwarding map: action -> (layer, module, method)
    _FORWARD_MAP: Dict[str, ForwardTarget] = {
        # Query actions → service layer
        "query": ForwardTarget("service", "query_service", "execute"),
        "status": ForwardTarget("service", "status_service", "get"),

        # Forward actions → orchestrator layer
        "forward": ForwardTarget("orchestrator", "internal_router", "route_request"),

        # Dispatch actions → service layer
        "dispatch": ForwardTarget("service", "dispatch_service", "process"),
    }

    def __init__(self, acceptance: InputAcceptance):
        self._acceptance = acceptance

    def accept_input(self, handler_input: HandlerInput) -> tuple[bool, List[str]]:
        """
        Delegate input acceptance to InputAcceptance.

        This handler does NOT make acceptance decisions itself.
        """
        return self._acceptance.validate(handler_input)

    def forward_call(self, handler_input: HandlerInput) -> ForwardTarget:
        """
        Determine forwarding target based on action.

        Strategy:
        1. Check if action is known
        2. Return pre-configured forward target
        3. Unknown actions forward to service for fallback

        NO business evaluation here.
        """
        action = handler_input.action

        if action in self._FORWARD_MAP:
            return self._FORWARD_MAP[action]

        # Fallback to service for unknown actions
        return ForwardTarget("service", "fallback_service", "accept")

    def prepare_forward_context(self, handler_input: HandlerInput) -> Dict[str, Any]:
        """
        Prepare context for downstream layers.

        Adds forwarding metadata and preserves original input.
        """
        target = self.forward_call(handler_input)

        return {
            "request_id": handler_input.request_id,
            "source": handler_input.source,
            "action": handler_input.action,
            "payload": handler_input.payload,
            "evidence_ref": handler_input.evidence_ref,
            "forward_target": {
                "layer": target.layer,
                "module": target.module,
                "method": target.method,
            },
            "forward_decision": "call_forwarder",
        }
