from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

URL_RE = re.compile(r"^https?://|^mailto:|^#")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class SkillRef:
    domain: str
    skill: str
    path: Path


def parse_frontmatter(text: str) -> tuple[bool, dict[str, str]]:
    if not text.startswith("---\n"):
        return False, {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return False, {}
    block = text[4:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip()
    return True, out


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def level_status(score: float, pass_min: float, warn_min: float) -> str:
    if score >= pass_min:
        return "PASS"
    if score >= warn_min:
        return "WARN"
    return "FAIL"


def grade_cost(tokens: int, t: dict[str, int], score_map: dict[str, int]) -> int:
    if tokens <= t["max_pass"]:
        return score_map["pass"]
    if tokens <= t["max_warn"]:
        return score_map["warn"]
    if tokens <= t["max_fail_soft"]:
        return score_map["fail_soft"]
    return score_map["fail_hard"]


def grade_redundancy(repeat_ratio: float, t: dict[str, float], score_map: dict[str, int]) -> int:
    if repeat_ratio <= t["max_pass"]:
        return score_map["pass"]
    if repeat_ratio <= t["max_warn"]:
        return score_map["warn"]
    if repeat_ratio <= t["max_fail_soft"]:
        return score_map["fail_soft"]
    return score_map["fail_hard"]


def grade_safety(text_lower: str, policy: dict[str, Any]) -> tuple[int, bool, bool, int]:
    hints = policy["safety"]
    has_disclaimer = any(k in text_lower for k in hints["disclaimer_hints"])
    has_review = any(k in text_lower for k in hints["review_hints"])
    sensitive_hits = sum(1 for k in hints["sensitive_keywords"] if k in text_lower)

    if sensitive_hits >= hints["sensitive_hits_high"] and not has_disclaimer:
        return hints["score_map"]["high_risk_without_disclaimer"], has_disclaimer, has_review, sensitive_hits
    if has_disclaimer and has_review:
        return hints["score_map"]["full"], has_disclaimer, has_review, sensitive_hits
    if has_disclaimer:
        return hints["score_map"]["disclaimer_only"], has_disclaimer, has_review, sensitive_hits
    if has_review:
        return hints["score_map"]["review_only"], has_disclaimer, has_review, sensitive_hits
    return hints["score_map"]["none"], has_disclaimer, has_review, sensitive_hits


def grade_structure(has_fm: bool, frontmatter: dict[str, str], headings: int, has_h1: bool, policy: dict[str, Any]) -> int:
    req = int(has_fm and ("name" in frontmatter) and ("description" in frontmatter))
    d = policy["structure"]["heading_depth"]
    depth = 1 if headings >= d["pass"] else (0.75 if headings >= d["warn"] else (0.5 if headings >= d["min"] else 0.2))
    h1 = 1 if has_h1 else 0
    w = policy["structure"]["weights"]
    return round((req * w["required_fields"] + depth * w["depth"] + h1 * w["h1"]) * 100)


def grade_evidence_readiness(text: str, broken_links: int, policy: dict[str, Any]) -> tuple[int, int, int, int]:
    checklist = text.count("- [ ]") + text.count("- [x]")
    numbered_steps = len(re.findall(r"(?m)^\d+\.\s", text))
    tables = text.count("|---")

    e = policy["evidence_ready"]
    points = (1 if checklist >= e["min_checklist"] else 0) + (1 if numbered_steps >= e["min_numbered_steps"] else 0) + (1 if tables >= e["min_tables"] else 0)
    score = e["base_score"] + points * e["points_per_signal"]
    if broken_links > 0:
        score -= min(e["max_broken_link_penalty"], broken_links * e["broken_link_penalty_per_item"])
    return max(e["min_score"], min(e["max_score"], score)), checklist, numbered_steps, tables


def count_broken_links(text: str, skill_file: Path, base: Path) -> int:
    broken = 0
    for match in MD_LINK_RE.finditer(text):
        raw = match.group(1).strip()
        target = raw.split()[0].strip("<>")
        if URL_RE.match(target):
            continue
        if target.startswith("/"):
            candidate = (base / target.lstrip("/")).resolve()
        else:
            candidate = (skill_file.parent / target).resolve()
        if not candidate.exists():
            broken += 1
    return broken


def load_policy(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_skills(base: Path, domains: list[str]) -> list[SkillRef]:
    refs: list[SkillRef] = []
    for domain in domains:
        p = base / domain / "skills"
        if not p.exists():
            continue
        for skill_dir in p.iterdir():
            skill_file = skill_dir / "SKILL.md"
            if skill_dir.is_dir() and skill_file.exists():
                refs.append(SkillRef(domain=domain, skill=skill_dir.name, path=skill_file))
    return refs


def pick_top_by_size(refs: list[SkillRef], top_n: int) -> list[SkillRef]:
    pairs = []
    for ref in refs:
        chars = len(ref.path.read_text(encoding="utf-8", errors="ignore"))
        pairs.append((chars, ref))
    pairs.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in pairs[:top_n]]


def audit_skill(base: Path, ref: SkillRef, policy: dict[str, Any], run_id: str) -> dict[str, Any]:
    text = ref.path.read_text(encoding="utf-8", errors="ignore")
    text_lower = text.lower()

    chars = len(text)
    est_tokens = round(chars / policy["token_estimator"]["chars_per_token"])
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    unique_line_count = len(set(lines))
    repeat_ratio = 1 - (unique_line_count / len(lines) if lines else 1)

    has_frontmatter, frontmatter = parse_frontmatter(text)
    headings = len(re.findall(r"(?m)^##+\s", text))
    has_h1 = bool(re.search(r"(?m)^#\s+\S+", text))
    broken_links = count_broken_links(text, ref.path, base)

    l1 = grade_cost(est_tokens, policy["cost"]["thresholds"], policy["cost"]["score_map"])
    l2 = grade_redundancy(repeat_ratio, policy["redundancy"]["thresholds"], policy["redundancy"]["score_map"])
    l3, has_disclaimer, has_review_warning, sensitive_hits = grade_safety(text_lower, policy)
    l4 = grade_structure(has_frontmatter, frontmatter, headings, has_h1, policy)
    l5, checklist_items, numbered_steps, tables = grade_evidence_readiness(text, broken_links, policy)

    layer_scores = {
        "L1_cost": l1,
        "L2_redundancy": l2,
        "L3_safety": l3,
        "L4_structure": l4,
        "L5_evidence_ready": l5,
    }
    pass_min = policy["levels"]["pass_min"]
    warn_min = policy["levels"]["warn_min"]
    layer_status = {k: level_status(v, pass_min=pass_min, warn_min=warn_min) for k, v in layer_scores.items()}
    fail_count = sum(1 for v in layer_status.values() if v == "FAIL")
    warn_count = sum(1 for v in layer_status.values() if v == "WARN")

    w = policy["overall_weights"]
    overall_score = round(
        l1 * w["L1_cost"] + l2 * w["L2_redundancy"] + l3 * w["L3_safety"] + l4 * w["L4_structure"] + l5 * w["L5_evidence_ready"],
        1,
    )

    gate_rules = policy["gate"]
    if layer_status["L3_safety"] == "FAIL" or fail_count >= gate_rules["fail_if_fail_count_gte"]:
        gate = "FAIL"
    elif fail_count >= gate_rules["warn_if_fail_count_gte"] or warn_count >= gate_rules["warn_if_warn_count_gte"]:
        gate = "WARN"
    else:
        gate = "PASS"

    row_evidence_ref = f"EV-L5S-{run_id}-{ref.domain}-{ref.skill}"

    return {
        "domain": ref.domain,
        "skill": ref.skill,
        "path": str(ref.path),
        "source_sha256": sha256_file(ref.path),
        "evidence_ref": row_evidence_ref,
        "chars": chars,
        "est_tokens": est_tokens,
        "repeat_ratio": round(repeat_ratio, 3),
        "broken_links": broken_links,
        "checklist_items": checklist_items,
        "numbered_steps": numbered_steps,
        "tables": tables,
        "sensitive_hits": sensitive_hits,
        "has_disclaimer": has_disclaimer,
        "has_review_warning": has_review_warning,
        "layer_scores": layer_scores,
        "layer_status": layer_status,
        "overall_score": overall_score,
        "gate": gate,
    }


def build_markdown_report(summary: dict[str, Any], results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# GM-SkillForge 5-Layer Audit Report")
    lines.append("")
    lines.append(f"- Date: {summary['run_date']}")
    lines.append(f"- Profile: {summary['profile']}")
    lines.append(f"- Policy version: {summary['policy_version']}")
    lines.append(f"- Scope: {summary['scope']}")
    lines.append(f"- Run ID: `{summary['run_id']}`")
    lines.append(f"- Evidence Ref: `{summary['evidence_ref']}`")
    lines.append(f"- Input Hash: `{summary['input_hash']}`")
    lines.append(f"- Result Hash: `{summary['result_hash']}`")
    lines.append(f"- Sample size: {summary['sample_size']}")
    lines.append(f"- Gate counts: PASS {summary['gate_counts']['PASS']} | WARN {summary['gate_counts']['WARN']} | FAIL {summary['gate_counts']['FAIL']}")
    lines.append(f"- Avg overall score: {summary['avg_overall_score']}")
    lines.append(f"- Avg estimated tokens per skill: {summary['avg_est_tokens']}")
    lines.append("")
    lines.append("## Result Table")
    lines.append("| Skill | Domain | Gate | Score | Est Tokens | Evidence Ref |")
    lines.append("|---|---|---:|---:|---:|---|")
    for row in sorted(results, key=lambda x: (x["gate"], x["overall_score"])):
        lines.append(
            f"| {row['skill']} | {row['domain']} | {row['gate']} | {row['overall_score']} | {row['est_tokens']} | `{row['evidence_ref']}` |"
        )
    lines.append("")
    lines.append("## Conclusion")
    if summary["gate_counts"]["FAIL"] > 0:
        lines.append("- Overall: FAIL (at least one skill failed hard gate).")
    elif summary["gate_counts"]["WARN"] > 0:
        lines.append("- Overall: WARN (no hard fail, but remediation needed).")
    else:
        lines.append("- Overall: PASS (all sampled skills passed gate).")
    lines.append("")
    lines.append("## Limitations")
    lines.append("- Static-only audit; no runtime GPU/memory/latency stress checks.")
    lines.append("- Token count is policy estimator unless tokenizer adapter is enabled.")
    return "\n".join(lines)


def generate_run_id(now: datetime) -> str:
    stamp = now.strftime("%Y%m%d%H%M%SZ")
    suffix = hashlib.sha256(stamp.encode("utf-8")).hexdigest()[:8].upper()
    return f"L5S-{stamp}-{suffix}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run policy-driven 5-layer static audit")
    parser.add_argument("--base", type=Path, default=Path("git-Claude仓库/knowledge-work-plugins"), help="Base path of knowledge-work-plugins repository")
    parser.add_argument("--out", type=Path, default=Path("reports/skill-audit"), help="Output directory for generated reports")
    parser.add_argument("--domains", type=str, default="finance,legal", help="Comma-separated domains to include")
    parser.add_argument("--top-n", type=int, default=10, help="Top N skills by SKILL.md chars in selected domains")
    parser.add_argument("--profile", type=str, default="l5-static", help="Audit profile name")
    parser.add_argument("--policy", type=Path, default=Path("configs/audit_policy_v1.json"), help="Policy JSON path")
    args = parser.parse_args()

    policy = load_policy(args.policy.resolve())
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]

    base = args.base.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    all_refs = discover_skills(base, domains)
    refs = pick_top_by_size(all_refs, top_n=args.top_n)

    now = datetime.now(timezone.utc)
    run_id = generate_run_id(now)
    evidence_ref = f"EV-L5S-{run_id}"

    input_descriptor = {
        "profile": args.profile,
        "policy_version": policy["policy_version"],
        "base": str(base),
        "domains": sorted(domains),
        "top_n": args.top_n,
        "skills": [f"{r.domain}/{r.skill}" for r in refs],
        "skill_source_hashes": {f"{r.domain}/{r.skill}": sha256_file(r.path) for r in refs},
    }
    input_hash = sha256_text(json.dumps(input_descriptor, ensure_ascii=False, sort_keys=True))

    results = [audit_skill(base, ref, policy, run_id=run_id) for ref in refs]
    results.sort(key=lambda x: (x["gate"] != "FAIL", x["overall_score"]))

    summary = {
        "run_date": now.strftime("%Y-%m-%d"),
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "profile": args.profile,
        "policy_version": policy["policy_version"],
        "policy_path": str(args.policy.resolve()),
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

    slug = f"{'_'.join(domains)}_top{args.top_n}_{args.profile}_{summary['run_date']}"
    json_path = out / f"{slug}.json"
    md_path = out / f"{slug}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(summary, results), encoding="utf-8")

    run_dir = out / "runs" / run_id
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

    print(f"[audit] run_id={run_id}")
    print(f"[audit] evidence_ref={evidence_ref}")
    print(f"[audit] policy_version={policy['policy_version']}")
    print(f"[audit] input_hash={input_hash}")
    print(f"[audit] result_hash={result_hash}")
    print(f"[audit] report_json={json_path}")
    print(f"[audit] report_md={md_path}")
    print(f"[audit] run_dir={run_dir}")


if __name__ == "__main__":
    main()
