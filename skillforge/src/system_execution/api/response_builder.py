"""
Response Builder Module

Builds API responses from routing results.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from .api_interface import ApiResponse


class ResponseBuilder:
    """
    Builds API responses from routing results.

    CONSTRAINTS:
    - Does NOT implement real HTTP protocol
    - Does NOT serialize to JSON/XML/etc
    - Only prepares response structure
    """

    def build_accepted(self, request_id: str, routing_result: Dict[str, Any]) -> ApiResponse:
        """
        Build accepted response with routing target.

        Args:
            request_id: Original request ID
            routing_result: Result from orchestrator prepare_context()

        Returns ApiResponse with routing target info.
        """
        return ApiResponse(
            request_id=request_id,
            status="accepted",
            message="Request accepted and routed",
            routing_target=routing_result.get("route_target"),
        )

    def build_rejected(self, request_id: str, reasons: list[str]) -> ApiResponse:
        """
        Build rejected response.

        Args:
            request_id: Original request ID
            reasons: List of rejection reasons

        Returns ApiResponse with rejection info.
        """
        return ApiResponse(
            request_id=request_id,
            status="rejected",
            message="Request rejected",
            data={"reasons": reasons},
        )

    def build_pending(self, request_id: str, message: str) -> ApiResponse:
        """
        Build pending response.

        Args:
            request_id: Original request ID
            message: Pending status message

        Returns ApiResponse with pending status.
        """
        return ApiResponse(
            request_id=request_id,
            status="pending",
            message=message,
        )
