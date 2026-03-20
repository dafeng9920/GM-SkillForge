"""
API Interface Definition

Defines the contract for API boundary layer preparation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestContext:
    """Immutable context for internal request processing."""
    request_id: str
    source: str  # "api" | "handler" | "internal"
    intent: Optional[str] = None
    evidence_ref: Optional[str] = None


@dataclass(frozen=True)
class ApiRequest:
    """Minimal API request structure (placeholder, no real HTTP)."""
    request_id: str
    request_type: str
    payload: Dict[str, Any]
    evidence_ref: Optional[str] = None


@dataclass(frozen=True)
class ApiResponse:
    """Minimal API response structure (placeholder, no real HTTP)."""
    request_id: str
    status: str  # "pending" | "accepted" | "rejected"
    message: str
    data: Optional[Dict[str, Any]] = None
    routing_target: Optional[Dict[str, str]] = None


class ApiInterface(ABC):
    """
    Abstract interface for API layer preparation.

    Responsibilities:
    - Accept external-style requests (minimal placeholders)
    - Adapt to orchestrator context
    - Prepare response structure

    Non-Responsibilities:
    - NO real HTTP protocol handling
    - NO external API exposure
    - NO real authentication/authorization
    - NO webhook/queue/db integration
    """

    @abstractmethod
    def accept_request(self, request: ApiRequest) -> tuple[bool, List[str]]:
        """
        Validate request meets minimal acceptance criteria.

        Returns:
            (accepted, rejection_reasons) tuple
        """
        pass

    @abstractmethod
    def to_routing_context(self, request: ApiRequest) -> RequestContext:
        """Convert API request to orchestrator routing context."""
        pass

    @abstractmethod
    def from_routing_result(self, request_id: str, result: Dict[str, Any]) -> ApiResponse:
        """Convert routing result to API response."""
        pass
