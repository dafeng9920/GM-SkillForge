from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class GateValidationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str | None = None
    summary: str | None = None


class GateValidationInput(BaseModel):
    """
    Minimal Gate-side validation input object sourced from GovernanceValidationIntake.

    This object is only a Gate-consumable input for pre-review gating structure.
    It is not a governance validation result, gate verdict, or audit outcome.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: str
    candidate_id: str
    checks: list[GateValidationCheck]
    summary: dict[str, Any]
    handoff_ready: bool
    build_validation_status: str

    missing_artifacts: list[str] = []
    broken_references: list[str] = []
    smoke_test_result: dict[str, Any] | None = None
    trace_result: dict[str, Any] | None = None

