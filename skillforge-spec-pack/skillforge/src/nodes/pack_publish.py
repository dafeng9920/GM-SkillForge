"""
PackPublish node — build L3 Audit Pack and publish to registry.

Path: ALL
Stage: 7

Aligned with AUDIT_ENGINE_PROTOCOL_v1.md:
- L3 Audit Pack MUST files:
  1. manifest.json       — file listing + sha256 + provenance
  2. policy_matrix.json  — findings with issue_key + evidence_ref
  3. static_analysis.log — raw scan output (may be gzipped)
  4. original_repo_snapshot.json — upstream ref + snapshot_hash
  5. repro_env.yml       — reproduction environment + limits
  6. evidence.jsonl      — evidence chain (one JSON per line)
  7. source_lineage.diff — optional, present if patched

T2 Extension: Registry/Graph Integrity Verification
- Pre-publish integrity check before allowing publish
- Tampering detection returns DENY with conflict evidence
- Integrity gate decisions recorded in gate_decisions

T3 Extension: Incremental Delta Artifacts
- UpdatedGraph: Describes skill graph changes (nodes/edges added/modified)
- ReleaseManifest: Complete release info with rollback capability

Output Contract
---------------
{
    "schema_version": "1.0.0",
    "audit_pack": {
        "audit_id": str,
        "skill_id": str,
        "version": str,
        "quality_level": "L3",
        "gate_decisions": [GateDecision...],
        "test_report": { ... },
        "trace_summary": { ... },
        "created_at": str,
        "files": { ... }          # L3 MUST files content
    },
    "audit_pack_path": str,
    "publish_result": {
        "skill_id": str,
        "version": str,
        "status": "published" | "rejected",
        "registry_url": str,
        "timestamp": str
    },
    "updated_graph": {              # T3: Graph update information
        "skill_id": str,
        "version": str,
        "nodes_added": list[str],
        "nodes_modified": list[str],
        "edges_added": list[dict],
        "parent_ref": str | None,
        "graph_hash": str
    },
    "release_manifest": {           # T3: Release manifest with rollback
        "release_id": str,
        "skill_id": str,
        "version": str,
        "previous_version": str | None,
        "change_type": "new" | "update" | "subskill",
        "rollback": {
            "supported": bool,
            "rollback_version": str | None,
            "rollback_path": str | None
        },
        "artifacts": list[str],
        "published_at": str
    }
}
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from skillforge.src.storage.repository import SkillRepository
from skillforge.src.utils.constitution import load_constitution


def _sha256(data: str | bytes) -> str:
    """Compute sha256 hex digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _now_iso() -> str:
    """ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_issue_catalog(catalog_path: str | Path | None = None) -> dict[str, Any]:
    """Load issue_catalog.yml and return its contents."""
    if catalog_path is None:
        # Default path relative to this file
        catalog_path = Path(__file__).resolve().parents[3] / "orchestration" / "issue_catalog.yml"
    else:
        catalog_path = Path(catalog_path)

    if not catalog_path.exists():
        return {}

    if HAS_YAML:
        with open(catalog_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _get_catalog_version(catalog: dict[str, Any]) -> str:
    """Extract catalog_version from issue_catalog data."""
    return catalog.get("catalog_version", "unknown")


def _get_issue_added_in(catalog: dict[str, Any], issue_key: str) -> str:
    """Get added_in version for a specific issue_key from catalog."""
    issues = catalog.get("issues", [])
    for issue in issues:
        if isinstance(issue, dict) and issue.get("issue_key") == issue_key:
            return issue.get("added_in", "unknown")
    return "unknown"


@dataclass
class PackPublish:
    """Build the L3 audit pack and publish the skill to the registry."""

    node_id: str = "pack_audit_and_publish"
    stage: int = 7

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate scaffold, sandbox, and skill_spec are present."""
        errors: list[str] = []

        scaffold = input_data.get("scaffold_skill_impl")
        if not isinstance(scaffold, dict):
            errors.append("EXEC_VALIDATION_FAILED: scaffold_skill_impl output is required")

        sandbox = input_data.get("sandbox_test_and_trace")
        if not isinstance(sandbox, dict):
            errors.append("EXEC_VALIDATION_FAILED: sandbox_test_and_trace output is required")

        # skill_spec from either source
        skill_compose = input_data.get("skill_compose")
        draft_skill_spec = input_data.get("draft_skill_spec")

        has_spec = False
        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            has_spec = True
        if isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            has_spec = True

        if not has_spec:
            errors.append(
                "EXEC_VALIDATION_FAILED: skill_spec is required "
                "(from skill_compose or draft_skill_spec)"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Build L3 Audit Pack and publish skill.

        Collects evidence from upstream nodes, builds the 7 L3 MUST files,
        and publishes to the registry.
        """
        scaffold = input_data.get("scaffold_skill_impl", {})
        sandbox = input_data.get("sandbox_test_and_trace", {})

        # Resolve skill_spec
        skill_compose = input_data.get("skill_compose", {})
        draft_skill_spec = input_data.get("draft_skill_spec", {})

        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            skill_spec = skill_compose["skill_spec"]
        elif isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            skill_spec = draft_skill_spec["skill_spec"]
        else:
            skill_spec = {}

        skill_id: str = skill_spec.get("name", "unknown-skill")
        version: str = skill_spec.get("version", "0.1.0")

        # ── Load constitution reference and hash ──
        constitution_ref, constitution_hash = load_constitution()

        # ── Load issue catalog for versioning ──
        issue_catalog = _load_issue_catalog()
        catalog_version = _get_catalog_version(issue_catalog)

        # Collect upstream data
        intake = input_data.get("intake_repo", {})
        license_gate = input_data.get("license_gate", {})
        repo_scan = input_data.get("repo_scan_fit_score", {})
        constitution_gate = input_data.get("constitution_risk_gate", {})
        test_report = sandbox.get("test_report", {})
        trace_events = sandbox.get("trace_events", [])
        success: bool = sandbox.get("success", False)

        # Extract static analysis results from sandbox
        static_analysis = sandbox.get("static_analysis", {})
        static_findings_raw = static_analysis.get("findings", [])
        static_raw_output = static_analysis.get("raw_output", "")

        timestamp = _now_iso()
        audit_id = "audit-" + uuid.uuid4().hex[:8]

        # ── Collect gate decisions ──
        gate_decisions: list[dict[str, Any]] = []
        if isinstance(license_gate, dict) and "decision" in license_gate:
            gate_decisions.append(license_gate)
        if isinstance(constitution_gate, dict) and "decision" in constitution_gate:
            gate_decisions.append(constitution_gate)

        # ── T2: Registry/Graph Integrity Verification ──
        # Pre-publish integrity check to detect tampering
        integrity_gate: dict[str, Any] | None = None
        integrity_tampering = False
        integrity_ruling: dict[str, Any] | None = None

        # Determine database path from workspace or environment
        db_path = Path(os.environ.get("SKILLFORGE_DB_PATH", "db/skillforge.sqlite"))
        repo = SkillRepository(db_path=db_path)

        try:
            # Check if skill exists in registry (not first publish)
            existing_skills = [s["skill_id"] for s in repo.list_skills()]

            if skill_id in existing_skills:
                # Verify integrity before allowing publish
                tamper_result = repo.detect_tampering(skill_id)

                if tamper_result["tampering_detected"]:
                    integrity_tampering = True
                    integrity_ruling = tamper_result["ruling"]

                    # Build integrity gate decision
                    integrity_gate = {
                        "node_id": "integrity_verification_gate",
                        "gate": "integrity_verification",
                        "decision": "DENY",
                        "ruling": integrity_ruling,
                        "reason": "Registry/graph integrity verification failed",
                        "timestamp": timestamp,
                        "evidence": tamper_result.get("integrity_result", {}).get("evidence"),
                    }
                    gate_decisions.append(integrity_gate)
                else:
                    # Integrity verified - record new hash for this publish
                    current_hash = repo.compute_registry_hash(skill_id)
                    repo.record_integrity_chain(
                        chain_type="registry",
                        entity_id=skill_id,
                        computed_hash=current_hash,
                        recorded_by="pack_publish",
                        metadata={"audit_id": audit_id, "version": version},
                    )
            else:
                # First publish - record initial integrity hash
                repo.ensure_skill(skill_id, skill_spec.get("title", skill_id))
                current_hash = repo.compute_registry_hash(skill_id)
                repo.record_integrity_chain(
                    chain_type="registry",
                    entity_id=skill_id,
                    computed_hash=current_hash,
                    recorded_by="pack_publish",
                    metadata={"audit_id": audit_id, "version": version, "first_publish": True},
                )
        except Exception as e:
            # If integrity check fails, log but don't block (fail-open for DB issues)
            # This prevents DB connection issues from blocking all publishes
            integrity_gate = {
                "node_id": "integrity_verification_gate",
                "gate": "integrity_verification",
                "decision": "WARN",
                "reason": f"Integrity check skipped due to error: {str(e)}",
                "timestamp": timestamp,
            }
            gate_decisions.append(integrity_gate)
        finally:
            repo.close()

        # ── Hard Gate Blocking: Check for DENY decisions ──
        # Any DENY from constitution_risk_gate OR integrity_verification_gate MUST block publishing
        deny_ruling: dict[str, Any] | None = None
        has_deny = False
        for gate in gate_decisions:
            if gate.get("decision") == "DENY":
                has_deny = True
                deny_ruling = gate.get("ruling")
                break

        # If any gate DENY, force rejection and include ruling in result
        if has_deny:
            success = False

        # ── Build Evidence Chain ──
        evidence_records: list[dict[str, Any]] = []
        evidence_counter = 0
        static_findings_with_evidence: list[dict[str, Any]] = []  # findings with evidence_id

        def _add_evidence(etype: str, source: str, payload: Any, extra: dict[str, Any] | None = None) -> str:
            nonlocal evidence_counter
            evidence_counter += 1
            ref = f"ev-{uuid.uuid4().hex[:8]}"
            payload_str = json.dumps(payload, default=str) if not isinstance(payload, str) else payload
            record: dict[str, Any] = {
                "evidence_id": ref,
                "type": etype,
                "sha256": _sha256(payload_str),
                "source": source,
                "created_at": timestamp,
            }
            if extra:
                record.update(extra)
            evidence_records.append(record)
            return ref

        # 1. Intake provenance evidence
        ev_intake = _add_evidence(
            "intake_provenance",
            "intake_repo",
            intake,
            {"repo_url": intake.get("repo_url", "unknown"), "commit_sha": intake.get("commit_sha", "unknown")},
        )

        # 2. Static analysis findings → evidence (each finding gets its own evidence_id)
        for finding in static_findings_raw:
            eid = _add_evidence(
                "static_analysis_finding",
                "semgrep",
                finding,
                {
                    "rule_id": finding.get("rule_id", "unknown"),
                    "severity": finding.get("severity", "info"),
                    "message": finding.get("message", ""),
                    "location": finding.get("location", {}),
                },
            )
            # Store finding with its evidence_id for policy_matrix
            static_findings_with_evidence.append({
                **finding,
                "evidence_id": eid,
            })

        # 3. Gate decisions evidence
        ev_license = _add_evidence(
            "gate_decision", "license_gate",
            license_gate.get("decision", "N/A"),
            {"gate": "license_gate", "decision": license_gate.get("decision", "N/A")},
        )
        ev_constitution = _add_evidence(
            "gate_decision", "constitution_risk_gate",
            constitution_gate.get("decision", "N/A"),
            {"gate": "constitution_risk_gate", "decision": constitution_gate.get("decision", "N/A")},
        )

        # T2: Add integrity gate evidence if present
        ev_integrity = None
        if integrity_gate:
            ev_integrity = _add_evidence(
                "gate_decision", "integrity_verification_gate",
                integrity_gate.get("decision", "N/A"),
                {
                    "gate": "integrity_verification_gate",
                    "decision": integrity_gate.get("decision", "N/A"),
                    "tampering_detected": integrity_tampering,
                },
            )

        # Legacy scan log evidence (for backward compatibility)
        ev_scan = _add_evidence(
            "scan_log", "repo_scan_fit_score",
            repo_scan.get("scan_result", {}),
        )
        ev_test = _add_evidence(
            "runtime_event", "sandbox_test_and_trace",
            test_report,
        )

        # ── 1. original_repo_snapshot.json ──
        # Resolve commit_sha: prefer intake_repo output, then input, then version fallback
        pipeline_input = input_data.get("input", {})
        commit_sha = (
            intake.get("commit_sha")
            or pipeline_input.get("commit_sha")
            or intake.get("version", "unknown")
        )
        original_repo_snapshot = {
            "source": intake.get("source", "github"),
            "id": intake.get("repo_url", "https://github.com/unknown/repo"),
            "commit_sha": commit_sha,
            "version": commit_sha,
            "fetched_at": intake.get("fetched_at", timestamp),
            "license_hint": license_gate.get("license_spdx",
                             license_gate.get("license", "unknown")),
            "snapshot_hash": intake.get("snapshot_hash",
                             _sha256(json.dumps(intake, default=str))),
        }

        # ── 2. static_analysis.log (use real semgrep output) ──
        if static_raw_output:
            static_analysis_log = static_raw_output
        else:
            # Fallback to repo_scan raw_log or generate from findings
            static_analysis_log = repo_scan.get("raw_log", "")
            if not static_analysis_log:
                scan_findings = repo_scan.get("findings", [])
                static_analysis_log = "\n".join(
                    f"[{f.get('severity', 'INFO')}] {f.get('message', 'no message')}"
                    for f in scan_findings
                ) if scan_findings else "[INFO] Static analysis complete. No findings."

        # ── 3. policy_matrix.json ──
        findings: list[dict[str, Any]] = []

        # Add static analysis findings with real evidence_ref
        for finding in static_findings_with_evidence:
            issue_key = self._map_to_issue_key(finding.get("rule_id", ""))
            findings.append({
                "rule_id": finding.get("rule_id", "POL-SCAN-GENERIC"),
                "description": finding.get("message", "static analysis finding"),
                "result": "fail" if finding.get("severity") in ("error", "ERROR", "critical", "CRITICAL") else "warn",
                "issue_key": issue_key,
                "evidence_ref": finding["evidence_id"],  # Points to real evidence
                "severity": finding.get("severity", "info"),
                "location": finding.get("location", {}),
                "rule_version": _get_issue_added_in(issue_catalog, issue_key),
            })

        # Add gate decision findings
        for decision in gate_decisions:
            d = decision.get("decision", "")
            node = decision.get("node_id", decision.get("gate", "unknown"))
            # Select appropriate evidence reference
            if "integrity" in str(node):
                evidence_ref = ev_integrity or ev_constitution
            elif "license" in str(node):
                evidence_ref = ev_license
            else:
                evidence_ref = ev_constitution
            gate_issue_key = f"GATE_{node.upper().replace('_', '-')}_CHECK"
            findings.append({
                "rule_id": f"POL-{node.upper().replace('_', '-')}",
                "description": f"Gate decision from {node}",
                "result": "pass" if d in ("ALLOW", "APPROVED", "allow") else "fail",
                "issue_key": gate_issue_key,
                "evidence_ref": evidence_ref,
                "rule_version": _get_issue_added_in(issue_catalog, gate_issue_key),
            })

        # Add scan findings
        for f in repo_scan.get("findings", []):
            scan_issue_key = f.get("issue_key", "SCAN_FINDING")
            findings.append({
                "rule_id": f.get("rule_id", "POL-SCAN-GENERIC"),
                "description": f.get("message", "scan finding"),
                "result": "fail" if f.get("severity") in ("error", "BLOCKER") else "warn",
                "issue_key": scan_issue_key,
                "evidence_ref": ev_scan,
                "rule_version": _get_issue_added_in(issue_catalog, scan_issue_key),
            })

        policy_matrix = {
            "schema_version": "1.0.0",
            "audit_id": audit_id,
            "skill_id": skill_id,
            "quality_level": "L3",
            "findings": findings,
            "required_changes": [],
            "generated_at": timestamp,
        }

        # ── 4. repro_env.yml (as dict — YAML-serializable) ──
        repro_env = {
            "python_version": "3.11",
            "timeout_s": 120,
            "max_concurrency": 4,
            "max_runs": 100,
            "isolation": "container",
            "network_policy": "deny-by-default",
            "source_mount": "read-only",
            "tools": ["semgrep", "pytest"],
            "generated_at": timestamp,
        }

        # ── 5. source_lineage.diff ──
        source_lineage_diff = scaffold.get("diff", "")
        if not source_lineage_diff:
            source_lineage_diff = "# No modifications made to original source."

        # ── 6. evidence.jsonl (list of dicts, one per line) ──
        # evidence_records already built above

        # ── 7. manifest.json ──
        pack_files = {
            "manifest.json": None,  # placeholder, will be filled
            "policy_matrix.json": json.dumps(policy_matrix, default=str),
            "static_analysis.log": static_analysis_log,
            "original_repo_snapshot.json": json.dumps(original_repo_snapshot, default=str),
            "repro_env.yml": json.dumps(repro_env, default=str),
            "evidence.jsonl": "\n".join(json.dumps(e, default=str) for e in evidence_records),
            "source_lineage.diff": source_lineage_diff,
        }

        file_entries = []
        for filename, content in pack_files.items():
            if filename == "manifest.json":
                continue  # skip self
            file_entries.append({
                "file": filename,
                "sha256": _sha256(content),
                "bytes": len(content.encode("utf-8")),
            })

        manifest = {
            "schema_version": "1.0.0",
            "audit_id": audit_id,
            "skill_id": skill_id,
            "pack_version": version,
            "quality_level": "L3",
            "build_time": timestamp,
            "provenance": {
                **original_repo_snapshot,
                "constitution_ref": constitution_ref,
                "constitution_hash": constitution_hash,
                "issue_catalog_version": catalog_version,
            },
            "files": file_entries,
        }
        pack_files["manifest.json"] = json.dumps(manifest, default=str)

        # ── Build final output ──
        audit_pack_path = f"/tmp/skillforge/audit/{audit_id}"

        audit_pack: dict[str, Any] = {
            "audit_id": audit_id,
            "skill_id": skill_id,
            "version": version,
            "quality_level": "L3",
            "gate_decisions": gate_decisions,
            "test_report": test_report,
            "trace_summary": {
                "total_events": len(trace_events),
                "node_id": self.node_id,
            },
            "created_at": timestamp,
            "files": {
                "manifest": manifest,
                "policy_matrix": policy_matrix,
                "original_repo_snapshot": original_repo_snapshot,
                "repro_env": repro_env,
                "evidence": evidence_records,  # Full evidence list for testing
                "evidence_count": len(evidence_records),
                "static_analysis_lines": static_analysis_log.count("\n") + 1,
                "source_lineage_present": bool(source_lineage_diff.strip()
                                               and not source_lineage_diff.startswith("#")),
            },
        }

        publish_status = "published" if success else "rejected"

        # Constitution missing forces rejection per §1.1 of architecture constraints
        if constitution_ref == "MISSING":
            publish_status = "rejected"

        # Hard gate blocking: DENY from gate forces rejection
        if has_deny:
            publish_status = "rejected"

        publish_result: dict[str, Any] = {
            "skill_id": skill_id,
            "version": version,
            "status": publish_status,
            "registry_url": f"http://localhost:8080/skills/{skill_id}/{version}",
            "timestamp": timestamp,
        }

        # Include ruling reference if blocked by gate
        if has_deny and deny_ruling:
            publish_result["ruling"] = deny_ruling
        elif constitution_ref == "MISSING":
            publish_result["ruling"] = {
                "verdict": "DENY",
                "rule_id": "CONSTITUTION_MISSING",
                "evidence_ref": None,
                "blocked": True,
            }

        # ── T3: Build UpdatedGraph ──
        # Extract delta_info from skill_compose output
        skill_compose_output = input_data.get("skill_compose", {})
        delta_info = skill_compose_output.get("delta_info", {}) if isinstance(skill_compose_output, dict) else {}

        is_incremental = delta_info.get("is_incremental", False)
        change_type = delta_info.get("change_type", "new")
        parent_skill = delta_info.get("parent_skill")

        # Build graph update information
        graph_nodes_added: list[str] = []
        graph_nodes_modified: list[str] = []
        graph_edges_added: list[dict[str, str]] = []

        if change_type == "new":
            graph_nodes_added = [skill_id]
        elif change_type == "update":
            graph_nodes_modified = [skill_id]
        elif change_type == "subskill" and parent_skill:
            graph_nodes_added = [skill_id]
            graph_edges_added = [{"from": parent_skill, "to": skill_id, "type": "derives"}]

        # Compute graph hash for integrity
        graph_content = json.dumps({
            "skill_id": skill_id,
            "version": version,
            "nodes_added": graph_nodes_added,
            "nodes_modified": graph_nodes_modified,
            "edges_added": graph_edges_added,
        }, sort_keys=True, default=str)
        graph_hash = _sha256(graph_content)

        updated_graph: dict[str, Any] = {
            "skill_id": skill_id,
            "version": version,
            "nodes_added": graph_nodes_added,
            "nodes_modified": graph_nodes_modified,
            "edges_added": graph_edges_added,
            "parent_ref": parent_skill,
            "graph_hash": graph_hash,
            "is_incremental": is_incremental,
            "change_type": change_type,
        }

        # ── T3: Build ReleaseManifest with rollback ──
        # Determine previous version for rollback
        previous_version = None
        rollback_supported = False

        if is_incremental and delta_info.get("base_version"):
            previous_version = delta_info["base_version"]
            rollback_supported = True

        # Build artifact list
        artifact_list = [
            "manifest.json",
            "policy_matrix.json",
            "static_analysis.log",
            "original_repo_snapshot.json",
            "repro_env.yml",
            "evidence.jsonl",
            "source_lineage.diff",
        ]

        release_manifest: dict[str, Any] = {
            "release_id": audit_id,
            "skill_id": skill_id,
            "version": version,
            "previous_version": previous_version,
            "change_type": change_type,
            "rollback": {
                "supported": rollback_supported,
                "rollback_version": previous_version,
                "rollback_path": f"/skills/{skill_id}/{previous_version}" if previous_version else None,
            },
            "artifacts": artifact_list,
            "published_at": timestamp,
            "publish_status": publish_status,
            "audit_pack_path": audit_pack_path,
        }

        # Add delta summary if incremental
        if is_incremental:
            release_manifest["delta_summary"] = {
                "base_version": delta_info.get("base_version"),
                "version_bump": delta_info.get("version_bump"),
                "changes_description": f"Updated from {delta_info.get('base_version')} to {version}",
            }

        return {
            "schema_version": "1.0.0",
            "audit_pack": audit_pack,
            "audit_pack_path": audit_pack_path,
            "publish_result": publish_result,
            "updated_graph": updated_graph,
            "release_manifest": release_manifest,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate publish output per Protocol v1 and T3 requirements."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "audit_pack", "publish_result"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # T3: updated_graph and release_manifest are required
        if "updated_graph" not in output_data:
            errors.append("SCHEMA_INVALID: updated_graph is required (T3)")
        if "release_manifest" not in output_data:
            errors.append("SCHEMA_INVALID: release_manifest is required (T3)")

        audit_pack = output_data.get("audit_pack")
        if isinstance(audit_pack, dict):
            for field in ("audit_id", "skill_id", "version", "quality_level"):
                if field not in audit_pack:
                    errors.append(f"SCHEMA_INVALID: audit_pack.{field} is required")

            # Validate L3 files metadata present
            files = audit_pack.get("files")
            if isinstance(files, dict):
                if "manifest" not in files:
                    errors.append("SF_PACK_AUDIT_FAILED: manifest missing from audit_pack.files")
                if "policy_matrix" not in files:
                    errors.append("SF_PACK_AUDIT_FAILED: policy_matrix missing from audit_pack.files")
            elif files is not None:
                errors.append("SCHEMA_INVALID: audit_pack.files must be a dict")

        elif audit_pack is not None:
            errors.append("SCHEMA_INVALID: audit_pack must be a dict")

        publish_result = output_data.get("publish_result")
        if isinstance(publish_result, dict):
            status = publish_result.get("status")
            if status is not None and status not in ("published", "rejected"):
                errors.append(
                    f"SCHEMA_INVALID: publish_result.status must be 'published' or 'rejected', got '{status}'"
                )
        elif publish_result is not None:
            errors.append("SCHEMA_INVALID: publish_result must be a dict")

        # T3: Validate updated_graph structure
        updated_graph = output_data.get("updated_graph")
        if isinstance(updated_graph, dict):
            required_graph_fields = ["skill_id", "version", "graph_hash"]
            for field in required_graph_fields:
                if field not in updated_graph:
                    errors.append(f"SCHEMA_INVALID: updated_graph.{field} is required (T3)")

            # Validate nodes_added and nodes_modified are lists
            nodes_added = updated_graph.get("nodes_added")
            if nodes_added is not None and not isinstance(nodes_added, list):
                errors.append("SCHEMA_INVALID: updated_graph.nodes_added must be a list")

            nodes_modified = updated_graph.get("nodes_modified")
            if nodes_modified is not None and not isinstance(nodes_modified, list):
                errors.append("SCHEMA_INVALID: updated_graph.nodes_modified must be a list")

            # Validate change_type
            change_type = updated_graph.get("change_type")
            valid_change_types = {"new", "update", "subskill"}
            if change_type is not None and change_type not in valid_change_types:
                errors.append(f"SCHEMA_INVALID: updated_graph.change_type must be one of {valid_change_types}")
        elif updated_graph is not None:
            errors.append("SCHEMA_INVALID: updated_graph must be a dict")

        # T3: Validate release_manifest structure
        release_manifest = output_data.get("release_manifest")
        if isinstance(release_manifest, dict):
            required_manifest_fields = ["release_id", "skill_id", "version", "change_type", "rollback"]
            for field in required_manifest_fields:
                if field not in release_manifest:
                    errors.append(f"SCHEMA_INVALID: release_manifest.{field} is required (T3)")

            # Validate rollback structure
            rollback = release_manifest.get("rollback")
            if isinstance(rollback, dict):
                if "supported" not in rollback:
                    errors.append("SCHEMA_INVALID: release_manifest.rollback.supported is required (T3)")
            elif rollback is not None:
                errors.append("SCHEMA_INVALID: release_manifest.rollback must be a dict")

            # Validate change_type matches updated_graph
            manifest_change_type = release_manifest.get("change_type")
            if manifest_change_type is not None and manifest_change_type not in valid_change_types:
                errors.append(f"SCHEMA_INVALID: release_manifest.change_type must be one of {valid_change_types}")
        elif release_manifest is not None:
            errors.append("SCHEMA_INVALID: release_manifest must be a dict")

        return errors

    def _map_to_issue_key(self, rule_id: str) -> str:
        """Map a semgrep rule_id to an issue_key from the catalog."""
        # Simple mapping: convert rule_id to uppercase issue_key format
        if not rule_id:
            return "SCAN_FINDING"
        # Example: python.lang.security.audit.dangerous-subprocess-use
        # → PYTHON_LANG_SECURITY_AUDIT_DANGEROUS_SUBPROCESS_USE
        return rule_id.upper().replace(".", "_").replace("-", "_")
