#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


TASK_RE = re.compile(r"\bT(\d+)\b")
OUT_RE = re.compile(
    r"`(?P<name>T\d+_(execution_report\.yaml|gate_decision\.json|compliance_attestation\.json)|[A-Za-z0-9_-]*final_gate_decision\.json)`"
)
RISK_KEYWORDS = [
    "delete",
    "file_delete",
    "shell",
    "shell_execution",
    "db",
    "database",
    "network",
    "drop table",
    "truncate",
    "rm ",
    "删除",
    "破坏",
    "数据库",
    "网络",
]


def extract_tasks(text: str) -> set[str]:
    return {f"T{m}" for m in TASK_RE.findall(text)}


def parse_dispatch_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        if cells[0].lower() in {"wave", "---"} or "Task" in cells[1]:
            continue
        rows.append(cells)
    return rows


def validate_owner_mapping(rows: list[list[str]]) -> list[str]:
    errors = []
    for idx, cells in enumerate(rows, start=1):
        task = cells[1]
        owner = cells[3]
        reviewer = cells[4]
        compliance = cells[5]
        if not TASK_RE.search(task):
            continue
        if "<" in owner or ">" in owner or owner == "":
            errors.append(f"row#{idx} {task}: missing named execution owner")
        if "<" in reviewer or ">" in reviewer or reviewer == "":
            errors.append(f"row#{idx} {task}: missing named reviewer")
        if "<" in compliance or ">" in compliance or compliance == "":
            errors.append(f"row#{idx} {task}: missing named compliance owner")
    return errors


def extract_outputs(text: str) -> set[str]:
    return {m.group("name") for m in OUT_RE.finditer(text)}


def detect_high_risk_tasks(rows: list[list[str]]) -> list[str]:
    risky: list[str] = []
    for cells in rows:
        task = cells[1]
        context = " | ".join(cells).lower()
        if any(k in context for k in RISK_KEYWORDS):
            risky.append(task)
    return risky


def has_governance_protocol_declared(*texts: str) -> bool:
    return any("governance_protocol" in t.lower() for t in texts)


def validate_dispatch_registry(registry_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not registry_path.exists():
        return [f"dispatch skill registry not found: {registry_path}"], warnings

    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid dispatch skill registry json: {e}"], warnings

    items = data.get("dispatch_skills", [])
    if not isinstance(items, list) or not items:
        return ["dispatch skill registry has empty dispatch_skills"], warnings

    names = set()
    for i, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"dispatch_skills[{i}] must be object")
            continue
        name = str(item.get("name", "")).strip()
        path = str(item.get("path", "")).strip()
        if not name:
            errors.append(f"dispatch_skills[{i}] missing name")
            continue
        names.add(name)
        if not path:
            errors.append(f"dispatch_skills[{i}] {name}: missing path")
            continue
        p = Path(path)
        if not p.exists():
            errors.append(f"dispatch_skills[{i}] {name}: path not found: {path}")

    if "governance-orchestrator-skill" not in names:
        errors.append("dispatch skill registry missing governance-orchestrator-skill")
    if "trinity-dispatch-orchestrator-skill" not in names:
        warnings.append("dispatch skill registry missing trinity-dispatch-orchestrator-skill (compatibility mode)")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate trinity dispatch pack.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--dispatch", required=True)
    parser.add_argument("--prompts", required=True)
    parser.add_argument(
        "--dispatch-registry",
        default="configs/dispatch_skill_registry.json",
        help="Machine-readable dispatch skill registry path",
    )
    parser.add_argument("--require-existing", action="store_true")
    args = parser.parse_args()

    dispatch = Path(args.dispatch)
    prompts = Path(args.prompts)
    errors: list[str] = []
    warnings: list[str] = []

    if not dispatch.exists():
        errors.append(f"dispatch not found: {dispatch}")
    if not prompts.exists():
        errors.append(f"prompts not found: {prompts}")
    if errors:
        for e in errors:
            print(f"[ERROR] {e}")
        return 1

    dispatch_text = dispatch.read_text(encoding="utf-8")
    prompts_text = prompts.read_text(encoding="utf-8")
    rows = parse_dispatch_rows(dispatch_text)

    if not rows:
        errors.append("no dispatch task rows found (expected markdown table with >=8 columns)")
    else:
        errors.extend(validate_owner_mapping(rows))

    dispatch_tasks = extract_tasks(dispatch_text)
    prompt_tasks = extract_tasks(prompts_text)
    missing_prompt = sorted(dispatch_tasks - prompt_tasks)
    if missing_prompt:
        errors.append(f"tasks missing in prompts: {', '.join(missing_prompt)}")

    outputs = extract_outputs(dispatch_text)
    if not any("final_gate_decision.json" in x for x in outputs):
        errors.append("missing final gate decision output path in dispatch")

    risky_tasks = detect_high_risk_tasks(rows)
    if risky_tasks and not has_governance_protocol_declared(dispatch_text, prompts_text):
        errors.append(
            "high-risk tasks detected but GOVERNANCE_PROTOCOL not declared "
            f"(tasks: {', '.join(sorted(set(risky_tasks)))})"
        )

    reg_errors, reg_warnings = validate_dispatch_registry(Path(args.dispatch_registry))
    errors.extend(reg_errors)
    warnings.extend(reg_warnings)

    expected_prefix = Path("docs") / args.date
    if expected_prefix.as_posix() not in dispatch.as_posix():
        warnings.append(f"dispatch path does not include expected prefix: {expected_prefix}")
    if expected_prefix.as_posix() not in prompts.as_posix():
        warnings.append(f"prompts path does not include expected prefix: {expected_prefix}")

    if args.require_existing:
        ver_dir = Path("docs") / args.date / "verification"
        for out in sorted(outputs):
            p = ver_dir / out
            if "final_gate_decision" in out:
                continue
            if not p.exists():
                errors.append(f"missing verification artifact: {p}")

    for w in warnings:
        print(f"[WARN] {w}")
    if errors:
        for e in errors:
            print(f"[ERROR] {e}")
        return 2

    print("[OK] dispatch/prompts structure valid")
    print(f"[OK] tasks={len(dispatch_tasks)} outputs={len(outputs)}")
    print(f"[OK] dispatch_registry={args.dispatch_registry}")
    if risky_tasks:
        print(f"[OK] high_risk_tasks={len(set(risky_tasks))} governance_protocol=declared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
