from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class PrePackagingGateCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    details: str | None = None


class PrePackagingGateInput(BaseModel):
    """
    Minimal Gate-side pre-packaging input sourced from PrePackagingReviewIntake.

    This object is only a Gate-consumable pre-review input. It is not a release
    permit, publish approval, or release-ready decision.
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
    integrity_checks: list[PrePackagingGateCheck] = []
    handoff_payload: dict[str, Any] | None = None

