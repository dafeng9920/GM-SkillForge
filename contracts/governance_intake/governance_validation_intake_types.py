from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class GovernanceValidationIntakeCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    severity: str | None = None
    summary: str | None = None


class GovernanceValidationIntake(BaseModel):
    """
    Governance-consumable validation intake object sourced from bridge payload.

    Upstream relation: GovernanceValidationIntakePayload.
    This object is not a GovernanceValidation result, gate outcome, audit
    result, or release judgment. It only carries build-side validation context
    into a governance intake boundary.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: str
    candidate_id: str
    checks: list[GovernanceValidationIntakeCheck]
    summary: dict[str, Any]
    handoff_ready: bool
    build_validation_status: str

    missing_artifacts: list[str] = []
    broken_references: list[str] = []
    smoke_test_result: dict[str, Any] | None = None
    trace_result: dict[str, Any] | None = None

