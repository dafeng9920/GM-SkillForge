from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ContractBundleStatus = Literal["draft", "validated", "rejected", "frozen"]


class ContractBundle(BaseModel):
    """
    Production contract object.

    `status="validated"` is retained for compatibility only. It is not a
    governance validated state and must not be used for gate/release semantics.
    This object only serves the 5-layer creation chain between IntentDraft and
    CandidateSkill. It is not a release-ready or audit-ready decision object.
    """

    model_config = ConfigDict(extra="allow")

    contract_id: str
    intent_id: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    state_schema: dict[str, Any]
    error_schema: dict[str, Any]
    trigger_spec: dict[str, Any]
    evidence_spec: dict[str, Any]
    required_gates: list[str]
    status: ContractBundleStatus = Field(
        description=(
            "Compatibility-only production status. Not governance validated. "
            "Not a gate pass signal. Not a release-ready signal."
        )
    )

    summary: str | None = None
    version: str | None = None
