"""Gate Store - 最小存储实现"""

import json
import os
import sqlite3
from dataclasses import asdict
from typing import Optional

from .gate_models import EvidencePackRef, PreflightReport, ReplayManifestRef


class GateStore:
    def __init__(self, db_path: str = "data/gates.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preflight_reports (
                    preflight_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_packs (
                    evidence_pack_ref TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS replay_manifests (
                    replay_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT
                )
                """
            )
            conn.commit()

    def get_preflight(self, preflight_id: str) -> Optional[PreflightReport]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM preflight_reports WHERE preflight_id = ?",
                (preflight_id,),
            ).fetchone()
        if not row:
            return None
        data = json.loads(row[0])
        return PreflightReport(**data)

    def save_preflight(self, report: PreflightReport) -> bool:
        try:
            payload = json.dumps(asdict(report), ensure_ascii=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO preflight_reports
                    (preflight_id, payload, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (report.preflight_id, payload, report.created_at),
                )
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_evidence(self, evidence_id: str) -> Optional[EvidencePackRef]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM evidence_packs WHERE evidence_pack_ref = ?",
                (evidence_id,),
            ).fetchone()
        if not row:
            return None
        data = json.loads(row[0])
        return EvidencePackRef(**data)

    def save_evidence(self, evidence: EvidencePackRef) -> bool:
        try:
            payload = json.dumps(asdict(evidence), ensure_ascii=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO evidence_packs
                    (evidence_pack_ref, payload, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (evidence.evidence_pack_ref, payload, evidence.created_at),
                )
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_replay_status(self, replay_id: str) -> Optional[ReplayManifestRef]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM replay_manifests WHERE replay_id = ?",
                (replay_id,),
            ).fetchone()
        if not row:
            return None
        data = json.loads(row[0])
        return ReplayManifestRef(**data)

    def save_replay(self, manifest: ReplayManifestRef) -> bool:
        try:
            payload = json.dumps(asdict(manifest), ensure_ascii=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO replay_manifests
                    (replay_id, payload, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (manifest.replay_id, payload, manifest.replayed_at),
                )
                conn.commit()
            return True
        except sqlite3.Error:
            return False


# ===== 工厂函数 =====

_gate_store_instance: Optional[GateStore] = None


def get_gate_store(db_path: str = "data/gates.db") -> GateStore:
    """
    获取 GateStore 单例实例

    Args:
        db_path: 数据库路径（默认：data/gates.db）

    Returns:
        GateStore 实例
    """
    global _gate_store_instance
    if _gate_store_instance is None:
        _gate_store_instance = GateStore(db_path=db_path)
    return _gate_store_instance
