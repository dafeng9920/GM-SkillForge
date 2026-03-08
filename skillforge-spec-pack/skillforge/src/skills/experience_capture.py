"""
ExperienceCapture — captures audit/fix/test experiences into evolution.json.

Implements the 3D RAG contract for experience capture with fail-closed rules.

Input Contract (Experience Capture Request)
-------------------------------------------
{
    "at_time_ref": {
        "uri": str,           # URI format, required
        "commit_sha": str,    # 40-char hex, required
        "at_time": str,       # ISO-8601, required
        "tombstone": bool     # required
    },
    "entries": [
        {
            "issue_key": str,       # pattern: ^[A-Z]+\.[A-Z0-9-]+$
            "evidence_ref": str,    # evidence path/URI
            "source_stage": str,    # enum: audit, fix, test
            "summary": str,         # 10-500 chars
            "action": str,          # 10-1000 chars
            "revision": str,        # pattern: ^rev-[0-9a-f]{8}$
            "created_at": str,      # ISO-8601
            "content_hash": str     # pattern: ^sha256:[0-9a-f]{64}$
        }
    ],
    "overwrite_protection": bool   # default true
}

Output Contract (Experience Capture Response)
---------------------------------------------
{
    "status": "PASSED" | "REJECTED",
    "entries_written": int,
    "entries_skipped": int,
    "evolution_ref": str,
    "audit_pack_ref": str | null,
    "rejection_reasons": [str]
}

Fail-Closed Rules
-----------------
AtTimeReference (FC-ATR-1 to FC-ATR-5):
  FC-ATR-1: uri invalid -> REJECTED
  FC-ATR-2: commit_sha not 40-char hex -> REJECTED
  FC-ATR-3: at_time not ISO-8601 -> REJECTED
  FC-ATR-4: tombstone field missing -> REJECTED
  FC-ATR-5: tombstone=true used in production -> REJECTED

ExperienceEntry (FC-EXP-1 to FC-EXP-6):
  FC-EXP-1: issue_key missing or invalid format -> REJECTED
  FC-EXP-2: evidence_ref missing or invalid -> REJECTED
  FC-EXP-3: source_stage not in enum -> REJECTED
  FC-EXP-4: revision mismatch -> REJECTED
  FC-EXP-5: content_hash verification failed -> REJECTED
  FC-EXP-6: summary/action length exceeded -> REJECTED

evolution.json (FC-EVO-1 to FC-EVO-4):
  FC-EVO-1: overwrite detected -> REJECTED
  FC-EVO-2: deduplication failed -> REJECTED
  FC-EVO-3: AuditPack固化 failed -> REJECTED (deferred for MVP)
  FC-EVO-4: required fields missing -> REJECTED

Closed-Loop (FC-LOOP-1 to FC-LOOP-3):
  FC-LOOP-1: AtTimeReference not traceable -> REJECTED
  FC-LOOP-2: EvidenceRef chain broken -> REJECTED
  FC-LOOP-3: feedback data validation failed -> REJECTED
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Valid source stages
SOURCE_STAGES = {"audit", "fix", "test"}

# Issue key pattern: e.g., GATE.FC-2, RISK.L5, SCAN.DEP-1
ISSUE_KEY_PATTERN = re.compile(r"^[A-Z]+\.[A-Z0-9-]+$")

# Revision pattern: rev-a1b2c3d4
REVISION_PATTERN = re.compile(r"^rev-[0-9a-f]{8}$")

# Content hash pattern: sha256:...
CONTENT_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

# Commit SHA pattern: 40-char hex
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class ExperienceCapture:
    """Capture audit/fix/test experiences into evolution.json."""

    node_id: str = "experience_capture"
    stage: int = 5

    # Evolution storage path (can be overridden for testing)
    evolution_base_path: str = "AuditPack/experience"

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate Experience Capture request against fail-closed rules.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # Validate at_time_ref
        at_time_ref = input_data.get("at_time_ref")
        if at_time_ref is None:
            errors.append("SCHEMA_INVALID: at_time_ref is required")
        else:
            atr_errors = self._validate_at_time_ref(at_time_ref)
            errors.extend(atr_errors)

        # Validate entries
        entries = input_data.get("entries")
        if entries is None:
            errors.append("SCHEMA_INVALID: entries is required")
        elif not isinstance(entries, list):
            errors.append("SCHEMA_INVALID: entries must be an array")
        elif len(entries) < 1:
            errors.append("SCHEMA_INVALID: entries must have at least 1 item")
        else:
            for i, entry in enumerate(entries):
                entry_errors = self._validate_experience_entry(entry, i)
                errors.extend(entry_errors)

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute Experience Capture: write entries to evolution.json.

        Implements:
        - Append-only write (FC-EVO-1)
        - content_hash deduplication (FC-EVO-2)
        - AuditPack reference generation

        Args:
            input_data: Validated input payload.

        Returns:
            Output payload conforming to Experience Capture response schema.
        """
        at_time_ref = input_data.get("at_time_ref", {})
        entries = input_data.get("entries", [])
        overwrite_protection = input_data.get("overwrite_protection", True)

        repo_url = at_time_ref.get("uri", "")
        commit_sha = at_time_ref.get("commit_sha", "")

        # Build evolution file path
        evolution_path = self._get_evolution_path(repo_url, commit_sha)

        # Load existing evolution data (or create new)
        evolution_data = self._load_evolution_file(evolution_path)

        # Track existing content hashes for deduplication
        existing_hashes = {
            entry.get("content_hash")
            for entry in evolution_data.get("entries", [])
        }

        entries_written = 0
        entries_skipped = 0
        rejection_reasons = []

        for entry in entries:
            content_hash = entry.get("content_hash", "")

            # FC-EVO-2: Deduplication check
            if content_hash in existing_hashes:
                # Skip duplicate - this is correct behavior
                entries_skipped += 1
                continue

            # FC-EVO-1: Check for overwrite attempts (if protection enabled)
            if overwrite_protection:
                # Verify this is truly a new entry, not an overwrite
                issue_key = entry.get("issue_key", "")
                if self._would_overwrite(evolution_data, issue_key, content_hash):
                    rejection_reasons.append(
                        f"FC-EVO-1: Overwrite detected for issue_key '{issue_key}'"
                    )
                    continue

            # Append entry
            evolution_data["entries"].append(entry)
            existing_hashes.add(content_hash)
            entries_written += 1

        # If any rejections occurred, return REJECTED status
        if rejection_reasons:
            return {
                "status": "REJECTED",
                "entries_written": entries_written,
                "entries_skipped": entries_skipped,
                "evolution_ref": None,
                "audit_pack_ref": None,
                "rejection_reasons": rejection_reasons
            }

        # Update evolution metadata
        evolution_data["revision"] = self._generate_revision(commit_sha)
        evolution_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Save evolution file
        self._save_evolution_file(evolution_path, evolution_data)

        # Build references
        evolution_ref = f"AuditPack/experience/{commit_sha}/evolution.json"
        audit_pack_ref = f"AuditPack/cognition_10d/{commit_sha}/"

        return {
            "status": "PASSED",
            "entries_written": entries_written,
            "entries_skipped": entries_skipped,
            "evolution_ref": evolution_ref,
            "audit_pack_ref": audit_pack_ref,
            "rejection_reasons": []
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """
        Validate output against Experience Capture response schema.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        # Required fields
        required_fields = ["status", "entries_written", "evolution_ref"]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # status validation
        status = output_data.get("status")
        if status not in ("PASSED", "REJECTED"):
            errors.append("SCHEMA_INVALID: status must be 'PASSED' or 'REJECTED'")

        # entries_written validation
        entries_written = output_data.get("entries_written")
        if not isinstance(entries_written, int) or entries_written < 0:
            errors.append("SCHEMA_INVALID: entries_written must be non-negative integer")

        # entries_skipped validation (optional)
        entries_skipped = output_data.get("entries_skipped")
        if entries_skipped is not None:
            if not isinstance(entries_skipped, int) or entries_skipped < 0:
                errors.append("SCHEMA_INVALID: entries_skipped must be non-negative integer")

        # rejection_reasons validation
        rejection_reasons = output_data.get("rejection_reasons")
        if not isinstance(rejection_reasons, list):
            errors.append("SCHEMA_INVALID: rejection_reasons must be an array")

        return errors

    # =========================================================================
    # AtTimeReference Validation (FC-ATR-1 to FC-ATR-5)
    # =========================================================================

    def _validate_at_time_ref(self, atr: Any) -> list[str]:
        """Validate AtTimeReference structure."""
        errors: list[str] = []

        if not isinstance(atr, dict):
            errors.append("SCHEMA_INVALID: at_time_ref must be an object")
            return errors

        # FC-ATR-1: uri invalid
        uri = atr.get("uri")
        if uri is None:
            errors.append("FC-ATR-1: uri is required")
        elif not isinstance(uri, str):
            errors.append("FC-ATR-1: uri must be a string")
        elif not self._is_valid_uri(uri):
            errors.append("FC-ATR-1: uri must be a valid URI")

        # FC-ATR-2: commit_sha not 40-char hex
        commit_sha = atr.get("commit_sha")
        if commit_sha is None:
            errors.append("FC-ATR-2: commit_sha is required")
        elif not isinstance(commit_sha, str):
            errors.append("FC-ATR-2: commit_sha must be a string")
        elif not COMMIT_SHA_PATTERN.match(commit_sha.lower()):
            errors.append("FC-ATR-2: commit_sha must be 40-char hex string")

        # FC-ATR-3: at_time not ISO-8601
        at_time = atr.get("at_time")
        if at_time is None:
            errors.append("FC-ATR-3: at_time is required")
        elif not isinstance(at_time, str):
            errors.append("FC-ATR-3: at_time must be a string")
        elif not self._is_valid_iso8601(at_time):
            errors.append("FC-ATR-3: at_time must be ISO-8601 format")

        # FC-ATR-4: tombstone field missing
        tombstone = atr.get("tombstone")
        if tombstone is None:
            errors.append("FC-ATR-4: tombstone is required")
        elif not isinstance(tombstone, bool):
            errors.append("FC-ATR-4: tombstone must be a boolean")

        # FC-ATR-5: tombstone=true used in production -> REJECTED
        # Tombstoned references cannot be used for new captures
        if isinstance(tombstone, bool) and tombstone is True:
            errors.append("FC-ATR-5: tombstone=true")

        return errors

    # =========================================================================
    # ExperienceEntry Validation (FC-EXP-1 to FC-EXP-6)
    # =========================================================================

    def _validate_experience_entry(self, entry: Any, index: int) -> list[str]:
        """Validate a single ExperienceEntry."""
        errors: list[str] = []

        if not isinstance(entry, dict):
            errors.append(f"FC-EXP-1: entry[{index}] must be an object")
            return errors

        # FC-EXP-1: issue_key missing or invalid format
        issue_key = entry.get("issue_key")
        if issue_key is None:
            errors.append(f"FC-EXP-1: entry[{index}] issue_key is required")
        elif not isinstance(issue_key, str):
            errors.append(f"FC-EXP-1: entry[{index}] issue_key must be a string")
        elif not ISSUE_KEY_PATTERN.match(issue_key):
            errors.append(
                f"FC-EXP-1: entry[{index}] issue_key must match pattern ^[A-Z]+\\.[A-Z0-9-]+$"
            )

        # FC-EXP-2: evidence_ref missing or invalid
        evidence_ref = entry.get("evidence_ref")
        if evidence_ref is None:
            errors.append(f"FC-EXP-2: entry[{index}] evidence_ref is required")
        elif not isinstance(evidence_ref, str):
            errors.append(f"FC-EXP-2: entry[{index}] evidence_ref must be a string")
        elif not evidence_ref.strip():
            errors.append(f"FC-EXP-2: entry[{index}] evidence_ref cannot be empty")

        # FC-EXP-3: source_stage not in enum
        source_stage = entry.get("source_stage")
        if source_stage is None:
            errors.append(f"FC-EXP-3: entry[{index}] source_stage is required")
        elif not isinstance(source_stage, str):
            errors.append(f"FC-EXP-3: entry[{index}] source_stage must be a string")
        elif source_stage not in SOURCE_STAGES:
            errors.append(
                f"FC-EXP-3: entry[{index}] source_stage must be one of {SOURCE_STAGES}"
            )

        # FC-EXP-4: revision format validation
        revision = entry.get("revision")
        if revision is None:
            errors.append(f"FC-EXP-4: entry[{index}] revision is required")
        elif not isinstance(revision, str):
            errors.append(f"FC-EXP-4: entry[{index}] revision must be a string")
        elif not REVISION_PATTERN.match(revision.lower()):
            errors.append(
                f"FC-EXP-4: entry[{index}] revision must match pattern ^rev-[0-9a-f]{{8}}$"
            )

        # FC-EXP-5: content_hash verification
        content_hash = entry.get("content_hash")
        if content_hash is None:
            errors.append(f"FC-EXP-5: entry[{index}] content_hash is required")
        elif not isinstance(content_hash, str):
            errors.append(f"FC-EXP-5: entry[{index}] content_hash must be a string")
        elif not CONTENT_HASH_PATTERN.match(content_hash.lower()):
            errors.append(
                f"FC-EXP-5: entry[{index}] content_hash must match pattern ^sha256:[0-9a-f]{{64}}$"
            )
        else:
            # Verify hash matches content
            computed_hash = self._compute_content_hash(entry)
            if computed_hash.lower() != content_hash.lower():
                errors.append(
                    f"FC-EXP-5: entry[{index}] content_hash verification failed"
                )

        # FC-EXP-6: summary/action length validation
        summary = entry.get("summary")
        if summary is None:
            errors.append(f"FC-EXP-6: entry[{index}] summary is required")
        elif not isinstance(summary, str):
            errors.append(f"FC-EXP-6: entry[{index}] summary must be a string")
        elif len(summary) < 10:
            errors.append(f"FC-EXP-6: entry[{index}] summary must be at least 10 characters")
        elif len(summary) > 500:
            errors.append(f"FC-EXP-6: entry[{index}] summary must be at most 500 characters")

        action = entry.get("action")
        if action is None:
            errors.append(f"FC-EXP-6: entry[{index}] action is required")
        elif not isinstance(action, str):
            errors.append(f"FC-EXP-6: entry[{index}] action must be a string")
        elif len(action) < 10:
            errors.append(f"FC-EXP-6: entry[{index}] action must be at least 10 characters")
        elif len(action) > 1000:
            errors.append(f"FC-EXP-6: entry[{index}] action must be at most 1000 characters")

        # created_at validation
        created_at = entry.get("created_at")
        if created_at is None:
            errors.append(f"SCHEMA_INVALID: entry[{index}] created_at is required")
        elif not isinstance(created_at, str):
            errors.append(f"SCHEMA_INVALID: entry[{index}] created_at must be a string")
        elif not self._is_valid_iso8601(created_at):
            errors.append(f"SCHEMA_INVALID: entry[{index}] created_at must be ISO-8601 format")

        return errors

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _is_valid_uri(self, uri: str) -> bool:
        """Check if string is a valid URI."""
        uri_pattern = r'^[a-zA-Z][a-zA-Z0-9+.-]*://\S+$'
        return bool(re.match(uri_pattern, uri))

    def _is_valid_iso8601(self, dt_str: str) -> bool:
        """Check if string is a valid ISO-8601 datetime."""
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$'
        return bool(re.match(iso_pattern, dt_str))

    def _compute_content_hash(self, entry: dict[str, Any]) -> str:
        """Compute SHA-256 hash of entry content for deduplication."""
        # Hash only the content fields (not metadata like created_at)
        content_fields = ["issue_key", "evidence_ref", "source_stage", "summary", "action"]
        content_str = "|".join(str(entry.get(f, "")) for f in content_fields)
        hash_hex = hashlib.sha256(content_str.encode()).hexdigest()
        return f"sha256:{hash_hex}"

    def _generate_revision(self, commit_sha: str) -> str:
        """Generate revision ID from commit SHA."""
        return f"rev-{commit_sha[:8]}"

    def _get_evolution_path(self, repo_url: str, commit_sha: str) -> Path:
        """Get the path to evolution.json for this repo/commit."""
        # Create path based on commit SHA
        path = Path(self.evolution_base_path) / commit_sha / "evolution.json"
        return path

    def _load_evolution_file(self, path: Path) -> dict[str, Any]:
        """Load existing evolution.json or create new structure."""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass  # Fall through to create new

        # Create new evolution structure
        return {
            "skill_id": "experience_capture",
            "repo_url": "",
            "commit_sha": "",
            "revision": "",
            "entries": [],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    def _save_evolution_file(self, path: Path, data: dict[str, Any]) -> None:
        """Save evolution data to file (append-only semantics enforced)."""
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically via temp file
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic rename
        temp_path.replace(path)

    def _would_overwrite(
        self,
        evolution_data: dict[str, Any],
        issue_key: str,
        content_hash: str
    ) -> bool:
        """
        Check if adding this entry would overwrite an existing entry.

        An overwrite is when:
        - Same issue_key exists with DIFFERENT content_hash
        - This would mean we're trying to modify history
        """
        for entry in evolution_data.get("entries", []):
            if entry.get("issue_key") == issue_key:
                if entry.get("content_hash") != content_hash:
                    return True
        return False


# Convenience function for CLI usage
def main():
    """CLI entry point for Experience Capture."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Capture experiences to evolution.json")
    parser.add_argument("--input-file", help="Input JSON file with capture request")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument(
        "--evolution-path",
        default="AuditPack/experience",
        help="Base path for evolution.json storage"
    )
    args = parser.parse_args()

    capture = ExperienceCapture(evolution_base_path=args.evolution_path)

    # Load input
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        print("Error: --input-file is required", file=sys.stderr)
        sys.exit(1)

    # Validate input
    validation_errors = capture.validate_input(input_data)
    if validation_errors:
        error_result = {
            "status": "REJECTED",
            "entries_written": 0,
            "entries_skipped": 0,
            "evolution_ref": None,
            "audit_pack_ref": None,
            "rejection_reasons": validation_errors
        }
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=2)
        else:
            print(json.dumps(error_result, indent=2))
        sys.exit(1)

    # Execute
    output = capture.execute(input_data)

    # Validate output
    output_errors = capture.validate_output(output)
    if output_errors:
        print(f"WARNING: Output validation errors: {output_errors}", file=sys.stderr)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if output["status"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
