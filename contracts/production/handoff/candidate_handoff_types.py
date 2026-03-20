from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from contracts.production.candidate.candidate_skill_model import CandidateSkill
from contracts.production.contract.contract_bundle_model import ContractBundle
from contracts.production.intent.intent_draft_model import IntentDraft


ALLOWED_CALLERS = ("intent-compiler", "contract-assembler")
FORBIDDEN_CALLERS = ("governor", "release-manager", "skill-creator")


class CandidateHandoffInput(BaseModel):
    """
    Type placeholder only.

    It defines the payload shape between candidate assembly stages. It is not
    an execution function, workflow binding, or orchestration entrypoint.
    """

    model_config = ConfigDict(extra="allow")

    intent: IntentDraft
    contract: ContractBundle
    candidate: CandidateSkill


class CandidateHandoffOutput(BaseModel):
    """
    Type placeholder only.

    It describes the structural output of candidate handoff. It does not imply
    that any workflow, router, or service has been implemented.
    """

    model_config = ConfigDict(extra="allow")

    candidate_id: str
    accepted: bool
    next_stage: Literal["build_validation"]
    note: str | None = None


class CandidateHandoffError(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str
    message: str
    retriable: bool = False
