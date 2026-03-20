from __future__ import annotations

from typing import Any

from contracts.production.candidate.candidate_skill_builder import build_candidate_skill
from contracts.production.candidate.candidate_skill_model import CandidateSkill
from contracts.production.contract.contract_bundle_builder import build_contract_bundle
from contracts.production.contract.contract_bundle_model import ContractBundle
from contracts.production.delivery.delivery_manifest_builder import build_delivery_manifest
from contracts.production.delivery.delivery_manifest_model import DeliveryManifest
from contracts.production.intent.intent_draft_builder import build_intent_draft
from contracts.production.intent.intent_draft_model import IntentDraft
from contracts.production.validation.build_validation_report_builder import build_validation_report
from contracts.production.validation.build_validation_report_model import BuildValidationReport


class ProductionChainResult:
    """
    Minimal in-memory assembly result for the 5-object production chain.

    This is not a workflow runner, orchestrator binding, governance pipeline,
    or release pipeline.
    """

    def __init__(
        self,
        *,
        intent: IntentDraft,
        contract: ContractBundle,
        candidate: CandidateSkill,
        validation_report: BuildValidationReport,
        delivery_manifest: DeliveryManifest,
    ) -> None:
        self.intent = intent
        self.contract = contract
        self.candidate = candidate
        self.validation_report = validation_report
        self.delivery_manifest = delivery_manifest


def assemble_minimal_production_chain(payload: dict[str, Any]) -> ProductionChainResult:
    """
    Assemble the minimal production chain:

    Requirement -> IntentDraft -> ContractBundle -> CandidateSkill
    -> BuildValidationReport -> DeliveryManifest

    The payload must already contain the source data for each object. This
    function only performs object construction and field wiring.
    """

    intent = build_intent_draft(
        payload["requirement"],
        intent_id=payload["intent_id"],
        required_gates=payload.get("required_gates", []),
    )
    contract = build_contract_bundle(
        intent,
        payload["contract_spec"],
        contract_id=payload["contract_id"],
    )
    candidate = build_candidate_skill(
        contract,
        payload["candidate_spec"],
        candidate_id=payload["candidate_id"],
    )
    validation_report = build_validation_report(
        candidate,
        payload["validation_spec"],
        report_id=payload["report_id"],
    )
    delivery_manifest = build_delivery_manifest(
        candidate,
        validation_report,
        payload["delivery_spec"],
        delivery_id=payload["delivery_id"],
    )
    return ProductionChainResult(
        intent=intent,
        contract=contract,
        candidate=candidate,
        validation_report=validation_report,
        delivery_manifest=delivery_manifest,
    )
