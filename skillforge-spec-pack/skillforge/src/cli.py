"""
SkillForge CLI — command-line entry point for the Skill production pipeline.

Usage:
    skillforge refine --mode nl "我需要一个SEO审计工具"
    skillforge refine --mode github https://github.com/user/repo
    skillforge refine --mode auto "一个能分析网页SEO的Python工具"
    skillforge snapshot <skill_id> [--at-time ISO]  # temporal snapshot
    skillforge index [--at-time ISO]                 # skill index
    skillforge revisions <skill_id>                  # revision history
    skillforge tombstone <skill_id> --reason "..."   # logical delete
    skillforge health                                # check adapter health
    skillforge version                               # print version

Exit codes:
    0  — success
    1  — pipeline error
    2  — gate denied
    3  — invalid arguments
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from skillforge.src import __version__
from skillforge.src.orchestration.engine import PipelineEngine
from skillforge.src.storage.repository import SkillRepository


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="skillforge",
        description="SkillForge — Skill production pipeline for GM OS",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # -- refine ---------------------------------------------------------------
    refine = subparsers.add_parser("refine", help="Run the Skill production pipeline")
    refine.add_argument(
        "--mode",
        required=True,
        choices=["nl", "github", "auto"],
        help="Pipeline mode",
    )
    refine.add_argument(
        "input",
        nargs="?",
        help="Natural language description or GitHub URL",
    )
    refine.add_argument(
        "--branch",
        default="main",
        help="Git branch (default: main)",
    )
    refine.add_argument(
        "--target-environment",
        default="python",
        choices=["python", "node", "docker"],
    )
    refine.add_argument(
        "--intended-use",
        default="automation",
        choices=["automation", "data", "web", "ops"],
    )
    refine.add_argument(
        "--visibility",
        default="public",
        choices=["public", "private", "team"],
    )
    refine.add_argument(
        "--sandbox-mode",
        default="strict",
        choices=["strict", "moderate", "permissive"],
    )
    refine.add_argument(
        "--output",
        default="-",
        help="Output file (default: stdout)",
    )

    # -- health ---------------------------------------------------------------
    subparsers.add_parser("health", help="Check adapter health")

    # -- snapshot -------------------------------------------------------------
    snap = subparsers.add_parser("snapshot", help="Get skill snapshot at a point in time")
    snap.add_argument("skill_id", help="Skill identifier")
    snap.add_argument("--at-time", default=None, help="ISO-8601 timestamp (default: now)")
    snap.add_argument("--db", default="db/skillforge.sqlite", help="Database path")

    # -- index ----------------------------------------------------------------
    idx = subparsers.add_parser("index", help="List all skills at a point in time")
    idx.add_argument("--at-time", default=None, help="ISO-8601 timestamp (default: now)")
    idx.add_argument("--include-deprecated", action="store_true")
    idx.add_argument("--db", default="db/skillforge.sqlite", help="Database path")

    # -- revisions ------------------------------------------------------------
    rev = subparsers.add_parser("revisions", help="List revisions for a skill")
    rev.add_argument("skill_id", help="Skill identifier")
    rev.add_argument("--include-deprecated", action="store_true")
    rev.add_argument("--db", default="db/skillforge.sqlite", help="Database path")

    # -- tombstone ------------------------------------------------------------
    tomb = subparsers.add_parser("tombstone", help="Tombstone (logical delete) a skill")
    tomb.add_argument("skill_id", help="Skill identifier")
    tomb.add_argument("--reason", required=True, help="Reason for tombstoning")
    tomb.add_argument("--db", default="db/skillforge.sqlite", help="Database path")

    return parser


def _build_pipeline_input(args: argparse.Namespace) -> dict[str, Any]:
    """Transform CLI args into a pipeline input dict."""
    pipeline_input: dict[str, Any] = {
        "mode": args.mode,
        "branch": args.branch,
        "options": {
            "target_environment": args.target_environment,
            "intended_use": args.intended_use,
            "visibility": args.visibility,
            "sandbox_mode": args.sandbox_mode,
        },
    }

    if args.mode == "nl":
        pipeline_input["natural_language"] = args.input
    elif args.mode == "github":
        pipeline_input["repo_url"] = args.input
    elif args.mode == "auto":
        pipeline_input["natural_language"] = args.input

    return pipeline_input


def _create_engine() -> PipelineEngine:
    """Create a PipelineEngine with all 12 node handlers registered."""
    from skillforge.src.nodes.intent_parser import IntentParser
    from skillforge.src.nodes.source_strategy import SourceStrategy
    from skillforge.src.nodes.github_discover import GitHubDiscovery
    from skillforge.src.nodes.skill_composer import SkillComposer
    from skillforge.src.nodes.intake_repo import IntakeRepo
    from skillforge.src.nodes.license_gate import LicenseGate
    from skillforge.src.nodes.repo_scan import RepoScan
    from skillforge.src.nodes.draft_spec import DraftSpec
    from skillforge.src.nodes.constitution_gate import ConstitutionGate
    from skillforge.src.nodes.scaffold_impl import ScaffoldImpl
    from skillforge.src.nodes.sandbox_test import SandboxTest
    from skillforge.src.nodes.pack_publish import PackPublish

    engine = PipelineEngine()
    for handler in [
        IntentParser(),
        SourceStrategy(),
        GitHubDiscovery(),
        SkillComposer(),
        IntakeRepo(),
        LicenseGate(),
        RepoScan(),
        DraftSpec(),
        ConstitutionGate(),
        ScaffoldImpl(),
        SandboxTest(),
        PackPublish(),
    ]:
        engine.register_node(handler)
    return engine


def cmd_refine(args: argparse.Namespace) -> int:
    """Execute the refine command."""
    pipeline_input = _build_pipeline_input(args)
    engine = _create_engine()
    result = engine.run(pipeline_input)

    output_str = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output == "-":
        print(output_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)

    status = result.get("status", "failed")
    if status == "completed":
        return 0
    elif status == "gate_denied":
        return 2
    else:
        return 1


def cmd_health(_args: argparse.Namespace) -> int:
    """Check health of all adapters."""
    from skillforge.src.adapters.github_fetch.adapter import GitHubFetchAdapter
    from skillforge.src.adapters.sandbox_runner.adapter import SandboxRunnerAdapter
    from skillforge.src.adapters.registry_client.adapter import RegistryClientAdapter

    adapters = [GitHubFetchAdapter(), SandboxRunnerAdapter(), RegistryClientAdapter()]
    all_ok = True
    for adapter in adapters:
        ok = adapter.health_check()
        status = "OK" if ok else "FAIL"
        print(f"  {adapter.adapter_id}: {status}")
        if not ok:
            all_ok = False

    return 0 if all_ok else 1


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "refine":
        return cmd_refine(args)
    elif args.command == "health":
        return cmd_health(args)
    elif args.command == "snapshot":
        return cmd_snapshot(args)
    elif args.command == "index":
        return cmd_index(args)
    elif args.command == "revisions":
        return cmd_revisions(args)
    elif args.command == "tombstone":
        return cmd_tombstone(args)
    else:
        parser.print_help()
        return 3


def cmd_snapshot(args: argparse.Namespace) -> int:
    """Get skill snapshot at a point in time."""
    repo = SkillRepository(args.db)
    result = repo.get_snapshot(args.skill_id, args.at_time)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    repo.close()
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    """List all skills at a point in time."""
    repo = SkillRepository(args.db)
    result = repo.get_index(args.at_time, include_deprecated=args.include_deprecated)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    repo.close()
    return 0


def cmd_revisions(args: argparse.Namespace) -> int:
    """List revisions for a skill."""
    repo = SkillRepository(args.db)
    result = repo.get_revisions(args.skill_id, include_deprecated=args.include_deprecated)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    repo.close()
    return 0


def cmd_tombstone(args: argparse.Namespace) -> int:
    """Tombstone a skill."""
    repo = SkillRepository(args.db)
    result = repo.tombstone_skill(args.skill_id, args.reason)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    repo.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
