"""
Beidou Emitter - 统一事件发射器
"""
import os
import logging
from typing import Optional, Dict, Any

from src.shared.models.beidou_event import (
    BeidouEvent, BeidouSource, BeidouType, BeidouSeverity,
    BeidouCorrelation, create_beidou_event
)
from src.services.beidou import get_beidou_store

logger = logging.getLogger(__name__)

def _is_beidou_enabled() -> bool:
    return os.environ.get("GM_OS_BEIDOU_ENABLED", "0") == "1"

def emit(event: BeidouEvent) -> Optional[str]:
    """
    发射事件到 Beidou Store

    Returns:
        event_id if emitted, None if disabled
    """
    if not _is_beidou_enabled():
        return None

    try:
        store = get_beidou_store()
        store.append(event)

        # 结构化日志
        logger.info(
            f"BEIDOU_EVENT_TRACE event_id={event.event_id} "
            f"source={event.source.value} type={event.type.value} "
            f"name={event.name} severity={event.severity.value}"
        )

        return event.event_id
    except Exception as e:
        logger.error(f"BEIDOU_EMIT_FAILED: {e}")
        return None

def emit_gate_event(
    gate_type: str,  # "preflight" | "commit" | "publish"
    passed: bool,
    error_code: Optional[str] = None,
    correlation: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    发射 GATE 相关事件
    """
    if passed:
        severity = BeidouSeverity.INFO
        name = f"GATE.{gate_type.upper()}.PASSED"
    else:
        severity = BeidouSeverity.ERROR
        name = error_code or f"GATE.{gate_type.upper()}.FAILED"

    corr = BeidouCorrelation(
        spec_hash=correlation.get("spec_hash") if correlation else None,
        decision_hash=correlation.get("decision_hash") if correlation else None,
        contract_id=correlation.get("contract_id") if correlation else None,
        session_id=correlation.get("session_id") if correlation else None,
    )

    event = create_beidou_event(
        name=name,
        source=BeidouSource.GATE,
        type=BeidouType.EVENT,
        severity=severity,
        correlation=corr,
        payload=payload or {},
    )

    return emit(event)

def emit_drift_event(
    spec_hash: str,
    decision_hash: str,
    prev_decision_hash: Optional[str] = None,
) -> Optional[str]:
    """
    发射 POLICY_DECISION_DRIFT 事件
    """
    event = create_beidou_event(
        name="POLICY_DECISION_DRIFT",
        source=BeidouSource.INNER,
        type=BeidouType.SIGNAL,
        severity=BeidouSeverity.WARN,
        correlation=BeidouCorrelation(
            spec_hash=spec_hash,
            decision_hash=decision_hash,
        ),
        payload={
            "prev_decision_hash": prev_decision_hash,
            "drift_detected": True,
        },
    )

    return emit(event)

def emit_replay_event(
    passed: bool,
    replay_id: Optional[str] = None,
    spec_hash: Optional[str] = None,
    error_reason: Optional[str] = None,
) -> Optional[str]:
    """
    发射 Replay 相关事件
    """
    if passed:
        name = "REPLAY.VERIFIED"
        severity = BeidouSeverity.INFO
    else:
        name = "REPLAY.FAILED"
        severity = BeidouSeverity.ERROR

    event = create_beidou_event(
        name=name,
        source=BeidouSource.SYSTEM,
        type=BeidouType.EVENT,
        severity=severity,
        correlation=BeidouCorrelation(spec_hash=spec_hash),
        payload={
            "replay_id": replay_id,
            "error_reason": error_reason,
        },
    )

    return emit(event)

def emit_ssot_violation(
    violation_type: str,
    file_path: Optional[str] = None,
    details: Optional[str] = None,
) -> Optional[str]:
    """
    发射 SSOT_VIOLATION 事件
    """
    event = create_beidou_event(
        name="SSOT_VIOLATION",
        source=BeidouSource.SYSTEM,
        type=BeidouType.ERROR,
        severity=BeidouSeverity.CRITICAL,
        payload={
            "violation_type": violation_type,
            "file_path": file_path,
            "details": details,
        },
    )

    return emit(event)

def emit_task_event(
    task_id: str,
    event_type: str,  # "ENQUEUED" | "ACTIVATED" | "COMPLETED" | "REJECTED" | "CONTEXT_MISSING" | "SWITCHED"
    session_id: Optional[str] = None,
    prev_task_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    发射 Task 状态变化事件
    """
    name = f"TASK.{event_type}"

    if event_type in ["REJECTED", "CONTEXT_MISSING"]:
        severity = BeidouSeverity.WARN
    else:
        severity = BeidouSeverity.INFO

    event = create_beidou_event(
        name=name,
        source=BeidouSource.SYSTEM,
        type=BeidouType.EVENT,
        severity=severity,
        correlation=BeidouCorrelation(
            session_id=session_id,
        ),
        payload={
            "task_id": task_id,
            "event_type": event_type,
            "prev_task_id": prev_task_id,
            **(payload or {}),
        },
    )

    return emit(event)
