"""
Orchestrator Interface Definition

Defines the contract between orchestrator and upstream (api/handler) layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class RouteTarget:
    """Immutable routing target specification."""
    layer: str  # "service" | "handler" | "external"
    module: str
    action: str


@dataclass(frozen=True)
class RoutingContext:
    """Immutable context for routing decisions."""
    request_id: str
    source: str  # "api" | "handler" | "internal"
    intent: Optional[str] = None
    evidence_ref: Optional[str] = None


class OrchestratorInterface(ABC):
    """
    Abstract interface for orchestrator preparation.

    Responsibilities:
    - Define routing boundaries
    - Accept upstream requests
    - Prepare context for service/handler layers

    Non-Responsibilities:
    - NO governance decisions (delegates to gates)
    - NO runtime execution (delegates to service)
    - NO external effects (delegates to handler)
    """

    @abstractmethod
    def route_request(self, context: RoutingContext) -> RouteTarget:
        """Determine which service/handler should handle the request."""
        pass

    @abstractmethod
    def validate_acceptance(self, context: RoutingContext) -> tuple[bool, List[str]]:
        """
        Validate that request meets acceptance criteria.

        Returns:
            (accepted, reasons) tuple
        """
        pass

    @abstractmethod
    def prepare_context(self, context: RoutingContext) -> Dict[str, Any]:
        """Prepare enriched context for downstream layers."""
        pass
