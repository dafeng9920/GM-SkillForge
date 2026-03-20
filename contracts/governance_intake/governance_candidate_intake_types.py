from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class GovernanceCandidateIntakeGeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    kind: str
    required: bool


class GovernanceCandidateIntakeEntrypoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    path: str | None = None
    kind: str | None = None


class GovernanceCandidateIntake(BaseModel):
    """
    Governance-consumable candidate intake object sourced from bridge payload.

    Upstream relation: GovernanceCandidateIntakePayload.
    This object is not a governance-approved candidate, gate decision, review
    result, or release signal. It only preserves the minimal intake-ready
    candidate context for later governance layers.
    """

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    intent_id: str
    contract_id: str
    skill_root: str
    generated_files: list[GovernanceCandidateIntakeGeneratedFile]
    production_status: str

    candidate_name: str | None = None
    entrypoints: list[GovernanceCandidateIntakeEntrypoint] = []
    dependencies: dict[str, Any] | None = None
    required_changes: list[dict[str, Any]] = []

