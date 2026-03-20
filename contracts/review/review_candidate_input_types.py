from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewCandidateGeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    kind: str
    required: bool


class ReviewCandidateEntrypoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    path: str | None = None
    kind: str | None = None


class ReviewCandidateInput(BaseModel):
    """
    Minimal Review-side candidate input sourced from GateCandidateInput.

    This object is only a Review-consumable pre-release input. It is not a
    review decision, release permit, or audit result.
    """

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    intent_id: str
    contract_id: str
    skill_root: str
    generated_files: list[ReviewCandidateGeneratedFile]
    production_status: str

    candidate_name: str | None = None
    entrypoints: list[ReviewCandidateEntrypoint] = []
    dependencies: dict[str, Any] | None = None
    required_changes: list[dict[str, Any]] = []
