import os

new_code = '''\"\"\"
Registry Store - Append-only Skill Registry Storage

SEEDS-P0-1: Registry (身份台账)

统一存储 skill_id + revision + pack_hash + permit + tombstone_state。

特性：
1. Append-only：只能追加，不能覆盖历史记录
2. 按skill_id读取最新ACTIVE revision
3. 支持tombstone标记
4. [NEW M3] 引入 SQLite 索引支持，解决 O(N) 扫描开销
5. [NEW M3] 双写过渡架构 (Dual-Write & Shadow Read)

Contract: docs/SEEDS_v0.md
Job ID: L45-D4-SEEDS-P0-20260220-004
\"\"\"
from __future__ import annotations

import json
import os
import threading
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any
import hashlib


# ============================================================================
# Constants
# ============================================================================

DEFAULT_REGISTRY_JSONL = Path(__file__).parent.parent.parent.parent / "registry" / "skills.jsonl"
DEFAULT_REGISTRY_SQLITE = Path(__file__).parent.parent.parent.parent / "registry" / "skills.db"
JOB_ID = "L45-D4-SEEDS-P0-20260220-004"
SKILL_ID = "l45_seeds_p0_foundation"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SkillRegistryEntry:
    \"\"\"
    Skill Registry Entry - 单条 registry 记录
    \"\"\"
    skill_id: str
    source: dict  
    revision: str
    pack_hash: str
    permit_id: str
    tombstone_state: str = "ACTIVE"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), separators=(',', ':'))

    @classmethod
    def from_json_line(cls, line: str) -> 'SkillRegistryEntry':
        data = json.loads(line.strip())
        return cls(**data)


@dataclass
class RegistryQueryResult:
    success: bool
    entry: Optional[SkillRegistryEntry] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


@dataclass
class RegistryAppendResult:
    success: bool
    revision: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


# ============================================================================
# Registry Store
# ============================================================================

class RegistryStore:
    \"\"\"
    Append-only Skill Registry Store supporting Dual Backend Migration.
    \"\"\"

    def __init__(self, jsonl_path: Optional[Path] = None, sqlite_path: Optional[Path] = None):
        self.jsonl_path = Path(jsonl_path) if jsonl_path else DEFAULT_REGISTRY_JSONL
        
        # Determine the correct sqlite path (replace .jsonl with .db if using same root)
        if sqlite_path:
            self.sqlite_path = Path(sqlite_path)
        elif jsonl_path:
            self.sqlite_path = Path(str(jsonl_path).replace(".jsonl", ".db"))
        else:
            self.sqlite_path = DEFAULT_REGISTRY_SQLITE

        self._lock = threading.Lock()
        
        # Feature Flags for Migration
        self.backend = os.getenv("REGISTRY_BACKEND", "jsonl").lower()
        self.is_dual_write = os.getenv("REGISTRY_DUAL_WRITE", "false").lower() == "true"
        self.is_shadow_compare = os.getenv("REGISTRY_SHADOW_READ_COMPARE", "false").lower() == "true"

        # Initialization
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.jsonl_path.exists():
            self.jsonl_path.touch()

        if self.backend == "sqlite" or self.is_dual_write or self.is_shadow_compare:
            self._init_sqlite()

    def _init_sqlite(self):
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.sqlite_path) as conn:
            cursor = conn.cursor()
            cursor.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS registry (
                    skill_id TEXT,
                    revision TEXT,
                    tombstone_state TEXT,
                    created_at TEXT,
                    payload TEXT
                )
            \"\"\")
            # Index for get_latest_active performance boost
            cursor.execute(\"CREATE INDEX IF NOT EXISTS idx_skill_state ON registry (skill_id, tombstone_state, created_at DESC)\")
            conn.commit()

    def _append_jsonl(self, entry: SkillRegistryEntry):
        with open(self.jsonl_path, 'a', encoding='utf-8') as f:
            f.write(entry.to_json_line() + '\\n')

    def _append_sqlite(self, entry: SkillRegistryEntry):
        with sqlite3.connect(self.sqlite_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO registry (skill_id, revision, tombstone_state, created_at, payload) VALUES (?, ?, ?, ?, ?)",
                (entry.skill_id, entry.revision, entry.tombstone_state, entry.created_at, entry.to_json_line())
            )
            conn.commit()

    def append(self, entry: SkillRegistryEntry) -> RegistryAppendResult:
        with self._lock:
            try:
                if not entry.skill_id:
                    return RegistryAppendResult(False, error_code="INVALID_ENTRY", error_message="skill_id is required")
                if not entry.revision:
                    return RegistryAppendResult(False, error_code="INVALID_ENTRY", error_message="revision is required")
                if entry.revision == "AUTO":
                    entry.revision = self._generate_revision()

                if self.backend == "sqlite":
                    self._append_sqlite(entry)
                    if self.is_dual_write:
                        self._append_jsonl(entry)
                else:
                    self._append_jsonl(entry)
                    if self.is_dual_write:
                        self._append_sqlite(entry)

                return RegistryAppendResult(True, revision=entry.revision)
            except Exception as e:
                return RegistryAppendResult(False, error_code="APPEND_ERROR", error_message=str(e))

    def _get_latest_active_jsonl(self, skill_id: str) -> Optional[SkillRegistryEntry]:
        latest_entry = None
        if not self.jsonl_path.exists():
            return None
        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    entry = SkillRegistryEntry.from_json_line(line)
                    if entry.skill_id == skill_id and entry.tombstone_state == "ACTIVE":
                        latest_entry = entry
                except json.JSONDecodeError:
                    continue
        return latest_entry

    def _get_latest_active_sqlite(self, skill_id: str) -> Optional[SkillRegistryEntry]:
        if not self.sqlite_path.exists():
            return None
        with sqlite3.connect(self.sqlite_path) as conn:
            cursor = conn.cursor()
            cursor.execute(\"\"\"
                SELECT payload FROM registry 
                WHERE skill_id = ? AND tombstone_state = 'ACTIVE' 
                ORDER BY created_at DESC, rowid DESC LIMIT 1
            \"\"\", (skill_id,))
            row = cursor.fetchone()
            if row:
                return SkillRegistryEntry.from_json_line(row[0])
        return None

    def get_latest_active(self, skill_id: str) -> RegistryQueryResult:
        try:
            primary_entry = None
            if self.backend == "sqlite":
                primary_entry = self._get_latest_active_sqlite(skill_id)
                if self.is_shadow_compare:
                    shadow_entry = self._get_latest_active_jsonl(skill_id)
                    # You could log mismatched entries here for telemetry
            else:
                primary_entry = self._get_latest_active_jsonl(skill_id)
                if self.is_shadow_compare:
                    shadow_entry = self._get_latest_active_sqlite(skill_id)

            if primary_entry:
                return RegistryQueryResult(True, entry=primary_entry)
            else:
                return RegistryQueryResult(False, error_code="NOT_FOUND", error_message="No ACTIVE entry found")
        except Exception as e:
            return RegistryQueryResult(False, error_code="QUERY_ERROR", error_message=str(e))

    def get_all_revisions(self, skill_id: str) -> list[SkillRegistryEntry]:
        entries: list[SkillRegistryEntry] = []
        try:
            if self.backend == "sqlite" and self.sqlite_path.exists():
                with sqlite3.connect(self.sqlite_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT payload FROM registry WHERE skill_id = ? ORDER BY created_at DESC", (skill_id,))
                    for row in cursor.fetchall():
                        entries.append(SkillRegistryEntry.from_json_line(row[0]))
            else:
                if not self.jsonl_path.exists():
                    return entries
                with open(self.jsonl_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line: continue
                        try:
                            entry = SkillRegistryEntry.from_json_line(line)
                            if entry.skill_id == skill_id:
                                entries.append(entry)
                        except json.JSONDecodeError:
                            continue
                entries.sort(key=lambda e: e.created_at, reverse=True)
            return entries
        except Exception:
            return entries

    def count_entries(self) -> int:
        try:
            if self.backend == "sqlite" and self.sqlite_path.exists():
                with sqlite3.connect(self.sqlite_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM registry")
                    return cursor.fetchone()[0]
            else:
                count = 0
                if not self.jsonl_path.exists(): return 0
                with open(self.jsonl_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip(): count += 1
                return count
        except Exception:
            return 0

    def _generate_revision(self) -> str:
        import uuid
        uid = uuid.uuid4().hex[:6].upper()
        return f"REV-{uid}"


# ============================================================================
# Singleton / Factory
# ============================================================================

_registry_store_instance: Optional[RegistryStore] = None
_registry_store_lock = threading.Lock()


def get_registry_store(registry_path: Optional[Path] = None) -> RegistryStore:
    global _registry_store_instance
    with _registry_store_lock:
        if _registry_store_instance is None:
            _registry_store_instance = RegistryStore(registry_path)
        return _registry_store_instance


def reset_registry_store():
    global _registry_store_instance
    with _registry_store_lock:
        _registry_store_instance = None
'''

file_path = r'd:\GM-SkillForge\skillforge\src\storage\registry_store.py'
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Rewrote registry_store.py with SQLite multi-backend architecture")
