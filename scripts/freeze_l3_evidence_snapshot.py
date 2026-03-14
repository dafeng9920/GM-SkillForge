#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_FILES = [
    "A_constitution_hard_gate.json",
    "B_registry_graph_integrity.json",
    "C_incremental_delta_enforced.json",
    "summary.json",
    "summary.md",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze L3 killer-test evidence snapshot with manifest")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"), help="Evidence date folder")
    parser.add_argument(
        "--src",
        default=None,
        help="Source directory (default: reports/l3_gap_closure/{date})",
    )
    parser.add_argument(
        "--dst",
        default=None,
        help="Destination directory (default: docs/{date}/verification/evidence_pass_snapshot)",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    src = Path(args.src) if args.src else root / "reports" / "l3_gap_closure" / args.date
    dst = Path(args.dst) if args.dst else root / "docs" / args.date / "verification" / "evidence_pass_snapshot"
    src = src.resolve()
    dst = dst.resolve()
    dst.mkdir(parents=True, exist_ok=True)

    manifest_items = []
    missing = []
    for name in REQUIRED_FILES:
        sp = src / name
        dp = dst / name
        if not sp.exists():
            missing.append(name)
            manifest_items.append(
                {
                    "file": name,
                    "path": str(dp),
                    "missing": True,
                }
            )
            continue

        shutil.copy2(sp, dp)
        stat = dp.stat()
        manifest_items.append(
            {
                "file": name,
                "path": str(dp),
                "sha256": sha256(dp),
                "last_write_time_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "size_bytes": stat.st_size,
                "missing": False,
            }
        )

    payload = {
        "generated_at_utc": utc_now(),
        "source_dir": str(src),
        "snapshot_dir": str(dst),
        "required_files": REQUIRED_FILES,
        "missing_count": len(missing),
        "missing_files": missing,
        "files": manifest_items,
    }
    manifest_path = dst / "MANIFEST.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[freeze] source={src}")
    print(f"[freeze] snapshot={dst}")
    print(f"[freeze] manifest={manifest_path}")
    if missing:
        print(f"[freeze] missing={missing}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
