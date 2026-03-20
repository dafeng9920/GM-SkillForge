from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewValidationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str | None = None
    summary: str | None = None


class ReviewValidationInput(BaseModel):
    """
    Minimal Review-side validation input sourced from GateValidationInput.

    This object is only a Review-consumable pre-release input. It is not a
    review verdict, release decision, or audit execution result.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: str
    candidate_id: str
    checks: list[ReviewValidationCheck]
    summary: dict[str, Any]
    handoff_ready: bool
    build_validation_status: str

    missing_artifacts: list[str] = []
    broken_references: list[str] = []
    smoke_test_result: dict[str, Any] | None = None
    trace_result: dict[str, Any] | None = None
