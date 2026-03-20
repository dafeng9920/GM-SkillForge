from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditValidationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str | None = None
    summary: str | None = None


class AuditValidationInput(BaseModel):
    """
    Minimal Audit-side validation input sourced from ReleaseValidationInput.

    This object is only an Audit-consumable pre-execution input. It is not a
    runtime verdict, execution route, or external integration trigger.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: str
    candidate_id: str
    checks: list[AuditValidationCheck]
    summary: dict[str, Any]
    handoff_ready: bool
    build_validation_status: str

    missing_artifacts: list[str] = []
    broken_references: list[str] = []
    smoke_test_result: dict[str, Any] | None = None
    trace_result: dict[str, Any] | None = None
