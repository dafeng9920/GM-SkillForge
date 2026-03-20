from __future__ import annotations

from typing import Any

from contracts.production.contract.contract_bundle_model import ContractBundle
from contracts.production.intent.intent_draft_model import IntentDraft


def build_contract_bundle(
    intent: IntentDraft,
    contract_spec: dict[str, Any],
    *,
    contract_id: str,
) -> ContractBundle:
    """
    Minimal IntentDraft -> ContractBundle assembler.

    This function only maps production-layer fields and keeps `validated` as a
    compatibility-only status value if present in input.
    """

    return ContractBundle(
        contract_id=contract_id,
        intent_id=intent.intent_id,
        summary=contract_spec.get("summary"),
        version=contract_spec.get("version"),
        input_schema=contract_spec["input_schema"],
        output_schema=contract_spec["output_schema"],
        state_schema=contract_spec["state_schema"],
        error_schema=contract_spec["error_schema"],
        trigger_spec=contract_spec["trigger_spec"],
        evidence_spec=contract_spec["evidence_spec"],
        required_gates=contract_spec.get("required_gates", intent.required_gates),
        status=contract_spec.get("status", "draft"),
    )
