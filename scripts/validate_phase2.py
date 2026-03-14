"""
Phase 2 研发层简化验证

验证 Phase 2 的 9 个 Skills
"""

import asyncio
import sys
from pathlib import Path


async def test_phase2_skills():
    """测试 Phase 2 所有 Skills"""
    print("\n" + "="*60)
    print("Phase 2 研发层 - Skills 结构验证")
    print("="*60)

    phase2_skills = [
        ("Indicator Calculator", "indicator-calculator-skill",
         ["SKILL.md", "__init__.py", "calculator.py", "requirements.txt", "example.py"]),
        ("Factor Analyzer", "factor-analyzer-skill",
         ["SKILL.md", "__init__.py", "analyzer.py", "requirements.txt"]),
        ("Backtest Engine", "backtest-engine-skill",
         ["SKILL.md", "__init__.py", "engine.py", "order.py", "requirements.txt"]),
        ("Signal Generator", "signal-generator-skill",
         ["SKILL.md", "__init__.py", "generator.py", "requirements.txt"]),
        ("Strategy Builder", "strategy-builder-skill",
         ["SKILL.md", "__init__.py", "builder.py", "requirements.txt"]),
        ("Optimizer", "optimizer-skill",
         ["SKILL.md", "__init__.py", "optimizer.py", "requirements.txt"]),
        ("Portfolio Manager", "portfolio-manager-skill",
         ["SKILL.md", "__init__.py", "manager.py", "requirements.txt"]),
        ("Risk Manager", "risk-manager-skill",
         ["SKILL.md", "__init__.py", "manager.py", "requirements.txt"]),
        ("Performance Analyzer", "performance-analyzer-skill",
         ["SKILL.md", "__init__.py", "analyzer.py", "requirements.txt"]),
    ]

    results = []

    for name, skill_dir, required_files in phase2_skills:
        print(f"\n测试: {name}")
        print("-" * 40)

        skill_path = Path("skills") / skill_dir
        all_exist = True

        for file in required_files:
            full_path = skill_path / file
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {file}")

            if exists and file.endswith('.py'):
                try:
                    content = full_path.read_text(encoding='utf-8')
                    print(f"      ({len(content)} 字符, {len(content.splitlines())} 行)")
                except:
                    pass

            all_exist = all_exist and exists

        results.append((name, all_exist))

    # 打印总结
    print("\n" + "="*60)
    print("Phase 2 测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nPhase 2: {passed}/{total} 通过")
    print(f"通过率: {passed/total*100:.1f}%")

    # 保存报告
    import json
    report = {
        "phase": "Phase 2 - 研发层",
        "total_skills": 98,
        "phase_skills": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": f"{passed/total*100:.1f}%",
        "results": [
            {"name": name, "status": "PASS" if result else "FAIL"}
            for name, result in results
        ]
    }

    report_path = Path("reports/phase2_validation.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\n✓ 验证报告已保存: {report_path}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(test_phase2_skills())
    sys.exit(0 if success else 1)
