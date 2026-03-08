"""
Orchestration Replay API - Wave 2

提供 turn 的回放功能，返回 spec/decision 快照。

开关：GM_OS_REPLAY_ENABLED=1

重要约束：
- Replay 只读，不调用任何推导器
- 返回的是 turn 存储时的快照，不是现场计算

Wave11-A: 使用统一 envelope 响应格式
Wave11-B: 使用 Config Center (settings.py)
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from src.services.orchestration.store_sqlite import get_store

# W7-C: Beidou Emitter
from src.services.beidou.beidou_emitter import emit_replay_event
from src.shared.http.envelope_helpers import ok
from src.config.settings import settings


router = APIRouter(prefix="/orchestration/replay", tags=["replay"])


# ==================== 开关检查 ====================

def _is_replay_enabled() -> bool:
    return settings.REPLAY_ENABLED


def _check_replay_enabled():
    if not _is_replay_enabled():
        raise HTTPException(
            status_code=403,
            detail="Replay API is disabled. Set GM_OS_REPLAY_ENABLED=1 to enable.",
        )


# ==================== 响应模型 ====================

class SpecRefResponse(BaseModel):
    spec_id: str
    spec_version: str
    spec_hash: str


class DecisionSnapshotResponse(BaseModel):
    decision_hash: str
    decision_struct: Optional[dict] = None


class ReplayResponse(BaseModel):
    """Replay API 响应"""
    session_id: str
    turn_id: str
    created_at: str

    # Spec 快照
    spec_ref: Optional[SpecRefResponse] = None
    spec_snapshot: Optional[dict] = None

    # Decision 快照
    decision_snapshot: Optional[DecisionSnapshotResponse] = None

    # 证据
    evidence_refs: Optional[list] = None

    # Meta（复用 Wave 1 结构）
    _meta: Optional[dict] = None


# ==================== 辅助函数 ====================

def get_db_connection():
    """获取数据库连接"""
    store = get_store()
    import sqlite3
    return sqlite3.connect(store.db_path)


def get_turn_for_replay(conn, session_id: str, turn_seq: int):
    """
    从数据库获取 turn 用于回放

    Args:
        conn: 数据库连接
        session_id: 会话 ID
        turn_seq: 轮次序号（1-based）

    Returns:
        dict: turn 数据，或 None
    """
    import json

    cursor = conn.cursor()

    # 根据现有的 schema，我们需要按 ts 排序获取第 N 条记录
    cursor.execute("""
        SELECT turn_id, session_id, ts, turn_json
        FROM turns
        WHERE session_id = ?
        ORDER BY ts ASC
        LIMIT 1 OFFSET ?
    """, (session_id, turn_seq - 1))  # turn_seq 是 1-based，OFFSET 是 0-based

    row = cursor.fetchone()
    if not row:
        return None

    turn_data = json.loads(row[3])

    # 包装为对象以便访问
    class TurnData:
        def __init__(self, data, turn_id, session_id, ts):
            self.turn_id = turn_id
            self.session_id = session_id
            self.ts = ts
            self.turn_seq = turn_seq
            self.created_at = ts
            self.data = data

            # 从 turn_json 中提取字段（如果存在）
            self.spec_ref = data.get("spec_ref")
            self.spec_snapshot = data.get("spec_snapshot")
            self.decision_hash = data.get("decision_hash")
            self.decision_struct = data.get("decision_struct")
            self.evidence_refs = data.get("evidence_refs")

    return TurnData(turn_data, row[0], row[1], row[2])


# ==================== API Endpoints ====================

@router.get("")
async def replay_turn(
    session_id: str = Query(..., description="Session ID"),
    turn_id: Optional[int] = Query(None, alias="turn_id", description="Turn sequence (turn_seq)"),
    turn_seq: Optional[int] = Query(None, description="Turn sequence (alias)"),
):
    """
    获取指定 turn 的回放数据

    Args:
        session_id: 会话 ID
        turn_id/turn_seq: 轮次序号（两个参数等价）

    Returns:
        ReplayResponse: 包含 spec/decision 快照

    Raises:
        403: Replay 功能未启用
        404: 指定的 turn 不存在
    """
    _check_replay_enabled()

    # 处理参数别名
    seq = turn_id if turn_id is not None else turn_seq
    if seq is None:
        raise HTTPException(
            status_code=400,
            detail="Either turn_id or turn_seq is required",
        )

    # 获取数据库连接
    conn = get_db_connection()

    try:
        # 获取 turn 记录
        turn = get_turn_for_replay(conn, session_id, seq)

        if not turn:
            # W7-C: 接入 Beidou 事件发射 - replay 失败
            try:
                emit_replay_event(
                    passed=False,
                    replay_id=f"{session_id}:{seq}",
                    error_reason="Turn not found",
                )
            except Exception:
                pass  # Beidou 发射失败不影响主流程

            raise HTTPException(
                status_code=404,
                detail=f"Turn not found: session_id={session_id}, turn_seq={seq}",
            )

        # W7-C: 接入 Beidou 事件发射 - replay 成功
        try:
            spec_hash = turn.spec_ref.get("spec_hash") if turn.spec_ref else None
            emit_replay_event(
                passed=True,
                replay_id=f"{session_id}:{seq}",
                spec_hash=spec_hash,
            )
        except Exception:
            pass  # Beidou 发射失败不影响主流程

        # 构建响应
        spec_ref_response = None
        if turn.spec_ref:
            spec_ref_response = SpecRefResponse(
                spec_id=turn.spec_ref.get("spec_id", ""),
                spec_version=turn.spec_ref.get("spec_version", ""),
                spec_hash=turn.spec_ref.get("spec_hash", ""),
            )

        decision_snapshot = None
        if turn.decision_hash or turn.decision_struct:
            decision_snapshot = DecisionSnapshotResponse(
                decision_hash=turn.decision_hash or "",
                decision_struct=turn.decision_struct,
            )

        # 构建 _meta（简化版，用于前端）
        meta = {
            "spec_ref": spec_ref_response.model_dump() if spec_ref_response else None,
            "decision_hash": turn.decision_hash,
            "trace_id": f"{session_id}:{seq}:replay",
            "is_replay": True,  # 标记这是回放数据
        }

        data = {
            "session_id": turn.session_id,
            "turn_id": turn.turn_id,
            "created_at": turn.created_at.isoformat() if hasattr(turn.created_at, 'isoformat') else str(turn.created_at),
            "spec_ref": spec_ref_response.model_dump() if spec_ref_response else None,
            "spec_snapshot": turn.spec_snapshot,
            "decision_snapshot": decision_snapshot.model_dump() if decision_snapshot else None,
            "evidence_refs": turn.evidence_refs,
        }

        return ok(data, meta=meta)

    finally:
        conn.close()


@router.get("/list")
async def list_session_turns(
    session_id: str = Query(..., description="Session ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of turns to return"),
) -> dict:
    """
    列出会话的所有 turn（用于选择回放目标）

    Args:
        session_id: 会话 ID
        limit: 最大返回数量

    Returns:
        {"turns": [{"turn_id": "...", "created_at": "...", "has_replay_data": true}, ...]}
    """
    _check_replay_enabled()

    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT turn_id, ts, turn_json
            FROM turns
            WHERE session_id = ?
            ORDER BY ts DESC
            LIMIT ?
        """, (session_id, limit))

        import json
        turns = []
        for row in cursor.fetchall():
            turn_data = json.loads(row[2])
            has_replay = turn_data.get("decision_hash") is not None or turn_data.get("spec_ref") is not None
            turns.append({
                "turn_id": row[0],
                "created_at": row[1],
                "has_replay_data": has_replay,
            })

        return ok({
            "session_id": session_id,
            "turns": turns,
            "total": len(turns),
        }, meta={"advisory_only": True})

    finally:
        conn.close()


