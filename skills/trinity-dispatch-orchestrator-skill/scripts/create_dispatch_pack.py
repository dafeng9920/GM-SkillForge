#!/usr/bin/env python3
import argparse
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise FileExistsError(f"File exists: {path} (use --force to overwrite)")
    path.write_text(content, encoding="utf-8")


def render(template: str, mapping: dict) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{" + key + "}", value)
    return out


def ensure_registry_reference(dispatch_text: str) -> str:
    marker = "configs/dispatch_skill_registry.json"
    if marker in dispatch_text:
        return dispatch_text

    block = (
        "\n## 调度入口（自动注入）\n\n"
        "- 统一 Skill 清单：`docs/templates/dispatch_skill_catalog.md`\n"
        "- 机器可读注册表：`configs/dispatch_skill_registry.json`\n"
    )
    return dispatch_text.rstrip() + "\n" + block


def main() -> int:
    parser = argparse.ArgumentParser(description="Create dispatch/prompts skeleton pack.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--dispatch-path", required=True)
    parser.add_argument("--prompts-path", required=True)
    parser.add_argument("--batch-name", default="BATCH")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    dispatch_tpl = skill_root / "assets" / "templates" / "task_dispatch.template.md"
    prompts_tpl = skill_root / "assets" / "templates" / "prompts.template.md"

    mapping = {
        "DATE": args.date,
        "JOB_ID": args.job_id,
        "TITLE": args.title,
        "DISPATCH_PATH": args.dispatch_path.replace("\\", "/"),
        "BATCH_NAME": args.batch_name,
    }

    dispatch_text = render(read_text(dispatch_tpl), mapping)
    dispatch_text = ensure_registry_reference(dispatch_text)
    prompts_text = render(read_text(prompts_tpl), mapping)

    dispatch_path = Path(args.dispatch_path)
    prompts_path = Path(args.prompts_path)

    write_text(dispatch_path, dispatch_text, args.force)
    write_text(prompts_path, prompts_text, args.force)

    print(f"[create-dispatch-pack] dispatch={dispatch_path}")
    print(f"[create-dispatch-pack] prompts={prompts_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
