"""
Internal Router Module

Routes requests between api → orchestrator → service/handler.
Does NOT make governance decisions or execute business logic.
"""

from __future__ import annotations

from typing import Any, Dict, List
from .orchestrator_interface import RouteTarget, RoutingContext, OrchestratorInterface
from .acceptance_boundary import AcceptanceBoundary


class InternalRouter(OrchestratorInterface):
    """
    Internal routing between execution layers.

    CONSTRAINTS:
    - Routes ONLY based on request type and context
    - Does NOT evaluate governance rules
    - Does NOT execute side effects
    """

    # Route mapping: request_type -> (layer, module, action)
    _ROUTE_MAP: Dict[str, RouteTarget] = {
        # Governance requests → handler layer (read-only, preparation)
        "governance_query": RouteTarget("handler", "governance_handler", "query"),
        "governance_status": RouteTarget("handler", "governance_handler", "status"),

        # Service requests → service layer (business logic)
        "skill_execution": RouteTarget("service", "skill_service", "execute"),
        "data_processing": RouteTarget("service", "data_service", "process"),

        # Pipeline requests → service layer
        "pipeline_submit": RouteTarget("service", "pipeline_service", "submit"),
        "pipeline_status": RouteTarget("service", "pipeline_service", "status"),
    }

    def __init__(self, acceptance: AcceptanceBoundary):
        self._acceptance = acceptance

    def route_request(self, context: RoutingContext) -> RouteTarget:
        """
        Route request to appropriate target layer.

        Strategy:
        1. Check if request type is known
        2. Return pre-configured route target
        3. Unknown types route to handler for fallback

        NO governance evaluation here.
        """
        request_type = context.intent or "unknown"

        if request_type in self._ROUTE_MAP:
            return self._ROUTE_MAP[request_type]

        # Fallback to handler for unknown types
        return RouteTarget("handler", "fallback_handler", "accept")

    def validate_acceptance(self, context: RoutingContext) -> tuple[bool, List[str]]:
        """
        Delegate acceptance validation to AcceptanceBoundary.

        This orchestrator does NOT make acceptance decisions itself.
        """
        return self._acceptance.validate(context)

    def prepare_context(self, context: RoutingContext) -> Dict[str, Any]:
        """
        Prepare enriched context for downstream layers.

        Adds routing metadata and preserves original context.
        """
        target = self.route_request(context)

        return {
            "request_id": context.request_id,
            "source": context.source,
            "intent": context.intent,
            "evidence_ref": context.evidence_ref,
            "route_target": {
                "layer": target.layer,
                "module": target.module,
                "action": target.action,
            },
            "routing_decision": "internal_router",
        }
