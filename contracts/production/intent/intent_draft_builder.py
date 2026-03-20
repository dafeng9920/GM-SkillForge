from __future__ import annotations

from typing import Any

from contracts.production.intent.intent_draft_model import IntentDraft


def build_intent_draft(
    requirement: dict[str, Any],
    *,
    intent_id: str,
    required_gates: list[str],
) -> IntentDraft:
    """
    Minimal Requirement -> IntentDraft assembler.

    This builder only assembles a production-chain object. It does not perform
    governance, release, or workflow actions.
    """

    return IntentDraft(
        intent_id=intent_id,
        intent_name=requirement.get("intent_name"),
        summary=requirement["summary"],
        goal=requirement["goal"],
        problem_statement=requirement.get("problem_statement", requirement.get("requirement_text")),
        in_scope=requirement.get("in_scope", []),
        out_of_scope=requirement.get("out_of_scope", []),
        inputs=requirement.get("inputs", []),
        outputs=requirement.get("outputs", []),
        constraints=requirement.get("constraints", []),
        required_gates=required_gates,
        status=requirement.get("status", "draft"),
        created_at=requirement.get("created_at"),
        updated_at=requirement.get("updated_at"),
        revision=requirement.get("revision"),
    )
