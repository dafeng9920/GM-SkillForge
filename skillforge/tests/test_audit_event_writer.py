"""
Tests for Audit Event Writer.

Verifies that:
- Every gate finish (PASS/FAIL/SKIPPED) writes an event
- Events are append-only (historical lines not modified)
- Query supports filtering by job_id and gate_node
"""
import json
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from skills.audit_event_writer import (
    AuditEventWriter,
    Decision,
    write_gate_finish_event,
    query_audit_events,
)


@pytest.fixture
def temp_audit_log():
    """Create a temporary audit log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("")
        path = Path(f.name)
    yield path
    # Cleanup
    if path.exists():
        path.unlink()


@pytest.fixture
def writer(temp_audit_log):
    """Create an AuditEventWriter with a temp log file."""
    return AuditEventWriter(audit_log_path=temp_audit_log)


class TestDecisionConstants:
    """Test decision constants."""

    def test_decision_pass_exists(self):
        assert Decision.PASS == "PASS"

    def test_decision_fail_exists(self):
        assert Decision.FAIL == "FAIL"

    def test_decision_skipped_exists(self):
        assert Decision.SKIPPED == "SKIPPED"

    def test_all_decisions_present(self):
        assert Decision.ALL == {"PASS", "FAIL", "SKIPPED"}


class TestWriteGateFinish:
    """Test write_gate_finish method."""

    def test_write_pass_event(self, writer, temp_audit_log):
        """PASS events must be written."""
        result = writer.write_gate_finish(
            job_id="TEST-JOB-001",
            gate_node="intake_repo",
            decision="PASS",
        )
        assert result["status"] == "WRITTEN"
        assert result["event"]["decision"] == "PASS"
        assert result["event"]["job_id"] == "TEST-JOB-001"

        # Verify file was written
        with open(temp_audit_log, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["decision"] == "PASS"

    def test_write_fail_event(self, writer, temp_audit_log):
        """FAIL events must be written."""
        result = writer.write_gate_finish(
            job_id="TEST-JOB-002",
            gate_node="license_gate",
            decision="FAIL",
            error_code="LICENSE_NOT_FOUND",
            issue_keys=["ISSUE-001"],
        )
        assert result["status"] == "WRITTEN"
        assert result["event"]["decision"] == "FAIL"
        assert result["event"]["error_code"] == "LICENSE_NOT_FOUND"

        # Verify file was written
        with open(temp_audit_log, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["decision"] == "FAIL"

    def test_write_skipped_event(self, writer, temp_audit_log):
        """SKIPPED events must be written."""
        result = writer.write_gate_finish(
            job_id="TEST-JOB-003",
            gate_node="sandbox_test",
            decision="SKIPPED",
            issue_keys=["ISSUE-002"],
            evidence_refs=["EV-SKIP-001"],
        )
        assert result["status"] == "WRITTEN"
        assert result["event"]["decision"] == "SKIPPED"

        # Verify file was written
        with open(temp_audit_log, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["decision"] == "SKIPPED"

    def test_invalid_decision_raises_error(self, writer):
        """Invalid decision should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid decision"):
            writer.write_gate_finish(
                job_id="TEST-JOB-004",
                gate_node="test_gate",
                decision="INVALID",
            )


class TestAppendOnlyBehavior:
    """Test that events are append-only."""

    def test_multiple_writes_are_appended(self, writer, temp_audit_log):
        """Multiple events should be appended, not overwrite."""
        # Write 3 events
        writer.write_gate_finish(job_id="JOB-1", gate_node="gate1", decision="PASS")
        writer.write_gate_finish(job_id="JOB-2", gate_node="gate2", decision="FAIL")
        writer.write_gate_finish(job_id="JOB-3", gate_node="gate3", decision="SKIPPED")

        # Read all lines
        with open(temp_audit_log, "r") as f:
            lines = f.readlines()

        assert len(lines) == 3

        # Verify each event
        events = [json.loads(line) for line in lines]
        assert events[0]["job_id"] == "JOB-1"
        assert events[1]["job_id"] == "JOB-2"
        assert events[2]["job_id"] == "JOB-3"

    def test_historical_events_unchanged(self, writer, temp_audit_log):
        """Previously written events should not be modified."""
        # Write first event
        writer.write_gate_finish(
            job_id="ORIGINAL-JOB",
            gate_node="original_gate",
            decision="PASS",
            evidence_refs=["EV-ORIGINAL"],
        )

        # Read first event
        with open(temp_audit_log, "r") as f:
            original_line = f.readline()

        # Write more events
        writer.write_gate_finish(job_id="JOB-2", gate_node="gate2", decision="FAIL")
        writer.write_gate_finish(job_id="JOB-3", gate_node="gate3", decision="SKIPPED")

        # Verify original line is unchanged
        with open(temp_audit_log, "r") as f:
            first_line = f.readline()

        assert first_line == original_line
        original_event = json.loads(original_line)
        assert original_event["job_id"] == "ORIGINAL-JOB"
        assert original_event["evidence_refs"] == ["EV-ORIGINAL"]


