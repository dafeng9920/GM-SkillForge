"""
Tests for Experience Capture v0.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from skillforge.src.skills.experience_capture import (
    ExperienceCaptureV0,
    FixKind,
    capture_gate_event,
    retrieve_experience_templates,
)


def test_capture_writes_entry_and_summary():
    """A valid entry should be appended and summary should be generated."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        evolution = root / "evolution.json"
        summary = root / "SKILL.md"
        capture = ExperienceCaptureV0(evolution_path=evolution, summary_path=summary)

        result = capture.capture(
            issue_key="SCAN-001",
            evidence_ref="file://AuditPack/evidence/scan_report_SCAN-001.json",
            gate_node="repo_scan_fit_score",
            summary="scan gate passed with stable fit score",
            fix_kind=FixKind.GATE_DECISION,
        )
        assert result["status"] == "CAPTURED"

        data = json.loads(evolution.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 1
        assert data["entries"][0]["issue_key"] == "SCAN-001"
        assert data["entries"][0]["content_hash"]
        assert summary.exists()
        assert "repo_scan_fit_score" in summary.read_text(encoding="utf-8")


def test_capture_missing_evidence_marked_and_rejected():
    """Entries without evidence must be marked MISSING_EVIDENCE and not captured."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        evolution = root / "evolution.json"
        summary = root / "SKILL.md"
        capture = ExperienceCaptureV0(evolution_path=evolution, summary_path=summary)

        result = capture.capture(
            issue_key="RISK-001",
            evidence_ref=None,
            gate_node="constitution_risk_gate",
            summary="risk gate rejected without evidence",
            fix_kind=FixKind.GATE_DECISION,
        )
        assert result["status"] == "MISSING_EVIDENCE"
        assert result["captured"] is False

        data = json.loads(evolution.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 0
        assert len(data["rejected_entries"]) == 1
        assert data["rejected_entries"][0]["status"] == "MISSING_EVIDENCE"


def test_capture_deduplicates_by_content_hash():
    """Same payload should be deduplicated by content_hash."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        evolution = root / "evolution.json"
        summary = root / "SKILL.md"
        capture = ExperienceCaptureV0(evolution_path=evolution, summary_path=summary)

        kwargs = {
            "issue_key": "INTAKE-001",
            "evidence_ref": "file://AuditPack/evidence/intake_manifest_REQ-1.json",
            "gate_node": "intake_repo",
            "summary": "intake accepted",
            "fix_kind": FixKind.GATE_DECISION,
        }
        first = capture.capture(**kwargs)
        second = capture.capture(**kwargs)

        assert first["status"] == "CAPTURED"
        assert second["status"] == "SKIPPED_DUPLICATE"

        data = json.loads(evolution.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 1


def test_capture_gate_event_helper_never_raises():
    """Helper should tolerate runtime usage and write one entry."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        old_cwd = Path.cwd()
        try:
            os.chdir(root)
            capture_gate_event(
                gate_node="pack_audit_and_publish",
                gate_decision="PASSED",
                evidence_refs=[
                    {
                        "issue_key": "PUBLISH-001",
                        "source_locator": "file://AuditPack/audit/manifest.json",
                        "content_hash": "abc",
                        "tool_revision": "0.1.0",
                        "timestamp": "2026-02-20T00:00:00Z",
                    }
                ],
                fix_kind=FixKind.PUBLISH_PACK,
                summary="publish gate passed",
            )
        finally:
            os.chdir(old_cwd)

        evolution = root / "AuditPack" / "experience" / "evolution.json"
        assert evolution.exists()
        data = json.loads(evolution.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 1


def test_retrieve_templates_by_issue_key_and_fix_kind():
    """Should retrieve templates by issue key prefix and fix kind."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        capture = ExperienceCaptureV0(
            evolution_path=root / "evolution.json",
            summary_path=root / "SKILL.md",
        )
        capture.capture(
            issue_key="SCAFFOLD-abc-001",
            evidence_ref="file://AuditPack/evidence/scaffold_1.json",
            gate_node="scaffold_skill_impl",
            summary="applied scaffold template A",
            fix_kind=FixKind.UPDATE_SCAFFOLD,
        )
        capture.capture(
            issue_key="SCAFFOLD-abc-002",
            evidence_ref="file://AuditPack/evidence/scaffold_2.json",
            gate_node="scaffold_skill_impl",
            summary="applied scaffold template B",
            fix_kind=FixKind.UPDATE_SCAFFOLD,
        )
        capture.capture(
            issue_key="RISK-001",
            evidence_ref="file://AuditPack/evidence/risk_1.json",
            gate_node="constitution_risk_gate",
            summary="risk gate decision",
            fix_kind=FixKind.GATE_DECISION,
        )

        result = capture.retrieve_templates(
            issue_key="SCAFFOLD-*",
            fix_kind=FixKind.UPDATE_SCAFFOLD,
            gate_node="scaffold_skill_impl",
            limit=10,
        )
        assert len(result) == 2
        assert all(item["issue_key"].startswith("SCAFFOLD-") for item in result)
        assert all(item["fix_kind"] == FixKind.UPDATE_SCAFFOLD for item in result)


def test_retrieve_templates_public_helper_returns_empty_when_missing():
    """Public helper must be safe and return empty list on missing store."""
    result = retrieve_experience_templates(
        issue_key="NONEXIST-*",
        fix_kind=FixKind.UPDATE_SCAFFOLD,
        gate_node="scaffold_skill_impl",
        limit=3,
    )
    assert isinstance(result, list)
