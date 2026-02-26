#!/usr/bin/env python3
"""
L4.2 migration closure check:
1) accept entries in library_intent_mapping_v2.md are fully present in intent_map.yml
2) contract paths in intent_map.yml exist
3) output a non-placeholder E2E markdown report
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
from typing import Dict, List, Set


ROOT = pathlib.Path(__file__).resolve().parents[1]
MAPPING_MD = ROOT / "docs" / "2026-02-17" / "图书馆迁移" / "library_intent_mapping_v2.md"
INTENT_MAP = ROOT / "skillforge" / "src" / "orchestration" / "intent_map.yml"
REPORT_MD = ROOT / "docs" / "2026-02-17" / "图书馆迁移" / "audit_repo_e2e_dry_run_report_v1.md"


def parse_accept_ids_from_markdown(path: pathlib.Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    result: List[str] = []
    for line in lines:
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 10:
            continue
        old_asset_id = cols[1]
        decision = cols[7].lower()
        if old_asset_id and old_asset_id != "旧资产ID" and decision == "accept":
            result.append(old_asset_id)
    return result


def parse_yaml_like_entries(path: pathlib.Path) -> Dict[str, str]:
    """
    Minimal parser for this specific file style:
      - source_asset_id: xxx
        ...
        contract_path: yyy
    """
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*-\s+source_asset_id:\s*", text)
    entries: Dict[str, str] = {}
    for block in blocks[1:]:
        lines = block.splitlines()
        source_id = lines[0].strip()
        contract_path = ""
        for ln in lines:
            m = re.match(r"\s*contract_path:\s*(.+)\s*$", ln)
            if m:
                contract_path = m.group(1).strip().strip("'\"")
                break
        entries[source_id] = contract_path
    return entries


def check_contract_paths(entries: Dict[str, str]) -> List[str]:
    missing: List[str] = []
    for sid, cpath in entries.items():
        if not cpath:
            missing.append(f"{sid} -> <missing contract_path>")
            continue
        target = ROOT / cpath
        # allow docs anchors like foo.md#bar
        anchor_stripped = str(target).split("#", 1)[0]
        if "*" in anchor_stripped:
            parent = pathlib.Path(anchor_stripped).parent
            if not parent.exists():
                missing.append(f"{sid} -> {cpath}")
            continue
        if not pathlib.Path(anchor_stripped).exists():
            missing.append(f"{sid} -> {cpath}")
    return missing


def render_report(
    accept_ids: List[str],
    mapped_entries: Dict[str, str],
    missing_ids: Set[str],
    missing_contracts: List[str],
) -> str:
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    passed = (not missing_ids) and (not missing_contracts)
    status = "PASSED" if passed else "FAILED"

    report = []
    report.append("# audit_repo E2E Dry Run Report v1")
    report.append("")
    report.append(f"> **Status: {status} (EXECUTED)**")
    report.append(f"> - Generated at: {now}")
    report.append("> - Mode: L4.2 migration closure check (contracts/gates/evidence connectivity)")
    report.append("> - This report replaces previous placeholder.")
    report.append("")
    report.append("## 1. Check Summary")
    report.append("")
    report.append(f"- accept entries in mapping v2: `{len(accept_ids)}`")
    report.append(f"- accept entries present in intent_map: `{len(accept_ids) - len(missing_ids)}`")
    report.append(f"- missing accept entries: `{len(missing_ids)}`")
    report.append(f"- missing contract paths: `{len(missing_contracts)}`")
    report.append("")
    report.append("## 2. Assertions")
    report.append("")
    report.append(f"1. `intent_map.yml exists`: {'PASS' if INTENT_MAP.exists() else 'FAIL'}")
    report.append(f"2. `accept coverage = 100%`: {'PASS' if not missing_ids else 'FAIL'}")
    report.append(f"3. `contract paths resolvable`: {'PASS' if not missing_contracts else 'FAIL'}")
    report.append("")

    if missing_ids:
        report.append("## 3. Missing Accept Entries")
        report.append("")
        for sid in sorted(missing_ids):
            report.append(f"- {sid}")
        report.append("")

    if missing_contracts:
        report.append("## 4. Missing Contract Paths")
        report.append("")
        for item in missing_contracts:
            report.append(f"- {item}")
        report.append("")

    report.append("## 5. Evidence")
    report.append("")
    report.append(f"- mapping source: `{MAPPING_MD.as_posix()}`")
    report.append(f"- intent map: `{INTENT_MAP.as_posix()}`")
    report.append(f"- report path: `{REPORT_MD.as_posix()}`")
    report.append("")
    return "\n".join(report) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true", help="write markdown report")
    args = parser.parse_args()

    if not MAPPING_MD.exists():
        print(f"[FAIL] mapping file not found: {MAPPING_MD}")
        return 2
    if not INTENT_MAP.exists():
        print(f"[FAIL] intent map not found: {INTENT_MAP}")
        return 2

    accept_ids = parse_accept_ids_from_markdown(MAPPING_MD)
    mapped_entries = parse_yaml_like_entries(INTENT_MAP)
    mapped_ids = set(mapped_entries.keys())
    missing_ids = set(accept_ids) - mapped_ids
    missing_contracts = check_contract_paths(mapped_entries)

    print(f"[INFO] accept_ids={len(accept_ids)} mapped_entries={len(mapped_entries)}")
    print(f"[INFO] missing_accept={len(missing_ids)} missing_contract_paths={len(missing_contracts)}")

    report = render_report(accept_ids, mapped_entries, missing_ids, missing_contracts)
    if args.write_report:
        REPORT_MD.write_text(report, encoding="utf-8")
        print(f"[WRITE] {REPORT_MD}")

    if missing_ids or missing_contracts:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