class TestQueryEvents:
    """Test query functionality."""

    def test_query_by_job_id(self, writer):
        """Query should filter by job_id."""
        writer.write_gate_finish(job_id="JOB-A", gate_node="gate1", decision="PASS")
        writer.write_gate_finish(job_id="JOB-B", gate_node="gate2", decision="FAIL")
        writer.write_gate_finish(job_id="JOB-A", gate_node="gate3", decision="SKIPPED")

        results = writer.query(job_id="JOB-A")
        assert len(results) == 2
        for r in results:
            assert r["job_id"] == "JOB-A"

    def test_query_by_gate_node(self, writer):
        """Query should filter by gate_node."""
        writer.write_gate_finish(job_id="JOB-1", gate_node="intake", decision="PASS")
        writer.write_gate_finish(job_id="JOB-2", gate_node="license", decision="FAIL")
        writer.write_gate_finish(job_id="JOB-3", gate_node="intake", decision="SKIPPED")

        results = writer.query(gate_node="intake")
        assert len(results) == 2
        for r in results:
            assert r["gate_node"] == "intake"

    def test_query_by_decision(self, writer):
        """Query should filter by decision."""
        writer.write_gate_finish(job_id="JOB-1", gate_node="g1", decision="PASS")
        writer.write_gate_finish(job_id="JOB-2", gate_node="g2", decision="FAIL")
        writer.write_gate_finish(job_id="JOB-3", gate_node="g3", decision="PASS")

        results = writer.query(decision="PASS")
        assert len(results) == 2
        for r in results:
            assert r["decision"] == "PASS"

    def test_query_combined_filters(self, writer):
        """Query should support combined filters."""
        writer.write_gate_finish(job_id="JOB-1", gate_node="intake", decision="PASS")
        writer.write_gate_finish(job_id="JOB-1", gate_node="license", decision="FAIL")
        writer.write_gate_finish(job_id="JOB-2", gate_node="intake", decision="PASS")

        results = writer.query(job_id="JOB-1", gate_node="intake")
        assert len(results) == 1
        assert results[0]["job_id"] == "JOB-1"
        assert results[0]["gate_node"] == "intake"

    def test_query_returns_most_recent_first(self, writer):
        """Query should return events sorted by timestamp, most recent first."""
        import time
        writer.write_gate_finish(job_id="JOB-1", gate_node="g1", decision="PASS")
        time.sleep(1.1)  # Ensure different timestamps (1 second precision)
        writer.write_gate_finish(job_id="JOB-2", gate_node="g2", decision="FAIL")
        time.sleep(1.1)
        writer.write_gate_finish(job_id="JOB-3", gate_node="g3", decision="SKIPPED")

        results = writer.query(limit=10)
        assert len(results) == 3
        # Last written should be first (most recent)
        assert results[0]["job_id"] == "JOB-3"
        assert results[1]["job_id"] == "JOB-2"
        assert results[2]["job_id"] == "JOB-1"

    def test_query_empty_log(self, temp_audit_log):
        """Query on empty log should return empty list."""
        empty_log = temp_audit_log.parent / "empty.jsonl"
        empty_log.touch()
        writer = AuditEventWriter(audit_log_path=empty_log)
        results = writer.query(job_id="ANY")
        assert results == []


class TestCountEvents:
    """Test count functionality."""

    def test_count_total(self, writer):
        """Count should return total number of events."""
        writer.write_gate_finish(job_id="J1", gate_node="g1", decision="PASS")
        writer.write_gate_finish(job_id="J2", gate_node="g2", decision="FAIL")
        writer.write_gate_finish(job_id="J3", gate_node="g3", decision="SKIPPED")

        counts = writer.count_events()
        assert counts["total"] == 3
        assert counts["by_decision"]["PASS"] == 1
        assert counts["by_decision"]["FAIL"] == 1
        assert counts["by_decision"]["SKIPPED"] == 1


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_write_gate_finish_event_function(self, temp_audit_log):
        """Test write_gate_finish_event convenience function."""
        result = write_gate_finish_event(
            job_id="CONV-JOB-001",
            gate_node="convenience_gate",
            decision="PASS",
            audit_log_path=temp_audit_log,
        )
        assert result["status"] == "WRITTEN"

    def test_query_audit_events_function(self, temp_audit_log):
        """Test query_audit_events convenience function."""
        # Write some events
        write_gate_finish_event(
            job_id="QUERY-JOB",
            gate_node="test_gate",
            decision="PASS",
            audit_log_path=temp_audit_log,
        )

        # Query
        results = query_audit_events(
            job_id="QUERY-JOB",
            audit_log_path=temp_audit_log,
        )
        assert len(results) == 1
        assert results[0]["job_id"] == "QUERY-JOB"


class TestEventSchema:
    """Test event schema compliance."""

    def test_event_has_required_fields(self, writer, temp_audit_log):
        """Event should have all required fields."""
        writer.write_gate_finish(
            job_id="SCHEMA-TEST",
            gate_node="schema_gate",
            decision="PASS",
            error_code=None,
            issue_keys=["ISSUE-A"],
            evidence_refs=["EV-A"],
        )

        with open(temp_audit_log, "r") as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "GATE_FINISH"
        assert event["job_id"] == "SCHEMA-TEST"
        assert event["gate_node"] == "schema_gate"
        assert event["decision"] == "PASS"
        assert event["error_code"] is None
        assert event["issue_keys"] == ["ISSUE-A"]
        assert event["evidence_refs"] == ["EV-A"]
        assert "ts" in event

    def test_timestamp_format(self, writer, temp_audit_log):
        """Timestamp should be ISO-8601 format."""
        writer.write_gate_finish(
            job_id="TS-TEST",
            gate_node="ts_gate",
            decision="PASS",
        )

        with open(temp_audit_log, "r") as f:
            event = json.loads(f.readline())

        # Should match ISO-8601 format: 2026-02-20T12:34:56Z
        ts = event["ts"]
        assert ts.endswith("Z")
        assert "T" in ts
        assert len(ts) == 20  # YYYY-MM-DDTHH:MM:SSZ
