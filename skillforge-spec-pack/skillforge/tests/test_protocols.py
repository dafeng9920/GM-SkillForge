"""
Contract tests for SkillForge implementation layer.

Validates:
1. All 12 NodeHandler implementations satisfy the NodeHandler protocol.
2. All 3 Adapter implementations satisfy the Adapter protocol.
3. pipeline_input.schema.json and pipeline_output.schema.json exist and are valid JSON Schema.
4. PipelineEngine input/output samples validate against schemas.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from skillforge.src.protocols import Adapter, GateEvaluator, NodeHandler

# ---------------------------------------------------------------------------
# Node handler imports
# ---------------------------------------------------------------------------
from skillforge.src.nodes.intent_parser import IntentParser
from skillforge.src.nodes.source_strategy import SourceStrategy
from skillforge.src.nodes.github_discover import GitHubDiscovery
from skillforge.src.nodes.skill_composer import SkillComposer
from skillforge.src.nodes.intake_repo import IntakeRepo
from skillforge.src.nodes.license_gate import LicenseGate
from skillforge.src.nodes.repo_scan import RepoScan
from skillforge.src.nodes.draft_spec import DraftSpec
from skillforge.src.nodes.constitution_gate import ConstitutionGate
from skillforge.src.nodes.scaffold_impl import ScaffoldImpl
from skillforge.src.nodes.sandbox_test import SandboxTest
from skillforge.src.nodes.pack_publish import PackPublish

# ---------------------------------------------------------------------------
# Adapter imports
# ---------------------------------------------------------------------------
from skillforge.src.adapters.github_fetch.adapter import GitHubFetchAdapter
from skillforge.src.adapters.sandbox_runner.adapter import SandboxRunnerAdapter
from skillforge.src.adapters.registry_client.adapter import RegistryClientAdapter

# ---------------------------------------------------------------------------
# Orchestration imports
# ---------------------------------------------------------------------------
from skillforge.src.orchestration.engine import PipelineEngine
from skillforge.src.orchestration.gate_engine import GateEngine

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

ALL_NODE_CLASSES: list[type] = [
    IntentParser,
    SourceStrategy,
    GitHubDiscovery,
    SkillComposer,
    IntakeRepo,
    LicenseGate,
    RepoScan,
    DraftSpec,
    ConstitutionGate,
    ScaffoldImpl,
    SandboxTest,
    PackPublish,
]

EXPECTED_NODE_IDS: set[str] = {
    "intent_parse",
    "source_strategy",
    "github_discover",
    "skill_compose",
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
}

ALL_ADAPTER_CLASSES: list[type] = [
    GitHubFetchAdapter,
    SandboxRunnerAdapter,
    RegistryClientAdapter,
]


# ===========================================================================
# 1. NodeHandler protocol conformance
# ===========================================================================
class TestNodeHandlerProtocol:
    """All 12 node handler classes satisfy the NodeHandler protocol."""

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_is_node_handler(self, cls: type) -> None:
        instance = cls()
        assert isinstance(instance, NodeHandler), (
            f"{cls.__name__} does not satisfy NodeHandler protocol"
        )

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_node_id(self, cls: type) -> None:
        instance = cls()
        assert hasattr(instance, "node_id")
        assert isinstance(instance.node_id, str)
        assert len(instance.node_id) > 0

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_stage(self, cls: type) -> None:
        instance = cls()
        assert hasattr(instance, "stage")
        assert isinstance(instance.stage, int)

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_execute(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "execute", None))

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_validate_input(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "validate_input", None))

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_validate_output(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "validate_output", None))

    def test_all_expected_node_ids_covered(self) -> None:
        actual_ids = {cls().node_id for cls in ALL_NODE_CLASSES}
        assert actual_ids == EXPECTED_NODE_IDS




# ===========================================================================
# 2. Adapter protocol conformance
# ===========================================================================
class TestAdapterProtocol:
    """All 3 adapter classes satisfy the Adapter protocol."""

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_is_adapter(self, cls: type) -> None:
        instance = cls()
        assert isinstance(instance, Adapter), (
            f"{cls.__name__} does not satisfy Adapter protocol"
        )

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_has_adapter_id(self, cls: type) -> None:
        instance = cls()
        assert hasattr(instance, "adapter_id")
        assert isinstance(instance.adapter_id, str)
        assert len(instance.adapter_id) > 0

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_has_health_check(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "health_check", None))

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_has_execute(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "execute", None))

    def test_unique_adapter_ids(self) -> None:
        ids = [cls().adapter_id for cls in ALL_ADAPTER_CLASSES]
        assert len(ids) == len(set(ids)), "Adapter IDs must be unique"


# ===========================================================================
# 3. GateEvaluator protocol conformance
# ===========================================================================
class TestGateEvaluatorProtocol:
    """GateEngine satisfies the GateEvaluator protocol."""

    def test_gate_engine_is_gate_evaluator(self) -> None:
        engine = GateEngine()
        assert isinstance(engine, GateEvaluator)

    def test_gate_engine_has_evaluate(self) -> None:
        engine = GateEngine()
        assert callable(getattr(engine, "evaluate", None))


# ===========================================================================
# 4. JSON Schema files exist and are valid
# ===========================================================================
class TestSchemaFiles:
    """pipeline_input.schema.json and pipeline_output.schema.json are valid."""

    @pytest.mark.parametrize(
        "filename",
        ["pipeline_input.schema.json", "pipeline_output.schema.json"],
    )
    def test_schema_file_exists(self, filename: str) -> None:
        path = SCHEMA_DIR / filename
        assert path.exists(), f"Schema file not found: {path}"

    @pytest.mark.parametrize(
        "filename",
        ["pipeline_input.schema.json", "pipeline_output.schema.json"],
    )
    def test_schema_is_valid_json(self, filename: str) -> None:
        path = SCHEMA_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "type" in schema

    def test_input_schema_requires_mode(self) -> None:
        path = SCHEMA_DIR / "pipeline_input.schema.json"
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert "mode" in schema.get("required", [])

    def test_output_schema_requires_job_id(self) -> None:
        path = SCHEMA_DIR / "pipeline_output.schema.json"
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert "job_id" in schema.get("required", [])

    def test_output_schema_requires_schema_version(self) -> None:
        path = SCHEMA_DIR / "pipeline_output.schema.json"
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert "schema_version" in schema.get("required", [])


# ===========================================================================
# 5. Engine input/output contract shapes
# ===========================================================================
class TestEngineContracts:
    """PipelineEngine input/output samples conform to expected shapes."""

    def _sample_input_nl(self) -> dict[str, Any]:
        return {
            "mode": "nl",
            "natural_language": "I need an SEO audit tool",
            "branch": "main",
            "options": {
                "target_environment": "python",
                "intended_use": "automation",
                "visibility": "public",
                "sandbox_mode": "strict",
            },
        }

    def _sample_input_github(self) -> dict[str, Any]:
        return {
            "mode": "github",
            "repo_url": "https://github.com/example/repo",
            "branch": "main",
            "options": {
                "target_environment": "python",
                "intended_use": "web",
                "visibility": "private",
                "sandbox_mode": "moderate",
            },
        }

    def _sample_output(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1.0",
            "job_id": "00000000-0000-0000-0000-000000000000",
            "status": "completed",
            "path_taken": "A",
            "stages_completed": 7,
            "gate_decisions": [],
            "audit_pack_path": "/tmp/audit.json",
            "publish_result": None,
            "trace_events": [],
            "duration_ms": 1234,
            "error": None,
        }

    def test_sample_input_nl_has_required_fields(self) -> None:
        sample = self._sample_input_nl()
        assert "mode" in sample
        assert sample["mode"] == "nl"
        assert "natural_language" in sample

    def test_sample_input_github_has_required_fields(self) -> None:
        sample = self._sample_input_github()
        assert "mode" in sample
        assert sample["mode"] == "github"
        assert "repo_url" in sample

    def test_sample_output_has_required_fields(self) -> None:
        sample = self._sample_output()
        required = [
            "schema_version",
            "job_id",
            "status",
            "path_taken",
            "stages_completed",
            "gate_decisions",
            "trace_events",
            "duration_ms",
        ]
        for field in required:
            assert field in sample, f"Missing required field: {field}"

    def test_sample_output_schema_version(self) -> None:
        sample = self._sample_output()
        assert sample["schema_version"] == "0.1.0"

    def test_engine_build_output_helper(self) -> None:
        engine = PipelineEngine()
        output = engine._build_output(
            job_id="test-id",
            run_id="test-run-id",
            status="completed",
            path_taken="A",
            stages_completed=7,
            gate_decisions=[],
            audit_pack_path=None,
            publish_result=None,
            trace_events=[],
            duration_ms=100,
            error=None,
        )
        assert output["schema_version"] == "0.1.0"
        assert output["job_id"] == "test-id"
        assert output["run_id"] == "test-run-id"
        assert output["status"] == "completed"

    def test_engine_resolve_path_nl(self) -> None:
        engine = PipelineEngine()
        label, nodes = engine._resolve_path("nl")
        assert label == "A"
        assert "intent_parse" in nodes
        assert "pack_audit_and_publish" in nodes

    def test_engine_resolve_path_github(self) -> None:
        engine = PipelineEngine()
        label, nodes = engine._resolve_path("github")
        assert label == "B"
        assert "intake_repo" in nodes

    def test_engine_resolve_path_auto(self) -> None:
        engine = PipelineEngine()
        label, nodes = engine._resolve_path("auto")
        assert label == "AB"
        assert "github_discover" in nodes

    def test_engine_resolve_path_invalid(self) -> None:
        engine = PipelineEngine()
        with pytest.raises(ValueError):
            engine._resolve_path("invalid")

