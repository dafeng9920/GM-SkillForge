"""
Audit Event Writer v0.

Append-only audit events for gate finish events:
- Every gate finish MUST write an event (PASS/FAIL/SKIPPED).
- Append-only: no modification of historical lines.
- Query support by job_id and gate_node.

Schema (from SEEDS_v0.md):
{"event_type":"GATE_FINISH","job_id":"JOB-PLACEHOLDER","gate_node":"intake_repo",
 "decision":"PASS","error_code":null,"issue_keys":[],"evidence_refs":["EV-PLACEHOLDER"],
 "ts":"2026-02-20T00:00:00Z"}
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


def _now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Decision:
    """Supported gate decision types."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"

    ALL = {PASS, FAIL, SKIPPED}


@dataclass
class AuditEventWriter:
    """Append-only audit event writer for gate finish events."""

    audit_log_path: Path = Path("logs/audit_events.jsonl")

    def write_gate_finish(
        self,
        *,
        job_id: str,
        gate_node: str,
        decision: str,
        error_code: Optional[str] = None,
        issue_keys: Optional[list[str]] = None,
        evidence_refs: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Write a GATE_FINISH event to the audit log.

        Args:
            job_id: Job identifier
            gate_node: Gate node name (e.g., "intake_repo")
            decision: PASS, FAIL, or SKIPPED
            error_code: Optional error code if decision is FAIL
            issue_keys: List of issue keys associated with this gate
            evidence_refs: List of evidence references
            metadata: Optional additional metadata

        Returns:
            dict with status and event details
        """
        if decision not in Decision.ALL:
            raise ValueError(f"Invalid decision: {decision}. Must be one of {Decision.ALL}")

        event = {
            "event_type": "GATE_FINISH",
            "job_id": job_id,
            "gate_node": gate_node,
            "decision": decision,
            "error_code": error_code,
            "issue_keys": issue_keys or [],
            "evidence_refs": evidence_refs or [],
            "ts": _now_iso(),
        }

        if metadata:
            event["metadata"] = metadata

        self._append_event(event)
        return {"status": "WRITTEN", "event": event}

    def _append_event(self, event: dict[str, Any]) -> None:
        """Append event to the audit log file (append-only, no modification)."""
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def query(
        self,
        *,
        job_id: Optional[str] = None,
        gate_node: Optional[str] = None,
        decision: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Query audit events by filters.

        Supports filtering by:
        - job_id: exact match
        - gate_node: exact match
        - decision: exact match (PASS/FAIL/SKIPPED)

        Args:
            job_id: Filter by job ID
            gate_node: Filter by gate node
            decision: Filter by decision type
            limit: Maximum number of results (default 100)

        Returns:
            List of matching events, most recent first
        """
        if not self.audit_log_path.exists():
            return []

        events: list[dict[str, Any]] = []
        with open(self.audit_log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    continue

        # Filter
        filtered: list[dict[str, Any]] = []
        for event in events:
            if job_id and event.get("job_id") != job_id:
                continue
            if gate_node and event.get("gate_node") != gate_node:
                continue
            if decision and event.get("decision") != decision:
                continue
            filtered.append(event)

        # Most recent first
        filtered.sort(key=lambda x: str(x.get("ts", "")), reverse=True)
        return filtered[:limit]

    def count_events(
        self,
        *,
        job_id: Optional[str] = None,
        gate_node: Optional[str] = None,
        decision: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Count events matching filters.

        Returns:
            dict with total count and counts by decision type
        """
        events = self.query(job_id=job_id, gate_node=gate_node, decision=decision, limit=10000)
        by_decision: dict[str, int] = {}
        for event in events:
            d = event.get("decision", "UNKNOWN")
            by_decision[d] = by_decision.get(d, 0) + 1

        return {"total": len(events), "by_decision": by_decision}


def write_gate_finish_event(
    *,
    job_id: str,
    gate_node: str,
    decision: str,
    error_code: Optional[str] = None,
    issue_keys: Optional[list[str]] = None,
    evidence_refs: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
    audit_log_path: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Convenience function to write a gate finish event.

    This function is designed to be called from gate modules.
    It never raises - if writing fails, it returns a status indicating the error.
    """
    if os.getenv("SKILLFORGE_AUDIT_EVENT_ENABLED", "1") == "0":
        return {"status": "DISABLED", "event": None}

    try:
        writer = AuditEventWriter(
            audit_log_path=audit_log_path or Path("logs/audit_events.jsonl")
        )
        return writer.write_gate_finish(
            job_id=job_id,
            gate_node=gate_node,
            decision=decision,
            error_code=error_code,
            issue_keys=issue_keys,
            evidence_refs=evidence_refs,
            metadata=metadata,
        )
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "event": None}


def query_audit_events(
    *,
    job_id: Optional[str] = None,
    gate_node: Optional[str] = None,
    decision: Optional[str] = None,
    limit: int = 100,
    audit_log_path: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """
    Convenience function to query audit events.

    This is a read-only operation safe for UI/reporting.
    """
    try:
        writer = AuditEventWriter(
            audit_log_path=audit_log_path or Path("logs/audit_events.jsonl")
        )
        return writer.query(
            job_id=job_id,
            gate_node=gate_node,
            decision=decision,
            limit=limit,
        )
    except Exception:
        return []
