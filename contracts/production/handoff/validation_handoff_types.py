from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from contracts.production.candidate.candidate_skill_model import CandidateSkill
from contracts.production.contract.contract_bundle_model import ContractBundle
from contracts.production.validation.build_validation_report_model import BuildValidationReport


ALLOWED_CALLERS = ("candidate-builder", "build-validator")
FORBIDDEN_CALLERS = ("governor", "release-manager", "audit-pack-builder")


class ValidationHandoffInput(BaseModel):
    """
    Type placeholder only.

    It defines the payload shape for build validation handoff. It does not
    implement validation execution, workflow binding, or orchestration logic.
    """

    model_config = ConfigDict(extra="allow")

    candidate: CandidateSkill
    contract: ContractBundle


class ValidationHandoffOutput(BaseModel):
    """
    Type placeholder only.

    It only carries structural output toward DeliveryManifest preparation. It
    does not encode review, audit, or release semantics.
    """

    model_config = ConfigDict(extra="allow")

    report: BuildValidationReport
    accepted: bool
    next_stage: Literal["delivery_manifest"]
    note: str | None = None


class ValidationHandoffError(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str
    message: str
    retriable: bool = False
