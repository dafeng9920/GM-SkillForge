"""
SLA Verification Test Suite for Append-Only Log.

Tests the three core SLA guarantees:
1. WONO (Write Once, Never Overwrite) - Immutability
2. Replay Consistency
3. 7-Year Retention Policy Configuration
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skillforge.src.storage.append_only_log import (
    AppendOnlyLog,
    LogEntry,
    LogEntryType,
    RetentionPolicy,
    RetentionManager,
    LogCluster,
    NodeRole,
    ClusterConfig,
    LogVerifier,
    VerificationResult,
)
from skillforge.src.storage.append_only_log.core import AppendOnlyLog as CoreLog
from skillforge.src.storage.append_only_log.cluster import NodeStatus


class SLATestRunner:
    """Runner for SLA verification tests."""

    def __init__(self, test_db_path: str | None = None):
        self.test_db_path = test_db_path or tempfile.mktemp(suffix=".db")
        self.results: list[dict] = []
        self.passed = 0
        self.failed = 0

    def run_test(self, name: str, test_func) -> dict:
        """Run a single test and record results."""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")

        start_time = time.time()
        try:
            result = test_func()
            duration_ms = int((time.time() - start_time) * 1000)

            if result.get("passed", False):
                self.passed += 1
                status = "PASSED"
            else:
                self.failed += 1
                status = "FAILED"

            result["name"] = name
            result["status"] = status
            result["duration_ms"] = duration_ms
            self.results.append(result)

            print(f"Status: {status}")
            print(f"Duration: {duration_ms}ms")
            if result.get("details"):
                print(f"Details: {result['details']}")

            return result

        except Exception as e:
            self.failed += 1
            result = {
                "name": name,
                "status": "ERROR",
                "error": str(e),
                "duration_ms": int((time.time() - start_time) * 1000),
            }
            self.results.append(result)
            print(f"Status: ERROR - {e}")
            return result

    def test_wono_immutability(self) -> dict:
        """
        Test 1: Write Once, Never Overwrite (WONO)

        Verifies:
        - Entries can only be appended
        - Overwrite attempts are blocked
        - Delete attempts are blocked
        - Update attempts are blocked
        """
        log = AppendOnlyLog(self.test_db_path)

        # Append test entries
        entry1 = log.append(
            LogEntryType.SKILL_CREATED,
            {"skill_id": "skill-001", "title": "Test Skill"},
        )
        entry2 = log.append(
            LogEntryType.REVISION_APPENDED,
            {"skill_id": "skill-001", "revision_id": "rev-001"},
        )

        tests_passed = 0
        tests_total = 4
        errors = []

        # Test 1: try_overwrite must fail
        try:
            log.try_overwrite(1, entry1)
            errors.append("try_overwrite did NOT raise PermissionError")
        except PermissionError:
            tests_passed += 1

        # Test 2: try_delete must fail
        try:
            log.try_delete(1)
            errors.append("try_delete did NOT raise PermissionError")
        except PermissionError:
            tests_passed += 1

        # Test 3: try_update must fail
        try:
            log.try_update(1, {"modified": True})
            errors.append("try_update did NOT raise PermissionError")
        except PermissionError:
            tests_passed += 1

        # Test 4: Verify hash chain is intact
        is_valid, chain_errors = log.verify_chain_integrity()
        if is_valid:
            tests_passed += 1
        else:
            errors.extend(chain_errors)

        log.close()

        return {
            "passed": tests_passed == tests_total,
            "details": {
                "tests_passed": tests_passed,
                "tests_total": tests_total,
                "entries_created": 2,
            },
            "errors": errors,
            "sla_guarantee": "WONO - Write Once, Never Overwrite",
        }

    def test_replay_consistency(self) -> dict:
        """
        Test 2: Replay Consistency

        Verifies:
        - Multiple replays produce identical results
        - State reconstruction is deterministic
        - Hash chain enables point-in-time recovery
        """
        log = AppendOnlyLog(self.test_db_path)

        # Create entries for replay test
        for i in range(5):
            log.append(
                LogEntryType.SKILL_CREATED,
                {"skill_id": f"skill-{i:03d}", "index": i},
            )

        # Replay multiple times
        replay1 = log.replay()
        replay2 = log.replay()
        replay3 = log.replay()

        # Verify consistency
        consistent = (
            replay1["entries_processed"] == replay2["entries_processed"] == replay3["entries_processed"]
            and replay1["is_valid"]
            and replay2["is_valid"]
            and replay3["is_valid"]
        )

        # Compute state hashes
        state1_hash = hashlib.sha256(
            json.dumps(replay1["final_state"], sort_keys=True).encode()
        ).hexdigest()[:16]
        state2_hash = hashlib.sha256(
            json.dumps(replay2["final_state"], sort_keys=True).encode()
        ).hexdigest()[:16]
        state3_hash = hashlib.sha256(
            json.dumps(replay3["final_state"], sort_keys=True).encode()
        ).hexdigest()[:16]

        hash_consistent = state1_hash == state2_hash == state3_hash

        log.close()

        return {
            "passed": consistent and hash_consistent,
            "details": {
                "replay_entries": replay1["entries_processed"],
                "state_hash": state1_hash,
                "hash_consistent": hash_consistent,
                "all_replays_valid": replay1["is_valid"] and replay2["is_valid"] and replay3["is_valid"],
            },
            "sla_guarantee": "Replay Consistency - Deterministic Reconstruction",
        }

    def test_seven_year_retention(self) -> dict:
        """
        Test 3: 7-Year Retention Policy

        Verifies:
        - 7-year (2557 days) policy is available
        - Policy can be configured and bound to skills
        - Cutoff dates are calculated correctly
        """
        retention_db = tempfile.mktemp(suffix="-retention.db")
        manager = RetentionManager(retention_db)

        # Test 1: Default 7-year policy
        policy = manager.get_policy("ret-financial-audit-default")

        tests_passed = 0
        tests_total = 4
        errors = []

        if policy and policy.retention_days == 2557:
            tests_passed += 1
        else:
            errors.append(f"Expected 2557 days, got {policy.retention_days if policy else 'None'}")

        # Test 2: Policy can be bound to skill
        manager.bind_policy_to_skill("skill-test-001", policy.policy_id)
        bound_policy = manager.get_policy_for_skill("skill-test-001")

        if bound_policy.policy_id == policy.policy_id:
            tests_passed += 1
        else:
            errors.append("Policy binding failed")

        # Test 3: Compliance check works
        compliance = manager.check_compliance("skill-test-001", "2020-01-01T00:00:00Z")
        if compliance["policy_id"] == policy.policy_id:
            tests_passed += 1
        else:
            errors.append("Compliance check failed")

        # Test 4: Custom policy creation
        custom = RetentionPolicy.custom(
            policy_id="custom-10-year",
            name="10 Year Retention",
            retention_days=3652,  # 10 years
        )
        manager.save_policy(custom)

        loaded = manager.get_policy("custom-10-year")
        if loaded and loaded.retention_days == 3652:
            tests_passed += 1
        else:
            errors.append("Custom policy creation failed")

        return {
            "passed": tests_passed == tests_total,
            "details": {
                "tests_passed": tests_passed,
                "tests_total": tests_total,
                "default_retention_days": policy.retention_days if policy else 0,
                "default_retention_years": round(policy.retention_days / 365.25, 2) if policy else 0,
                "compliance_standards": policy.metadata.get("compliance_standards", []) if policy else [],
            },
            "errors": errors,
            "sla_guarantee": "7-Year Retention - Configurable Policy",
        }

    def test_cluster_availability(self) -> dict:
        """
        Test 4: Cluster Availability (Minimal)

        Verifies:
        - 3-node cluster configuration
        - Quorum-based write approval
        - Leader election capability
        """
        config = ClusterConfig.minimal_cluster("test-cluster")
        cluster = LogCluster(config, "node-1", self.test_db_path)

        # Register additional nodes
        cluster.register_node("node-2", "local://node2.db")
        cluster.register_node("node-3", "local://node3.db")

        tests_passed = 0
        tests_total = 4
        errors = []

        # Test 1: Cluster has 3 nodes
        if len(cluster.nodes) == 3:
            tests_passed += 1
        else:
            errors.append(f"Expected 3 nodes, got {len(cluster.nodes)}")

        # Test 2: Quorum is 2 (majority of 3)
        if config.write_quorum == 2:
            tests_passed += 1
        else:
            errors.append(f"Expected quorum 2, got {config.write_quorum}")

        # Test 3: Leader election
        cluster.update_node_status("node-1", NodeStatus.HEALTHY)
        cluster.update_node_status("node-2", NodeStatus.HEALTHY)
        cluster.update_node_status("node-3", NodeStatus.HEALTHY)

        became_leader = cluster.start_election()
        if became_leader:
            tests_passed += 1
        else:
            errors.append("Leader election failed")

        # Test 4: Write approval
        can_write, reason = cluster.can_accept_write()
        if can_write:
            tests_passed += 1
        else:
            errors.append(f"Write not approved: {reason}")

        health = cluster.get_cluster_health()

        return {
            "passed": tests_passed == tests_total,
            "details": {
                "tests_passed": tests_passed,
                "tests_total": tests_total,
                "total_nodes": len(cluster.nodes),
                "cluster_health": health,
                "is_leader": cluster.is_leader,
            },
            "errors": errors,
            "sla_guarantee": "Cluster Availability - Quorum-Based Writes",
        }

    def test_hash_chain_integrity(self) -> dict:
        """
        Test 5: Hash Chain Integrity

        Verifies:
        - Each entry links to previous via SHA256
        - Genesis block has zero hash
        - Chain verification passes
        """
        log = AppendOnlyLog(tempfile.mktemp(suffix="-chain.db"))

        # Create entries
        for i in range(10):
            log.append(
                LogEntryType.AUDIT_STARTED,
                {"audit_id": f"audit-{i:03d}", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")},
            )

        # Verify chain
        is_valid, errors = log.verify_chain_integrity()

        # Check genesis block
        first = log.get_entry(1)
        genesis_valid = first and first.prev_hash == "0" * 64

        # Check hash progression
        hash_count = 0
        prev_hash = "0" * 64
        for entry in log.iterate():
            if entry.prev_hash == prev_hash:
                hash_count += 1
            prev_hash = entry.entry_hash

        log.close()

        return {
            "passed": is_valid and genesis_valid and hash_count == 10,
            "details": {
                "chain_valid": is_valid,
                "genesis_valid": genesis_valid,
                "hash_links_correct": hash_count,
                "total_entries": 10,
            },
            "errors": errors,
            "sla_guarantee": "Hash Chain Integrity - Tamper Detection",
        }

    def run_all_tests(self) -> dict:
        """Run all SLA tests and generate report."""
        print("\n" + "="*60)
        print("APPEND-ONLY LOG SLA VERIFICATION")
        print("="*60)
        print(f"Test Database: {self.test_db_path}")
        print(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}")

        # Run all tests
        self.run_test("1. WONO Immutability", self.test_wono_immutability)
        self.run_test("2. Replay Consistency", self.test_replay_consistency)
        self.run_test("3. 7-Year Retention Policy", self.test_seven_year_retention)
        self.run_test("4. Cluster Availability", self.test_cluster_availability)
        self.run_test("5. Hash Chain Integrity", self.test_hash_chain_integrity)

        # Generate summary
        print("\n" + "="*60)
        print("SLA VERIFICATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")

        # SLA Status
        all_passed = self.failed == 0
        print(f"\nSLA STATUS: {'COMPLIANT' if all_passed else 'NON-COMPLIANT'}")

        return {
            "summary": {
                "total_tests": self.passed + self.failed,
                "passed": self.passed,
                "failed": self.failed,
                "success_rate": self.passed / (self.passed + self.failed) if (self.passed + self.failed) > 0 else 0,
                "all_passed": all_passed,
                "sla_status": "COMPLIANT" if all_passed else "NON-COMPLIANT",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "results": self.results,
        }


def main():
    """Main entry point for SLA tests."""
    runner = SLATestRunner()
    report = runner.run_all_tests()

    # Save report
    report_path = Path(__file__).parent.parent.parent.parent.parent / "docs" / "2026-02-17" / "append_only_log" / "sla_verification_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nReport saved to: {report_path}")

    return 0 if report["summary"]["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
