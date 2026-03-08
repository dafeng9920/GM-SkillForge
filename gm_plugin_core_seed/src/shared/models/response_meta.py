"""
Response Meta Models for Wave 1 Observability.
SSOT: single source of truth for all _meta fields.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class SpecRef:
    """Spec reference for tracking the active spec version."""
    spec_id: str
    spec_version: str
    spec_hash: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DriftSignal:
    """Drift signal when spec is unchanged but decision changes."""
    signal_type: str  # e.g., "POLICY_DECISION_DRIFT"
    detected_at: str
    prev_decision_hash: Optional[str] = None
    curr_decision_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResponseMeta:
    """
    Response meta, Wave 1 core deliverable.

    All orchestration/decision responses must carry this when
    GM_OS_META_ENABLED=1.
    """
    spec_ref: SpecRef
    decision_hash: str
    spec_changed: bool
    decision_changed: bool
    signals: List[str] = field(default_factory=list)
    evidence_pack: Optional[str] = None
    trace_id: str = ""
    _not_ssot: bool = False  # compat projection marker

    def to_dict(self) -> dict:
        result = {
            "spec_ref": self.spec_ref.to_dict(),
            "decision_hash": self.decision_hash,
            "spec_changed": self.spec_changed,
            "decision_changed": self.decision_changed,
            "signals": self.signals,
            "evidence_pack": self.evidence_pack,
            "trace_id": self.trace_id,
        }
        if self._not_ssot:
            result["_not_ssot"] = True
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def create_empty(cls, trace_id: str = "") -> "ResponseMeta":
        return cls(
            spec_ref=SpecRef(spec_id="", spec_version="", spec_hash=""),
            decision_hash="",
            spec_changed=False,
            decision_changed=False,
            signals=[],
            evidence_pack=None,
            trace_id=trace_id,
        )


def create_spec_ref(spec_id: str, spec_version: str, spec_hash: str) -> SpecRef:
    """Factory: create SpecRef."""
    return SpecRef(spec_id=spec_id, spec_version=spec_version, spec_hash=spec_hash)


def create_response_meta(
    spec_ref: SpecRef,
    decision_hash: str,
    spec_changed: bool,
    decision_changed: bool,
    trace_id: str,
    signals: Optional[List[str]] = None,
    evidence_pack: Optional[str] = None,
) -> ResponseMeta:
    """Factory: create ResponseMeta."""
    return ResponseMeta(
        spec_ref=spec_ref,
        decision_hash=decision_hash,
        spec_changed=spec_changed,
        decision_changed=decision_changed,
        signals=signals or [],
        evidence_pack=evidence_pack,
        trace_id=trace_id,
    )
