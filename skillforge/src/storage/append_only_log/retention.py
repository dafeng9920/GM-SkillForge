"""
Retention Policy Module for Append-Only Log.

Implements configurable retention policies for audit compliance.
Default: 7 years (2557 days) per financial audit requirements.

Note: Retention applies to DATA accessibility, not LOG entries.
Log entries remain immutable forever for chain integrity.
Compacted data archives maintain evidence for retention period.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class RetentionTier(str, Enum):
    """Retention tier levels."""
    # Standard financial audit retention
    FINANCIAL_AUDIT = "financial_audit"  # 7 years

    # Regulatory compliance (SOX, HIPAA, etc.)
    REGULATORY = "regulatory"  # 7 years

    # Standard business retention
    BUSINESS_STANDARD = "business_standard"  # 3 years

    # Short-term debugging/analysis
    SHORT_TERM = "short_term"  # 90 days

    # Custom retention period
    CUSTOM = "custom"


@dataclass
class RetentionPolicy:
    """
    Retention policy configuration.

    Defines how long data must be retained for compliance purposes.
    The append-only log itself is immutable; retention affects:
    1. Snapshot/compaction frequency
    2. Archive storage duration
    3. Evidence availability windows
    """
    policy_id: str
    name: str
    tier: RetentionTier
    retention_days: int
    description: str = ""

    # Compaction settings
    compaction_interval_days: int = 30
    snapshot_interval_days: int = 7

    # Archive settings
    archive_after_days: int = 365
    archive_format: str = "jsonl.gz"

    # Verification settings
    verify_chain_on_snapshot: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def financial_audit_default(cls) -> "RetentionPolicy":
        """Create default 7-year financial audit retention policy."""
        return cls(
            policy_id="ret-financial-audit-default",
            name="Financial Audit Standard (7 Years)",
            tier=RetentionTier.FINANCIAL_AUDIT,
            retention_days=2557,  # 7 * 365 + leap days
            description="Standard 7-year retention for financial audit compliance (SOX, SEC)",
            compaction_interval_days=30,
            snapshot_interval_days=7,
            archive_after_days=365,
            metadata={
                "compliance_standards": ["SOX", "SEC 17a-4", "FINRA 4511"],
                "jurisdiction": "US",
            },
        )

    @classmethod
    def regulatory_default(cls) -> "RetentionPolicy":
        """Create default regulatory retention policy."""
        return cls(
            policy_id="ret-regulatory-default",
            name="Regulatory Compliance (7 Years)",
            tier=RetentionTier.REGULATORY,
            retention_days=2557,
            description="7-year retention for regulatory compliance (HIPAA, GDPR where applicable)",
            compaction_interval_days=30,
            snapshot_interval_days=7,
            archive_after_days=365,
            metadata={
                "compliance_standards": ["HIPAA", "GDPR"],
            },
        )

    @classmethod
    def business_standard(cls) -> "RetentionPolicy":
        """Create 3-year business standard retention policy."""
        return cls(
            policy_id="ret-business-standard",
            name="Business Standard (3 Years)",
            tier=RetentionTier.BUSINESS_STANDARD,
            retention_days=1095,  # 3 * 365
            description="3-year retention for standard business records",
            compaction_interval_days=60,
            snapshot_interval_days=14,
            archive_after_days=180,
        )

    @classmethod
    def custom(
        cls,
        policy_id: str,
        name: str,
        retention_days: int,
        **kwargs: Any,
    ) -> "RetentionPolicy":
        """Create custom retention policy."""
        return cls(
            policy_id=policy_id,
            name=name,
            tier=RetentionTier.CUSTOM,
            retention_days=retention_days,
            description=kwargs.get("description", f"Custom retention: {retention_days} days"),
            compaction_interval_days=kwargs.get("compaction_interval_days", 30),
            snapshot_interval_days=kwargs.get("snapshot_interval_days", 7),
            archive_after_days=kwargs.get("archive_after_days", 365),
            metadata=kwargs.get("metadata", {}),
        )

    @property
    def retention_years(self) -> float:
        """Retention period in years."""
        return self.retention_days / 365.25

    @property
    def cutoff_date(self) -> str:
        """Calculate cutoff date for retention."""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> dict[str, Any]:
        """Serialize policy to dictionary."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "tier": self.tier.value,
            "retention_days": self.retention_days,
            "description": self.description,
            "compaction_interval_days": self.compaction_interval_days,
            "snapshot_interval_days": self.snapshot_interval_days,
            "archive_after_days": self.archive_after_days,
            "archive_format": self.archive_format,
            "verify_chain_on_snapshot": self.verify_chain_on_snapshot,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RetentionPolicy":
        """Deserialize policy from dictionary."""
        return cls(
            policy_id=data["policy_id"],
            name=data["name"],
            tier=RetentionTier(data["tier"]),
            retention_days=data["retention_days"],
            description=data.get("description", ""),
            compaction_interval_days=data.get("compaction_interval_days", 30),
            snapshot_interval_days=data.get("snapshot_interval_days", 7),
            archive_after_days=data.get("archive_after_days", 365),
            archive_format=data.get("archive_format", "jsonl.gz"),
            verify_chain_on_snapshot=data.get("verify_chain_on_snapshot", True),
            metadata=data.get("metadata", {}),
        )


