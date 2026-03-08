"""
Append-Only Log Infrastructure for SkillForge.

Core principles:
1. IMMUTABILITY: Once written, entries can NEVER be modified or deleted
2. REPLAY: Full history can be reconstructed from log
3. RETENTION: Configurable retention (default 7 years for audit compliance)

Per AUDIT_ENGINE_PROTOCOL:
- All operations are logged before execution
- Every entry has SHA256 hash chain
- Supports temporal queries at any point in history
"""
from __future__ import annotations

from .core import AppendOnlyLog, LogEntry, LogEntryType
from .retention import RetentionPolicy, RetentionManager
from .cluster import LogCluster, NodeRole, ClusterConfig
from .verifier import LogVerifier, VerificationResult

__all__ = [
    "AppendOnlyLog",
    "LogEntry",
    "LogEntryType",
    "RetentionPolicy",
    "RetentionManager",
    "LogCluster",
    "NodeRole",
    "ClusterConfig",
    "LogVerifier",
    "VerificationResult",
]
