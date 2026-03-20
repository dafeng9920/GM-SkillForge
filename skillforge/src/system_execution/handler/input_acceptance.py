"""
Input Acceptance Module

Handles input validation and acceptance for handler layer.
Does NOT make business decisions or trigger side effects.
"""

from __future__ import annotations

from typing import List
from .handler_interface import HandlerInput


class InputAcceptance:
    """
    Input acceptance criteria for handler layer.

    CONSTRAINTS:
    - Checks ONLY structural validity
    - Does NOT evaluate business rules
    - Does NOT trigger side effects

    Accepted inputs must:
    1. Have valid request_id
    2. Have known source
    3. Have valid action
    4. Have valid payload structure

    Business rule checks happen at service/gate layer, NOT here.
    """

    # Known sources
    _KNOWN_SOURCES = {"api", "orchestrator", "service"}

    # Known actions (minimal set for preparation)
    _KNOWN_ACTIONS = {
        "query",
        "status",
        "forward",
        "dispatch",
    }

    def validate(self, handler_input: HandlerInput) -> tuple[bool, List[str]]:
        """
        Validate input meets acceptance criteria.

        Returns:
            (accepted, rejection_reasons)

        Note: This is NOT a business rule check.
        Business checks happen at service/gate layer.
        """
        reasons: List[str] = []

        # Check 1: request_id must be non-empty
        if not handler_input.request_id or not handler_input.request_id.strip():
            reasons.append("request_id is required")

        # Check 2: source must be known
        if handler_input.source not in self._KNOWN_SOURCES:
            reasons.append(f"unknown source: {handler_input.source}")

        # Check 3: action must be known
        if handler_input.action not in self._KNOWN_ACTIONS:
            reasons.append(f"unknown action: {handler_input.action}")

        # Check 4: payload must be a dict
        if not isinstance(handler_input.payload, dict):
            reasons.append("payload must be a dictionary")

        # Check 5: evidence_ref is optional but if provided, must be string
        if handler_input.evidence_ref is not None and not isinstance(handler_input.evidence_ref, str):
            reasons.append("evidence_ref must be a string")

        return (len(reasons) == 0, reasons)

    def is_forwardable(self, handler_input: HandlerInput) -> bool:
        """
        Check if input should be forwarded to service layer.

        Returns True if source is "api" or "orchestrator".
        """
        return handler_input.source in {"api", "orchestrator"}
