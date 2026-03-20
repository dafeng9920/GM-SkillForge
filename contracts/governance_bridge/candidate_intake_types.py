from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class GovernanceCandidateGeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    kind: str
    required: bool


class GovernanceCandidateEntrypoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    path: str | None = None
    kind: str | None = None


class GovernanceCandidateIntakePayload(BaseModel):
    """
    Minimal bridge payload sourced from CandidateSkill.

    This object is only a governance intake input payload. It is not an
    approved candidate, gate-pass signal, or release-ready object.
    Downstream intake relation: future governance intake may consume it, but no
    execution or decision logic exists in this object.
    """

    model_config = ConfigDict(extra="forbid")

    payload_type: Literal["GovernanceCandidateIntakePayload"] = "GovernanceCandidateIntakePayload"
    source_object: Literal["CandidateSkill"] = "CandidateSkill"
    candidate_id: str
    intent_id: str
    contract_id: str
    skill_root: str
    generated_files: list[GovernanceCandidateGeneratedFile]
    production_status: str

    candidate_name: str | None = None
    entrypoints: list[GovernanceCandidateEntrypoint] = []
    dependencies: dict[str, Any] | None = None
    required_changes: list[dict[str, Any]] = []
    boundary_note: str | None = None

