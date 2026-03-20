"""
API Layer Preparation (Minimal Landing)

This module provides minimal API boundary interface preparation.
Does NOT expose real external protocols or integrations.
"""

from .api_interface import (
    ApiInterface,
    ApiRequest,
    ApiResponse,
    RequestContext,
)
from .request_adapter import RequestAdapter
from .response_builder import ResponseBuilder

__all__ = [
    "ApiInterface",
    "ApiRequest",
    "ApiResponse",
    "RequestContext",
    "RequestAdapter",
    "ResponseBuilder",
]