class RetentionManager:
    """
    Manages retention policies for the append-only log.

    Responsibilities:
    1. Store and retrieve retention policies
    2. Check retention compliance
    3. Manage snapshots and archives
    4. Track retention policy changes
    """

    RETENTION_SCHEMA = """
    CREATE TABLE IF NOT EXISTS retention_policies (
        policy_id     TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        tier          TEXT NOT NULL,
        retention_days INTEGER NOT NULL,
        description   TEXT,
        config_json   TEXT NOT NULL,
        created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
        updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    );

    CREATE TABLE IF NOT EXISTS retention_policy_bindings (
        skill_id      TEXT NOT NULL,
        policy_id     TEXT NOT NULL REFERENCES retention_policies(policy_id),
        bound_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
        bound_by      TEXT,
        PRIMARY KEY (skill_id, policy_id)
    );

    CREATE TABLE IF NOT EXISTS snapshots (
        snapshot_id   TEXT PRIMARY KEY,
        snapshot_type TEXT NOT NULL,
        sequence_from INTEGER NOT NULL,
        sequence_to   INTEGER NOT NULL,
        snapshot_hash TEXT NOT NULL,
        file_path     TEXT,
        created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
        verified_at   TEXT,
        metadata      TEXT
    );

    CREATE TABLE IF NOT EXISTS archives (
        archive_id    TEXT PRIMARY KEY,
        snapshot_id   TEXT REFERENCES snapshots(snapshot_id),
        archive_path  TEXT NOT NULL,
        archive_hash  TEXT NOT NULL,
        date_from     TEXT NOT NULL,
        date_to       TEXT NOT NULL,
        policy_id     TEXT REFERENCES retention_policies(policy_id),
        created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
        expires_at    TEXT NOT NULL
    );
    """

    def __init__(self, db_path: str | Path, default_policy: RetentionPolicy | None = None):
        """
        Initialize retention manager.

        Args:
            db_path: Path to SQLite database
            default_policy: Default retention policy (7-year if not specified)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.default_policy = default_policy or RetentionPolicy.financial_audit_default()

        self._conn: sqlite3.Connection | None = None
        self._initialize_db()
        self._ensure_default_policy()

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
        self.conn.executescript(self.RETENTION_SCHEMA)
        self.conn.commit()

    def _ensure_default_policy(self) -> None:
        """Ensure default policy exists."""
        self.save_policy(self.default_policy)

    def save_policy(self, policy: RetentionPolicy) -> None:
        """Save or update a retention policy."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        self.conn.execute(
            """INSERT OR REPLACE INTO retention_policies
               (policy_id, name, tier, retention_days, description, config_json, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                policy.policy_id,
                policy.name,
                policy.tier.value,
                policy.retention_days,
                policy.description,
                json.dumps(policy.to_dict()),
                now,
            ),
        )
        self.conn.commit()

    def get_policy(self, policy_id: str) -> RetentionPolicy | None:
        """Get a retention policy by ID."""
        row = self.conn.execute(
            "SELECT config_json FROM retention_policies WHERE policy_id = ?",
            (policy_id,),
        ).fetchone()

        if not row:
            return None

        return RetentionPolicy.from_dict(json.loads(row["config_json"]))

    def list_policies(self) -> list[RetentionPolicy]:
        """List all retention policies."""
        rows = self.conn.execute(
            "SELECT config_json FROM retention_policies ORDER BY name"
        ).fetchall()

        return [RetentionPolicy.from_dict(json.loads(r["config_json"])) for r in rows]

    def bind_policy_to_skill(self, skill_id: str, policy_id: str, bound_by: str = "") -> None:
        """Bind a retention policy to a skill."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        self.conn.execute(
            """INSERT OR REPLACE INTO retention_policy_bindings
               (skill_id, policy_id, bound_at, bound_by)
               VALUES (?, ?, ?, ?)""",
            (skill_id, policy_id, now, bound_by),
        )
        self.conn.commit()

    def get_policy_for_skill(self, skill_id: str) -> RetentionPolicy:
        """Get the retention policy for a skill (or default)."""
        row = self.conn.execute(
            """SELECT rp.config_json
               FROM retention_policy_bindings rpb
               JOIN retention_policies rp ON rpb.policy_id = rp.policy_id
               WHERE rpb.skill_id = ?""",
            (skill_id,),
        ).fetchone()

        if row:
            return RetentionPolicy.from_dict(json.loads(row["config_json"]))

        return self.default_policy

    def check_compliance(
        self,
        skill_id: str,
        entries_from_date: str,
    ) -> dict[str, Any]:
        """
        Check if retention is compliant for a skill.

        Args:
            skill_id: Skill to check
            entries_from_date: Oldest entry date required

        Returns:
            Compliance status and details
        """
        policy = self.get_policy_for_skill(skill_id)
        cutoff_date = policy.cutoff_date

        is_compliant = entries_from_date >= cutoff_date

        return {
            "skill_id": skill_id,
            "policy_id": policy.policy_id,
            "policy_name": policy.name,
            "retention_days": policy.retention_days,
            "cutoff_date": cutoff_date,
            "oldest_required": entries_from_date,
            "is_compliant": is_compliant,
            "deficit_days": max(0, (datetime.strptime(cutoff_date[:10], "%Y-%m-%d") -
                                    datetime.strptime(entries_from_date[:10], "%Y-%m-%d")).days) if not is_compliant else 0,
        }

    def create_snapshot(
        self,
        snapshot_id: str,
        snapshot_type: str,
        sequence_from: int,
        sequence_to: int,
        snapshot_hash: str,
        file_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record a snapshot creation."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        self.conn.execute(
            """INSERT INTO snapshots
               (snapshot_id, snapshot_type, sequence_from, sequence_to, snapshot_hash, file_path, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                snapshot_id,
                snapshot_type,
                sequence_from,
                sequence_to,
                snapshot_hash,
                file_path,
                json.dumps(metadata or {}),
            ),
        )
        self.conn.commit()

        return {
            "snapshot_id": snapshot_id,
            "snapshot_type": snapshot_type,
            "sequence_from": sequence_from,
            "sequence_to": sequence_to,
            "snapshot_hash": snapshot_hash,
            "created_at": now,
        }

    def list_snapshots(self, snapshot_type: str | None = None) -> list[dict[str, Any]]:
        """List all snapshots, optionally filtered by type."""
        if snapshot_type:
            rows = self.conn.execute(
                "SELECT * FROM snapshots WHERE snapshot_type = ? ORDER BY created_at DESC",
                (snapshot_type,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM snapshots ORDER BY created_at DESC"
            ).fetchall()

        return [dict(r) for r in rows]

    def create_archive(
        self,
        archive_id: str,
        snapshot_id: str,
        archive_path: str,
        archive_hash: str,
        date_from: str,
        date_to: str,
        policy_id: str,
    ) -> dict[str, Any]:
        """Create an archive record with expiration based on retention policy."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        policy = self.get_policy(policy_id)
        if not policy:
            policy = self.default_policy

        # Calculate expiration date
        expires_at = (
            datetime.utcnow() + timedelta(days=policy.retention_days)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.conn.execute(
            """INSERT INTO archives
               (archive_id, snapshot_id, archive_path, archive_hash, date_from, date_to, policy_id, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                archive_id,
                snapshot_id,
                archive_path,
                archive_hash,
                date_from,
                date_to,
                policy_id,
                expires_at,
            ),
        )
        self.conn.commit()

        return {
            "archive_id": archive_id,
            "snapshot_id": snapshot_id,
            "archive_path": archive_path,
            "expires_at": expires_at,
            "policy_id": policy_id,
        }

    def get_expired_archives(self) -> list[dict[str, Any]]:
        """Get archives that have expired past retention period."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        rows = self.conn.execute(
            "SELECT * FROM archives WHERE expires_at < ?",
            (now,),
        ).fetchall()

        return [dict(r) for r in rows]

    def cleanup_expired_archives(self) -> list[str]:
        """
        Remove expired archive records (for compliance tracking).

        Note: This only removes the DATABASE RECORDS for expired archives.
        Actual file deletion should be handled by a separate process
        with appropriate approvals.
        """
        expired = self.get_expired_archives()
        archive_ids = [a["archive_id"] for a in expired]

        if archive_ids:
            placeholders = ",".join("?" * len(archive_ids))
            self.conn.execute(
                f"DELETE FROM archives WHERE archive_id IN ({placeholders})",
                archive_ids,
            )
            self.conn.commit()

        return archive_ids


# Predefined 7-year policy instance
SEVEN_YEAR_POLICY = RetentionPolicy.financial_audit_default()
