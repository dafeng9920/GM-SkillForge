#!/usr/bin/env python3
"""
SkillForge 发现链统一运行脚本 (T7)

一条命令跑通 T1-T6 完整发现链。

使用方法:
    python scripts/run_discovery_chain.py \\
        --intent-id AUDIT_REPO_SKILL \\
        --repo-url https://github.com/genesismind-bot/GM-SkillForge \\
        --commit-sha abc123def456 \\
        --skill-dir skillforge/src/skills/quant

输出目录: run/<run_id>/
  - intake_request.json
  - normalized_skill_spec.json
  - validation_report.json
  - rule_scan_report.json
  - pattern_detection_report.json
  - findings.json

@contact: 执行者 Kior-C
@task_id: T7
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent  # scripts 的父目录是项目根目录
sys.path.insert(0, str(project_root))

from skillforge.src.contracts.discovery_pipeline import run_discovery_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="SkillForge 发现链统一运行脚本 (T7)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行完整发现链
  python scripts/run_discovery_chain.py \\
      --intent-id AUDIT_REPO_SKILL \\
      --repo-url https://github.com/genesismind-bot/GM-SkillForge \\
      --commit-sha abc123def456 \\
      --skill-dir skillforge/src/skills/quant

  # 指定输出目录
  python scripts/run_discovery_chain.py \\
      --intent-id AUDIT_REPO_SKILL \\
      --repo-url https://github.com/genesismind-bot/GM-SkillForge \\
      --commit-sha abc123def456 \\
      --skill-dir skillforge/src/skills/quant \\
      --output-dir run/my_audit

  # 指定运行 ID
  python scripts/run_discovery_chain.py \\
      --intent-id AUDIT_REPO_SKILL \\
      --repo-url https://github.com/genesismind-bot/GM-SkillForge \\
      --commit-sha abc123def456 \\
      --skill-dir skillforge/src/skills/quant \\
      --run-id my_custom_run_id
        """
    )

    parser.add_argument(
        "--intent-id",
        required=True,
        choices=["AUDIT_REPO_SKILL", "AUDIT_CONTRACT_COMPLIANCE", "AUDIT_SECURITY_SCAN", "AUDIT_PERFORMANCE_ANALYSIS"],
        help="审计意图 ID (T1 白名单)",
    )
    parser.add_argument(
        "--repo-url",
        required=True,
        help="仓库 URL",
    )
    parser.add_argument(
        "--commit-sha",
        required=True,
        help="提交 SHA (7-40 字符十六进制)",
    )
    parser.add_argument(
        "--skill-dir",
        required=True,
        help="skill 目录路径",
    )
    parser.add_argument(
        "--output-dir",
        default="run",
        help="输出目录 (默认: run/)",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="运行 ID (可选，自动生成)",
    )
    parser.add_argument(
        "--at-time",
        default=None,
        help="审计时间 (ISO-8601，可选)",
    )
    parser.add_argument(
        "--issue-key",
        default=None,
        help="问题单号 (可选)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("SkillForge 发现链 (T1-T6)")
    print("=" * 60)
    print(f"Intent ID: {args.intent_id}")
    print(f"Repo URL: {args.repo_url}")
    print(f"Commit SHA: {args.commit_sha}")
    print(f"Skill Dir: {args.skill_dir}")
    print(f"Output Dir: {args.output_dir}")
    print("=" * 60)
    print()

    # 运行流水线
    result = run_discovery_pipeline(
        intent_id=args.intent_id,
        repo_url=args.repo_url,
        commit_sha=args.commit_sha,
        skill_dir=args.skill_dir,
        output_dir=args.output_dir,
        at_time=args.at_time,
        issue_key=args.issue_key,
    )

    # 输出结果
    print()
    print("=" * 60)
    print("执行结果")
    print("=" * 60)
    print(f"Run ID: {result.run_id}")
    print(f"状态: {result.status}")
    print(f"输出目录: {result.output_dir}")
    print(f"总 Findings: {result.total_findings}")
    print()

    print("步骤详情:")
    for step in result.steps:
        status_icon = "✅" if step.status == "completed" else "❌"
        print(f"  {status_icon} {step.step_name}: {step.status}")
        if step.error:
            print(f"     └─ 错误: {step.error}")
        if step.output_path:
            print(f"     └─ 输出: {Path(step.output_path).relative_to(Path(args.output_dir))}")

    if result.error_summary:
        print()
        print("错误摘要:")
        for error in result.error_summary:
            print(f"  - {error}")

    # 显示 findings 摘要
    findings_path = Path(result.output_dir) / "findings.json"
    if findings_path.exists():
        with open(findings_path, "r", encoding="utf-8") as f:
            findings_data = json.load(f)
        summary = findings_data.get("summary", {})
        by_severity = summary.get("by_severity", {})
        print()
        print("Findings 摘要:")
        print(f"  总计: {summary.get('total_findings', 0)}")
        print(f"  CRITICAL: {by_severity.get('CRITICAL', 0)}")
        print(f"  HIGH: {by_severity.get('HIGH', 0)}")
        print(f"  MEDIUM: {by_severity.get('MEDIUM', 0)}")
        print(f"  LOW: {by_severity.get('LOW', 0)}")

    # 返回状态码
    sys.exit(0 if result.status == "success" else 1)


if __name__ == "__main__":
    main()
