"""
System Execution Handler

HARD CONSTRAINTS:
- This module is INPUT ACCEPTANCE and CALL FORWARDING only
- NO side effects (delegates to service layer)
- NO runtime branch control
- NO external integrations
"""

from .handler_interface import HandlerInterface
from .input_acceptance import InputAcceptance
from .call_forwarder import CallForwarder

__all__ = [
    "HandlerInterface",
    "InputAcceptance",
    "CallForwarder",
]
