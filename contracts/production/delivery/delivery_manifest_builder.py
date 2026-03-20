from __future__ import annotations

from typing import Any

from contracts.production.candidate.candidate_skill_model import CandidateSkill
from contracts.production.delivery.delivery_manifest_model import DeliveryManifest
from contracts.production.validation.build_validation_report_model import BuildValidationReport


def build_delivery_manifest(
    candidate: CandidateSkill,
    validation_report: BuildValidationReport,
    delivery_spec: dict[str, Any],
    *,
    delivery_id: str,
) -> DeliveryManifest:
    """
    Minimal BuildValidationReport -> DeliveryManifest assembler.

    This builder produces a packaging-layer handoff object only. It is not a
    release permit or publish decision.
    """

    return DeliveryManifest(
        delivery_id=delivery_id,
        candidate_id=candidate.candidate_id,
        validation_report_id=validation_report.report_id,
        delivery_name=delivery_spec.get("delivery_name"),
        package_input_root=delivery_spec["package_input_root"],
        handoff_target=delivery_spec["handoff_target"],
        package_manifest=delivery_spec["package_manifest"],
        integrity_checks=delivery_spec.get("integrity_checks", []),
        handoff_payload=delivery_spec.get("handoff_payload"),
        status=delivery_spec.get("status", "prepared"),
    )
