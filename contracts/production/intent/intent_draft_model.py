from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


IntentDraftStatus = Literal["draft", "reviewed", "locked", "rejected"]


class IntentFieldSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    type: str
    required: bool
    description: str | None = None


class IntentConstraint(BaseModel):
    model_config = ConfigDict(extra="allow")

    key: str
    value: Any
    description: str | None = None


class IntentDraft(BaseModel):
    """
    Production-line intent object.

    Role: the structured entry object for the 5-layer creation chain.
    Boundary: not a governance object, not a release object, not a decision
    carrier.
    """

    model_config = ConfigDict(extra="allow")

    intent_id: str
    summary: str
    goal: str
    in_scope: list[str]
    out_of_scope: list[str]
    inputs: list[IntentFieldSpec]
    outputs: list[IntentFieldSpec]
    constraints: list[IntentConstraint]
    required_gates: list[str]
    status: IntentDraftStatus

    intent_name: str | None = None
    problem_statement: str | None = None

    # Compatibility-only metadata retained from schema/sample layer.
    # These fields are descriptive only and do not change chain behavior.
    created_at: str | None = Field(default=None, description="Compatibility metadata only.")
    updated_at: str | None = Field(default=None, description="Compatibility metadata only.")
    revision: str | None = Field(default=None, description="Compatibility metadata only.")
