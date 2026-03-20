from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class PrePackagingReviewIntakeCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    details: str | None = None


class PrePackagingReviewIntake(BaseModel):
    """
    Governance-side pre-packaging review intake object sourced from bridge payload.

    Upstream relation: PrePackagingReviewIntakePayload.
    This object is not a release permit, publish approval, or release-ready
    decision. skill-creator remains downstream in packaging and is not moved
    into this intake boundary.
    """

    model_config = ConfigDict(extra="forbid")

    delivery_id: str
    candidate_id: str
    validation_report_id: str
    package_input_root: str
    handoff_target: str
    package_manifest: dict[str, Any]
    delivery_status: str

    delivery_name: str | None = None
    integrity_checks: list[PrePackagingReviewIntakeCheck] = []
    handoff_payload: dict[str, Any] | None = None

