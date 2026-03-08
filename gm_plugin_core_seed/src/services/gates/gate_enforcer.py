"""Gate Enforcer - 三门禁校验逻辑"""
import os
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime

from .gate_errors import GateErrors
from .gate_models import PreflightReport, EvidencePackRef, ReplayManifestRef, GateStatus
from .gate_store import GateStore


def _is_gates_enabled() -> bool:
    return os.environ.get("GM_OS_GATES_ENABLED", "0") == "1"


def _is_preflight_enabled() -> bool:
    return os.environ.get("GM_OS_PREFLIGHT_GATE_ENABLED", "0") == "1"


def _is_evidence_enabled() -> bool:
    return os.environ.get("GM_OS_EVIDENCE_GATE_ENABLED", "0") == "1"


def _is_replay_enabled() -> bool:
    return os.environ.get("GM_OS_REPLAY_GATE_ENABLED", "0") == "1"


def _is_strict_mode() -> bool:
    return os.environ.get("GM_OS_GATE_STRICT_MODE", "0") == "1"


def enforce_preflight(
    preflight_id: Optional[str],
    contract_hash: str,
    store: Optional[GateStore] = None,
) -> Tuple[bool, Optional[str], str, List[str]]:
    """
    Seal-A: Preflight Gate

    Returns:
        (ok, error_code, reason, signals)
    """
    signals = []

    if not _is_gates_enabled() or not _is_preflight_enabled():
        return True, None, "Gate disabled", signals

    # 1. preflight_id 存在性
    if not preflight_id:
        return False, GateErrors.PREFLIGHT_MISSING, "Preflight ID is required", ["GATE_PREFLIGHT_MISSING"]

    # 2. 获取 preflight report
    if store:
        report = store.get_preflight(preflight_id)
    else:
        report = None

    if not report:
        return False, GateErrors.PREFLIGHT_MISSING, f"Preflight {preflight_id} not found", ["GATE_PREFLIGHT_MISSING"]

    # 3. 检查状态
    if report.status != "PASS":
        return False, GateErrors.PREFLIGHT_FAILED, f"Preflight status is {report.status}", ["GATE_PREFLIGHT_FAILED"]

    # 4. 检查 contract_hash 一致性
    if report.contract_hash != contract_hash:
        return False, GateErrors.PREFLIGHT_CONTRACT_MISMATCH, "Contract hash mismatch", ["GATE_PREFLIGHT_CONTRACT_MISMATCH"]

    # 5. 检查过期
    if report.expires_at:
        try:
            expires = datetime.fromisoformat(report.expires_at.replace("Z", "+00:00"))
            if datetime.now(expires.tzinfo) > expires:
                return False, GateErrors.PREFLIGHT_EXPIRED, "Preflight has expired", ["GATE_PREFLIGHT_EXPIRED"]
        except:
            pass

    return True, None, "Preflight passed", signals


def enforce_evidence(
    evidence_id: Optional[str],
    store: Optional[GateStore] = None,
) -> Tuple[bool, Optional[str], str, List[str]]:
    """
    Seal-B: Evidence Gate

    Returns:
        (ok, error_code, reason, signals)
    """
    signals = []

    if not _is_gates_enabled() or not _is_evidence_enabled():
        return True, None, "Gate disabled", signals

    # 1. evidence_id 存在性
    if not evidence_id:
        return False, GateErrors.EVIDENCE_MISSING, "Evidence ID is required", ["GATE_EVIDENCE_MISSING"]

    # 2. 获取 evidence
    if store:
        evidence = store.get_evidence(evidence_id)
    else:
        evidence = None

    if not evidence:
        return False, GateErrors.EVIDENCE_MISSING, f"Evidence {evidence_id} not found", ["GATE_EVIDENCE_MISSING"]

    # 3. 检查完整性
    if evidence.integrity != "OK":
        return False, GateErrors.EVIDENCE_INTEGRITY_FAILED, f"Evidence integrity is {evidence.integrity}", ["GATE_EVIDENCE_INTEGRITY_FAILED"]

    return True, None, "Evidence verified", signals


def enforce_replay(
    replay_id: Optional[str],
    store: Optional[GateStore] = None,
) -> Tuple[bool, Optional[str], str, List[str]]:
    """
    Seal-C: Replay Gate

    Returns:
        (ok, error_code, reason, signals)
    """
    signals = []

    if not _is_gates_enabled() or not _is_replay_enabled():
        return True, None, "Gate disabled", signals

    # 沙盒模式跳过
    if os.environ.get("GM_OS_GATE_SANDBOX_ONLY", "0") == "1":
        return True, None, "Sandbox mode - replay gate skipped", ["GATE_SANDBOX_ONLY"]

    # 1. replay_id 存在性
    if not replay_id:
        return False, GateErrors.REPLAY_MISSING, "Replay ID is required", ["GATE_REPLAY_MISSING"]

    # 2. 获取 replay manifest
    if store:
        manifest = store.get_replay_status(replay_id)
    else:
        manifest = None

    if not manifest:
        return False, GateErrors.REPLAY_MISSING, f"Replay {replay_id} not found", ["GATE_REPLAY_MISSING"]

    # 3. 检查 replay_verified
    if not manifest.replay_verified:
        return False, GateErrors.REPLAY_FAILED, "Replay verification failed", ["GATE_REPLAY_FAILED"]

    return True, None, "Replay verified", signals


def build_gate_meta(
    preflight: GateStatus,
    evidence: GateStatus,
    replay: GateStatus,
) -> Dict[str, Any]:
    """构建 _meta.gate 结构"""
    return {
        "preflight": {"ok": preflight.ok, "error_code": preflight.error_code},
        "evidence": {"ok": evidence.ok, "error_code": evidence.error_code},
        "replay": {"ok": replay.ok, "error_code": replay.error_code},
    }
