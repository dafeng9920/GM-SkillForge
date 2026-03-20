from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


DeliveryHandoffTarget = Literal["skill_creator", "internal_packer"]
DeliveryManifestStatus = Literal["prepared", "handed_off", "package_failed", "delivered"]


class DeliveryIntegrityCheck(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    status: str | None = None
    details: str | None = None


class DeliveryManifest(BaseModel):
    """
    Delivery handoff object for the packaging layer.

    `delivered` must not be interpreted as released or publish-approved.
    This object is consumed by packaging-oriented downstream layers only. It is
    not a permit, release decision, or audit result.
    """

    model_config = ConfigDict(extra="allow")

    delivery_id: str
    candidate_id: str
    validation_report_id: str
    package_input_root: str
    handoff_target: DeliveryHandoffTarget
    package_manifest: dict[str, Any]
    status: DeliveryManifestStatus

    delivery_name: str | None = None
    integrity_checks: list[DeliveryIntegrityCheck] = []
    handoff_payload: dict[str, Any] | None = None
