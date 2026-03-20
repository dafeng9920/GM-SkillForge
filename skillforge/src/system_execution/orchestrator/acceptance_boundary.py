"""
Acceptance Boundary Module

Defines what requests are accepted for internal routing.
Does NOT grant permits or make governance decisions.
"""

from __future__ import annotations

from typing import List
from .orchestrator_interface import RoutingContext


class AcceptanceBoundary:
    """
    Acceptance criteria for orchestrator layer.

    CONSTRAINTS:
    - Checks ONLY structural validity
    - Does NOT evaluate governance permits
    - Does NOT check business rules

    Accepted requests must:
    1. Have valid request_id
    2. Have known source
    3. NOT be empty/malformed

    Governance/permit checks happen at gate layer, NOT here.
    """

    # Known sources
    _KNOWN_SOURCES = {"api", "handler", "internal"}

    def validate(self, context: RoutingContext) -> tuple[bool, List[str]]:
        """
        Validate request meets acceptance criteria.

        Returns:
            (accepted, rejection_reasons)

        Note: This is NOT a governance check.
        Governance checks happen at gate layer.
        """
        reasons: List[str] = []

        # Check 1: request_id must be non-empty
        if not context.request_id or not context.request_id.strip():
            reasons.append("request_id is required")

        # Check 2: source must be known
        if context.source not in self._KNOWN_SOURCES:
            reasons.append(f"unknown source: {context.source}")

        # Check 3: evidence_ref is optional but if provided, must be string
        if context.evidence_ref is not None and not isinstance(context.evidence_ref, str):
            reasons.append("evidence_ref must be a string")

        return (len(reasons) == 0, reasons)

    def is_internal_only(self, context: RoutingContext) -> bool:
        """
        Check if request should remain internal (no external routing).

        Returns True if source is "internal" or "handler".
        """
        return context.source in {"internal", "handler"}
