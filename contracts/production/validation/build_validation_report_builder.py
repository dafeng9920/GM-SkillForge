from __future__ import annotations

from typing import Any

from contracts.production.candidate.candidate_skill_model import CandidateSkill
from contracts.production.validation.build_validation_report_model import BuildValidationReport


def build_validation_report(
    candidate: CandidateSkill,
    validation_spec: dict[str, Any],
    *,
    report_id: str,
) -> BuildValidationReport:
    """
    Minimal CandidateSkill -> BuildValidationReport assembler.

    This builder creates a build-side validation object only. It does not
    perform governance validation.
    """

    return BuildValidationReport(
        report_id=report_id,
        candidate_id=candidate.candidate_id,
        checks=validation_spec["checks"],
        summary=validation_spec["summary"],
        missing_artifacts=validation_spec.get("missing_artifacts", []),
        broken_references=validation_spec.get("broken_references", []),
        smoke_test_result=validation_spec.get("smoke_test_result"),
        trace_result=validation_spec.get("trace_result"),
        handoff_ready=validation_spec["handoff_ready"],
        status=validation_spec.get("status", "verified_candidate"),
    )
