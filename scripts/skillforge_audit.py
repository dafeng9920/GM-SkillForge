#!/usr/bin/env python3
"""
SkillForge Audit CLI - Unified entry point for running audits.

Usage:
    skillforge audit run --profile l5-static --domains finance,legal --top-n 10 --output-dir reports/skill-audit

This CLI wraps run_skill_5layer_audit.py without modifying it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import subprocess

# Import core functions from the existing audit script.
# Support both execution modes:
# 1) python scripts/skillforge_audit.py ...
# 2) skillforge ... (console script via package import)
try:
    from .run_skill_5layer_audit import (
        discover_skills,
        generate_run_id,
        load_policy,
        pick_top_by_size,
        audit_skill,
        build_markdown_report,
        sha256_text,
        sha256_file,
    )
except ImportError:
    from run_skill_5layer_audit import (
        discover_skills,
        generate_run_id,
        load_policy,
        pick_top_by_size,
        audit_skill,
        build_markdown_report,
        sha256_text,
        sha256_file,
    )

from datetime import datetime, timezone
import json
import hashlib


def compute_policy_hash(policy: dict) -> str:
    """Compute SHA256 hash of policy content (excluding change_log) for traceability."""
    hash_content = dict(policy)
    if "metadata" in hash_content and "change_log" in hash_content["metadata"]:
        metadata_copy = dict(hash_content["metadata"])
        del metadata_copy["change_log"]
        hash_content["metadata"] = metadata_copy
    content = json.dumps(hash_content, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def cmd_audit_run(args: argparse.Namespace) -> int:
    """Execute the audit run command."""
    # Resolve paths
    base_path = args.base.resolve()
    out_dir = args.output_dir.resolve()
    policy_path = args.policy.resolve()

    # Load policy
    policy = load_policy(policy_path)
    policy_hash = compute_policy_hash(policy)

    # Parse domains (no hardcoding)
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]

    if not domains:
        print("[error] No domains specified. Use --domains finance,legal")
        return 1

    # Ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)

    # Discover and select skills
    all_refs = discover_skills(base_path, domains)
    refs = pick_top_by_size(all_refs, top_n=args.top_n)

    if not refs:
        print(f"[warn] No skills found for domains: {domains}")
        # Still produce an empty report to indicate success
        refs = []

    now = datetime.now(timezone.utc)
    run_id = generate_run_id(now)
    evidence_ref = f"EV-L5S-{run_id}"

    # Build input descriptor for hashing
    input_descriptor = {
        "profile": args.profile,
        "policy_version": policy["policy_version"],
        "policy_hash": policy_hash,
        "base": str(base_path),
        "domains": sorted(domains),
        "top_n": args.top_n,
        "skills": [f"{r.domain}/{r.skill}" for r in refs],
        "skill_source_hashes": {f"{r.domain}/{r.skill}": sha256_file(r.path) for r in refs},
    }
    input_hash = sha256_text(json.dumps(input_descriptor, ensure_ascii=False, sort_keys=True))

    # Run audits
    results = [audit_skill(base_path, ref, policy, run_id=run_id) for ref in refs]
    results.sort(key=lambda x: (x["gate"] != "FAIL", x["overall_score"]))

    # Build summary
    summary = {
        "run_date": now.strftime("%Y-%m-%d"),
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "profile": args.profile,
        "policy_version": policy["policy_version"],
        "policy_hash": policy_hash,
        "policy_path": str(policy_path),
        "scope": f"domains={','.join(domains)} top_n={args.top_n} size_rank=chars",
        "run_id": run_id,
        "evidence_ref": evidence_ref,
        "input_hash": input_hash,
        "sample_size": len(results),
        "gate_counts": {
            "PASS": sum(1 for r in results if r["gate"] == "PASS"),
            "WARN": sum(1 for r in results if r["gate"] == "WARN"),
            "FAIL": sum(1 for r in results if r["gate"] == "FAIL"),
        },
        "avg_overall_score": round(sum(r["overall_score"] for r in results) / len(results), 1) if results else 0,
        "avg_est_tokens": round(sum(r["est_tokens"] for r in results) / len(results), 1) if results else 0,
        "high_cost_count_ge_3000_tokens": sum(1 for r in results if r["est_tokens"] >= 3000),
        "high_redundancy_count_ge_0.26": sum(1 for r in results if r["repeat_ratio"] >= 0.26),
    }

    result_hash = sha256_text(json.dumps(results, ensure_ascii=False, sort_keys=True))
    summary["result_hash"] = result_hash

    payload = {"summary": summary, "results": results}

    # Write outputs
    slug = f"{'_'.join(domains)}_top{args.top_n}_{args.profile}_{summary['run_date']}"
    json_path = out_dir / f"{slug}.json"
    md_path = out_dir / f"{slug}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(summary, results), encoding="utf-8")

    # Also write to runs/<run_id>/ for traceability
    run_dir = out_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    run_json = run_dir / "report.json"
    run_md = run_dir / "report.md"
    run_meta = run_dir / "run_meta.json"

    run_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    run_md.write_text(build_markdown_report(summary, results), encoding="utf-8")
    run_meta.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "evidence_ref": evidence_ref,
                "policy_version": policy["policy_version"],
                "policy_hash": policy_hash,
                "profile": args.profile,
                "input_hash": input_hash,
                "result_hash": result_hash,
                "report_json": str(json_path),
                "report_md": str(md_path),
                "run_json": str(run_json),
                "run_md": str(run_md),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # Print summary to stdout
    print(f"[audit] run_id={run_id}")
    print(f"[audit] evidence_ref={evidence_ref}")
    print(f"[audit] profile={args.profile}")
    print(f"[audit] policy_version={policy['policy_version']}")
    print(f"[audit] policy_hash={policy_hash}")
    print(f"[audit] input_hash={input_hash}")
    print(f"[audit] result_hash={result_hash}")
    print(f"[audit] report_json={json_path}")
    print(f"[audit] report_md={md_path}")
    print(f"[audit] run_dir={run_dir}")
    print(f"[audit] gate_counts: PASS={summary['gate_counts']['PASS']} WARN={summary['gate_counts']['WARN']} FAIL={summary['gate_counts']['FAIL']}")

    return 0


def cmd_dispatch_next(args: argparse.Namespace) -> int:
    script = Path(__file__).parent / "dispatch_next.py"
    cmd = [
        sys.executable,
        str(script),
        "--date",
        args.date,
        "--dispatch",
        str(args.dispatch),
        "--prompts",
        str(args.prompts),
    ]
    if args.task:
        cmd.extend(["--task", args.task])
    return subprocess.call(cmd)


def cmd_dispatch_validate(args: argparse.Namespace) -> int:
    script = Path(__file__).parent.parent / "skills" / "trinity-dispatch-orchestrator-skill" / "scripts" / "validate_dispatch_pack.py"
    cmd = [
        sys.executable,
        str(script),
        "--date",
        args.date,
        "--dispatch",
        str(args.dispatch),
        "--prompts",
        str(args.prompts),
        "--dispatch-registry",
        str(args.dispatch_registry),
    ]
    if args.require_existing:
        cmd.append("--require-existing")
    return subprocess.call(cmd)


def cmd_gate_final(args: argparse.Namespace) -> int:
    script = Path(__file__).parent / "gate_final_decision.py"
    cmd = [
        sys.executable,
        str(script),
        "--date",
        args.date,
        "--job-id",
        args.job_id,
    ]
    if args.verification_dir:
        cmd.extend(["--verification-dir", str(args.verification_dir)])
    if args.output:
        cmd.extend(["--output", str(args.output)])
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the skillforge audit CLI."""
    parser = argparse.ArgumentParser(
        prog="skillforge",
        description="SkillForge Audit CLI - Unified entry point for running audits",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # audit subcommand
    audit_parser = subparsers.add_parser("audit", help="Audit operations")
    audit_subparsers = audit_parser.add_subparsers(dest="audit_command", help="Audit subcommands")

    # audit run subcommand
    run_parser = audit_subparsers.add_parser("run", help="Run an audit")
    run_parser.add_argument(
        "--profile",
        type=str,
        default="l5-static",
        help="Audit profile name (default: l5-static)",
    )
    run_parser.add_argument(
        "--domains",
        type=str,
        required=True,
        help="Comma-separated domains to audit (e.g., finance,legal)",
    )
    run_parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Top N skills by SKILL.md chars to audit (default: 10)",
    )
    run_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/skill-audit"),
        help="Output directory for generated reports (default: reports/skill-audit)",
    )
    run_parser.add_argument(
        "--base",
        type=Path,
        default=Path("git-Claude仓库/knowledge-work-plugins"),
        help="Base path of knowledge-work-plugins repository",
    )
    run_parser.add_argument(
        "--policy",
        type=Path,
        default=Path("configs/audit_policy_v1.json"),
        help="Policy JSON path (default: configs/audit_policy_v1.json)",
    )

    # dispatch subcommand
    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch operations")
    dispatch_subparsers = dispatch_parser.add_subparsers(dest="dispatch_command", help="Dispatch subcommands")

    dispatch_next = dispatch_subparsers.add_parser("next", help="Show next startable task and forward prompt")
    dispatch_next.add_argument("--date", required=True)
    dispatch_next.add_argument("--dispatch", type=Path, required=True)
    dispatch_next.add_argument("--prompts", type=Path, required=True)
    dispatch_next.add_argument("--task", type=str, default=None)

    dispatch_validate = dispatch_subparsers.add_parser("validate", help="Validate dispatch/prompts/registry structure")
    dispatch_validate.add_argument("--date", required=True)
    dispatch_validate.add_argument("--dispatch", type=Path, required=True)
    dispatch_validate.add_argument("--prompts", type=Path, required=True)
    dispatch_validate.add_argument("--dispatch-registry", type=Path, default=Path("configs/dispatch_skill_registry.json"))
    dispatch_validate.add_argument("--require-existing", action="store_true")

    # gate subcommand
    gate_parser = subparsers.add_parser("gate", help="Gate operations")
    gate_subparsers = gate_parser.add_subparsers(dest="gate_command", help="Gate subcommands")

    gate_final = gate_subparsers.add_parser("final", help="Compute final gate decision")
    gate_final.add_argument("--date", required=True)
    gate_final.add_argument("--job-id", required=True)
    gate_final.add_argument("--verification-dir", type=Path, default=None)
    gate_final.add_argument("--output", type=Path, default=None)

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "audit" and args.audit_command == "run":
        return cmd_audit_run(args)
    if args.command == "dispatch" and args.dispatch_command == "next":
        return cmd_dispatch_next(args)
    if args.command == "dispatch" and args.dispatch_command == "validate":
        return cmd_dispatch_validate(args)
    if args.command == "gate" and args.gate_command == "final":
        return cmd_gate_final(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
