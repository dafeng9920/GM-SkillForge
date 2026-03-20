from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class DeliveryReviewCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    details: str | None = None


class DeliveryReviewInput(BaseModel):
    """
    Minimal Review-side delivery input sourced from PrePackagingGateInput.

    This object is only a Review-consumable pre-release structure. It is not a
    release permit, publish approval, or audit ownership result.
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
    integrity_checks: list[DeliveryReviewCheck] = []
    handoff_payload: dict[str, Any] | None = None
