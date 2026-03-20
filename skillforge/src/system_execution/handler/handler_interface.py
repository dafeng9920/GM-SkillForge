"""
Handler Interface Definition

Defines the contract for input acceptance and call forwarding.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class HandlerInput:
    """Immutable input for handler layer."""
    request_id: str
    source: str  # "api" | "orchestrator" | "service"
    action: str
    payload: Dict[str, Any]
    evidence_ref: Optional[str] = None


@dataclass(frozen=True)
class ForwardTarget:
    """Immutable forwarding target specification."""
    layer: str  # "service" | "orchestrator"
    module: str
    method: str


class HandlerInterface(ABC):
    """
    Abstract interface for handler layer.

    Responsibilities:
    - Accept structured input from upstream
    - Forward calls to appropriate service/orchestrator
    - Prepare context for downstream layers

    Non-Responsibilities:
    - NO side effects (delegates to service)
    - NO runtime branch control (delegates to orchestrator)
    - NO external integrations (delegates to service)
    """

    @abstractmethod
    def accept_input(self, handler_input: HandlerInput) -> tuple[bool, List[str]]:
        """
        Validate input meets acceptance criteria.

        Returns:
            (accepted, rejection_reasons) tuple
        """
        pass

    @abstractmethod
    def forward_call(self, handler_input: HandlerInput) -> ForwardTarget:
        """
        Determine where to forward the call.

        Returns:
            ForwardTarget with destination layer/module/method
        """
        pass

    @abstractmethod
    def prepare_forward_context(self, handler_input: HandlerInput) -> Dict[str, Any]:
        """
        Prepare context for downstream layers.

        Returns:
            Enriched context dict
        """
        pass
