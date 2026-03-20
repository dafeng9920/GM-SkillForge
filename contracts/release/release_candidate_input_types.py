from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ReleaseCandidateGeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    kind: str
    required: bool


class ReleaseCandidateEntrypoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    path: str | None = None
    kind: str | None = None


class ReleaseCandidateInput(BaseModel):
    """
    Minimal Release-side candidate input sourced from ReviewCandidateInput.

    This object is only a Release-consumable pre-audit input. It is not a
    release decision, publish approval, or audit ownership result.
    """

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    intent_id: str
    contract_id: str
    skill_root: str
    generated_files: list[ReleaseCandidateGeneratedFile]
    production_status: str

    candidate_name: str | None = None
    entrypoints: list[ReleaseCandidateEntrypoint] = []
    dependencies: dict[str, Any] | None = None
    required_changes: list[dict[str, Any]] = []
