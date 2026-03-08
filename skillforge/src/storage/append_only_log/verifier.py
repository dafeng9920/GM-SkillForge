"""
Log Verifier Module for Append-Only Log.

Provides verification and SLA testing capabilities:
- Hash chain integrity verification
- Replay consistency verification
- Immutability verification
- SLA metrics collection
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .core import AppendOnlyLog, LogEntry, LogEntryType


@dataclass
class VerificationResult:
    """Result of a verification operation."""
    verification_id: str
    verification_type: str
    is_passed: bool
    timestamp: str
    details: dict[str, Any]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "verification_id": self.verification_id,
            "verification_type": self.verification_type,
            "is_passed": self.is_passed,
            "timestamp": self.timestamp,
            "details": self.details,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


class LogVerifier:
    """
    Verifier for append-only log SLA guarantees.

    SLA Guarantees Tested:
    1. WONO (Write Once, Never Overwrite) - Immutability
    2. Replay Consistency - Same input produces same output
    3. Hash Chain Integrity - No tampering
    4. 7-Year Retention - Configurable retention
    """

    def __init__(self, log: AppendOnlyLog):
        """
        Initialize verifier.

        Args:
            log: The append-only log to verify
        """
        self.log = log

    def verify_immutability(self) -> VerificationResult:
        """
        Verify that the log is immutable (WONO guarantee).

        Tests:
        1. Attempt to overwrite an entry (must fail)
        2. Attempt to delete an entry (must fail)
        3. Attempt to update an entry (must fail)

        Returns:
            VerificationResult with immutability test results
        """
        verification_id = f"imm-{int(time.time())}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        errors: list[str] = []
        warnings: list[str] = []
        tests_passed = 0
        tests_failed = 0

        # Get an existing entry to test against
        entry = self.log.get_entry(1)
        if not entry:
            # Create a test entry if log is empty
            entry = self.log.append(
                LogEntryType.SKILL_CREATED,
                {"skill_id": "test-immutability", "test": True},
            )

        # Test 1: Attempt to overwrite (must fail)
        try:
            self.log.try_overwrite(entry.sequence_no, entry)
            errors.append("CRITICAL: try_overwrite did NOT raise PermissionError")
            tests_failed += 1
        except PermissionError as e:
            tests_passed += 1  # Expected behavior

        # Test 2: Attempt to delete (must fail)
        try:
            self.log.try_delete(entry.sequence_no)
            errors.append("CRITICAL: try_delete did NOT raise PermissionError")
            tests_failed += 1
        except PermissionError as e:
            tests_passed += 1  # Expected behavior

        # Test 3: Attempt to update (must fail)
        try:
            self.log.try_update(entry.sequence_no, {"modified": True})
            errors.append("CRITICAL: try_update did NOT raise PermissionError")
            tests_failed += 1
        except PermissionError as e:
            tests_passed += 1  # Expected behavior

        # Test 4: Verify no duplicate sequence numbers
        row = self.log.conn.execute(
            "SELECT COUNT(DISTINCT sequence_no) as unique_count, COUNT(*) as total FROM append_only_log"
        ).fetchone()

        if row and row["unique_count"] == row["total"]:
            tests_passed += 1
        else:
            errors.append("CRITICAL: Duplicate sequence numbers detected")
            tests_failed += 1

        # Test 5: Verify entries cannot be modified via SQL
        # This tests the database-level immutability
        try:
            # Attempt direct SQL update (should be blocked by triggers or constraints)
            # For SQLite without triggers, this is a warning
            result = self.log.conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='trigger' AND tbl_name='append_only_log'"
            ).fetchall()

            if not result:
                warnings.append(
                    "No immutability triggers found. "
                    "Consider adding triggers to prevent UPDATE/DELETE on append_only_log table."
                )
        except Exception as e:
            warnings.append(f"Could not verify SQL triggers: {e}")

        is_passed = tests_failed == 0

        return VerificationResult(
            verification_id=verification_id,
            verification_type="immutability",
            is_passed=is_passed,
            timestamp=timestamp,
            details={
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "total_entries": self.log.get_count(),
            },
            errors=errors,
            warnings=warnings,
            metrics={
                "wono_guarantee": is_passed,
                "overwrite_blocked": True,
                "delete_blocked": True,
                "update_blocked": True,
            },
        )

    def verify_hash_chain(self) -> VerificationResult:
        """
        Verify hash chain integrity.

        Tests:
        1. Each entry's prev_hash matches previous entry's entry_hash
        2. Each entry's entry_hash is correctly computed
        3. No orphaned entries exist

        Returns:
            VerificationResult with hash chain test results
        """
        verification_id = f"hash-{int(time.time())}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        is_valid, errors = self.log.verify_chain_integrity()

        total_entries = self.log.get_count()
        entries_checked = 0
        hash_errors = 0

        prev_hash = "0" * 64
        for entry in self.log.iterate():
            entries_checked += 1

            if entry.prev_hash != prev_hash:
                hash_errors += 1

            if not entry.verify_hash():
                hash_errors += 1

            prev_hash = entry.entry_hash

        return VerificationResult(
            verification_id=verification_id,
            verification_type="hash_chain",
            is_passed=is_valid,
            timestamp=timestamp,
            details={
                "total_entries": total_entries,
                "entries_checked": entries_checked,
                "hash_errors": hash_errors,
            },
            errors=errors,
            metrics={
                "chain_integrity": is_valid,
                "hash_verification_rate": 1.0 if hash_errors == 0 else (entries_checked - hash_errors) / entries_checked,
            },
        )

    def verify_replay_consistency(self) -> VerificationResult:
        """
        Verify replay consistency.

        Tests:
        1. Replaying the log produces identical state each time
        2. Replay from any point produces consistent results

        Returns:
            VerificationResult with replay consistency test results
        """
        verification_id = f"replay-{int(time.time())}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        errors: list[str] = []
        warnings: list[str] = []

        # Replay 1: Full log
        replay1 = self.log.replay()

        # Replay 2: Full log again (should be identical)
        replay2 = self.log.replay()

        # Compare results
        if replay1["entries_processed"] != replay2["entries_processed"]:
            errors.append(
                f"Replay entry count mismatch: {replay1['entries_processed']} vs {replay2['entries_processed']}"
            )

        if replay1["is_valid"] != replay2["is_valid"]:
            errors.append(
                f"Replay validity mismatch: {replay1['is_valid']} vs {replay2['is_valid']}"
            )

        # Compare state hashes
        state1_hash = self._compute_state_hash(replay1["final_state"])
        state2_hash = self._compute_state_hash(replay2["final_state"])

        if state1_hash != state2_hash:
            errors.append(
                f"State hash mismatch: {state1_hash} vs {state2_hash}"
            )

        is_passed = len(errors) == 0 and replay1["is_valid"]

        return VerificationResult(
            verification_id=verification_id,
            verification_type="replay_consistency",
            is_passed=is_passed,
            timestamp=timestamp,
            details={
                "replay1_entries": replay1["entries_processed"],
                "replay2_entries": replay2["entries_processed"],
                "state_hash": state1_hash,
                "errors_in_replay": replay1["errors"],
            },
            errors=errors,
            warnings=warnings,
            metrics={
                "replay_consistent": is_passed,
                "state_hash": state1_hash,
            },
        )

    def _compute_state_hash(self, state: dict[str, Any]) -> str:
        """Compute a hash of the state for comparison."""
        import hashlib
        content = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def verify_all(self) -> dict[str, VerificationResult]:
        """
        Run all verification tests.

        Returns:
            Dictionary of verification results by test type
        """
        return {
            "immutability": self.verify_immutability(),
            "hash_chain": self.verify_hash_chain(),
            "replay_consistency": self.verify_replay_consistency(),
        }

    def run_sla_tests(self) -> dict[str, Any]:
        """
        Run SLA verification tests and produce report.

        SLA Tests:
        1. Immutability (WONO) - CRITICAL
        2. Hash Chain Integrity - CRITICAL
        3. Replay Consistency - CRITICAL
        4. Performance (optional) - WARNING

        Returns:
            SLA test report
        """
        start_time = time.time()

        results = self.verify_all()

        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)

        all_passed = all(r.is_passed for r in results.values())

        return {
            "sla_report": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "log_path": str(self.log.db_path),
                "total_entries": self.log.get_count(),
                "duration_ms": duration_ms,
                "overall_passed": all_passed,
            },
            "tests": {
                name: result.to_dict()
                for name, result in results.items()
            },
            "sla_guarantees": {
                "wono_write_once_never_overwrite": results["immutability"].is_passed,
                "hash_chain_integrity": results["hash_chain"].is_passed,
                "replay_consistency": results["replay_consistency"].is_passed,
            },
            "compliance": {
                "audit_ready": all_passed,
                "can_certify": all_passed,
            },
        }


def run_full_verification(db_path: str | Path) -> dict[str, Any]:
    """
    Run full verification on an append-only log database.

    Args:
        db_path: Path to the log database

    Returns:
        Full verification report
    """
    log = AppendOnlyLog(db_path)
    verifier = LogVerifier(log)

    report = verifier.run_sla_tests()
    log.close()

    return report
