"""
Tests for Registry Store - SEEDS-P0-1 Registry 测试

测试覆盖：
1. Append-only 操作
2. 按skill_id读取最新ACTIVE revision
3. 不覆盖历史记录
4. 不跳过ACTIVE过滤

Contract: docs/SEEDS_v0.md
Job ID: L45-D4-SEEDS-P0-20260220-004
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from storage.registry_store import (
    RegistryStore,
    SkillRegistryEntry,
    RegistryQueryResult,
    RegistryAppendResult,
    get_registry_store,
    reset_registry_store,
)


# ============================================================================
# Test Constants
# ============================================================================

TEST_SKILL_ID = "SKILL-TEST-001"
TEST_REPO_URL = "https://github.com/test/skill-package"
TEST_COMMIT_SHA = "a1b2c3d4e5f6789012345678901234567890abcd"
JOB_ID = "L45-D4-SEEDS-P0-20260220-004"


# ============================================================================
# Test Cases
# ============================================================================

class TestRegistryStore(unittest.TestCase):
    """Registry Store Tests."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary registry file for each test
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / "test_skills.jsonl"
        self.store = RegistryStore(self.registry_path)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if self.registry_path.exists():
            self.registry_path.unlink()
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_entry(self, skill_id: str, revision: str, tombstone_state: str = "ACTIVE") -> SkillRegistryEntry:
        """Helper to create a test entry."""
        return SkillRegistryEntry(
            skill_id=skill_id,
            source={
                "type": "repo",
                "repo_url": TEST_REPO_URL,
                "commit_sha": TEST_COMMIT_SHA,
            },
            revision=revision,
            pack_hash=f"PACK-HASH-{revision}",
            permit_id=f"PERMIT-{revision}",
            tombstone_state=tombstone_state,
        )

    # -------------------------------------------------------------------------
    # Test 1: Append-only operation
    # -------------------------------------------------------------------------
    def test_append_single_entry(self):
        """
        Test 1: Append a single entry to the registry.

        Expected: Entry is written to file and can be retrieved.
        """
        print("\n=== Test 1: Append Single Entry ===")

        entry = self._create_entry(TEST_SKILL_ID, "REV-001")
        result = self.store.append(entry)

        print(f"  Append result: success={result.success}, revision={result.revision}")

        self.assertTrue(result.success)
        self.assertEqual(result.revision, "REV-001")

        # Verify file contains the entry
        self.assertEqual(self.store.count_entries(), 1)

    def test_append_multiple_entries(self):
        """
        Test 2: Append multiple entries (append-only, no overwrite).

        Expected: All entries are preserved, none are overwritten.
        """
        print("\n=== Test 2: Append Multiple Entries ===")

        entries = [
            self._create_entry(TEST_SKILL_ID, "REV-001"),
            self._create_entry(TEST_SKILL_ID, "REV-002"),
            self._create_entry(TEST_SKILL_ID, "REV-003"),
        ]

        for entry in entries:
            result = self.store.append(entry)
            self.assertTrue(result.success, f"Failed to append {entry.revision}")

        # Verify all entries are preserved (append-only, no overwrite)
        self.assertEqual(self.store.count_entries(), 3)
        print(f"  Total entries: {self.store.count_entries()}")

        # Verify history is preserved
        all_revisions = self.store.get_all_revisions(TEST_SKILL_ID)
        self.assertEqual(len(all_revisions), 3)
        print(f"  All revisions preserved: {[e.revision for e in all_revisions]}")

    # -------------------------------------------------------------------------
    # Test 3: Read latest ACTIVE revision
    # -------------------------------------------------------------------------
    def test_get_latest_active(self):
        """
        Test 3: Get latest ACTIVE revision for a skill_id.

        Expected: Returns the most recent entry with tombstone_state == "ACTIVE"
        """
        print("\n=== Test 3: Get Latest Active ===")

        # Append multiple entries
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-001"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-002"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-003"))

        # Get latest ACTIVE
        result = self.store.get_latest_active(TEST_SKILL_ID)

        print(f"  Latest ACTIVE: revision={result.entry.revision if result.entry else None}")

        self.assertTrue(result.success)
        self.assertIsNotNone(result.entry)
        self.assertEqual(result.entry.revision, "REV-003")
        self.assertEqual(result.entry.tombstone_state, "ACTIVE")

    def test_get_latest_active_with_tombstone(self):
        """
        Test 4: Get latest ACTIVE when some entries are TOMBSTONED.

        Expected: Only ACTIVE entries are considered, TOMBSTONED are skipped.
        """
        print("\n=== Test 4: Get Latest Active with Tombstone ===")

        # Append entries with mixed states
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-001", "ACTIVE"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-002", "TOMBSTONED"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-003", "ACTIVE"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-004", "TOMBSTONED"))

        # Get latest ACTIVE
        result = self.store.get_latest_active(TEST_SKILL_ID)

        print(f"  Latest ACTIVE: revision={result.entry.revision if result.entry else None}")

        self.assertTrue(result.success)
        self.assertEqual(result.entry.revision, "REV-003")  # REV-004 is tombstoned
        self.assertEqual(result.entry.tombstone_state, "ACTIVE")

    # -------------------------------------------------------------------------
    # Test 5: ACTIVE filter not skipped
    # -------------------------------------------------------------------------
    def test_active_filter_not_skipped(self):
        """
        Test 5: ACTIVE filter must not be skipped.

        Expected: TOMBSTONED entries are never returned by get_latest_active.
        """
        print("\n=== Test 5: ACTIVE Filter Not Skipped ===")

        # Append only TOMBSTONED entries
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-001", "TOMBSTONED"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-002", "TOMBSTONED"))

        # Try to get latest ACTIVE
        result = self.store.get_latest_active(TEST_SKILL_ID)

        print(f"  Result: success={result.success}, error_code={result.error_code}")

        # Should fail - no ACTIVE entries
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "NOT_FOUND")
        self.assertIsNone(result.entry)

    # -------------------------------------------------------------------------
    # Test 6: History not overwritten
    # -------------------------------------------------------------------------
    def test_history_not_overwritten(self):
        """
        Test 6: History must not be overwritten.

        Expected: All historical entries are preserved and queryable.
        """
        print("\n=== Test 6: History Not Overwritten ===")

        # Append entries
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-001"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-002"))
        self.store.append(self._create_entry(TEST_SKILL_ID, "REV-003"))

        # Get all revisions
        all_revisions = self.store.get_all_revisions(TEST_SKILL_ID)

        print(f"  All revisions: {[e.revision for e in all_revisions]}")

        # Verify all are preserved
        self.assertEqual(len(all_revisions), 3)
        revisions = [e.revision for e in all_revisions]
        self.assertIn("REV-001", revisions)
        self.assertIn("REV-002", revisions)
        self.assertIn("REV-003", revisions)

    # -------------------------------------------------------------------------
    # Test 7: Different skill_ids
    # -------------------------------------------------------------------------
    def test_different_skill_ids(self):
        """
        Test 7: Multiple skill_ids can coexist.

        Expected: Each skill_id has its own revision history.
        """
        print("\n=== Test 7: Different Skill IDs ===")

        # Append entries for different skills
        self.store.append(self._create_entry("SKILL-A", "REV-A001"))
        self.store.append(self._create_entry("SKILL-B", "REV-B001"))
        self.store.append(self._create_entry("SKILL-A", "REV-A002"))
        self.store.append(self._create_entry("SKILL-B", "REV-B002"))

        # Get latest for each
        result_a = self.store.get_latest_active("SKILL-A")
        result_b = self.store.get_latest_active("SKILL-B")

        print(f"  SKILL-A latest: {result_a.entry.revision if result_a.entry else None}")
        print(f"  SKILL-B latest: {result_b.entry.revision if result_b.entry else None}")

        self.assertEqual(result_a.entry.revision, "REV-A002")
        self.assertEqual(result_b.entry.revision, "REV-B002")

    # -------------------------------------------------------------------------
    # Test 8: Entry validation
    # -------------------------------------------------------------------------
    def test_entry_validation(self):
        """
        Test 8: Entry validation.

        Expected: Invalid entries are rejected with appropriate error.
        """
        print("\n=== Test 8: Entry Validation ===")

        # Test missing skill_id
        entry = SkillRegistryEntry(
            skill_id="",
            source={"type": "repo"},
            revision="REV-001",
            pack_hash="PACK-HASH",
            permit_id="PERMIT-001",
        )
        result = self.store.append(entry)

        print(f"  Empty skill_id result: success={result.success}, error_code={result.error_code}")

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "INVALID_ENTRY")

    # -------------------------------------------------------------------------
    # Test 9: SkillRegistryEntry serialization
    # -------------------------------------------------------------------------
    def test_entry_serialization(self):
        """
        Test 9: SkillRegistryEntry serialization/deserialization.

        Expected: Entry can be serialized to JSONL and deserialized correctly.
        """
        print("\n=== Test 9: Entry Serialization ===")

        entry = SkillRegistryEntry(
            skill_id=TEST_SKILL_ID,
            source={"type": "repo", "repo_url": TEST_REPO_URL, "commit_sha": TEST_COMMIT_SHA},
            revision="REV-001",
            pack_hash="PACK-HASH-001",
            permit_id="PERMIT-001",
            tombstone_state="ACTIVE",
            created_at="2026-02-20T12:00:00Z",
        )

        # Serialize
        json_line = entry.to_json_line()
        print(f"  JSON line: {json_line}")

        # Deserialize
        parsed = SkillRegistryEntry.from_json_line(json_line)

        self.assertEqual(parsed.skill_id, entry.skill_id)
        self.assertEqual(parsed.revision, entry.revision)
        self.assertEqual(parsed.pack_hash, entry.pack_hash)
        self.assertEqual(parsed.permit_id, entry.permit_id)
        self.assertEqual(parsed.tombstone_state, entry.tombstone_state)
        self.assertEqual(parsed.created_at, entry.created_at)

    # -------------------------------------------------------------------------
    # Test 10: Singleton factory
    # -------------------------------------------------------------------------
    def test_singleton_factory(self):
        """
        Test 10: Singleton factory.

        Expected: get_registry_store returns the same instance.
        """
        print("\n=== Test 10: Singleton Factory ===")

        # Reset first
        reset_registry_store()

        store1 = get_registry_store()
        store2 = get_registry_store()

        self.assertIs(store1, store2)
        print(f"  Singleton verified: same instance")

        # Clean up
        reset_registry_store()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
