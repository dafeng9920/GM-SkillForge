from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditCandidateGeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    kind: str
    required: bool


class AuditCandidateEntrypoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    path: str | None = None
    kind: str | None = None


class AuditCandidateInput(BaseModel):
    """
    Minimal Audit-side candidate input sourced from ReleaseCandidateInput.

    This object is only an Audit-consumable pre-execution input. It is not a
    runtime control object, external execution approval, or orchestration signal.
    """

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    intent_id: str
    contract_id: str
    skill_root: str
    generated_files: list[AuditCandidateGeneratedFile]
    production_status: str

    candidate_name: str | None = None
    entrypoints: list[AuditCandidateEntrypoint] = []
    dependencies: dict[str, Any] | None = None
    required_changes: list[dict[str, Any]] = []
