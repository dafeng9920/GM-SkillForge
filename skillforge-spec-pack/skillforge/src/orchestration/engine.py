"""
PipelineEngine — dual-path orchestration engine for SkillForge.

Input Contract
--------------
{
    "mode": "nl" | "github" | "auto",
    "natural_language": str | None,
    "repo_url": str | None,
    "branch": str  (default "main"),
    "options": {
        "target_environment": "python" | "node" | "docker",
        "intended_use": "automation" | "data" | "web" | "ops",
        "visibility": "public" | "private" | "team",
        "sandbox_mode": "strict" | "moderate" | "permissive"
    }
}

Output Contract
---------------
{
    "job_id": "UUID",
    "run_id": "UUID",           # L5 G3: traceability
    "status": "completed" | "failed" | "gate_denied",
    "path_taken": "A" | "B" | "AB",
    "stages_completed": int,
    "gate_decisions": [GateDecision...],
    "audit_pack_path": str | None,
    "publish_result": dict | None,
    "updated_graph": dict | None,       # T3: Graph update information
    "release_manifest": dict | None,    # T3: Release manifest with rollback
    "ruling": {                         # T1: Top-level ruling for gate decisions
        "verdict": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
        "rule_id": str,
        "evidence_ref": str | None,
        "blocked": bool
    } | None,
    "ruling_path": str | None,          # T1: Path to ruling in gate_decisions
    "trace_events": [TraceEvent...],
    "duration_ms": int,
    "error": { "code": str, "message": str } | None
}

Path routing
------------
- mode "nl"     → Path A:  intent_parse → source_strategy → skill_compose
                            → constitution_risk_gate → scaffold → sandbox → publish
- mode "github" → Path B:  intake_repo → license_gate → repo_scan → draft_spec
                            → constitution_risk_gate → scaffold → sandbox → publish
- mode "auto"   → Path AB: intent_parse → source_strategy → github_discover
                            → intake_repo → … → publish
"""
from __future__ import annotations

import hashlib
import json
import uuid
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from skillforge.src.protocols import NodeHandler, GateEvaluator
from skillforge.src.storage.repository import SkillRepository


# -- T3: Incremental request detection keywords -------------------------------
INCREMENTAL_KEYWORDS = [
    "已有", "基础上", "新增", "升级", "扩展", "修改", "更新",
    "增强", "添加", "改进", "优化", "调整", "变更",
    "extend", "update", "upgrade", "enhance", "modify", "add",
    "improve", "optimize", "adjust", "change", "existing", "based on",
]


# -- Path definitions ---------------------------------------------------------

PATH_A: list[str] = [
    "intent_parse",
    "source_strategy",
    "skill_compose",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
]

PATH_B: list[str] = [
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
]

PATH_AB: list[str] = [
    "intent_parse",
    "source_strategy",
    "github_discover",
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
]

GATE_NODES: set[str] = {"license_gate", "constitution_risk_gate"}


