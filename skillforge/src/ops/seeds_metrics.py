"""
SEEDS Metrics Collector - 三账本健康指标与阈值告警

SEEDS-P2: 运行时观测
Job ID: L45-D6-SEEDS-P2-20260220-006

Collects metrics from:
- registry/skills.jsonl
- logs/audit_events.jsonl
- logs/usage.jsonl

Constraints:
- 至少输出 ingest_rate/error_rate/missing_evidence_rate
- 阈值必须可配置
- 快照可复核
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional


# ============================================================================
# Constants
# ============================================================================

# Default paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_REGISTRY_PATH = PROJECT_ROOT / "registry" / "skills.jsonl"
DEFAULT_AUDIT_EVENTS_PATH = PROJECT_ROOT / "logs" / "audit_events.jsonl"
DEFAULT_USAGE_PATH = PROJECT_ROOT / "logs" / "usage.jsonl"

# Environment variables for paths
REGISTRY_PATH_ENV = "SKILLFORGE_REGISTRY_PATH"
AUDIT_EVENTS_PATH_ENV = "SKILLFORGE_AUDIT_EVENTS_PATH"
USAGE_PATH_ENV = "SKILLFORGE_USAGE_PATH"

# Default thresholds (configurable via environment or config file)
DEFAULT_THRESHOLDS = {
    "ingest_rate_min": 0.0,  # Minimum ingest rate per minute
    "error_rate_max": 0.05,  # Maximum error rate (5%)
    "missing_evidence_rate_max": 0.01,  # Maximum missing evidence rate (1%)
    "registry_size_min": 1,  # Minimum registry entries
    "audit_events_age_max_hours": 24,  # Maximum age of latest audit event
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class MetricThresholds:
    """Configurable thresholds for alerts."""
    ingest_rate_min: float = 0.0
    error_rate_max: float = 0.05
    missing_evidence_rate_max: float = 0.01
    registry_size_min: int = 1
    audit_events_age_max_hours: int = 24

    @classmethod
    def from_dict(cls, data: dict) -> "MetricThresholds":
        """Create thresholds from dictionary."""
        return cls(
            ingest_rate_min=data.get("ingest_rate_min", DEFAULT_THRESHOLDS["ingest_rate_min"]),
            error_rate_max=data.get("error_rate_max", DEFAULT_THRESHOLDS["error_rate_max"]),
            missing_evidence_rate_max=data.get("missing_evidence_rate_max", DEFAULT_THRESHOLDS["missing_evidence_rate_max"]),
            registry_size_min=data.get("registry_size_min", DEFAULT_THRESHOLDS["registry_size_min"]),
            audit_events_age_max_hours=data.get("audit_events_age_max_hours", DEFAULT_THRESHOLDS["audit_events_age_max_hours"]),
        )

    @classmethod
    def from_env(cls) -> "MetricThresholds":
        """Create thresholds from environment variables."""
        def get_float(key: str, default: float) -> float:
            val = os.environ.get(f"SKILLFORGE_THRESHOLD_{key.upper()}")
            return float(val) if val else default

        def get_int(key: str, default: int) -> int:
            val = os.environ.get(f"SKILLFORGE_THRESHOLD_{key.upper()}")
            return int(val) if val else default

        return cls(
            ingest_rate_min=get_float("ingest_rate_min", DEFAULT_THRESHOLDS["ingest_rate_min"]),
            error_rate_max=get_float("error_rate_max", DEFAULT_THRESHOLDS["error_rate_max"]),
            missing_evidence_rate_max=get_float("missing_evidence_rate_max", DEFAULT_THRESHOLDS["missing_evidence_rate_max"]),
            registry_size_min=get_int("registry_size_min", DEFAULT_THRESHOLDS["registry_size_min"]),
            audit_events_age_max_hours=get_int("audit_events_age_max_hours", DEFAULT_THRESHOLDS["audit_events_age_max_hours"]),
        )


@dataclass
class Alert:
    """Represents an alert triggered by threshold breach."""
    metric_name: str
    current_value: float
    threshold: float
    severity: str  # "warning", "critical"
    message: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
        }


@dataclass
class MetricsSnapshot:
    """Snapshot of all metrics at a point in time."""
    timestamp: str
    # Registry metrics
    registry_size: int
    registry_active_count: int
    registry_tombstoned_count: int
    # Audit events metrics
    audit_events_count: int
    audit_events_pass_count: int
    audit_events_fail_count: int
    audit_events_skip_count: int
    audit_events_latest_ts: Optional[str]
    audit_events_age_hours: Optional[float]
    # Usage metrics
    usage_count: int
    usage_total_units: int
    # Computed metrics
    ingest_rate: float  # Events per minute (last hour)
    error_rate: float
    missing_evidence_rate: float
    # Raw values (for复核)
    raw_values: dict = field(default_factory=dict)
    # Alerts
    alerts: list[Alert] = field(default_factory=list)
    # Health status
    healthy: bool = True

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "registry": {
                "size": self.registry_size,
                "active_count": self.registry_active_count,
                "tombstoned_count": self.registry_tombstoned_count,
            },
            "audit_events": {
                "count": self.audit_events_count,
                "pass_count": self.audit_events_pass_count,
                "fail_count": self.audit_events_fail_count,
                "skip_count": self.audit_events_skip_count,
                "latest_ts": self.audit_events_latest_ts,
                "age_hours": self.audit_events_age_hours,
            },
            "usage": {
                "count": self.usage_count,
                "total_units": self.usage_total_units,
            },
            "computed": {
                "ingest_rate": self.ingest_rate,
                "error_rate": self.error_rate,
                "missing_evidence_rate": self.missing_evidence_rate,
            },
            "raw_values": self.raw_values,
            "alerts": [a.to_dict() for a in self.alerts],
            "healthy": self.healthy,
        }


# ============================================================================
# SEEDS Metrics Collector
# ============================================================================

class SeedsMetricsCollector:
    """
    SEEDS 三账本健康指标收集器。

    Collects metrics from:
    - registry/skills.jsonl
    - logs/audit_events.jsonl
    - logs/usage.jsonl

    Outputs:
    - ingest_rate: Events per minute
    - error_rate: Proportion of failed events
    - missing_evidence_rate: Proportion of events without evidence
    """

    def __init__(
        self,
        registry_path: Optional[Path] = None,
        audit_events_path: Optional[Path] = None,
        usage_path: Optional[Path] = None,
        thresholds: Optional[MetricThresholds] = None,
    ):
        """Initialize the collector with paths and thresholds."""
        self.registry_path = registry_path or self._get_path(REGISTRY_PATH_ENV, DEFAULT_REGISTRY_PATH)
        self.audit_events_path = audit_events_path or self._get_path(AUDIT_EVENTS_PATH_ENV, DEFAULT_AUDIT_EVENTS_PATH)
        self.usage_path = usage_path or self._get_path(USAGE_PATH_ENV, DEFAULT_USAGE_PATH)
        self.thresholds = thresholds or MetricThresholds.from_env()

    def _get_path(self, env_var: str, default: Path) -> Path:
        """Get path from environment or default."""
        env_path = os.environ.get(env_var)
        return Path(env_path) if env_path else default

    def _read_jsonl(self, path: Path) -> list[dict]:
        """Read all entries from a JSONL file."""
        if not path.exists():
            return []

        entries = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries

    def _parse_timestamp(self, ts_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO-8601 timestamp."""
        if not ts_str:
            return None
        try:
            # Handle various ISO formats
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            return datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            return None

    def collect_registry_metrics(self) -> dict:
        """Collect metrics from registry/skills.jsonl."""
        entries = self._read_jsonl(self.registry_path)

        active_count = sum(1 for e in entries if e.get("tombstone_state") == "ACTIVE")
        tombstoned_count = sum(1 for e in entries if e.get("tombstone_state") == "TOMBSTONED")

        return {
            "size": len(entries),
            "active_count": active_count,
            "tombstoned_count": tombstoned_count,
            "entries": entries,
        }

    def collect_audit_events_metrics(self) -> dict:
        """Collect metrics from logs/audit_events.jsonl."""
        entries = self._read_jsonl(self.audit_events_path)

        pass_count = sum(1 for e in entries if e.get("decision") == "PASS")
        fail_count = sum(1 for e in entries if e.get("decision") == "FAIL")
        skip_count = sum(1 for e in entries if e.get("decision") == "SKIPPED")

        # Find latest timestamp
        timestamps = []
        for e in entries:
            ts = self._parse_timestamp(e.get("ts"))
            if ts:
                timestamps.append(ts)

        latest_ts = max(timestamps) if timestamps else None
        now = datetime.now(timezone.utc)
        age_hours = (now - latest_ts).total_seconds() / 3600 if latest_ts else None

        # Count missing evidence
        missing_evidence = sum(
            1 for e in entries
            if not e.get("evidence_refs") or len(e.get("evidence_refs", [])) == 0
        )

        # Calculate ingest rate (events per minute in last hour)
        one_hour_ago = now - timedelta(hours=1)
        recent_events = [
            e for e in entries
            if self._parse_timestamp(e.get("ts")) and self._parse_timestamp(e.get("ts")) > one_hour_ago
        ]
        ingest_rate = len(recent_events) / 60.0 if recent_events else 0.0

        return {
            "count": len(entries),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "skip_count": skip_count,
            "latest_ts": latest_ts.isoformat() if latest_ts else None,
            "age_hours": age_hours,
            "missing_evidence_count": missing_evidence,
            "ingest_rate": ingest_rate,
            "entries": entries,
        }

    def collect_usage_metrics(self) -> dict:
        """Collect metrics from logs/usage.jsonl."""
        entries = self._read_jsonl(self.usage_path)

        total_units = sum(e.get("units", 0) for e in entries)

        return {
            "count": len(entries),
            "total_units": total_units,
            "entries": entries,
        }

    def collect(self) -> MetricsSnapshot:
        """
        Collect all metrics and generate snapshot.

        Returns:
            MetricsSnapshot with all metrics and alerts
        """
        now = datetime.now(timezone.utc)

        # Collect metrics from each ledger
        registry = self.collect_registry_metrics()
        audit_events = self.collect_audit_events_metrics()
        usage = self.collect_usage_metrics()

        # Compute rates
        total_events = audit_events["count"]
        fail_count = audit_events["fail_count"]
        missing_evidence = audit_events["missing_evidence_count"]

        error_rate = (fail_count / total_events) if total_events > 0 else 0.0
        missing_evidence_rate = (missing_evidence / total_events) if total_events > 0 else 0.0

        # Generate alerts
        alerts = []

        # Check ingest rate
        if audit_events["ingest_rate"] < self.thresholds.ingest_rate_min:
            alerts.append(Alert(
                metric_name="ingest_rate",
                current_value=audit_events["ingest_rate"],
                threshold=self.thresholds.ingest_rate_min,
                severity="warning",
                message=f"Ingest rate {audit_events['ingest_rate']:.4f} below minimum {self.thresholds.ingest_rate_min}",
                timestamp=now.isoformat(),
            ))

        # Check error rate
        if error_rate > self.thresholds.error_rate_max:
            severity = "critical" if error_rate > self.thresholds.error_rate_max * 2 else "warning"
            alerts.append(Alert(
                metric_name="error_rate",
                current_value=error_rate,
                threshold=self.thresholds.error_rate_max,
                severity=severity,
                message=f"Error rate {error_rate:.4f} exceeds threshold {self.thresholds.error_rate_max}",
                timestamp=now.isoformat(),
            ))

        # Check missing evidence rate
        if missing_evidence_rate > self.thresholds.missing_evidence_rate_max:
            alerts.append(Alert(
                metric_name="missing_evidence_rate",
                current_value=missing_evidence_rate,
                threshold=self.thresholds.missing_evidence_rate_max,
                severity="warning",
                message=f"Missing evidence rate {missing_evidence_rate:.4f} exceeds threshold {self.thresholds.missing_evidence_rate_max}",
                timestamp=now.isoformat(),
            ))

        # Check registry size
        if registry["size"] < self.thresholds.registry_size_min:
            alerts.append(Alert(
                metric_name="registry_size",
                current_value=registry["size"],
                threshold=self.thresholds.registry_size_min,
                severity="warning",
                message=f"Registry size {registry['size']} below minimum {self.thresholds.registry_size_min}",
                timestamp=now.isoformat(),
            ))

        # Check audit events age
        if audit_events["age_hours"] is not None and audit_events["age_hours"] > self.thresholds.audit_events_age_max_hours:
            alerts.append(Alert(
                metric_name="audit_events_age_hours",
                current_value=audit_events["age_hours"],
                threshold=self.thresholds.audit_events_age_max_hours,
                severity="warning",
                message=f"Latest audit event age {audit_events['age_hours']:.2f}h exceeds threshold {self.thresholds.audit_events_age_max_hours}h",
                timestamp=now.isoformat(),
            ))

        # Determine overall health
        critical_alerts = [a for a in alerts if a.severity == "critical"]
        healthy = len(critical_alerts) == 0

        # Build raw values for复核
        raw_values = {
            "registry_size": registry["size"],
            "registry_active_count": registry["active_count"],
            "registry_tombstoned_count": registry["tombstoned_count"],
            "audit_events_count": audit_events["count"],
            "audit_events_pass_count": audit_events["pass_count"],
            "audit_events_fail_count": audit_events["fail_count"],
            "audit_events_skip_count": audit_events["skip_count"],
            "audit_events_missing_evidence_count": missing_evidence,
            "usage_count": usage["count"],
            "usage_total_units": usage["total_units"],
        }

        return MetricsSnapshot(
            timestamp=now.isoformat(),
            registry_size=registry["size"],
            registry_active_count=registry["active_count"],
            registry_tombstoned_count=registry["tombstoned_count"],
            audit_events_count=audit_events["count"],
            audit_events_pass_count=audit_events["pass_count"],
            audit_events_fail_count=audit_events["fail_count"],
            audit_events_skip_count=audit_events["skip_count"],
            audit_events_latest_ts=audit_events["latest_ts"],
            audit_events_age_hours=audit_events["age_hours"],
            usage_count=usage["count"],
            usage_total_units=usage["total_units"],
            ingest_rate=audit_events["ingest_rate"],
            error_rate=error_rate,
            missing_evidence_rate=missing_evidence_rate,
            raw_values=raw_values,
            alerts=alerts,
            healthy=healthy,
        )


# ============================================================================
# Convenience Functions
# ============================================================================

_collector_instance: Optional[SeedsMetricsCollector] = None


def get_metrics_collector() -> SeedsMetricsCollector:
    """Get the singleton metrics collector instance."""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = SeedsMetricsCollector()
    return _collector_instance


def collect_metrics() -> MetricsSnapshot:
    """Convenience function to collect metrics."""
    return get_metrics_collector().collect()


def save_snapshot(snapshot: MetricsSnapshot, path: Path) -> None:
    """Save snapshot to JSON file for复核."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot.to_dict(), f, indent=2)
