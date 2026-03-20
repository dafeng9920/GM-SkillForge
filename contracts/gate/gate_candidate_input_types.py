from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class GateCandidateGeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    kind: str
    required: bool


class GateCandidateEntrypoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    path: str | None = None
    kind: str | None = None


class GateCandidateInput(BaseModel):
    """
    Minimal Gate-side candidate input object sourced from GovernanceCandidateIntake.

    This object is only a Gate-consumable pre-review input. It is not a gate
    verdict, review decision, or release signal.
    """

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    intent_id: str
    contract_id: str
    skill_root: str
    generated_files: list[GateCandidateGeneratedFile]
    production_status: str

    candidate_name: str | None = None
    entrypoints: list[GateCandidateEntrypoint] = []
    dependencies: dict[str, Any] | None = None
    required_changes: list[dict[str, Any]] = []

