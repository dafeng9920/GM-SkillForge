"""
Integration tests for IssueKey/FixKind template reader usage in scaffold gate.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from skillforge.src.skills.experience_capture import ExperienceCaptureV0, FixKind
from skillforge.src.skills.gates.gate_scaffold import GateScaffoldSkill


def test_scaffold_gate_returns_experience_templates():
    """Scaffold gate should include retrieved historical templates in output."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        old_cwd = Path.cwd()
        try:
            os.chdir(root)

            capture = ExperienceCaptureV0()
            capture.capture(
                issue_key="SCAFFOLD-demo-001",
                evidence_ref="file://AuditPack/evidence/scaffold_demo_001.json",
                gate_node="scaffold_skill_impl",
                summary="historical scaffold fix template",
                fix_kind=FixKind.UPDATE_SCAFFOLD,
            )

            gate = GateScaffoldSkill()
            result = gate.execute(
                {
                    "scaffold_skill_impl": {
                        "files_generated": ["main.py"],
                        "manifest": {
                            "skill_id": "demo-skill",
                            "version": "0.1.0",
                            "checksum": "abc123",
                        },
                    }
                }
            )

            assert result["gate_decision"] == "PASSED"
            assert "experience_templates" in result
            assert isinstance(result["experience_templates"], list)
            assert len(result["experience_templates"]) >= 1
            assert result["experience_templates"][0]["fix_kind"] == FixKind.UPDATE_SCAFFOLD
        finally:
            os.chdir(old_cwd)

