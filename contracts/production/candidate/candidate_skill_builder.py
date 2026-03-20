from __future__ import annotations

from typing import Any

from contracts.production.candidate.candidate_skill_model import CandidateSkill
from contracts.production.contract.contract_bundle_model import ContractBundle


def build_candidate_skill(
    contract: ContractBundle,
    candidate_spec: dict[str, Any],
    *,
    candidate_id: str,
) -> CandidateSkill:
    """
    Minimal ContractBundle -> CandidateSkill assembler.

    This function creates the candidate object only. It does not trigger
    validation, review, packaging, or any external side effect.
    """

    return CandidateSkill(
        candidate_id=candidate_id,
        intent_id=contract.intent_id,
        contract_id=contract.contract_id,
        candidate_name=candidate_spec.get("candidate_name"),
        skill_root=candidate_spec["skill_root"],
        directory_layout=candidate_spec["directory_layout"],
        generated_files=candidate_spec["generated_files"],
        entrypoints=candidate_spec.get("entrypoints", []),
        dependencies=candidate_spec.get("dependencies"),
        required_changes=candidate_spec.get("required_changes", []),
        status=candidate_spec.get("status", "draft_candidate"),
    )
