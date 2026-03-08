"""
SQLite 存储层 - C3 Orchestration

落盘时机：每次 OrchestrationTurn 生成完成时
失败策略：fail-closed（落盘失败不影响主流程，但记录错误日志）
"""

import sqlite3
import json
import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.shared.models.orchestration_turn import OrchestrationTurn
from src.shared.models.response_meta import SpecRef, ResponseMeta, create_spec_ref

logger = logging.getLogger(__name__)


# 默认 DB 路径
DEFAULT_DB_PATH = os.getenv(
    "GM_OS_ORCH_DB_URL",
    "step4/out/mini_db/orchestration.db"
).replace("sqlite:///", "").replace("sqlite://", "")


@dataclass
class TurnRecord:
    """Turn record with replay fields (Wave 2)."""
    session_id: str
    turn_seq: int
    user_input: str
    assistant_output: str
    created_at: str
    spec_ref: Optional[SpecRef] = None
    decision_hash: Optional[str] = None
    decision_struct: Optional[Dict[str, Any]] = None
    spec_snapshot: Optional[Dict[str, Any]] = None
    evidence_refs: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turn_seq": self.turn_seq,
            "user_input": self.user_input,
            "assistant_output": self.assistant_output,
            "created_at": self.created_at,
            "spec_ref": self.spec_ref.to_dict() if self.spec_ref else None,
            "decision_hash": self.decision_hash,
            "decision_struct": self.decision_struct,
            "spec_snapshot": self.spec_snapshot,
            "evidence_refs": self.evidence_refs,
        }


def save_turn_with_replay_data(
    conn,
    session_id: str,
    turn_seq: int,
    user_input: str,
    assistant_output: str,
    meta: Optional[ResponseMeta] = None,
    decision_struct: Optional[Dict[str, Any]] = None,
    spec_snapshot: Optional[Dict[str, Any]] = None,
    evidence_refs: Optional[List[str]] = None,
) -> int:
    """
    Save a turn with replay data attached.
    """
    cursor = conn.cursor()

    spec_ref_json = None
    decision_hash = None
    if meta:
        spec_ref_json = json.dumps(meta.spec_ref.to_dict(), ensure_ascii=False)
        decision_hash = meta.decision_hash

    decision_struct_json = (
        json.dumps(decision_struct, ensure_ascii=False)
        if decision_struct is not None
        else None
    )
    spec_snapshot_json = (
        json.dumps(spec_snapshot, ensure_ascii=False)
        if spec_snapshot is not None
        else None
    )
    evidence_refs_json = (
        json.dumps(evidence_refs, ensure_ascii=False)
        if evidence_refs is not None
        else None
    )

    cursor.execute("""
        INSERT INTO turns (
            session_id, turn_seq, user_input, assistant_output,
            spec_ref_json, decision_hash, decision_struct_json,
            spec_snapshot_json, evidence_refs_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id, turn_seq) DO UPDATE SET
            user_input = excluded.user_input,
            assistant_output = excluded.assistant_output,
            spec_ref_json = excluded.spec_ref_json,
            decision_hash = excluded.decision_hash,
            decision_struct_json = excluded.decision_struct_json,
            spec_snapshot_json = excluded.spec_snapshot_json,
            evidence_refs_json = excluded.evidence_refs_json
    """, (
        session_id, turn_seq, user_input, assistant_output,
        spec_ref_json, decision_hash, decision_struct_json,
        spec_snapshot_json, evidence_refs_json,
    ))

    conn.commit()
    return cursor.lastrowid


