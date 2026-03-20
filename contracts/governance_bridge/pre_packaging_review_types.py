from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class PrePackagingIntegrityCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    details: str | None = None


class PrePackagingReviewIntakePayload(BaseModel):
    """
    Minimal bridge payload sourced from DeliveryManifest.

    This payload is only a pre-packaging review input object. It is not a
    release permit, publish approval, or release-ready decision object.
    skill-creator remains downstream in the packaging layer and is not moved
    into this bridge payload.
    """

    model_config = ConfigDict(extra="forbid")

    payload_type: Literal["PrePackagingReviewIntakePayload"] = "PrePackagingReviewIntakePayload"
    source_object: Literal["DeliveryManifest"] = "DeliveryManifest"
    delivery_id: str
    candidate_id: str
    validation_report_id: str
    package_input_root: str
    handoff_target: str
    package_manifest: dict[str, Any]
    delivery_status: str

    delivery_name: str | None = None
    integrity_checks: list[PrePackagingIntegrityCheck] = []
    handoff_payload: dict[str, Any] | None = None
    boundary_note: str | None = None

