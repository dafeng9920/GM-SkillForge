from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


CandidateSkillStatus = Literal[
    "draft_candidate",
    "compiled",
    "compile_failed",
    "handed_to_validation",
]


class GeneratedFileSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    path: str
    kind: str
    required: bool


class CandidateEntrypoint(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    path: str | None = None
    kind: str | None = None


class CandidateSkill(BaseModel):
    """
    Candidate skill object in the production chain.

    Upstream reference: IntentDraft / ContractBundle by `intent_id` and
    `contract_id`.
    Downstream consumer: BuildValidationReport by `candidate_id`.
    Boundary: `handed_to_validation` is a production handoff state only, not a
    governance review or release state.
    """

    model_config = ConfigDict(extra="allow")

    candidate_id: str
    intent_id: str
    contract_id: str
    skill_root: str
    directory_layout: dict[str, Any]
    generated_files: list[GeneratedFileSpec]
    status: CandidateSkillStatus

    candidate_name: str | None = None
    entrypoints: list[CandidateEntrypoint] = []
    dependencies: dict[str, Any] | None = None
    required_changes: list[dict[str, Any]] = []