@router.get("/compare")
async def compare_turns(
    session_id: str = Query(..., description="Session ID"),
    turn_seq_a: int = Query(..., description="First turn to compare"),
    turn_seq_b: int = Query(..., description="Second turn to compare"),
) -> dict:
    """
    比较两个 turn 的 spec/decision

    用于检测漂移和变化

    Args:
        session_id: 会话 ID
        turn_seq_a: 第一个 turn
        turn_seq_b: 第二个 turn

    Returns:
        比较结果，包含 spec_changed, decision_changed 等
    """
    _check_replay_enabled()

    conn = get_db_connection()

    try:
        turn_a = get_turn_for_replay(conn, session_id, turn_seq_a)
        turn_b = get_turn_for_replay(conn, session_id, turn_seq_b)

        if not turn_a:
            raise HTTPException(status_code=404, detail=f"Turn A not found: {turn_seq_a}")
        if not turn_b:
            raise HTTPException(status_code=404, detail=f"Turn B not found: {turn_seq_b}")

        # 比较
        spec_hash_a = turn_a.spec_ref.get("spec_hash") if turn_a.spec_ref else None
        spec_hash_b = turn_b.spec_ref.get("spec_hash") if turn_b.spec_ref else None

        return ok({
            "session_id": session_id,
            "turn_a": {
                "turn_seq": turn_seq_a,
                "turn_id": turn_a.turn_id,
                "spec_hash": spec_hash_a,
                "decision_hash": turn_a.decision_hash,
            },
            "turn_b": {
                "turn_seq": turn_seq_b,
                "turn_id": turn_b.turn_id,
                "spec_hash": spec_hash_b,
                "decision_hash": turn_b.decision_hash,
            },
            "comparison": {
                "spec_changed": spec_hash_a != spec_hash_b,
                "decision_changed": turn_a.decision_hash != turn_b.decision_hash,
                "is_drift": (spec_hash_a == spec_hash_b) and (turn_a.decision_hash != turn_b.decision_hash),
            },
        }, meta={"advisory_only": True})

    finally:
        conn.close()
