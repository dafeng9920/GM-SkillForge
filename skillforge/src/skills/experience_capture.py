"""
Experience Capture v0.

Minimal, auditable "learning seed":
- Append-only `evolution.json` for machine consumption.
- Human-readable `SKILL.md` summary.
- Strong evidence requirement: entries without evidence are marked
  `MISSING_EVIDENCE` and stored in rejected_entries.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


def _now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256(content: str) -> str:
    """Compute SHA-256 hash hex."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class FixKind:
    """Supported fix kinds for experience entries."""

    ADD_CONTRACT = "ADD_CONTRACT"
    ADD_TESTS = "ADD_TESTS"
    UPDATE_SCAFFOLD = "UPDATE_SCAFFOLD"
    APPLY_PATCH = "APPLY_PATCH"
    PUBLISH_PACK = "PUBLISH_PACK"
    GATE_DECISION = "GATE_DECISION"

    ALL = {
        ADD_CONTRACT,
        ADD_TESTS,
        UPDATE_SCAFFOLD,
        APPLY_PATCH,
        PUBLISH_PACK,
        GATE_DECISION,
    }


@dataclass
class ExperienceCaptureV0:
    """Append-only experience sink with light dedup and summary writeback."""

    evolution_path: Path = Path("AuditPack/experience/evolution.json")
    summary_path: Path = Path("AuditPack/experience/SKILL.md")
    tool_revision: str = "experience-capture-v0.1.0"

    def capture(
        self,
        *,
        issue_key: str,
        evidence_ref: Optional[str],
        gate_node: str,
        summary: str,
        fix_kind: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Capture one experience entry.

        Required fields:
        - issue_key
        - evidence_ref
        - gate_node
        - summary
        - fix_kind
        - content_hash (auto-generated)
        """
        metadata = metadata or {}
        captured_at = _now_iso()

        if not issue_key:
            issue_key = f"ISSUE-{int(time.time())}"

        if fix_kind not in FixKind.ALL:
            fix_kind = FixKind.GATE_DECISION

        data = self._load_or_init()

        # Strong evidence-first rule.
        if not evidence_ref:
            rejected = {
                "issue_key": issue_key,
                "gate_node": gate_node,
                "summary": summary,
                "fix_kind": fix_kind,
                "status": "MISSING_EVIDENCE",
                "captured_at": captured_at,
                "metadata": metadata,
            }
            data["rejected_entries"].append(rejected)
            self._save(data)
            self._write_summary(data)
            return {"status": "MISSING_EVIDENCE", "captured": False}

        canonical_payload = {
            "issue_key": issue_key,
            "evidence_ref": evidence_ref,
            "gate_node": gate_node,
            "summary": summary,
            "fix_kind": fix_kind,
            "metadata": metadata,
        }
        canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"))
        content_hash = _sha256(canonical)

        # Deduplicate by content hash (append-only, no mutation).
        existing_hashes = {e.get("content_hash") for e in data["entries"]}
        if content_hash in existing_hashes:
            return {"status": "SKIPPED_DUPLICATE", "captured": False, "content_hash": content_hash}

        entry = {
            "issue_key": issue_key,
            "evidence_ref": evidence_ref,
            "gate_node": gate_node,
            "summary": summary,
            "fix_kind": fix_kind,
            "content_hash": content_hash,
            "captured_at": captured_at,
            "tool_revision": self.tool_revision,
            "metadata": metadata,
        }
        data["entries"].append(entry)
        self._save(data)
        self._write_summary(data)
        return {"status": "CAPTURED", "captured": True, "content_hash": content_hash}

    def _load_or_init(self) -> dict[str, Any]:
        """Load existing evolution data, or initialize if missing."""
        if self.evolution_path.exists():
            with open(self.evolution_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                loaded.setdefault("entries", [])
                loaded.setdefault("rejected_entries", [])
                return loaded
        return {
            "schema_version": "experience-capture-v0",
            "entries": [],
            "rejected_entries": [],
            "created_at": _now_iso(),
        }

    def _save(self, data: dict[str, Any]) -> None:
        """Atomically save evolution data."""
        self.evolution_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.evolution_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(self.evolution_path)

    def _write_summary(self, data: dict[str, Any]) -> None:
        """Write human-readable summary to SKILL.md."""
        self.summary_path.parent.mkdir(parents=True, exist_ok=True)
        total = len(data.get("entries", []))
        missing = len(data.get("rejected_entries", []))

        by_gate: dict[str, int] = {}
        by_fix: dict[str, int] = {}
        for entry in data.get("entries", []):
            gate = entry.get("gate_node", "unknown")
            kind = entry.get("fix_kind", "unknown")
            by_gate[gate] = by_gate.get(gate, 0) + 1
            by_fix[kind] = by_fix.get(kind, 0) + 1

        lines: list[str] = [
            "# Experience Summary",
            "",
            f"- Updated at: {_now_iso()}",
            f"- Captured entries: {total}",
            f"- Missing evidence entries: {missing}",
            "",
            "## By Gate",
        ]
        if by_gate:
            for gate, count in sorted(by_gate.items()):
                lines.append(f"- {gate}: {count}")
        else:
            lines.append("- (no entries)")

        lines.append("")
        lines.append("## By FixKind")
        if by_fix:
            for kind, count in sorted(by_fix.items()):
                lines.append(f"- {kind}: {count}")
        else:
            lines.append("- (no entries)")

        lines.append("")
        lines.append("## Latest Entries")
        latest = data.get("entries", [])[-10:]
        if latest:
            for item in reversed(latest):
                lines.append(
                    f"- [{item.get('captured_at')}] {item.get('gate_node')} "
                    f"{item.get('fix_kind')} :: {item.get('summary')}"
                )
        else:
            lines.append("- (no entries)")

        with open(self.summary_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def retrieve_templates(
        self,
        *,
        issue_key: Optional[str] = None,
        fix_kind: Optional[str] = None,
        gate_node: Optional[str] = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve historical experience templates.

        Filters:
        - issue_key: exact match, prefix with '*' (e.g. 'SCAFFOLD-*'), or startswith fallback
        - fix_kind: one of FixKind values
        - gate_node: exact gate node filter
        """
        data = self._load_or_init()
        entries = list(data.get("entries", []))

        def _issue_key_match(entry_issue_key: str, expected: str) -> bool:
            if expected.endswith("*"):
                return entry_issue_key.startswith(expected[:-1])
            if expected == entry_issue_key:
                return True
            return entry_issue_key.startswith(expected)

        filtered: list[dict[str, Any]] = []
        for entry in entries:
            entry_issue_key = str(entry.get("issue_key", ""))
            entry_fix_kind = str(entry.get("fix_kind", ""))
            entry_gate_node = str(entry.get("gate_node", ""))

            if issue_key and not _issue_key_match(entry_issue_key, issue_key):
                continue
            if fix_kind and entry_fix_kind != fix_kind:
                continue
            if gate_node and entry_gate_node != gate_node:
                continue
            filtered.append(entry)

        # Latest first
        filtered.sort(key=lambda x: str(x.get("captured_at", "")), reverse=True)
        return filtered[: max(1, limit)]


def _extract_evidence_ref(evidence_refs: Any) -> Optional[str]:
    """Extract a usable evidence ref string from GateResult evidence_refs."""
    if not isinstance(evidence_refs, list) or not evidence_refs:
        return None
    first = evidence_refs[0]
    if isinstance(first, dict):
        return first.get("source_locator") or first.get("issue_key")
    return None


def _extract_issue_key(evidence_refs: Any, gate_node: str) -> str:
    """Extract issue key from evidence refs or create fallback."""
    if isinstance(evidence_refs, list) and evidence_refs:
        first = evidence_refs[0]
        if isinstance(first, dict) and first.get("issue_key"):
            return str(first["issue_key"])
    return f"{gate_node.upper()}-{int(time.time())}"


def capture_gate_event(
    *,
    gate_node: str,
    gate_decision: str,
    evidence_refs: Any,
    error_code: Optional[str] = None,
    fix_kind: str = FixKind.GATE_DECISION,
    summary: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """
    Best-effort capture helper for gate modules.

    This helper never raises, so it will not change gate decision behavior.
    """
    if os.getenv("SKILLFORGE_EXPERIENCE_CAPTURE_ENABLED", "1") == "0":
        return

    try:
        evidence_ref = _extract_evidence_ref(evidence_refs)
        issue_key = _extract_issue_key(evidence_refs, gate_node)
        message = summary or f"{gate_node} -> {gate_decision}"
        meta = metadata or {}
        if error_code:
            meta = {**meta, "error_code": error_code}
        ExperienceCaptureV0().capture(
            issue_key=issue_key,
            evidence_ref=evidence_ref,
            gate_node=gate_node,
            summary=message,
            fix_kind=fix_kind,
            metadata={**meta, "gate_decision": gate_decision},
        )
    except Exception:
        # Do not impact primary gate flow.
        return


def retrieve_experience_templates(
    *,
    issue_key: Optional[str] = None,
    fix_kind: Optional[str] = None,
    gate_node: Optional[str] = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Public helper to retrieve templates from evolution.json.

    This helper is intentionally side-effect free and safe for read-before-gate flows.
    """
    try:
        return ExperienceCaptureV0().retrieve_templates(
            issue_key=issue_key,
            fix_kind=fix_kind,
            gate_node=gate_node,
            limit=limit,
        )
    except Exception:
        return []
