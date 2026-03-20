from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class GovernanceValidationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str | None = None
    summary: str | None = None


class GovernanceValidationIntakePayload(BaseModel):
    """
    Minimal bridge payload sourced from BuildValidationReport.

    This payload is only governance-consumable input from the production-side
    validation layer. It is not a governance validation result and must not be
    read as pass/fail, validated, or release judgment.
    """

    model_config = ConfigDict(extra="forbid")

    payload_type: Literal["GovernanceValidationIntakePayload"] = "GovernanceValidationIntakePayload"
    source_object: Literal["BuildValidationReport"] = "BuildValidationReport"
    report_id: str
    candidate_id: str
    checks: list[GovernanceValidationCheck]
    summary: dict[str, Any]
    handoff_ready: bool
    build_validation_status: str

    missing_artifacts: list[str] = []
    broken_references: list[str] = []
    smoke_test_result: dict[str, Any] | None = None
    trace_result: dict[str, Any] | None = None
    boundary_note: str | None = None

