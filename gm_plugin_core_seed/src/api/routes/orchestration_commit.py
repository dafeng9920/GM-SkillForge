"""
Orchestration Commit API - Wave 3

提供 commit endpoint，接收用户确认后生成 execute_contract。

开关：GM_OS_C3_COMMIT_ENABLED=1

重要约束：
- commit 必须携带 spec_ref + decision_hash
- commit 后必须可 replay（写入 store）
- GM_OS_C3_COMMIT_ENABLED=0 时返回 403
"""
import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.orchestration.store_sqlite import get_store
from src.services.orchestration.meta_builder import build_meta
from src.services.gates.gate_enforcer import enforce_evidence, build_gate_meta
from src.services.gates.gate_models import GateStatus

# W7-B: Beidou Emitter
from src.services.beidou.beidou_emitter import emit_gate_event

# W9-C: Task Guard
from src.services.tasks.task_guard import check_task_context


router = APIRouter(prefix="/orchestration", tags=["commit"])


# ==================== 开关检查 ====================

def _is_commit_enabled() -> bool:
    return os.environ.get("GM_OS_C3_COMMIT_ENABLED", "0") == "1"


def _check_commit_enabled():
    if not _is_commit_enabled():
        raise HTTPException(
            status_code=403,
            detail="Commit API is disabled. Set GM_OS_C3_COMMIT_ENABLED=1 to enable.",
        )


# ==================== 请求/响应模型 ====================

class SpecRef(BaseModel):
    """Spec 引用"""
    spec_id: str
    spec_version: str
    spec_hash: str


class UserConfirmation(BaseModel):
    """用户确认"""
    type: str = Field(..., description="确认类型，如 'manual_review', 'cost_approval'")
    confirmed_at: str = Field(..., description="确认时间 (ISO 8601)")
    user_id: Optional[str] = Field(None, description="用户 ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class CommitRequest(BaseModel):
    """Commit 请求"""
    session_id: str = Field(..., description="会话 ID")
    turn_id: int = Field(..., description="轮次 ID")
    spec_ref: SpecRef = Field(..., description="Spec 引用")
    decision_hash: str = Field(..., description="Decision 哈希")
    user_confirmations: List[UserConfirmation] = Field(
        default=[],
        description="用户确认列表"
    )
    evidence_pack_ref: Optional[str] = Field(
        None,
        description="Evidence Pack 引用 (Seal-B: Evidence Gate)"
    )


class ExecuteContract(BaseModel):
    """执行契约"""
    contract_id: str
    spec_ref: SpecRef
    decision_hash: str
    user_confirmations: List[UserConfirmation]
    evidence_refs: List[str]
    created_at: str


class CommitResponse(BaseModel):
    """Commit 响应"""
    execute_contract: ExecuteContract
    _meta: Optional[Dict[str, Any]] = None


# ==================== 辅助函数 ====================

def _verify_spec_and_decision(
    session_id: str,
    turn_id: int,
    spec_ref: SpecRef,
    decision_hash: str,
) -> bool:
    """
    验证 spec_ref 和 decision_hash 是否匹配当前 session 的最新 turn

    Args:
        session_id: 会话 ID
        turn_id: 轮次 ID
        spec_ref: Spec 引用
        decision_hash: Decision 哈希

    Returns:
        bool: 验证是否通过
    """
    import sqlite3
    import json

    store = get_store()
    conn = sqlite3.connect(store.db_path)
    try:
        cursor = conn.cursor()

        # 获取指定 turn 的数据
        cursor.execute("""
            SELECT turn_json
            FROM turns
            WHERE session_id = ?
            ORDER BY ts ASC
            LIMIT 1 OFFSET ?
        """, (session_id, turn_id - 1))  # turn_id 是 1-based，OFFSET 是 0-based

        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Turn {turn_id} not found for session {session_id}"
            )

        turn_json = json.loads(row[0])

        # 验证 spec_ref
        if "_meta" in turn_json:
            stored_spec_ref = turn_json["_meta"].get("spec_ref")
            if stored_spec_ref:
                if (stored_spec_ref.get("spec_id") != spec_ref.spec_id or
                    stored_spec_ref.get("spec_version") != spec_ref.spec_version or
                    stored_spec_ref.get("spec_hash") != spec_ref.spec_hash):
                    return False

        # 验证 decision_hash
        if "_meta" in turn_json:
            stored_decision_hash = turn_json["_meta"].get("decision_hash")
            if stored_decision_hash and stored_decision_hash != decision_hash:
                return False

        return True

    finally:
        conn.close()


def _write_contract_to_store(
    session_id: str,
    turn_id: int,
    contract: ExecuteContract,
) -> None:
    """
    将 contract 写入 store（用于后续 replay）

    Args:
        session_id: 会话 ID
        turn_id: 轮次 ID
        contract: 执行契约
    """
    import sqlite3
    import json

    store = get_store()
    conn = sqlite3.connect(store.db_path)
    try:
        cursor = conn.cursor()

        # 创建 contracts 表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                contract_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                turn_id INTEGER NOT NULL,
                contract_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(session_id, turn_id)
            )
        """)

        # 写入 contract
        contract_json = {
            "contract_id": contract.contract_id,
            "spec_ref": contract.spec_ref.dict(),
            "decision_hash": contract.decision_hash,
            "user_confirmations": [c.dict() for c in contract.user_confirmations],
            "evidence_refs": contract.evidence_refs,
            "created_at": contract.created_at,
        }

        cursor.execute("""
            INSERT OR REPLACE INTO contracts
            (contract_id, session_id, turn_id, contract_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            contract.contract_id,
            session_id,
            turn_id,
            json.dumps(contract_json, ensure_ascii=False),
            contract.created_at,
        ))

        conn.commit()

    finally:
        conn.close()