def get_turn_for_replay(
    conn,
    session_id: str,
    turn_seq: int,
) -> Optional[TurnRecord]:
    """
    Load a turn with replay data.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            session_id, turn_seq, user_input, assistant_output, created_at,
            spec_ref_json, decision_hash, decision_struct_json,
            spec_snapshot_json, evidence_refs_json
        FROM turns
        WHERE session_id = ? AND turn_seq = ?
    """, (session_id, turn_seq))

    row = cursor.fetchone()
    if not row:
        return None

    spec_ref = None
    if row[5]:
        spec_ref_dict = json.loads(row[5])
        spec_ref = create_spec_ref(
            spec_ref_dict.get("spec_id", ""),
            spec_ref_dict.get("spec_version", ""),
            spec_ref_dict.get("spec_hash", ""),
        )

    decision_struct = json.loads(row[7]) if row[7] else None
    spec_snapshot = json.loads(row[8]) if row[8] else None
    evidence_refs = json.loads(row[9]) if row[9] else None

    return TurnRecord(
        session_id=row[0],
        turn_seq=row[1],
        user_input=row[2],
        assistant_output=row[3],
        created_at=row[4],
        spec_ref=spec_ref,
        decision_hash=row[6],
        decision_struct=decision_struct,
        spec_snapshot=spec_snapshot,
        evidence_refs=evidence_refs,
    )


def migrate_turns_table(conn) -> None:
    """
    Ensure turns table has Wave 2 replay columns.
    """
    cursor = conn.cursor()
    columns_to_add = [
        ("spec_ref_json", "TEXT"),
        ("decision_hash", "TEXT"),
        ("decision_struct_json", "TEXT"),
        ("spec_snapshot_json", "TEXT"),
        ("evidence_refs_json", "TEXT"),
    ]

    cursor.execute("PRAGMA table_info(turns)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE turns ADD COLUMN {col_name} {col_type}")
            except Exception as exc:
                logger.warning(
                    "Failed to add column %s to turns: %s",
                    col_name,
                    exc,
                )

    conn.commit()


