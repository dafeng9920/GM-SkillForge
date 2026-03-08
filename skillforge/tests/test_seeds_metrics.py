"""
Tests for SEEDS Metrics Collector

SEEDS-P2: 运行时观测
Contract: T29 (L45-D6-SEEDS-P2-20260220-006)
Coverage: ingest_rate/error_rate/missing_evidence_rate, thresholds, snapshot
"""
import json
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from skillforge.src.ops.seeds_metrics import (
    DEFAULT_THRESHOLDS,
    MetricThresholds,
    Alert,
    MetricsSnapshot,
    SeedsMetricsCollector,
    collect_metrics,
    get_metrics_collector,
    save_snapshot,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_registry(tmp_path):
    """Create temporary registry file."""
    registry_path = tmp_path / "registry" / "skills.jsonl"
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    entries = [
        {
            "skill_id": "SKILL-001",
            "source": {"type": "repo", "repo_url": "https://example.com", "commit_sha": "abc123"},
            "revision": "rev-001",
            "pack_hash": "hash001",
            "permit_id": "PERMIT-001",
            "tombstone_state": "ACTIVE",
            "created_at": "2026-02-20T10:00:00Z"
        },
        {
            "skill_id": "SKILL-002",
            "source": {"type": "repo", "repo_url": "https://example.com", "commit_sha": "def456"},
            "revision": "rev-002",
            "pack_hash": "hash002",
            "permit_id": "PERMIT-002",
            "tombstone_state": "TOMBSTONED",
            "created_at": "2026-02-20T11:00:00Z"
        },
    ]

    with open(registry_path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return registry_path


@pytest.fixture
def temp_audit_events(tmp_path):
    """Create temporary audit events file."""
    events_path = tmp_path / "logs" / "audit_events.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    entries = [
        {
            "event_type": "GATE_FINISH",
            "job_id": "JOB-001",
            "gate_node": "intake_repo",
            "decision": "PASS",
            "error_code": None,
            "issue_keys": [],
            "evidence_refs": ["EV-001"],
            "ts": (now - timedelta(minutes=30)).isoformat()
        },
        {
            "event_type": "GATE_FINISH",
            "job_id": "JOB-002",
            "gate_node": "license_gate",
            "decision": "PASS",
            "error_code": None,
            "issue_keys": [],
            "evidence_refs": ["EV-002"],
            "ts": (now - timedelta(minutes=20)).isoformat()
        },
        {
            "event_type": "GATE_FINISH",
            "job_id": "JOB-003",
            "gate_node": "repo_scan",
            "decision": "FAIL",
            "error_code": "E001",
            "issue_keys": ["ISSUE-001"],
            "evidence_refs": [],
            "ts": (now - timedelta(minutes=10)).isoformat()
        },
        {
            "event_type": "GATE_FINISH",
            "job_id": "JOB-004",
            "gate_node": "draft_spec",
            "decision": "SKIPPED",
            "error_code": None,
            "issue_keys": [],
            "evidence_refs": ["EV-004"],
            "ts": now.isoformat()
        },
    ]

    with open(events_path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return events_path


@pytest.fixture
def temp_usage(tmp_path):
    """Create temporary usage file."""
    usage_path = tmp_path / "logs" / "usage.jsonl"
    usage_path.parent.mkdir(parents=True, exist_ok=True)

    entries = [
        {
            "account_id": "ACC-001",
            "action": "AUDIT_L3",
            "units": 1,
            "job_id": "JOB-001",
            "ts": "2026-02-20T10:00:00Z"
        },
        {
            "account_id": "ACC-001",
            "action": "AUDIT_L3",
            "units": 2,
            "job_id": "JOB-002",
            "ts": "2026-02-20T11:00:00Z"
        },
    ]

    with open(usage_path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return usage_path


@pytest.fixture
def collector(temp_registry, temp_audit_events, temp_usage):
    """Create collector with temp files."""
    return SeedsMetricsCollector(
        registry_path=temp_registry,
        audit_events_path=temp_audit_events,
        usage_path=temp_usage,
        thresholds=MetricThresholds(
            ingest_rate_min=0.0,
            error_rate_max=0.5,
            missing_evidence_rate_max=0.5,
            registry_size_min=1,
            audit_events_age_max_hours=24,
        ),
    )


# ============================================================================
# MetricThresholds Tests
# ============================================================================

class TestMetricThresholds:
    """Tests for metric thresholds."""

    def test_default_thresholds(self):
        """Default thresholds should be defined."""
        thresholds = MetricThresholds()
        assert thresholds.ingest_rate_min == DEFAULT_THRESHOLDS["ingest_rate_min"]
        assert thresholds.error_rate_max == DEFAULT_THRESHOLDS["error_rate_max"]
        assert thresholds.missing_evidence_rate_max == DEFAULT_THRESHOLDS["missing_evidence_rate_max"]

    def test_thresholds_from_dict(self):
        """Should create thresholds from dict."""
        data = {
            "ingest_rate_min": 0.1,
            "error_rate_max": 0.1,
        }
        thresholds = MetricThresholds.from_dict(data)
        assert thresholds.ingest_rate_min == 0.1
        assert thresholds.error_rate_max == 0.1

    def test_thresholds_from_env(self, monkeypatch):
        """Should create thresholds from environment."""
        monkeypatch.setenv("SKILLFORGE_THRESHOLD_ERROR_RATE_MAX", "0.25")
        thresholds = MetricThresholds.from_env()
        assert thresholds.error_rate_max == 0.25


# ============================================================================
# Registry Metrics Tests
# ============================================================================

class TestRegistryMetrics:
    """Tests for registry metrics collection."""

    def test_registry_size(self, collector):
        """Should count registry entries."""
        registry = collector.collect_registry_metrics()
        assert registry["size"] == 2

    def test_registry_active_count(self, collector):
        """Should count ACTIVE entries."""
        registry = collector.collect_registry_metrics()
        assert registry["active_count"] == 1

    def test_registry_tombstoned_count(self, collector):
        """Should count TOMBSTONED entries."""
        registry = collector.collect_registry_metrics()
        assert registry["tombstoned_count"] == 1

    def test_registry_empty(self, tmp_path):
        """Should handle missing registry."""
        collector = SeedsMetricsCollector(
            registry_path=tmp_path / "nonexistent.jsonl",
        )
        registry = collector.collect_registry_metrics()
        assert registry["size"] == 0


# ============================================================================
# Audit Events Metrics Tests
# ============================================================================

class TestAuditEventsMetrics:
    """Tests for audit events metrics collection."""

    def test_audit_events_count(self, collector):
        """Should count audit events."""
        metrics = collector.collect_audit_events_metrics()
        assert metrics["count"] == 4

    def test_audit_events_pass_count(self, collector):
        """Should count PASS events."""
        metrics = collector.collect_audit_events_metrics()
        assert metrics["pass_count"] == 2

    def test_audit_events_fail_count(self, collector):
        """Should count FAIL events."""
        metrics = collector.collect_audit_events_metrics()
        assert metrics["fail_count"] == 1

    def test_audit_events_skip_count(self, collector):
        """Should count SKIPPED events."""
        metrics = collector.collect_audit_events_metrics()
        assert metrics["skip_count"] == 1

    def test_missing_evidence_count(self, collector):
        """Should count events without evidence."""
        metrics = collector.collect_audit_events_metrics()
        assert metrics["missing_evidence_count"] == 1

    def test_ingest_rate(self, collector):
        """Should calculate ingest rate."""
        metrics = collector.collect_audit_events_metrics()
        # 4 events in last hour, rate = 4/60
        assert metrics["ingest_rate"] >= 0

    def test_audit_events_age(self, collector):
        """Should calculate latest event age."""
        metrics = collector.collect_audit_events_metrics()
        assert metrics["age_hours"] is not None
        assert metrics["age_hours"] < 1  # Recent events


# ============================================================================
# Usage Metrics Tests
# ============================================================================

class TestUsageMetrics:
    """Tests for usage metrics collection."""

    def test_usage_count(self, collector):
        """Should count usage entries."""
        usage = collector.collect_usage_metrics()
        assert usage["count"] == 2

    def test_usage_total_units(self, collector):
        """Should sum usage units."""
        usage = collector.collect_usage_metrics()
        assert usage["total_units"] == 3


# ============================================================================
# Computed Metrics Tests
# ============================================================================

class TestComputedMetrics:
    """Tests for computed metrics (rates)."""

    def test_error_rate(self, collector):
        """Should compute error rate."""
        snapshot = collector.collect()
        # 1 fail out of 4 total
        assert snapshot.error_rate == 0.25

    def test_missing_evidence_rate(self, collector):
        """Should compute missing evidence rate."""
        snapshot = collector.collect()
        # 1 missing evidence out of 4 total
        assert snapshot.missing_evidence_rate == 0.25

    def test_ingest_rate_in_snapshot(self, collector):
        """Should include ingest rate in snapshot."""
        snapshot = collector.collect()
        assert snapshot.ingest_rate >= 0


# ============================================================================
# Alert Tests
# ============================================================================

class TestAlerts:
    """Tests for alert generation."""

    def test_no_alerts_when_healthy(self, collector):
        """Should not generate alerts when within thresholds."""
        snapshot = collector.collect()
        assert len(snapshot.alerts) == 0
        assert snapshot.healthy is True

    def test_alert_on_high_error_rate(self, temp_registry, temp_audit_events, temp_usage):
        """Should alert when error rate exceeds threshold."""
        collector = SeedsMetricsCollector(
            registry_path=temp_registry,
            audit_events_path=temp_audit_events,
            usage_path=temp_usage,
            thresholds=MetricThresholds(error_rate_max=0.1),  # 10% threshold
        )
        snapshot = collector.collect()

        error_alerts = [a for a in snapshot.alerts if a.metric_name == "error_rate"]
        assert len(error_alerts) == 1
        assert error_alerts[0].current_value == 0.25

    def test_alert_on_missing_evidence(self, temp_registry, temp_audit_events, temp_usage):
        """Should alert when missing evidence rate exceeds threshold."""
        collector = SeedsMetricsCollector(
            registry_path=temp_registry,
            audit_events_path=temp_audit_events,
            usage_path=temp_usage,
            thresholds=MetricThresholds(missing_evidence_rate_max=0.1),
        )
        snapshot = collector.collect()

        evidence_alerts = [a for a in snapshot.alerts if a.metric_name == "missing_evidence_rate"]
        assert len(evidence_alerts) == 1

    def test_alert_on_small_registry(self, temp_registry, temp_audit_events, temp_usage):
        """Should alert when registry size below minimum."""
        collector = SeedsMetricsCollector(
            registry_path=temp_registry,
            audit_events_path=temp_audit_events,
            usage_path=temp_usage,
            thresholds=MetricThresholds(registry_size_min=10),
        )
        snapshot = collector.collect()

        registry_alerts = [a for a in snapshot.alerts if a.metric_name == "registry_size"]
        assert len(registry_alerts) == 1

    def test_alert_to_dict(self):
        """Alert should serialize to dict."""
        alert = Alert(
            metric_name="test_metric",
            current_value=0.5,
            threshold=0.3,
            severity="warning",
            message="Test alert",
            timestamp="2026-02-20T10:00:00Z",
        )
        d = alert.to_dict()
        assert d["metric_name"] == "test_metric"
        assert d["severity"] == "warning"


# ============================================================================
# Snapshot Tests
# ============================================================================

class TestSnapshot:
    """Tests for metrics snapshot."""

    def test_snapshot_timestamp(self, collector):
        """Snapshot should have timestamp."""
        snapshot = collector.collect()
        assert snapshot.timestamp is not None

    def test_snapshot_to_dict(self, collector):
        """Snapshot should serialize to dict."""
        snapshot = collector.collect()
        d = snapshot.to_dict()

        assert "timestamp" in d
        assert "registry" in d
        assert "audit_events" in d
        assert "usage" in d
        assert "computed" in d
        assert "alerts" in d
        assert "healthy" in d

    def test_snapshot_has_raw_values(self, collector):
        """Snapshot should include raw values for复核."""
        snapshot = collector.collect()
        assert snapshot.raw_values is not None
        assert "registry_size" in snapshot.raw_values
        assert "audit_events_count" in snapshot.raw_values

    def test_snapshot_has_all_required_metrics(self, collector):
        """Snapshot must include all required metrics."""
        snapshot = collector.collect()
        d = snapshot.to_dict()

        computed = d["computed"]
        assert "ingest_rate" in computed
        assert "error_rate" in computed
        assert "missing_evidence_rate" in computed


# ============================================================================
# Save/Load Tests
# ============================================================================

class TestSaveSnapshot:
    """Tests for saving and loading snapshots."""

    def test_save_snapshot(self, collector, tmp_path):
        """Should save snapshot to JSON file."""
        snapshot = collector.collect()
        path = tmp_path / "snapshot.json"

        save_snapshot(snapshot, path)

        assert path.exists()

        with open(path) as f:
            data = json.load(f)

        assert data["timestamp"] == snapshot.timestamp
        assert "computed" in data

    def test_snapshot_is_json_serializable(self, collector):
        """Snapshot must be JSON serializable for复核."""
        snapshot = collector.collect()
        d = snapshot.to_dict()

        # Should not raise
        json.dumps(d)


# ============================================================================
# Convenience Functions Tests
# ============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_metrics_collector_singleton(self):
        """get_metrics_collector should return singleton."""
        c1 = get_metrics_collector()
        c2 = get_metrics_collector()
        assert c1 is c2

    def test_collect_metrics_function(self):
        """collect_metrics should work."""
        snapshot = collect_metrics()
        assert snapshot is not None
        assert snapshot.timestamp is not None


# ============================================================================
# Required Metrics Tests
# ============================================================================

class TestRequiredMetrics:
    """Tests for required metrics (per contract)."""

    def test_output_includes_ingest_rate(self, collector):
        """Must output ingest_rate."""
        snapshot = collector.collect()
        assert snapshot.ingest_rate is not None
        assert isinstance(snapshot.ingest_rate, float)

    def test_output_includes_error_rate(self, collector):
        """Must output error_rate."""
        snapshot = collector.collect()
        assert snapshot.error_rate is not None
        assert isinstance(snapshot.error_rate, float)

    def test_output_includes_missing_evidence_rate(self, collector):
        """Must output missing_evidence_rate."""
        snapshot = collector.collect()
        assert snapshot.missing_evidence_rate is not None
        assert isinstance(snapshot.missing_evidence_rate, float)

    def test_output_raw_values_not_only_charts(self, collector):
        """Must output raw values, not only charts."""
        snapshot = collector.collect()
        d = snapshot.to_dict()

        # Raw values must be present
        assert "raw_values" in d
        raw = d["raw_values"]
        assert len(raw) > 0

        # All computed metrics must have raw backing
        computed = d["computed"]
        assert computed["ingest_rate"] >= 0  # Raw numeric value
        assert computed["error_rate"] >= 0  # Raw numeric value
        assert computed["missing_evidence_rate"] >= 0  # Raw numeric value


# ============================================================================
# Thresholds Configurable Tests
# ============================================================================

class TestThresholdsConfigurable:
    """Tests for configurable thresholds."""

    def test_thresholds_can_be_customized(self, temp_registry, temp_audit_events, temp_usage):
        """Thresholds must be configurable."""
        custom_thresholds = MetricThresholds(
            ingest_rate_min=0.5,
            error_rate_max=0.01,
            missing_evidence_rate_max=0.01,
        )

        collector = SeedsMetricsCollector(
            registry_path=temp_registry,
            audit_events_path=temp_audit_events,
            usage_path=temp_usage,
            thresholds=custom_thresholds,
        )

        assert collector.thresholds.ingest_rate_min == 0.5
        assert collector.thresholds.error_rate_max == 0.01

    def test_thresholds_from_dict_configurable(self):
        """Thresholds should be loadable from config dict."""
        config = {"error_rate_max": 0.2}
        thresholds = MetricThresholds.from_dict(config)
        assert thresholds.error_rate_max == 0.2
