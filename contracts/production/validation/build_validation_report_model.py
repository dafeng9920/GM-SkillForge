from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


BuildCheckStatus = Literal["PASS", "FAIL", "WARN", "SKIP"]
BuildValidationStatus = Literal["verified_candidate", "validation_failed", "partially_verified"]


class BuildValidationCheck(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    status: BuildCheckStatus
    severity: str | None = None
    summary: str | None = None


class BuildValidationReport(BaseModel):
    """
    Build-side validation object only.

    It must not be interpreted as governance validation.
    Upstream reference: CandidateSkill by `candidate_id`.
    Downstream consumer: DeliveryManifest by `report_id` / `validation_report_id`.
    """

    model_config = ConfigDict(extra="allow")

    report_id: str
    candidate_id: str
    checks: list[BuildValidationCheck]
    summary: dict[str, Any]
    handoff_ready: bool
    status: BuildValidationStatus

    missing_artifacts: list[str] = []
    broken_references: list[str] = []
    smoke_test_result: dict[str, Any] | None = None
    trace_result: dict[str, Any] | None = None
