"""
Phase 5 组合层+集成测试 验证
"""

import asyncio
import sys
from pathlib import Path


async def validate_phase5():
    """验证 Phase 5"""

    phase5_skills = [
        ("Multi-Strategy Portfolio", "multi-strategy-portfolio-skill",
         ["SKILL.md", "__init__.py", "portfolio.py"]),
        ("Strategy Integration", "strategy-integration-skill",
         ["SKILL.md", "integrator.py"]),
        ("System Test", "system-test-skill",
         ["SKILL.md", "tester.py"]),
        ("Deployment", "deployment-skill",
         ["SKILL.md", "deployer.py"]),
    ]

    print("\n" + "="*60)
    print("Phase 5 组合层+集成测试 - 验证")
    print("="*60)

    results = []

    for name, skill_dir, required_files in phase5_skills:
        print(f"\n{name}:")
        skill_path = Path("skills") / skill_dir
        all_exist = True

        for file in required_files:
            full_path = skill_path / file
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {file}")
            all_exist = all_exist and exists

        results.append((name, all_exist))

    # 总结
    print("\n" + "="*60)
    print("Phase 5 测试总结")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nPhase 5: {passed}/{total} 通过")
    print(f"通过率: {passed/total*100:.1f}%")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(validate_phase5())
    sys.exit(0 if success else 1)
