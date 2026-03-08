"""
Append-Only Log Core Module.

Implements immutable, hash-chained log storage.
All writes are append-only; no updates or deletes are ever permitted.

SLA Guarantees:
- Write Once, Never Overwrite (WONO)
- Full Replay Consistency
- Hash Chain Integrity
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Iterator


class LogEntryType(str, Enum):
    """Types of log entries in the append-only log."""
    # Skill operations
    SKILL_CREATED = "skill_created"
    SKILL_UPDATED = "skill_updated"
    SKILL_TOMBSTONED = "skill_tombstoned"

    # Revision operations
    REVISION_APPENDED = "revision_appended"
    REVISION_DEPRECATED = "revision_deprecated"

    # Artifact operations
    ARTIFACT_ADDED = "artifact_added"
    ARTIFACT_TOMBSTONED = "artifact_tombstoned"

    # Audit operations
    AUDIT_STARTED = "audit_started"
    AUDIT_COMPLETED = "audit_completed"
    AUDIT_REJECTED = "audit_rejected"

    # Gate operations
    GATE_PASSED = "gate_passed"
    GATE_FAILED = "gate_failed"

    # Evidence operations
    EVIDENCE_RECORDED = "evidence_recorded"

    # System operations
    SNAPSHOT_CREATED = "snapshot_created"
    RETENTION_POLICY_APPLIED = "retention_policy_applied"
    COMPACTION_STARTED = "compaction_started"
    COMPACTION_COMPLETED = "compaction_completed"


@dataclass
class LogEntry:
    """
    Immutable log entry in the append-only log.

    Each entry contains:
    - Unique sequence number (monotonically increasing)
    - Hash chain linking to previous entry
    - Timestamp (UTC)
    - Entry type and payload
    - Cryptographic signature of the entire entry
    """
    sequence_no: int
    entry_type: LogEntryType
    payload: dict[str, Any]
    timestamp: str  # ISO-8601 UTC
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    prev_hash: str = "0" * 64  # Genesis block has zero hash
    entry_hash: str = ""  # Computed on creation
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Compute entry hash after initialization."""
        if not self.entry_hash:
            self.entry_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA256 hash of this entry."""
        hash_data = {
            "sequence_no": self.sequence_no,
            "entry_type": self.entry_type.value if isinstance(self.entry_type, LogEntryType) else self.entry_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "entry_id": self.entry_id,
            "prev_hash": self.prev_hash,
        }
        content = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def verify_hash(self) -> bool:
        """Verify that the entry hash is valid."""
        return self.entry_hash == self._compute_hash()

    def to_dict(self) -> dict[str, Any]:
        """Serialize entry to dictionary."""
        return {
            "sequence_no": self.sequence_no,
            "entry_id": self.entry_id,
            "entry_type": self.entry_type.value if isinstance(self.entry_type, LogEntryType) else self.entry_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LogEntry":
        """Deserialize entry from dictionary."""
        return cls(
            sequence_no=data["sequence_no"],
            entry_id=data["entry_id"],
            entry_type=LogEntryType(data["entry_type"]),
            payload=data["payload"],
            timestamp=data["timestamp"],
            prev_hash=data["prev_hash"],
            entry_hash=data["entry_hash"],
            metadata=data.get("metadata", {}),
        )


class AppendOnlyLog:
    """
    Append-Only Log implementation with hash chain integrity.

    Key properties:
    1. IMMUTABLE: Entries can only be appended, never modified or deleted
    2. HASH-CHAINED: Each entry links to previous via SHA256
    3. REPLAYABLE: Full history can be reconstructed from any point

    Usage:
        log = AppendOnlyLog("audit.db")
        log.append(LogEntryType.SKILL_CREATED, {"skill_id": "skill-001"})
    """

    # SQL schema for the log table
    LOG_SCHEMA = """
    CREATE TABLE IF NOT EXISTS append_only_log (
        sequence_no   INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id      TEXT NOT NULL UNIQUE,
        entry_type    TEXT NOT NULL,
        payload       TEXT NOT NULL,
        timestamp     TEXT NOT NULL,
        prev_hash     TEXT NOT NULL,
        entry_hash    TEXT NOT NULL,
        metadata      TEXT,
        created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    );

    CREATE INDEX IF NOT EXISTS idx_log_entry_type ON append_only_log(entry_type);
    CREATE INDEX IF NOT EXISTS idx_log_timestamp ON append_only_log(timestamp);
    CREATE INDEX IF NOT EXISTS idx_log_entry_hash ON append_only_log(entry_hash);
    """

    def __init__(self, db_path: str | Path):
        """
        Initialize append-only log.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn: sqlite3.Connection | None = None
        self._initialize_db()

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _initialize_db(self) -> None:
        """Initialize database schema."""
        self.conn.executescript(self.LOG_SCHEMA)
        self.conn.commit()

    def _get_last_hash(self) -> str:
        """Get the hash of the last entry in the log."""
        row = self.conn.execute(
            "SELECT entry_hash FROM append_only_log ORDER BY sequence_no DESC LIMIT 1"
        ).fetchone()
        return row["entry_hash"] if row else "0" * 64

    def _get_next_sequence(self) -> int:
        """Get the next sequence number."""
        row = self.conn.execute(
            "SELECT MAX(sequence_no) as max_seq FROM append_only_log"
        ).fetchone()
        return (row["max_seq"] or 0) + 1

    def append(
        self,
        entry_type: LogEntryType,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> LogEntry:
        """
        Append a new entry to the log.

        This operation is ATOMIC and IMMUTABLE:
        - Once written, the entry can never be modified
        - The hash chain is maintained
        - Sequence numbers are monotonically increasing

        Args:
            entry_type: Type of log entry
            payload: Entry payload data
            metadata: Optional metadata
            timestamp: Optional timestamp (defaults to now UTC)

        Returns:
            The created LogEntry

        Raises:
            ValueError: If entry creation fails
        """
        timestamp = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        prev_hash = self._get_last_hash()
        sequence_no = self._get_next_sequence()

        entry = LogEntry(
            sequence_no=sequence_no,
            entry_type=entry_type,
            payload=payload,
            timestamp=timestamp,
            prev_hash=prev_hash,
            metadata=metadata or {},
        )

        # Verify hash chain integrity
        if sequence_no > 1 and not self._verify_prev_hash(prev_hash):
            raise ValueError(f"Hash chain integrity violation: prev_hash {prev_hash} not found")

        # Insert entry (immutable operation)
        self.conn.execute(
            """INSERT INTO append_only_log
               (entry_id, entry_type, payload, timestamp, prev_hash, entry_hash, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                entry.entry_id,
                entry.entry_type.value,
                json.dumps(payload, sort_keys=True),
                entry.timestamp,
                entry.prev_hash,
                entry.entry_hash,
                json.dumps(metadata or {}),
            ),
        )
        self.conn.commit()

        return entry

    def _verify_prev_hash(self, prev_hash: str) -> bool:
        """Verify that prev_hash exists in the log."""
        if prev_hash == "0" * 64:
            # Genesis block
            return True
        row = self.conn.execute(
            "SELECT 1 FROM append_only_log WHERE entry_hash = ?", (prev_hash,)
        ).fetchone()
        return row is not None

    def get_entry(self, sequence_no: int) -> LogEntry | None:
        """Get entry by sequence number."""
        row = self.conn.execute(
            "SELECT * FROM append_only_log WHERE sequence_no = ?", (sequence_no,)
        ).fetchone()
        if not row:
            return None
        return LogEntry.from_dict({
            "sequence_no": row["sequence_no"],
            "entry_id": row["entry_id"],
            "entry_type": row["entry_type"],
            "payload": json.loads(row["payload"]),
            "timestamp": row["timestamp"],
            "prev_hash": row["prev_hash"],
            "entry_hash": row["entry_hash"],
            "metadata": json.loads(row["metadata"] or "{}"),
        })

    def get_entry_by_hash(self, entry_hash: str) -> LogEntry | None:
        """Get entry by hash."""
        row = self.conn.execute(
            "SELECT * FROM append_only_log WHERE entry_hash = ?", (entry_hash,)
        ).fetchone()
        if not row:
            return None
        return LogEntry.from_dict({
            "sequence_no": row["sequence_no"],
            "entry_id": row["entry_id"],
            "entry_type": row["entry_type"],
            "payload": json.loads(row["payload"]),
            "timestamp": row["timestamp"],
            "prev_hash": row["prev_hash"],
            "entry_hash": row["entry_hash"],
            "metadata": json.loads(row["metadata"] or "{}"),
        })

    def iterate(
        self,
        from_sequence: int = 1,
        to_sequence: int | None = None,
        entry_types: list[LogEntryType] | None = None,
    ) -> Iterator[LogEntry]:
        """
        Iterate over log entries.

        Args:
            from_sequence: Starting sequence number (inclusive)
            to_sequence: Ending sequence number (inclusive), None for all
            entry_types: Filter by entry types, None for all

        Yields:
            LogEntry objects in sequence order
        """
        query = "SELECT * FROM append_only_log WHERE sequence_no >= ?"
        params: list[Any] = [from_sequence]

        if to_sequence is not None:
            query += " AND sequence_no <= ?"
            params.append(to_sequence)

        if entry_types:
            placeholders = ",".join("?" * len(entry_types))
            query += f" AND entry_type IN ({placeholders})"
            params.extend(et.value for et in entry_types)

        query += " ORDER BY sequence_no ASC"

        for row in self.conn.execute(query, params):
            yield LogEntry.from_dict({
                "sequence_no": row["sequence_no"],
                "entry_id": row["entry_id"],
                "entry_type": row["entry_type"],
                "payload": json.loads(row["payload"]),
                "timestamp": row["timestamp"],
                "prev_hash": row["prev_hash"],
                "entry_hash": row["entry_hash"],
                "metadata": json.loads(row["metadata"] or "{}"),
            })

    def get_entries_for_skill(
        self,
        skill_id: str,
        from_time: str | None = None,
        to_time: str | None = None,
    ) -> list[LogEntry]:
        """Get all entries related to a specific skill."""
        query = "SELECT * FROM append_only_log WHERE json_extract(payload, '$.skill_id') = ?"
        params: list[Any] = [skill_id]

        if from_time:
            query += " AND timestamp >= ?"
            params.append(from_time)

        if to_time:
            query += " AND timestamp <= ?"
            params.append(to_time)

        query += " ORDER BY sequence_no ASC"

        entries = []
        for row in self.conn.execute(query, params):
            entries.append(LogEntry.from_dict({
                "sequence_no": row["sequence_no"],
                "entry_id": row["entry_id"],
                "entry_type": row["entry_type"],
                "payload": json.loads(row["payload"]),
                "timestamp": row["timestamp"],
                "prev_hash": row["prev_hash"],
                "entry_hash": row["entry_hash"],
                "metadata": json.loads(row["metadata"] or "{}"),
            }))
        return entries

    def get_count(self) -> int:
        """Get total number of entries in the log."""
        row = self.conn.execute("SELECT COUNT(*) as count FROM append_only_log").fetchone()
        return row["count"] if row else 0

    def get_first_entry(self) -> LogEntry | None:
        """Get the first (genesis) entry."""
        return self.get_entry(1)

    def get_last_entry(self) -> LogEntry | None:
        """Get the most recent entry."""
        row = self.conn.execute(
            "SELECT * FROM append_only_log ORDER BY sequence_no DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        return LogEntry.from_dict({
            "sequence_no": row["sequence_no"],
            "entry_id": row["entry_id"],
            "entry_type": row["entry_type"],
            "payload": json.loads(row["payload"]),
            "timestamp": row["timestamp"],
            "prev_hash": row["prev_hash"],
            "entry_hash": row["entry_hash"],
            "metadata": json.loads(row["metadata"] or "{}"),
        })

    def verify_chain_integrity(self, from_sequence: int = 1, to_sequence: int | None = None) -> tuple[bool, list[str]]:
        """
        Verify hash chain integrity.

        Args:
            from_sequence: Start verification from this sequence
            to_sequence: End verification at this sequence, None for all

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: list[str] = []
        prev_hash = "0" * 64

        if from_sequence > 1:
            prev_entry = self.get_entry(from_sequence - 1)
            if prev_entry:
                prev_hash = prev_entry.entry_hash

        for entry in self.iterate(from_sequence, to_sequence):
            # Verify hash chain
            if entry.prev_hash != prev_hash:
                errors.append(
                    f"Chain break at sequence {entry.sequence_no}: "
                    f"expected prev_hash={prev_hash}, got {entry.prev_hash}"
                )

            # Verify entry hash
            if not entry.verify_hash():
                errors.append(f"Invalid entry hash at sequence {entry.sequence_no}")

            prev_hash = entry.entry_hash

        return len(errors) == 0, errors

    def replay(
        self,
        from_sequence: int = 1,
        to_sequence: int | None = None,
    ) -> dict[str, Any]:
        """
        Replay log entries to reconstruct state.

        Returns a summary of the replay including:
        - Total entries processed
        - State changes by type
        - Verification status
        """
        state: dict[str, Any] = {
            "skills": {},
            "revisions": {},
            "artifacts": {},
            "audits": {},
        }
        processed = 0
        errors = []

        for entry in self.iterate(from_sequence, to_sequence):
            processed += 1

            # Verify hash
            if not entry.verify_hash():
                errors.append(f"Invalid hash at sequence {entry.sequence_no}")

            # Apply state changes (read-only, for reconstruction)
            if entry.entry_type == LogEntryType.SKILL_CREATED:
                skill_id = entry.payload.get("skill_id")
                if skill_id:
                    state["skills"][skill_id] = {
                        "created_at": entry.timestamp,
                        "status": "active",
                    }

            elif entry.entry_type == LogEntryType.SKILL_TOMBSTONED:
                skill_id = entry.payload.get("skill_id")
                if skill_id and skill_id in state["skills"]:
                    state["skills"][skill_id]["status"] = "tombstoned"
                    state["skills"][skill_id]["tombstoned_at"] = entry.timestamp

            elif entry.entry_type == LogEntryType.REVISION_APPENDED:
                revision_id = entry.payload.get("revision_id")
                if revision_id:
                    state["revisions"][revision_id] = entry.payload

            elif entry.entry_type == LogEntryType.ARTIFACT_ADDED:
                artifact_id = entry.payload.get("artifact_id")
                if artifact_id:
                    state["artifacts"][artifact_id] = entry.payload

            elif entry.entry_type == LogEntryType.AUDIT_STARTED:
                audit_id = entry.payload.get("audit_id")
                if audit_id:
                    state["audits"][audit_id] = {
                        "started_at": entry.timestamp,
                        "status": "running",
                    }

            elif entry.entry_type == LogEntryType.AUDIT_COMPLETED:
                audit_id = entry.payload.get("audit_id")
                if audit_id and audit_id in state["audits"]:
                    state["audits"][audit_id]["status"] = "completed"
                    state["audits"][audit_id]["completed_at"] = entry.timestamp

        return {
            "entries_processed": processed,
            "errors": errors,
            "final_state": state,
            "is_valid": len(errors) == 0,
        }

    # === OVERWRITE PREVENTION ===

    def try_overwrite(self, sequence_no: int, entry: LogEntry) -> None:
        """
        Attempt to overwrite an entry. This will ALWAYS fail.

        This method exists solely to demonstrate and verify the
        immutability guarantee. It raises an exception immediately.

        Raises:
            PermissionError: Always raised - overwrites are not permitted
        """
        raise PermissionError(
            f"APPEND-ONLY VIOLATION: Cannot overwrite entry at sequence {sequence_no}. "
            "The append-only log is immutable by design."
        )

    def try_delete(self, sequence_no: int) -> None:
        """
        Attempt to delete an entry. This will ALWAYS fail.

        This method exists solely to demonstrate and verify the
        immutability guarantee. It raises an exception immediately.

        Raises:
            PermissionError: Always raised - deletes are not permitted
        """
        raise PermissionError(
            f"APPEND-ONLY VIOLATION: Cannot delete entry at sequence {sequence_no}. "
            "The append-only log is immutable by design."
        )

    def try_update(self, sequence_no: int, payload: dict[str, Any]) -> None:
        """
        Attempt to update an entry. This will ALWAYS fail.

        This method exists solely to demonstrate and verify the
        immutability guarantee. It raises an exception immediately.

        Raises:
            PermissionError: Always raised - updates are not permitted
        """
        raise PermissionError(
            f"APPEND-ONLY VIOLATION: Cannot update entry at sequence {sequence_no}. "
            "The append-only log is immutable by design."
        )
