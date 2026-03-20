from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ReleaseValidationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str | None = None
    summary: str | None = None


class ReleaseValidationInput(BaseModel):
    """
    Minimal Release-side validation input sourced from ReviewValidationInput.

    This object is only a Release-consumable pre-audit input. It is not a
    release decision, publish approval, or audit execution result.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: str
    candidate_id: str
    checks: list[ReleaseValidationCheck]
    summary: dict[str, Any]
    handoff_ready: bool
    build_validation_status: str

    missing_artifacts: list[str] = []
    broken_references: list[str] = []
    smoke_test_result: dict[str, Any] | None = None
    trace_result: dict[str, Any] | None = None
