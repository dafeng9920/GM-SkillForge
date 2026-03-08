#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
TASK_RE = re.compile(r"\bT\d+\b")
DECISION_RE = re.compile(r"^(T\d+)\s*=\s*(ALLOW|PASS|DENY|FAIL|REQUIRES_CHANGES)\s*$")


@dataclass
class TaskRow:
    wave: str
    task_id: str
    module: str
    owner: str
    reviewer: str
    compliance: str
    depends_on: str
    output_file: str


@dataclass
class TaskState:
    done: bool
    decision: Optional[str]
    output_path: Path


def parse_dispatch_table(dispatch_text: str) -> List[TaskRow]:
    rows: List[TaskRow] = []
    in_table = False
    for line in dispatch_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if in_table and rows:
                break
            continue
        m = TABLE_ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 8:
            continue
        header_like = cells[0].lower() == "wave" or cells[1].lower() == "task"
        divider_like = all(c.replace("-", "").replace(":", "").strip() == "" for c in cells[:8])
        if header_like or divider_like:
            in_table = True
            continue
        in_table = True

        output_file = cells[7].strip("`")
        owner = cells[3]
        owner = owner.split("(", 1)[0].strip()
        rows.append(
            TaskRow(
                wave=cells[0],
                task_id=cells[1],
                module=cells[2],
                owner=owner,
                reviewer=cells[4],
                compliance=cells[5],
                depends_on=cells[6],
                output_file=output_file,
            )
        )
    return rows


def read_decision_from_json(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    value = payload.get("decision")
    if isinstance(value, str):
        return value.strip().upper()
    return None


def build_task_states(rows: List[TaskRow], verification_dir: Path) -> Dict[str, TaskState]:
    states: Dict[str, TaskState] = {}
    for row in rows:
        out = verification_dir / row.output_file
        done = out.exists()
        decision: Optional[str] = None
        if out.suffix.lower() == ".json":
            decision = read_decision_from_json(out)
        states[row.task_id] = TaskState(done=done, decision=decision, output_path=out)
    return states


def parse_dependency_tokens(depends_on: str) -> List[str]:
    dep = depends_on.strip()
    if dep in {"-", ""}:
        return []
    return [d.strip() for d in dep.split(",") if d.strip()]


def dependency_satisfied(token: str, states: Dict[str, TaskState]) -> Tuple[bool, str]:
    m = DECISION_RE.match(token)
    if m:
        dep_task, required = m.group(1), m.group(2)
        st = states.get(dep_task)
        if st is None:
            return False, f"{dep_task} missing"
        if not st.done:
            return False, f"{dep_task} not done"
        if (st.decision or "") != required:
            return False, f"{dep_task} decision={(st.decision or 'UNKNOWN')} != {required}"
        return True, f"{token} satisfied"

    if TASK_RE.fullmatch(token):
        st = states.get(token)
        if st is None:
            return False, f"{token} missing"
        if not st.done:
            return False, f"{token} not done"
        return True, f"{token} done"

    return False, f"unsupported dependency token: {token}"


def find_startable(rows: List[TaskRow], states: Dict[str, TaskState]) -> List[Tuple[TaskRow, List[str]]]:
    startable: List[Tuple[TaskRow, List[str]]] = []
    for row in rows:
        if states[row.task_id].done:
            continue
        reasons: List[str] = []
        ok = True
        for token in parse_dependency_tokens(row.depends_on):
            sat, reason = dependency_satisfied(token, states)
            reasons.append(reason)
            if not sat:
                ok = False
        if ok:
            startable.append((row, reasons))
    return startable


def extract_prompt_sections(prompts_text: str) -> List[Tuple[str, str]]:
    lines = prompts_text.splitlines()
    sections: List[Tuple[str, str]] = []
    current_title: Optional[str] = None
    current: List[str] = []
    for line in lines:
        if line.startswith("## "):
            if current_title is not None:
                sections.append((current_title, "\n".join(current).strip()))
            current_title = line.strip()
            current = [line]
        else:
            if current_title is not None:
                current.append(line)
    if current_title is not None:
        sections.append((current_title, "\n".join(current).strip()))
    return sections


def find_prompt_section(prompts_text: str, owner: str, task_id: str) -> Optional[str]:
    sections = extract_prompt_sections(prompts_text)
    owner_lower = owner.lower()
    task_lower = task_id.lower()

    for title, body in sections:
        if owner_lower in title.lower() and task_lower in title.lower():
            return body
    for title, body in sections:
        if owner_lower in title.lower() and task_lower in body.lower():
            return body
    for title, body in sections:
        if owner_lower in title.lower():
            return body
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Show next dispatchable task from task_dispatch and prompts.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--dispatch", required=True, help="Path to task_dispatch markdown")
    parser.add_argument("--prompts", required=True, help="Path to prompts markdown")
    parser.add_argument("--task", help="Optional task id to inspect, e.g. T90")
    args = parser.parse_args()

    dispatch_path = Path(args.dispatch)
    prompts_path = Path(args.prompts)
    verification_dir = Path("docs") / args.date / "verification"

    if not dispatch_path.exists():
        print(f"[ERROR] dispatch not found: {dispatch_path}")
        return 1
    if not prompts_path.exists():
        print(f"[ERROR] prompts not found: {prompts_path}")
        return 1

    dispatch_text = dispatch_path.read_text(encoding="utf-8")
    prompts_text = prompts_path.read_text(encoding="utf-8")
    rows = parse_dispatch_table(dispatch_text)
    if not rows:
        print("[ERROR] no task rows parsed from dispatch table")
        return 2

    states = build_task_states(rows, verification_dir)
    startable = find_startable(rows, states)

    done_count = sum(1 for row in rows if states[row.task_id].done)
    print(f"[INFO] total={len(rows)} done={done_count} pending={len(rows) - done_count} startable={len(startable)}")

    target: Optional[TaskRow] = None
    reasons: List[str] = []

    if args.task:
        tid = args.task.upper()
        target = next((r for r in rows if r.task_id.upper() == tid), None)
        if target is None:
            print(f"[ERROR] task not found: {tid}")
            return 3
        for token in parse_dependency_tokens(target.depends_on):
            _, reason = dependency_satisfied(token, states)
            reasons.append(reason)
    else:
        if not startable:
            print("[WARN] no startable task right now (check dependencies/decisions)")
            return 0
        target, reasons = startable[0]

    tstate = states[target.task_id]
    print(f"[NEXT] task={target.task_id} owner={target.owner} wave={target.wave}")
    print(f"[NEXT] module={target.module}")
    print(f"[NEXT] depends_on={target.depends_on}")
    print(f"[NEXT] expected_output={tstate.output_path.as_posix()}")
    if reasons:
        print("[NEXT] dependency_check:")
        for r in reasons:
            print(f"  - {r}")

    section = find_prompt_section(prompts_text, target.owner, target.task_id)
    if section:
        print("\n=== FORWARD PROMPT ===")
        print(section)
    else:
        print("\n[WARN] prompt section not found for owner/task")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

