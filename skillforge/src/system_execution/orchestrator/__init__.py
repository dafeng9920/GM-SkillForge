"""
System Execution Orchestrator

HARD CONSTRAINTS:
- This module is INTERNAL ROUTING and ACCEPTANCE only
- NO governance decision-making (delegates to gates/contracts)
- NO runtime control (preparation only)
- NO external integrations (delegates to service layer)
"""

from .internal_router import InternalRouter
from .acceptance_boundary import AcceptanceBoundary
from .orchestrator_interface import OrchestratorInterface

__all__ = [
    "InternalRouter",
    "AcceptanceBoundary",
    "OrchestratorInterface",
]
