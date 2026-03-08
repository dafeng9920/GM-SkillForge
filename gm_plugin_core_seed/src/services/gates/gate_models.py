"""Gate Models - 宪法 v0.1 最低字段规范"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class PreflightReport:
    """Preflight Report 最低字段"""

    preflight_id: str
    status: str  # PASS | FAIL | SKIPPED_EMERGENCY
    spec_ref: Dict[str, str]  # spec_id, spec_version, spec_hash
    decision_hash: str
    contract_hash: str
    checks: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = ""
    expires_at: Optional[str] = None
    emergency_mode: bool = False


@dataclass
class EvidencePackRef:
    """Evidence Pack 最低字段"""

    evidence_pack_ref: str
    trace_id: str
    session_id: str
    turn_id: int
    spec_ref: Dict[str, str]
    decision_hash: str
    execution_summary: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, str]] = field(default_factory=list)
    integrity: str = "OK"  # OK | FAILED
    created_at: str = ""
    emergency_flag: bool = False


@dataclass
class ReplayManifestRef:
    """Replay Manifest 最低字段"""

    replay_id: str
    session_id: str
    turn_seq: int
    spec_ref: Dict[str, str]
    decision_hash: str
    replay_verified: bool = False
    policy_version: str = ""
    workflow_version: str = ""
    replayed_at: str = ""


@dataclass
class GateStatus:
    """Gate 状态（用于 _meta.gate）"""

    ok: bool
    error_code: Optional[str] = None
    reason: str = ""
