from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class DeliveryAuditCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    details: str | None = None


class DeliveryAuditInput(BaseModel):
    """
    Minimal Audit-side delivery input sourced from DeliveryReleaseInput.

    This object is only an Audit-consumable pre-execution structure. It is not
    an external execution approval, runtime control object, or integration action.
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
    integrity_checks: list[DeliveryAuditCheck] = []
    handoff_payload: dict[str, Any] | None = None
