#!/usr/bin/env python3
"""
scan_and_register_skills.py — FIX-007: Scan skills/ directory and register all skills into registry.

Usage:
    python scripts/scan_and_register_skills.py [--dry-run] [--output registry/skills.jsonl]

Behavior:
- Scans all immediate subdirectories of skills/ as skill candidates
- For each skill dir, looks for SKILL.md or manifest.json to extract metadata
- Appends missing skills to registry/skills.jsonl (idempotent: skips already-registered skill_ids)
- Prints a summary table

Exit codes:
    0 = OK (all skills registered or already present)
    1 = Error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"
DEFAULT_REGISTRY = Path(__file__).parent.parent / "registry" / "skills.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stable_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()[:16]


def load_existing_skill_ids(registry_path: Path) -> set[str]:
    """Return set of skill_ids already in registry."""
    ids: set[str] = set()
    if not registry_path.exists():
        return ids
    with open(registry_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                sid = entry.get("skill_id") or entry.get("source", {}).get("skill_id")
                if sid:
                    ids.add(sid)
            except json.JSONDecodeError:
                continue
    return ids


def scan_skill_dir(skill_dir: Path) -> dict | None:
    """
    Extract skill metadata from a skill directory.
    Priority: manifest.json > SKILL.md (name only) > directory name.
    """
    skill_id = skill_dir.name  # default: folder name

    # Try manifest.json
    manifest_file = skill_dir / "manifest.json"
    if manifest_file.exists():
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            skill_id = manifest.get("skill_id", skill_id)
            return {
                "skill_id": skill_id,
                "revision": manifest.get("version", "v0.0.1"),
                "pack_hash": stable_hash(skill_id + manifest.get("version", "v0.0.1")),
                "permit_id": f"PERMIT-SCAN-{skill_id[:8].upper()}",
                "tombstone_state": "ACTIVE",
                "created_at": now_iso(),
                "source": {
                    "kind": "scanned",
                    "locator": str(skill_dir.relative_to(SKILLS_DIR.parent)),
                    "scan_timestamp": now_iso(),
                },
            }
        except (json.JSONDecodeError, OSError):
            pass

    # Try SKILL.md (first line as description)
    skill_md = skill_dir / "SKILL.md"
    description = ""
    if skill_md.exists():
        try:
            lines = skill_md.read_text(encoding="utf-8").splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    description = line[:120]
                    break
        except OSError:
            pass

    return {
        "skill_id": skill_id,
        "revision": "v0.0.1",
        "pack_hash": stable_hash(skill_id + "v0.0.1"),
        "permit_id": f"PERMIT-SCAN-{skill_id[:8].upper()}",
        "tombstone_state": "ACTIVE",
        "created_at": now_iso(),
        "source": {
            "kind": "scanned",
            "locator": str(skill_dir.relative_to(SKILLS_DIR.parent)),
            "description": description,
            "scan_timestamp": now_iso(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan skills/ and register into registry")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written, don't write")
    parser.add_argument("--output", type=Path, default=DEFAULT_REGISTRY, help="Output registry JSONL path")
    args = parser.parse_args()

    if not SKILLS_DIR.exists():
        print(f"[ERROR] skills/ directory not found: {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    print(f"[SCAN] Found {len(skill_dirs)} skill directories in {SKILLS_DIR}")

    existing_ids = load_existing_skill_ids(args.output)
    print(f"[REGISTRY] {len(existing_ids)} skill(s) already registered in {args.output}")

    new_entries: list[dict] = []
    skipped: list[str] = []

    for skill_dir in skill_dirs:
        entry = scan_skill_dir(skill_dir)
        if entry is None:
            continue
        sid = entry["skill_id"]
        if sid in existing_ids:
            skipped.append(sid)
        else:
            new_entries.append(entry)

    print(f"\n{'DRY-RUN ' if args.dry_run else ''}RESULTS:")
    print(f"  New to register : {len(new_entries)}")
    print(f"  Already present : {len(skipped)}")
    print()

    if new_entries:
        if not args.dry_run:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "a", encoding="utf-8") as f:
                for entry in new_entries:
                    f.write(json.dumps(entry, separators=(",", ":"), ensure_ascii=False) + "\n")
            print(f"[OK] Appended {len(new_entries)} skill(s) to {args.output}")
        else:
            print("[DRY-RUN] Would append:")
            for e in new_entries:
                print(f"  + {e['skill_id']}")
    else:
        print("[OK] No new skills to register.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
