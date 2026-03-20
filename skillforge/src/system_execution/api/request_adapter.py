"""
Request Adapter Module

Adapts API requests to orchestrator routing context.
"""

from __future__ import annotations

from typing import Any, Dict, List
from .api_interface import ApiRequest, RequestContext


class RequestAdapter:
    """
    Adapts API requests to orchestrator context.

    CONSTRAINTS:
    - Does NOT handle real HTTP protocol
    - Does NOT validate business rules
    - Only adapts structure for routing
    """

    # Known request types (placeholder mapping)
    _KNOWN_REQUEST_TYPES = {
        "governance_query",
        "governance_status",
        "skill_execution",
        "data_processing",
        "pipeline_submit",
        "pipeline_status",
    }

    def adapt(self, request: ApiRequest) -> RequestContext:
        """
        Adapt API request to routing context.

        Returns RequestContext for orchestrator layer.
        """
        return RequestContext(
            request_id=request.request_id,
            source="api",
            intent=request.request_type if request.request_type in self._KNOWN_REQUEST_TYPES else None,
            evidence_ref=request.evidence_ref,
        )

    def validate_request_structure(self, request: ApiRequest) -> tuple[bool, List[str]]:
        """
        Validate minimal request structure.

        Returns (accepted, rejection_reasons)
        """
        reasons: List[str] = []

        # Check 1: request_id must be non-empty
        if not request.request_id or not request.request_id.strip():
            reasons.append("request_id is required")

        # Check 2: request_type must be non-empty
        if not request.request_type or not request.request_type.strip():
            reasons.append("request_type is required")

        # Check 3: evidence_ref is optional but if provided, must be string
        if request.evidence_ref is not None and not isinstance(request.evidence_ref, str):
            reasons.append("evidence_ref must be a string")

        return (len(reasons) == 0, reasons)
