from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class DeliveryReleaseCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    details: str | None = None


class DeliveryReleaseInput(BaseModel):
    """
    Minimal Release-side delivery input sourced from DeliveryReviewInput.

    This object is only a Release-consumable pre-audit structure. It is not a
    publish approval, audit ownership result, or audit execution object.
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
    integrity_checks: list[DeliveryReleaseCheck] = []
    handoff_payload: dict[str, Any] | None = None