# ==================== API Endpoints ====================

@router.post("/commit", response_model=CommitResponse)
async def commit_contract(
    request: CommitRequest,
    x_task_id: Optional[str] = Header(None, alias="X-Task-Id"),
) -> CommitResponse:
    """
    Commit endpoint - 接收用户确认后生成 execute_contract

    请求:
    - session_id: 会话 ID
    - turn_id: 轮次 ID
    - spec_ref: Spec 引用
    - decision_hash: Decision 哈希
    - user_confirmations: 用户确认列表
    - evidence_pack_ref: Evidence Pack 引用 (Seal-B: Evidence Gate)

    响应:
    - execute_contract: 执行契约（包含所有确认信息）
    - _meta: 元数据（用于可观测性，包含 gate 状态）

    验证逻辑:
    1. W9-C: Task Guard - 检查 task 上下文（防止串线）
    2. 检查开关 GM_OS_C3_COMMIT_ENABLED
    3. Seal-B: Evidence Gate 校验 (evidence_pack_ref 必须存在且 integrity=OK)
    4. 验证 spec_ref 和 decision_hash 匹配当前 session
    5. 生成 execute_contract
    6. 写入 contract 到 store（可审计）
    7. 返回 execute_contract（包含 gate 状态）

    Evidence Gate 失败时返回:
    - status: INVALID_RUN
    - error_code: GATE.EVIDENCE.MISSING 或 GATE.EVIDENCE.INTEGRITY_FAILED
    - next_action: provide_evidence
    """
    # 1. W9-C: Task Guard - 检查 task 上下文
    task_id = check_task_context(x_task_id)

    # 2. 检查开关
    _check_commit_enabled()

    # 2. Seal-B: Evidence Gate
    evidence_id = request.evidence_pack_ref or ""
    ok, error_code, reason, signals = enforce_evidence(evidence_id=evidence_id)

    # W7-B: Emit Beidou event for Evidence/Commit Gate
    emit_gate_event(
        "commit",
        passed=ok,
        error_code=error_code if not ok else None,
        correlation={"spec_hash": request.spec_ref.spec_hash, "decision_hash": request.decision_hash},
        payload={"reason": reason, "session_id": request.session_id},
    )

    if not ok:
        # 拒绝 commit，标记 INVALID_RUN
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": error_code,
                "reason": reason,
                "status": "INVALID_RUN",
                "_meta": {
                    "gate": {"evidence": {"ok": False, "error_code": error_code}},
                    "signals": signals,
                },
                "next_action": "provide_evidence",
            }
        )

    # 3. 验证 spec_ref 和 decision_hash
    is_valid = _verify_spec_and_decision(
        session_id=request.session_id,
        turn_id=request.turn_id,
        spec_ref=request.spec_ref,
        decision_hash=request.decision_hash,
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Spec ref or decision hash does not match the current session state"
        )

    # 4. 生成 execute_contract
    contract_id = f"contract-{uuid.uuid4().hex[:8].upper()}"
    created_at = datetime.now().isoformat()

    execute_contract = ExecuteContract(
        contract_id=contract_id,
        spec_ref=request.spec_ref,
        decision_hash=request.decision_hash,
        user_confirmations=request.user_confirmations,
        evidence_refs=[],
        created_at=created_at,
    )

    # 5. 写入 store
    _write_contract_to_store(
        session_id=request.session_id,
        turn_id=request.turn_id,
        contract=execute_contract,
    )

    # 6. 构建 _meta
    from src.shared.models.response_meta import create_spec_ref

    spec_ref_for_meta = create_spec_ref(
        request.spec_ref.spec_id,
        request.spec_ref.spec_version,
        request.spec_ref.spec_hash,
    )

    decision_payload = {
        "decision_hash": request.decision_hash,
        "confirmations": [c.dict() for c in request.user_confirmations],
    }

    meta = build_meta(
        spec_ref=spec_ref_for_meta,
        decision_payload=decision_payload,
        session_id=request.session_id,
        turn_id=str(request.turn_id),
        evidence_pack_ref=f"contract-{contract_id}",
    )

    # 构建完整的 _meta，包含 gate 状态
    meta_dict = meta.to_dict()
    meta_dict["gate"] = build_gate_meta(
        preflight=GateStatus(ok=True),
        evidence=GateStatus(ok=True),
        replay=GateStatus(ok=True),
    )

    return CommitResponse(
        execute_contract=execute_contract,
        _meta=meta_dict,
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "service": "orchestration-commit",
        "status": "ok",
        "commit_enabled": _is_commit_enabled(),
        "timestamp": datetime.now().isoformat(),
    }
