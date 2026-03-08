"""
Gate Error Codes - Re-exports from SSOT

SSOT: src/shared/configs/gate_errors.py

This module re-exports error codes from the single source of truth
for backward compatibility. All new code should import from:
    from src.shared.configs.gate_errors import GateErrorCode
"""

# Re-export from SSOT
from src.shared.configs.gate_errors import (
    GateErrorCode,
    GateViolation,
    PhaseContext,
    get_phase_context,
    set_phase_context,
    clear_phase_context,
)

# For backward compatibility, create a GateErrors class that aliases to GateErrorCode
class GateErrors:
    """
    向后兼容类：将 GateErrorCode 暴露为类属性

    DEPRECATED: 请使用 GateErrorCode from src.shared.configs.gate_errors
    """
    # Phase2 Seal 证据链错误 (CVT-01, CVT-10, CVT-11)
    SEAL_MISSING = "CVT-01"  # Phase2 confirm 时 seal 字段缺失
    CONTRACT_HASH_MISMATCH = "CVT-11"  # Phase2 confirm 时 contract_hash 与存储的 canonical 不一致

    # CVT-10 is CONTROL_PLANE_MISSING (not SEAL_MISSING)
    CONTROL_PLANE_MISSING = "CVT-10"

    # Preflight Gate (Seal-A)
    PREFLIGHT_MISSING = "GATE.PREFLIGHT.MISSING"
    PREFLIGHT_FAILED = "GATE.PREFLIGHT.FAILED"
    PREFLIGHT_CONTRACT_MISMATCH = "GATE.PREFLIGHT.CONTRACT_MISMATCH"
    PREFLIGHT_EXPIRED = "GATE.PREFLIGHT.EXPIRED"

    # Evidence Gate (Seal-B)
    EVIDENCE_MISSING = "GATE.EVIDENCE.MISSING"
    EVIDENCE_INTEGRITY_FAILED = "GATE.EVIDENCE.INTEGRITY_FAILED"
    EVIDENCE_WRITE_FAILED = "GATE.EVIDENCE.WRITE_FAILED"

    # Replay Gate (Seal-C)
    REPLAY_MISSING = "GATE.REPLAY.MISSING"
    REPLAY_FAILED = "GATE.REPLAY.FAILED"
    REPLAY_VERSION_DRIFT = "GATE.REPLAY.VERSION_DRIFT"

    # Ticket (Phase2-Confirm → Phase2-Run)
    TICKET_MISSING = "GATE.TICKET.MISSING"
    TICKET_NOT_FOUND = "GATE.TICKET.NOT_FOUND"
    TICKET_MISMATCH = "GATE.TICKET.MISMATCH"
    TICKET_USED = "GATE.TICKET.USED"

    # Side Effects Authorization (CVT-12)
    UNAUTHORIZED_SIDE_EFFECTS = "CVT-12"  # Phase2-Confirm 时 side_effects 未授权

    # Gate Snapshot (Phase2-Compose)
    GATE_SNAPSHOT_MISMATCH = "GATE.SNAPSHOT.MISMATCH"


# HTTP 状态码映射（向后兼容）
ERROR_HTTP_CODES = {
    GateErrors.PREFLIGHT_MISSING: 400,
    GateErrors.PREFLIGHT_FAILED: 403,
    GateErrors.PREFLIGHT_CONTRACT_MISMATCH: 400,
    GateErrors.PREFLIGHT_EXPIRED: 403,
    GateErrors.EVIDENCE_MISSING: 400,
    GateErrors.EVIDENCE_INTEGRITY_FAILED: 400,
    GateErrors.REPLAY_MISSING: 403,
    GateErrors.REPLAY_FAILED: 500,
    GateErrors.REPLAY_VERSION_DRIFT: 400,
    # Phase2 Seal 证据链错误
    GateErrors.SEAL_MISSING: 400,  # CVT-01 → 400
    GateErrors.CONTRACT_HASH_MISMATCH: 400,  # CVT-11 → 400
    GateErrors.UNAUTHORIZED_SIDE_EFFECTS: 403,  # CVT-12 → 403
}


__all__ = [
    "GateErrorCode",
    "GateViolation",
    "PhaseContext",
    "get_phase_context",
    "set_phase_context",
    "clear_phase_context",
    "GateErrors",  # 向后兼容
    "ERROR_HTTP_CODES",  # 向后兼容
]
