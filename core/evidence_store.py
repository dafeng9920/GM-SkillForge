#!/usr/bin/env python3
"""
Evidence Store - EvidenceRef Append-Only Storage Entry Point (v0)

Thin wrapper for the audit pack storage implementation.
Provides the single entry point for EvidenceRef append-only operations.

This is the designated module for:
- EvidenceRef writing with hash + locator + tool_revision
- Append-only storage constraints
- AuditPack storage and retrieval

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
Implementation: skillforge/src/storage/audit_pack_store.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add skillforge directory to path
_skillforge_path = Path(__file__).parent.parent / "skillforge"
if str(_skillforge_path) not in sys.path:
    sys.path.insert(0, str(_skillforge_path))

try:
    from skillforge.src.storage.audit_pack_store import (
        AuditPackStore,
        EvidenceRef,
        get_audit_pack_store,
    )
    _IMPLEMENTATION_SOURCE = "skillforge/src/storage/audit_pack_store.py"
except ImportError:
    # Fallback implementation if skillforge is not available
    from dataclasses import dataclass, field

    @dataclass
    class EvidenceRef:
        """Evidence reference in an AuditPack."""
        ref_id: str
        type: str
        source_locator: str
        content_hash: str
        timestamp: str
        tool_revision: Optional[str] = None

        def to_dict(self) -> dict:
            result = {
                "ref_id": self.ref_id,
                "type": self.type,
                "source_locator": self.source_locator,
                "content_hash": self.content_hash,
                "timestamp": self.timestamp,
            }
            if self.tool_revision:
                result["tool_revision"] = self.tool_revision
            return result

    class AuditPackStore:
        """Fallback audit pack store implementation."""
        def __init__(self, storage_path: Optional[Path] = None):
            self.storage_path = storage_path or Path("data/audit_packs")
            self._evidence_refs: list[EvidenceRef] = []

        def store_evidence_ref(self, ref: EvidenceRef) -> bool:
            """Store an evidence reference (append-only)."""
            self._evidence_refs.append(ref)
            return True

        def get_evidence_refs(self) -> list[EvidenceRef]:
            """Get all stored evidence references."""
            return self._evidence_refs.copy()

    _IMPLEMENTATION_SOURCE = "builtin_fallback"

__all__ = [
    "AuditPackStore",
    "EvidenceRef",
    "get_audit_pack_store",
    "IMPLEMENTATION_SOURCE",
]

IMPLEMENTATION_SOURCE = _IMPLEMENTATION_SOURCE

# Re-export classes and functions
AuditPackStore = _impl if "_impl" in dir() else AuditPackStore
EvidenceRef = EvidenceRef
try:
    get_audit_pack_store = _impl.get_audit_pack_store if "_impl" in dir() else lambda: AuditPackStore()
except:
    def get_audit_pack_store() -> AuditPackStore:
        """Get the singleton AuditPackStore instance."""
        return AuditPackStore()


def create_evidence_ref(
    ref_id: str,
    evidence_type: str,
    source_locator: str,
    content: str | dict,
    tool_revision: str | None = None
) -> EvidenceRef:
    """
    Create an EvidenceRef with hash calculation.

    Args:
        ref_id: Unique reference identifier
        evidence_type: Type of evidence (e.g., "static_scan", "test_run")
        source_locator: Location where evidence can be found
        content: Content to hash
        tool_revision: Version of the tool that created this evidence

    Returns:
        EvidenceRef with calculated content_hash
    """
    # Calculate content hash
    if isinstance(content, dict):
        content_str = json.dumps(content, sort_keys=True)
    else:
        content_str = content

    content_hash = "sha256:" + hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    return EvidenceRef(
        ref_id=ref_id,
        type=evidence_type,
        source_locator=source_locator,
        content_hash=content_hash,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        tool_revision=tool_revision,
    )


def main() -> int:
    """CLI entry point for evidence store operations."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Evidence store operations (v0)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Store command
    store_parser = subparsers.add_parser("store", help="Store an evidence reference")
    store_parser.add_argument("--ref-id", required=True, help="Reference ID")
    store_parser.add_argument("--type", required=True, help="Evidence type")
    store_parser.add_argument("--locator", required=True, help="Source locator")
    store_parser.add_argument("--content", required=True, help="Content to hash (JSON string or file path)")
    store_parser.add_argument("--tool-revision", help="Tool revision")
    store_parser.add_argument("--from-file", action="store_true", help="Read content from file")

    # List command
    list_parser = subparsers.add_parser("list", help="List all evidence references")

    args = parser.parse_args()

    store = get_audit_pack_store()

    if args.command == "store":
        # Load content
        if args.from_file:
            try:
                content = json.loads(Path(args.content).read_text(encoding="utf-8"))
            except Exception as e:
                print(f"ERROR: Failed to load content: {e}", file=sys.stderr)
                return 1
        else:
            try:
                content = json.loads(args.content)
            except json.JSONDecodeError:
                content = args.content

        # Create and store evidence ref
        ref = create_evidence_ref(
            ref_id=args.ref_id,
            evidence_type=args.type,
            source_locator=args.locator,
            content=content,
            tool_revision=args.tool_revision,
        )

        if hasattr(store, "store_evidence_ref"):
            success = store.store_evidence_ref(ref)
        else:
            # Fallback: just add to internal list
            if not hasattr(store, "_evidence_refs"):
                store._evidence_refs = []
            store._evidence_refs.append(ref)
            success = True

        if success:
            print(f"OK: Stored evidence reference {args.ref_id}")
            print(f"  hash: {ref.content_hash}")
        else:
            print(f"ERROR: Failed to store evidence reference", file=sys.stderr)
            return 1

    elif args.command == "list":
        if hasattr(store, "get_evidence_refs"):
            refs = store.get_evidence_refs()
        elif hasattr(store, "_evidence_refs"):
            refs = store._evidence_refs
        else:
            refs = []

        print(f"Total evidence references: {len(refs)}")
        for ref in refs:
            print(f"  [{ref.ref_id}] {ref.type} @ {ref.source_locator}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
