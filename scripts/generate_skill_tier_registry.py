#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
AGENTS_SKILLS_DIR = ROOT / ".agents" / "skills"
DISPATCH_REGISTRY = ROOT / "configs" / "dispatch_skill_registry.json"
OUT_REGISTRY = ROOT / "configs" / "skill_tier_registry.json"


@dataclass
class SkillTierItem:
    name: str
    source: str
    path: str
    has_openai_yaml: bool
    tier: str
    enabled_for_mainline: bool
    reason: str


def load_dispatch_names() -> set[str]:
    if not DISPATCH_REGISTRY.exists():
        return set()
    payload = json.loads(DISPATCH_REGISTRY.read_text(encoding="utf-8"))
    names = set()
    for item in payload.get("dispatch_skills", []):
        raw = str(item.get("name", "")).strip()
        if not raw:
            continue
        names.add(raw)
        # normalize agent-style uppercase alias
        if raw.upper() == raw:
            names.add(raw.lower())
    return names


def list_repo_skills() -> list[tuple[str, Path, bool]]:
    items = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue
        openai_yaml = d / "agents" / "openai.yaml"
        items.append((d.name, skill_md, openai_yaml.exists()))
    return items


def list_agent_skills() -> list[tuple[str, Path]]:
    items = []
    if not AGENTS_SKILLS_DIR.exists():
        return items
    for d in sorted(AGENTS_SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if skill_md.exists():
            items.append((d.name, skill_md))
    return items


def classify_repo_skill(name: str, has_openai: bool, dispatch_names: set[str]) -> tuple[str, bool, str]:
    in_dispatch = name in dispatch_names
    if in_dispatch:
        return "core", True, "Referenced by dispatch registry"
    if has_openai:
        return "support", False, "Has openai.yaml but not mapped to mainline dispatch"
    return "experimental", False, "Skeleton or local-only skill without openai.yaml"


def classify_agent_skill(name: str, dispatch_names: set[str]) -> tuple[str, bool, str]:
    in_dispatch = (name in dispatch_names) or (name.upper() in dispatch_names) or (name.lower() in dispatch_names)
    if in_dispatch:
        return "core", True, "Agent skill explicitly referenced by dispatch registry"
    return "support", False, "Agent-level helper not explicitly wired into mainline"


def main() -> int:
    dispatch_names = load_dispatch_names()
    items: list[SkillTierItem] = []

    for name, skill_md, has_openai in list_repo_skills():
        tier, enabled, reason = classify_repo_skill(name, has_openai, dispatch_names)
        items.append(
            SkillTierItem(
                name=name,
                source="repo",
                path=str(skill_md.relative_to(ROOT)).replace("\\", "/"),
                has_openai_yaml=has_openai,
                tier=tier,
                enabled_for_mainline=enabled,
                reason=reason,
            )
        )

    for name, skill_md in list_agent_skills():
        tier, enabled, reason = classify_agent_skill(name, dispatch_names)
        items.append(
            SkillTierItem(
                name=name,
                source="agents",
                path=str(skill_md.relative_to(ROOT)).replace("\\", "/"),
                has_openai_yaml=False,
                tier=tier,
                enabled_for_mainline=enabled,
                reason=reason,
            )
        )

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "total": len(items),
            "core": sum(1 for i in items if i.tier == "core"),
            "support": sum(1 for i in items if i.tier == "support"),
            "experimental": sum(1 for i in items if i.tier == "experimental"),
            "enabled_for_mainline": sum(1 for i in items if i.enabled_for_mainline),
        },
    }

    payload = {
        "version": "2026-02-26.v1",
        "policy": {
            "tiers": ["core", "support", "experimental"],
            "mainline_rule": "Only core skills with enabled_for_mainline=true can be hard-wired in execution path",
            "promotion_gate": "experimental/support -> core requires certification PASS + registry approval",
        },
        "summary": summary,
        "skills": [asdict(i) for i in items],
    }

    OUT_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    OUT_REGISTRY.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Generated: {OUT_REGISTRY}")
    print(f"[OK] total={summary['counts']['total']} core={summary['counts']['core']} support={summary['counts']['support']} experimental={summary['counts']['experimental']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

