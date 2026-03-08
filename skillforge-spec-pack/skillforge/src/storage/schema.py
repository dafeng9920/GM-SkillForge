"""
SQLite schema and migration for SkillForge Storage Layer.

Tables: skills, revisions, artifacts, tombstones, rag_chunks, integrity_chains
Per AUDIT_ENGINE_PROTOCOL_v1.md Section 5: Upstream Intake & Provenance
Per 对话记录.md Section 五: 数据库核心模型
Per L3 Gap Closure Task T2: Registry/Graph Integrity Verification
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 3

DDL = """
-- SkillForge Storage Schema v2
-- 3D Model: Entity(skill_id) × Artifact(type) × Time(revision)

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id   TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS revisions (
    revision_id     TEXT PRIMARY KEY,
    skill_id        TEXT NOT NULL REFERENCES skills(skill_id),
    effective_at    TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE', 'DEPRECATED', 'TOMBSTONED')),
    manifest_sha256 TEXT,
    path            TEXT,
    quality_level   TEXT CHECK (quality_level IN ('L1','L2','L3','L4','L5')),
    metadata        TEXT,  -- JSON field for catalog_version and other metadata
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_revisions_skill ON revisions(skill_id, effective_at);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id   TEXT PRIMARY KEY,
    revision_id   TEXT NOT NULL REFERENCES revisions(revision_id),
    artifact_type TEXT NOT NULL,
    filename      TEXT NOT NULL,
    sha256        TEXT NOT NULL,
    size_bytes    INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_artifacts_revision ON artifacts(revision_id);

CREATE TABLE IF NOT EXISTS tombstones (
    tombstone_id  TEXT PRIMARY KEY,
    skill_id      TEXT REFERENCES skills(skill_id),
    revision_id   TEXT REFERENCES revisions(revision_id),
    artifact_id   TEXT REFERENCES artifacts(artifact_id),
    reason        TEXT NOT NULL,
    tombstoned_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    tombstoned_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_tombstones_skill ON tombstones(skill_id);

CREATE TABLE IF NOT EXISTS rag_chunks (
    chunk_id     TEXT PRIMARY KEY,
    skill_id     TEXT NOT NULL REFERENCES skills(skill_id),
    revision_id  TEXT NOT NULL REFERENCES revisions(revision_id),
    artifact_id  TEXT REFERENCES artifacts(artifact_id),
    content_text TEXT NOT NULL,
    embedding    BLOB,
    created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_rag_skill ON rag_chunks(skill_id);

-- T2: Registry/Graph Integrity Chain
-- Stores cryptographic hashes of registry state for tamper detection
CREATE TABLE IF NOT EXISTS integrity_chains (
    chain_id        TEXT PRIMARY KEY,
    chain_type      TEXT NOT NULL CHECK (chain_type IN ('registry', 'graph', 'manifest')),
    entity_id       TEXT,                     -- skill_id or graph_id this chain protects
    hash_algorithm  TEXT NOT NULL DEFAULT 'sha256',
    computed_hash   TEXT NOT NULL,            -- hash of entity state at recorded_at
    prev_hash       TEXT,                     -- previous chain entry hash (append-only chain)
    signature       TEXT,                     -- optional cryptographic signature
    recorded_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    recorded_by     TEXT,                     -- node_id or process that recorded this
    metadata        TEXT                      -- JSON field for additional context
);
CREATE INDEX IF NOT EXISTS idx_integrity_entity ON integrity_chains(entity_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_integrity_chain_type ON integrity_chains(chain_type, recorded_at);
"""

# Migration from v1 to v2: add metadata column
MIGRATION_V1_TO_V2 = """
ALTER TABLE revisions ADD COLUMN metadata TEXT;
"""

# Migration from v2 to v3: add integrity_chains table for T2
MIGRATION_V2_TO_V3 = """
CREATE TABLE IF NOT EXISTS integrity_chains (
    chain_id        TEXT PRIMARY KEY,
    chain_type      TEXT NOT NULL CHECK (chain_type IN ('registry', 'graph', 'manifest')),
    entity_id       TEXT,
    hash_algorithm  TEXT NOT NULL DEFAULT 'sha256',
    computed_hash   TEXT NOT NULL,
    prev_hash       TEXT,
    signature       TEXT,
    recorded_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    recorded_by     TEXT,
    metadata        TEXT
);
CREATE INDEX IF NOT EXISTS idx_integrity_entity ON integrity_chains(entity_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_integrity_chain_type ON integrity_chains(chain_type, recorded_at);
"""


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Initialize SQLite database with SkillForge schema."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript(DDL)

    # Check and run migrations if needed
    current_version = check_schema_version(conn)
    if current_version < SCHEMA_VERSION:
        _run_migrations(conn, current_version)

    # Set schema version
    conn.execute(
        "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
        ("schema_version", str(SCHEMA_VERSION)),
    )
    conn.commit()
    return conn


def _run_migrations(conn: sqlite3.Connection, from_version: int) -> None:
    """Run database migrations from a given version to the latest."""
    if from_version < 2:
        try:
            conn.execute(MIGRATION_V1_TO_V2)
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists, ignore
            pass
    if from_version < 3:
        try:
            conn.executescript(MIGRATION_V2_TO_V3)
            conn.commit()
        except sqlite3.OperationalError:
            # Table already exists, ignore
            pass


def check_schema_version(conn: sqlite3.Connection) -> int:
    """Return the current schema version, or 0 if not set."""
    try:
        row = conn.execute(
            "SELECT value FROM schema_meta WHERE key = 'schema_version'"
        ).fetchone()
        return int(row["value"]) if row else 0
    except sqlite3.OperationalError:
        return 0