class OrchestrationStore:
    """OrchestrationTurn 存储层"""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """确保 DB 文件和表结构存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # 读取 schema 并初始化
        schema_path = Path(__file__).parent / "schema_sqlite.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(schema_sql)
            conn.commit()
            migrate_turns_table(conn)
        finally:
            conn.close()

    def upsert_session(
        self,
        session_id: str,
        user_hash: Optional[str] = None,
        client_meta: Optional[Dict[str, Any]] = None
    ):
        """创建或更新会话"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO sessions (session_id, user_hash, client_meta_json, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    updated_at = excluded.updated_at
            """, (
                session_id,
                user_hash,
                json.dumps(client_meta or {}),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
        finally:
            conn.close()

    def insert_turn(self, turn: OrchestrationTurn):
        """插入轮次记录"""
        # SSOT_VIOLATION guard
        if os.getenv("GM_OS_SPEC_V2_READ_PREFERRED") == "1":
            # 检测 intent_map 是否为投影生成
            if hasattr(turn, 'intent_map') and turn.intent_map is not None:
                from src.shared.projections.spec_projections import is_from_projection
                if not is_from_projection(turn.intent_map):
                    raise RuntimeError(
                        "SSOT_VIOLATION: forbidden legacy spec write-back under READ_PREFERRED"
                    )

        conn = sqlite3.connect(self.db_path)
        try:
            # 提取 policy_checks 摘要
            policy_summary = {
                "total": len(turn.policy_checks),
                "passed": sum(1 for p in turn.policy_checks if p.passed),
                "failed": sum(1 for p in turn.policy_checks if not p.passed)
            }

            conn.execute("""
                INSERT INTO turns (
                    turn_id, session_id, ts, level_before, level_after,
                    turn_json, policy_summary_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                turn.turn_id,
                turn.session_id,
                turn.ts.isoformat(),
                turn.level_before,
                turn.level_after,
                turn.model_dump_json(),  # Pydantic v2
                json.dumps(policy_summary)
            ))
            conn.commit()
        finally:
            conn.close()

    def insert_artifact(
        self,
        artifact_id: str,
        session_id: str,
        turn_id: Optional[str],
        artifact_type: str,
        content: Dict[str, Any],
        summary: Optional[str] = None
    ):
        """插入产物记录"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO artifacts (
                    artifact_id, session_id, turn_id, artifact_type,
                    summary, content_json
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                artifact_id,
                session_id,
                turn_id,
                artifact_type,
                summary,
                json.dumps(content, ensure_ascii=False)
            ))
            conn.commit()
        finally:
            conn.close()

    def get_latest_turn(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话的最新一轮记录"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT turn_json FROM turns
                WHERE session_id = ?
                ORDER BY ts DESC
                LIMIT 1
            """, (session_id,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
        finally:
            conn.close()

    def load_answers_cumulative(self, session_id: str) -> Dict[str, Any]:
        """从历史 Turn 中聚合所有 answers_delta，确保状态不丢失"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT turn_json FROM turns
                WHERE session_id = ?
                ORDER BY ts ASC
            """, (session_id,))
            cumulative = {}
            for row in cursor.fetchall():
                try:
                    turn_data = json.loads(row[0])
                    # 聚合 intent_map.inputs
                    delta = turn_data.get("intent_map", {}).get("inputs", {})
                    if delta:
                        cumulative.update(delta)
                except:
                    continue
            return cumulative
        finally:
            conn.close()

    def get_turn_count(self, session_id: str) -> int:
        """获取指定 Session 的 Turn 数量"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM turns WHERE session_id = ?",
                (session_id,)
            )
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_session_turns(self, session_id: str) -> list:
        """获取会话的所有轮次"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT turn_json FROM turns
                WHERE session_id = ?
                ORDER BY ts ASC
            """, (session_id,))
            return [json.loads(row[0]) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_turn(self, turn_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """获取指定 turn_id 的记录"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT turn_json FROM turns
                WHERE turn_id = ? AND session_id = ?
            """, (turn_id, session_id))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
        finally:
            conn.close()

    def get_turn_by_id(self, turn_id: str) -> Optional[Dict[str, Any]]:
        """获取指定 turn_id 的记录（不需要 session_id）"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT turn_json FROM turns
                WHERE turn_id = ?
            """, (turn_id,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
        finally:
            conn.close()

    def update_turn_with_phase2(
        self,
        turn_id: str,
        session_id: str,
        three_cards: Optional[Dict[str, Any]] = None,
        execution_pack: Optional[Dict[str, Any]] = None,
        n8n_execution: Optional[Dict[str, Any]] = None,
    ):
        """更新 turn 的 Phase 2 数据"""
        conn = sqlite3.connect(self.db_path)
        try:
            # 先获取现有的 turn_json
            cursor = conn.execute("""
                SELECT turn_json FROM turns
                WHERE turn_id = ? AND session_id = ?
            """, (turn_id, session_id))
            row = cursor.fetchone()
            if not row:
                return

            turn_data = json.loads(row[0])

            # 更新 Phase 2 数据
            if three_cards is not None:
                turn_data["three_cards"] = three_cards
            if execution_pack is not None:
                turn_data["execution_pack"] = execution_pack
            if n8n_execution is not None:
                turn_data["n8n_execution"] = n8n_execution

            # 更新数据库
            conn.execute("""
                UPDATE turns
                SET turn_json = ?
                WHERE turn_id = ? AND session_id = ?
            """, (json.dumps(turn_data, ensure_ascii=False), turn_id, session_id))
            conn.commit()
        finally:
            conn.close()

    def get_artifact(self, artifact_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """获取指定 artifact_id 的记录"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT content_json FROM artifacts
                WHERE artifact_id = ? AND session_id = ?
            """, (artifact_id, session_id))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息（用于验收）"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT
                    (SELECT COUNT(*) FROM sessions) as sessions,
                    (SELECT COUNT(*) FROM turns) as turns,
                    (SELECT COUNT(*) FROM artifacts) as artifacts
            """)
            row = cursor.fetchone()
            return {
                "sessions": row[0],
                "turns": row[1],
                "artifacts": row[2]
            }
        finally:
            conn.close()


# 全局单例
_store: Optional[OrchestrationStore] = None


def get_store() -> OrchestrationStore:
    """获取全局存储实例"""
    global _store
    if _store is None:
        _store = OrchestrationStore()
    return _store
