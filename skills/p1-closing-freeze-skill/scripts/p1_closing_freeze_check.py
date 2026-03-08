#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate P1 closing freeze pack.")
    parser.add_argument(
        "--verify-dir",
        default="docs/2026-02-22/verification",
        help="Verification directory containing freeze artifacts",
    )
    parser.add_argument(
        "--require-allow",
        action="store_true",
        help="Require final_gate_decision_p1 decision == ALLOW",
    )
    parser.add_argument(
        "--require-hash-filled",
        action="store_true",
        help="Require all artifact sha256 fields are filled",
    )
    parser.add_argument(
        "--output-mode",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    return parser.parse_args()


def validate(verify_dir: Path, require_allow: bool, require_hash_filled: bool) -> dict:
    required_changes: list[str] = []
    evidence_refs: list[str] = []

    freeze_md = verify_dir / "P1_CLOSING_FREEZE.md"
    pack_json = verify_dir / "closing_pack_index.json"
    final_json = verify_dir / "final_gate_decision_p1.json"

    for p in [freeze_md, pack_json, final_json]:
        if not p.exists():
            required_changes.append(f"Missing file: {p}")
        else:
            evidence_refs.append(str(p))

    if required_changes:
        return {
            "decision": "REQUIRES_CHANGES",
            "required_changes": required_changes,
            "evidence_refs": evidence_refs,
        }

    try:
        pack = json.loads(pack_json.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "decision": "REQUIRES_CHANGES",
            "required_changes": [f"Invalid JSON: {pack_json} ({exc.__class__.__name__})"],
            "evidence_refs": evidence_refs,
        }

    try:
        final_decision = json.loads(final_json.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "decision": "REQUIRES_CHANGES",
            "required_changes": [f"Invalid JSON: {final_json} ({exc.__class__.__name__})"],
            "evidence_refs": evidence_refs,
        }

    approval = pack.get("approval", {})
    for field in ["reviewer", "compliance_officer", "approved_at", "note"]:
        value = approval.get(field)
        if not isinstance(value, str) or not value.strip() or value.startswith("[TO_FILL"):
            required_changes.append(f"approval.{field} is missing or placeholder")

    integrity = pack.get("integrity_checks", {})
    for field in [
        "all_required_files_present",
        "all_hashes_filled",
        "gate_allow_confirmed",
        "compliance_pass_confirmed",
    ]:
        if integrity.get(field) is not True:
            required_changes.append(f"integrity_checks.{field} is not true")

    artifacts = pack.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        required_changes.append("artifacts list is missing or empty")
    else:
        for item in artifacts:
            path = item.get("path", "UNKNOWN_PATH")
            sha = item.get("sha256", "")
            if item.get("required") is True and not Path(path).exists():
                required_changes.append(f"required artifact missing: {path}")
            if require_hash_filled:
                if not isinstance(sha, str) or not sha.strip() or sha.startswith("[TO_FILL"):
                    required_changes.append(f"artifact sha256 missing: {path}")

    if require_allow and final_decision.get("decision") != "ALLOW":
        required_changes.append("final_gate_decision_p1 decision is not ALLOW")

    return {
        "decision": "ALLOW" if not required_changes else "REQUIRES_CHANGES",
        "required_changes": required_changes,
        "evidence_refs": evidence_refs,
    }


def main() -> int:
    args = parse_args()
    result = validate(
        verify_dir=Path(args.verify_dir),
        require_allow=args.require_allow,
        require_hash_filled=args.require_hash_filled,
    )

    if args.output_mode == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[p1-freeze-check] decision={result['decision']}")
        print(f"[p1-freeze-check] required_changes={len(result['required_changes'])}")
        for item in result["required_changes"]:
            print(f"- {item}")
        for ev in result["evidence_refs"]:
            print(f"[evidence] {ev}")

    return 0 if result["decision"] == "ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())