@dataclass
class PipelineEngine:
    """
    Dual-path orchestration engine.

    Attributes:
        node_registry: Mapping of node_id → NodeHandler instance.
        gate_evaluator: GateEvaluator used for gate nodes.
        schema_version: Output schema version tag.
    """

    node_registry: dict[str, NodeHandler] = field(default_factory=dict)
    gate_evaluator: GateEvaluator | None = None
    schema_version: str = "0.1.0"
    db_path: str | Path = "db/skillforge.sqlite"
    _repo: SkillRepository | None = field(default=None, repr=False, init=False)

    @property
    def repo(self) -> SkillRepository:
        """Lazy-initialized storage repository."""
        if self._repo is None:
            self._repo = SkillRepository(self.db_path)
        return self._repo

    # -- public API -----------------------------------------------------------

    def register_node(self, handler: NodeHandler) -> None:
        """Register a NodeHandler by its node_id."""
        self.node_registry[handler.node_id] = handler

    def run(self, input_data: dict[str, Any], run_id: str | None = None) -> dict[str, Any]:
        """
        Execute the full pipeline for the given input.

        Args:
            input_data: A dict conforming to pipeline_input.schema.json.
            run_id: Optional run identifier for L5 G3 traceability.
                   If None, a UUID will be generated.

        Returns:
            A dict conforming to pipeline_output.schema.json.
        """
        # Generate or use provided run_id (L5 G3 requirement)
        if run_id is None or run_id == "":
            run_id = str(uuid.uuid4())

        job_id = str(uuid.uuid4())
        start_time = time.time()
        trace_events: list[dict[str, Any]] = []
        gate_decisions: list[dict[str, Any]] = []
        stages_completed = 0
        path_taken = ""
        node_ids: list[str] = []
        artifacts: dict[str, Any] = {}

        # Counter for deterministic trace_id generation (L5 G4 requirement)
        trace_counter = 0

        try:
            # ── validate input ────────────────────────────────────
            mode = input_data.get("mode", "")

            if mode not in ("nl", "github", "auto"):
                return self._build_output(
                    job_id=job_id, run_id=run_id, status="failed", path_taken="",
                    stages_completed=0, gate_decisions=gate_decisions,
                    audit_pack_path=None, publish_result=None,
                    trace_events=trace_events,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error={"code": "EXEC_INVALID_INPUT",
                           "message": "mode must be one of: nl, github, auto"},
                )

            if mode == "nl" and not input_data.get("natural_language"):
                return self._build_output(
                    job_id=job_id, run_id=run_id, status="failed", path_taken="",
                    stages_completed=0, gate_decisions=gate_decisions,
                    audit_pack_path=None, publish_result=None,
                    trace_events=trace_events,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error={"code": "EXEC_INVALID_INPUT",
                           "message": "natural_language is required for mode 'nl'"},
                )

            if mode == "github" and not input_data.get("repo_url"):
                return self._build_output(
                    job_id=job_id, run_id=run_id, status="failed", path_taken="",
                    stages_completed=0, gate_decisions=gate_decisions,
                    audit_pack_path=None, publish_result=None,
                    trace_events=trace_events,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error={"code": "EXEC_INVALID_INPUT",
                           "message": "repo_url is required for mode 'github'"},
                )

            if mode == "auto" and not input_data.get("natural_language"):
                return self._build_output(
                    job_id=job_id, run_id=run_id, status="failed", path_taken="",
                    stages_completed=0, gate_decisions=gate_decisions,
                    audit_pack_path=None, publish_result=None,
                    trace_events=trace_events,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error={"code": "EXEC_INVALID_INPUT",
                           "message": "natural_language is required for mode 'auto'"},
                )

            # ── resolve path ──────────────────────────────────────
            path_taken, node_ids = self._resolve_path(mode)

            # ── init artifacts with run_id context (L5 G3) ─────────
            artifacts = {"input": input_data, "_run_context": {"run_id": run_id}}

            # ── T3: Detect incremental request and load existing skill ───────────
            if mode in ("nl", "auto"):
                natural_language = input_data.get("natural_language", "")
                is_incremental, change_request = self._detect_incremental_request(natural_language)
                if is_incremental:
                    existing_skill = self._find_related_skill(natural_language)
                    if existing_skill:
                        artifacts["_incremental_context"] = {
                            "is_incremental": True,
                            "existing_skill": existing_skill,
                            "change_request": change_request,
                        }

            # ── iterate nodes ─────────────────────────────────────
            for node_id in node_ids:
                # check registration
                if node_id not in self.node_registry:
                    return self._build_output(
                        job_id=job_id, run_id=run_id, status="failed", path_taken=path_taken,
                        stages_completed=stages_completed,
                        gate_decisions=gate_decisions,
                        audit_pack_path=None, publish_result=None,
                        trace_events=trace_events,
                        duration_ms=int((time.time() - start_time) * 1000),
                        error={"code": "EXEC_NODE_NOT_FOUND",
                               "message": f"node '{node_id}' is not registered"},
                    )

                handler = self.node_registry[node_id]

                # gate node - use gate_evaluator if available, otherwise use handler directly
                if node_id in GATE_NODES:
                    if self.gate_evaluator is not None:
                        gate_decision = self.gate_evaluator.evaluate(
                            node_id, artifacts
                        )
                    else:
                        # Fallback: call handler.execute() directly for gate nodes
                        gate_decision = handler.execute(artifacts)

                    gate_decisions.append(gate_decision)
                    # Store gate decision in artifacts for downstream nodes
                    artifacts[node_id] = gate_decision
                    decision = gate_decision.get("decision", "")

                    if decision == "DENY":
                        return self._build_output(
                            job_id=job_id, run_id=run_id, status="gate_denied",
                            path_taken=path_taken,
                            stages_completed=stages_completed,
                            gate_decisions=gate_decisions,
                            audit_pack_path=None, publish_result=None,
                            trace_events=trace_events,
                            duration_ms=int((time.time() - start_time) * 1000),
                            error={"code": "GATE_DENIED",
                                   "message": gate_decision.get("reason", "")},
                        )

                    if decision == "REQUIRES_CHANGES":
                        return self._build_output(
                            job_id=job_id, run_id=run_id, status="failed",
                            path_taken=path_taken,
                            stages_completed=stages_completed,
                            gate_decisions=gate_decisions,
                            audit_pack_path=None, publish_result=None,
                            trace_events=trace_events,
                            duration_ms=int((time.time() - start_time) * 1000),
                            error={"code": "GATE_REQUIRES_CHANGES",
                                   "message": gate_decision.get("reason", "")},
                        )

                # regular node
                else:
                    input_snapshot = dict(artifacts)

                    # validate input
                    input_errors = handler.validate_input(input_snapshot)
                    if input_errors:
                        return self._build_output(
                            job_id=job_id, run_id=run_id, status="failed",
                            path_taken=path_taken,
                            stages_completed=stages_completed,
                            gate_decisions=gate_decisions,
                            audit_pack_path=None, publish_result=None,
                            trace_events=trace_events,
                            duration_ms=int((time.time() - start_time) * 1000),
                            error={"code": "EXEC_VALIDATION_FAILED",
                                   "message": f"{node_id}: {'; '.join(input_errors)}"},
                        )

                    # execute
                    result = handler.execute(artifacts)

                    # validate output
                    output_errors = handler.validate_output(result)
                    if output_errors:
                        return self._build_output(
                            job_id=job_id, run_id=run_id, status="failed",
                            path_taken=path_taken,
                            stages_completed=stages_completed,
                            gate_decisions=gate_decisions,
                            audit_pack_path=None, publish_result=None,
                            trace_events=trace_events,
                            duration_ms=int((time.time() - start_time) * 1000),
                            error={"code": "EXEC_OUTPUT_INVALID",
                                   "message": f"{node_id}: {'; '.join(output_errors)}"},
                        )

                    # store result
                    artifacts[node_id] = result

                    # ── AB path bridge ────────────────────────────
                    # When github_discover selects a repo in AB path,
                    # inject its URL into artifacts["input"]["repo_url"]
                    # so intake_repo can find it downstream.
                    if (
                        node_id == "github_discover"
                        and path_taken == "AB"
                        and isinstance(result, dict)
                    ):
                        selected = result.get("selected")
                        if isinstance(selected, dict) and selected.get("repo_url"):
                            artifacts.setdefault("input", {})
                            artifacts["input"]["repo_url"] = selected["repo_url"]

                stages_completed += 1

                # trace event with run_id and deterministic trace_id (L5 G3/G4)
                trace_events.append(self._make_trace_event(
                    run_id=run_id,
                    trace_counter=trace_counter,
                    node_id=node_id,
                    event_type="complete",
                ))
                trace_counter += 1

            # ── extract final outputs ─────────────────────────────
            audit_pack_path: str | None = None
            publish_result: dict[str, Any] | None = None
            updated_graph: dict[str, Any] | None = None
            release_manifest: dict[str, Any] | None = None
            final_key = "pack_audit_and_publish"
            if final_key in artifacts and isinstance(
                artifacts[final_key], dict
            ):
                audit_pack_path = artifacts[final_key].get("audit_pack_path")
                publish_result = artifacts[final_key].get("publish_result")
                # T3: Extract updated_graph and release_manifest
                updated_graph = artifacts[final_key].get("updated_graph")
                release_manifest = artifacts[final_key].get("release_manifest")

            # ── persist to storage ────────────────────────────────
            self._persist_to_storage(artifacts)

            # ── build output ──────────────────────────────────────
            return self._build_output(
                job_id=job_id, run_id=run_id, status="completed", path_taken=path_taken,
                stages_completed=stages_completed,
                gate_decisions=gate_decisions,
                audit_pack_path=audit_pack_path,
                publish_result=publish_result,
                updated_graph=updated_graph,
                release_manifest=release_manifest,
                trace_events=trace_events,
                duration_ms=int((time.time() - start_time) * 1000),
                error=None,
            )

        except Exception as exc:
            return self._build_output(
                job_id=job_id, run_id=run_id, status="failed", path_taken=path_taken,
                stages_completed=stages_completed,
                gate_decisions=gate_decisions,
                audit_pack_path=None, publish_result=None,
                trace_events=trace_events,
                duration_ms=int((time.time() - start_time) * 1000),
                error={"code": "SYS_UNEXPECTED", "message": str(exc)},
            )

    # -- internal helpers -----------------------------------------------------

    def _persist_to_storage(self, artifacts: dict[str, Any]) -> None:
        """Persist audit pack results to SQLite storage."""
        final = artifacts.get("pack_audit_and_publish")
        if not isinstance(final, dict):
            return

        audit_pack = final.get("audit_pack", {})
        if not isinstance(audit_pack, dict):
            return

        skill_id = audit_pack.get("skill_id", "")
        audit_id = audit_pack.get("audit_id", "")
        quality_level = audit_pack.get("quality_level", "L1")
        created_at = audit_pack.get("created_at", "")

        if not skill_id or not audit_id:
            return

        try:
            # Create skill and revision
            self.repo.ensure_skill(skill_id)

            files_meta = audit_pack.get("files", {})
            manifest = files_meta.get("manifest", {})
            manifest_json = json.dumps(manifest, default=str)
            manifest_sha = hashlib.sha256(manifest_json.encode()).hexdigest()

            rev = self.repo.append_revision(
                skill_id=skill_id,
                revision_id=audit_id,
                effective_at=created_at,
                manifest_sha256=manifest_sha,
                path=final.get("audit_pack_path", ""),
                quality_level=quality_level,
            )

            # Add artifacts for each L3 file
            l3_files = [
                "manifest.json", "policy_matrix.json", "static_analysis.log",
                "original_repo_snapshot.json", "repro_env.yml",
                "evidence.jsonl", "source_lineage.diff",
            ]
            for filename in l3_files:
                self.repo.add_artifact(
                    revision_id=audit_id,
                    artifact_type="l3_pack",
                    filename=filename,
                    sha256=manifest_sha[:16] + "-" + filename,
                    size_bytes=0,
                )
        except Exception:
            pass  # Storage failure must not break pipeline

    def _resolve_path(self, mode: str) -> tuple[str, list[str]]:
        """Return (path_label, ordered list of node_ids) for the given mode."""
        if mode == "nl":
            return ("A", PATH_A)
        elif mode == "github":
            return ("B", PATH_B)
        elif mode == "auto":
            return ("AB", PATH_AB)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _make_trace_event(
        self,
        *,
        run_id: str,
        trace_counter: int,
        node_id: str,
        event_type: str,
        detail: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build a trace_event dict with run_id and deterministic trace_id.

        L5 G3/G4 requirements:
        - trace_id is deterministic based on run_id + counter for replayability
        - run_id is included for traceability

        Args:
            run_id: The pipeline run identifier.
            trace_counter: Sequential counter for deterministic trace_id.
            node_id: Originating node.
            event_type: One of node_start, node_complete, node_error.
            detail: Optional extra payload.

        Returns:
            TraceEvent dict with schema_version = "0.1.0".
        """
        # Deterministic trace_id: hash of run_id + counter (L5 G4)
        trace_seed = f"{run_id}-{trace_counter}"
        trace_hash = hashlib.sha256(trace_seed.encode()).hexdigest()[:32]

        return {
            "schema_version": "0.1.0",
            "run_id": run_id,
            "trace_id": f"trace-{trace_hash}",
            "node_id": node_id,
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "detail": detail or {},
        }

    def _build_output(
        self,
        *,
        job_id: str,
        run_id: str,
        status: str,
        path_taken: str,
        stages_completed: int,
        gate_decisions: list[dict[str, Any]],
        audit_pack_path: str | None,
        publish_result: dict[str, Any] | None,
        updated_graph: dict[str, Any] | None = None,
        release_manifest: dict[str, Any] | None = None,
        trace_events: list[dict[str, Any]],
        duration_ms: int,
        error: dict[str, str] | None,
    ) -> dict[str, Any]:
        """Construct a pipeline_output conforming dict."""
        # Extract top-level ruling from gate_decisions (T1 requirement)
        ruling: dict[str, Any] | None = None
        ruling_path: str | None = None
        for i, gate in enumerate(gate_decisions):
            if isinstance(gate, dict):
                gate_ruling = gate.get("ruling")
                if isinstance(gate_ruling, dict):
                    ruling = gate_ruling
                    ruling_path = f"gate_decisions[{i}].ruling"
                    break

        return {
            "schema_version": self.schema_version,
            "job_id": job_id,
            "run_id": run_id,
            "status": status,
            "path_taken": path_taken,
            "stages_completed": stages_completed,
            "gate_decisions": gate_decisions,
            "audit_pack_path": audit_pack_path,
            "publish_result": publish_result,
            "updated_graph": updated_graph,
            "release_manifest": release_manifest,
            "ruling": ruling,
            "ruling_path": ruling_path,
            "trace_events": trace_events,
            "duration_ms": duration_ms,
            "error": error,
        }

    # -- T3: Incremental request detection helpers ---------------------------------

    def _detect_incremental_request(self, natural_language: str) -> tuple[bool, dict[str, Any]]:
        """
        Detect if the request is incremental (update to existing skill).

        Returns:
            (is_incremental, change_request) tuple.
        """
        if not natural_language:
            return (False, {})

        nl_lower = natural_language.lower()

        # Check for incremental keywords
        has_incremental_keyword = any(kw in nl_lower for kw in INCREMENTAL_KEYWORDS)

        if not has_incremental_keyword:
            return (False, {})

        # Determine change scope based on keywords
        change_scope = "minor"  # default

        major_keywords = ["remove", "delete", "breaking", "删除", "移除", "重大"]
        if any(kw in nl_lower for kw in major_keywords):
            change_scope = "major"

        subskill_keywords = ["fork", "variant", "alternative", "extend", "扩展", "分支"]
        if any(kw in nl_lower for kw in subskill_keywords):
            change_scope = "subskill"

        # Extract description for change request
        change_request: dict[str, Any] = {
            "description": natural_language,
            "scope": change_scope,
            "detected_keywords": [kw for kw in INCREMENTAL_KEYWORDS if kw in nl_lower],
        }

        return (True, change_request)

    def _find_related_skill(self, natural_language: str) -> dict[str, Any] | None:
        """
        Find the most recent skill that matches the incremental request context.

        This queries the database for existing skills and returns the most relevant one.
        Returns semantic version (x.y.z format) for proper version bumping.
        """
        try:
            skills = self.repo.list_skills()
            if not skills:
                return None

            # Get the most recently created/updated skill
            # In a real implementation, we would do semantic matching
            # For now, return the latest skill with a valid skill_spec
            for skill in reversed(skills):
                skill_id = skill.get("skill_id")
                if not skill_id:
                    continue

                # Try to get the latest revision and extract semantic version
                revisions = self.repo.get_revisions(skill_id)
                semantic_version = "0.1.0"  # default

                if revisions:
                    latest_rev = revisions[0] if isinstance(revisions, list) else revisions
                    # Try to extract semantic version from metadata
                    metadata = latest_rev.get("metadata")
                    if isinstance(metadata, dict):
                        semantic_version = metadata.get("semantic_version", "0.1.0")
                    elif isinstance(metadata, str):
                        try:
                            import json
                            meta_dict = json.loads(metadata)
                            semantic_version = meta_dict.get("semantic_version", "0.1.0")
                        except (json.JSONDecodeError, TypeError):
                            pass

                    # Construct skill_spec from stored data with semantic version
                    return {
                        "skill_spec": {
                            "name": skill_id,
                            "version": semantic_version,
                            "description": f"Existing skill {skill_id}",
                        }
                    }

                # Fallback: return skill with basic spec
                return {
                    "skill_spec": {
                        "name": skill_id,
                        "version": "0.1.0",
                        "description": f"Existing skill {skill_id}",
                    }
                }

            return None
        except Exception:
            return None
