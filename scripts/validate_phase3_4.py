"""
Phase 3 执行层 + Phase 4 风控+治理层 联合验证
"""

import asyncio
import sys
from pathlib import Path


async def validate_phases():
    """验证 Phase 3 和 Phase 4"""

    # Phase 3 Skills (4个)
    phase3_skills = [
        ("Order Router", "order-router-skill",
         ["SKILL.md", "__init__.py", "router.py", "requirements.txt"]),
        ("Execution Monitor", "execution-monitor-skill",
         ["SKILL.md", "__init__.py", "monitor.py", "requirements.txt"]),
        ("Compliance Check", "compliance-check-skill",
         ["SKILL.md", "__init__.py", "checker.py", "requirements.txt"]),
        ("Audit Logger", "audit-logger-skill",
         ["SKILL.md", "__init__.py", "logger.py", "requirements.txt"]),
    ]

    # Phase 4 Skills (12个)
    phase4_skills = [
        ("Circuit Breaker", "circuit-breaker-skill",
         ["SKILL.md", "__init__.py", "breaker.py", "requirements.txt"]),
        ("Real-time Risk", "real-time-risk-skill",
         ["SKILL.md", "__init__.py", "monitor.py", "requirements.txt"]),
        ("Position Controller", "position-controller-skill",
         ["SKILL.md", "controller.py"]),
        ("Stop Loss Manager", "stop-loss-manager-skill",
         ["SKILL.md", "manager.py"]),
        ("Permission Manager", "permission-manager-skill",
         ["SKILL.md", "manager.py"]),
        ("Governance Protocol", "governance-protocol-skill",
         ["SKILL.md", "protocol.py"]),
        ("Risk Report", "risk-report-skill",
         ["SKILL.md", "reporter.py"]),
        ("Monitoring Dashboard", "monitoring-dashboard-skill",
         ["SKILL.md", "dashboard.py"]),
        ("Anomaly Detector", "anomaly-detector-skill",
         ["SKILL.md", "detector.py"]),
        ("Compliance Report", "compliance-report-skill",
         ["SKILL.md", "reporter.py"]),
        ("Fund Guard", "fund-guard-skill",
         ["SKILL.md", "guard.py"]),
        ("Health Check", "health-check-skill",
         ["SKILL.md", "checker.py"]),
    ]

    all_results = []

    # 验证 Phase 3
    print("\n" + "="*60)
    print("Phase 3 执行层 - 验证")
    print("="*60)

    for name, skill_dir, required_files in phase3_skills:
        print(f"\n{name}:")
        skill_path = Path("skills") / skill_dir
        all_exist = True

        for file in required_files:
            full_path = skill_path / file
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {file}")
            all_exist = all_exist and exists

        all_results.append(("Phase 3", name, all_exist))

    # 验证 Phase 4
    print("\n" + "="*60)
    print("Phase 4 风控+治理层 - 验证")
    print("="*60)

    for name, skill_dir, required_files in phase4_skills:
        print(f"\n{name}:")
        skill_path = Path("skills") / skill_dir
        all_exist = True

        for file in required_files:
            full_path = skill_path / file
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {file}")
            all_exist = all_exist and exists

        all_results.append(("Phase 4", name, all_exist))

    # 总结
    print("\n" + "="*60)
    print("验证总结")
    print("="*60)

    phase3_results = [r for r in all_results if r[0] == "Phase 3"]
    phase4_results = [r for r in all_results if r[0] == "Phase 4"]

    p3_pass = sum(1 for _, _, r in phase3_results if r)
    p4_pass = sum(1 for _, _, r in phase4_results if r)

    print(f"\nPhase 3: {p3_pass}/{len(phase3_results)} 通过")
    for _, name, result in phase3_results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")

    print(f"\nPhase 4: {p4_pass}/{len(phase4_results)} 通过")
    for _, name, result in phase4_results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")

    # 保存报告
    import json
    report = {
        "phase3": {
            "total": len(phase3_results),
            "passed": p3_pass,
            "pass_rate": f"{p3_pass/len(phase3_results)*100:.1f}%",
        },
        "phase4": {
            "total": len(phase4_results),
            "passed": p4_pass,
            "pass_rate": f"{p4_pass/len(phase4_results)*100:.1f}%",
        },
    }

    report_path = Path("reports/phase3_4_validation.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n✓ 报告已保存: {report_path}")

    return p3_pass == len(phase3_results) and p4_pass == len(phase4_results)


if __name__ == "__main__":
    success = asyncio.run(validate_phases())
    sys.exit(0 if success else 1)
