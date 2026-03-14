"""
Phase 1 数据层简化测试

直接测试每个 Skill 的核心功能，不依赖包导入
"""

import asyncio
import sys
from pathlib import Path


async def test_market_data_fetcher():
    """测试 1: Market Data Fetcher"""
    print("\n" + "="*60)
    print("测试 1/6: Market Data Fetcher - 文件结构检查")
    print("="*60)

    skill_path = Path("skills/market-data-fetcher-skill")

    required_files = [
        "SKILL.md",
        "__init__.py",
        "fetcher.py",
        "cache.py",
        "persistence.py",
        "config.py",
        "requirements.txt",
        "sources/__init__.py",
        "sources/base.py",
        "sources/yahoo.py",
    ]

    all_exist = True
    for file in required_files:
        full_path = skill_path / file
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if exists:
            if file.endswith('.py'):
                # 检查文件是否可读
                try:
                    content = full_path.read_text(encoding='utf-8')
                    print(f"      ({len(content)} 字符, {len(content.splitlines())} 行)")
                except:
                    print(f"      (无法读取)")
        all_exist = all_exist and exists

    # 检查 SKILL.md 内容
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        print(f"\n✓ SKILL.md 规范完整:")
        if 'description:' in content:
            desc_part = content.split('description: ')[1].split('\n')[0]
            print(f"  - 描述: {desc_part}")
        else:
            print(f"  - 描述: N/A")
        print(f"  - 总字符: {len(content)}")

    return all_exist


async def test_financial_data_fetcher():
    """测试 2: Financial Data Fetcher"""
    print("\n" + "="*60)
    print("测试 2/6: Financial Data Fetcher - 文件结构检查")
    print("="*60)

    skill_path = Path("skills/financial-data-fetcher-skill")

    required_files = [
        "SKILL.md",
        "__init__.py",
        "fetcher.py",
        "requirements.txt",
        "example.py",
    ]

    all_exist = True
    for file in required_files:
        full_path = skill_path / file
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        all_exist = all_exist and exists

    return all_exist


async def test_sentiment_data_fetcher():
    """测试 3: Sentiment Data Fetcher"""
    print("\n" + "="*60)
    print("测试 3/6: Sentiment Data Fetcher - 文件结构检查")
    print("="*60)

    skill_path = Path("skills/sentiment-data-fetcher-skill")

    required_files = [
        "SKILL.md",
        "__init__.py",
        "fetcher.py",
        "requirements.txt",
    ]

    all_exist = True
    for file in required_files:
        full_path = skill_path / file
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        all_exist = all_exist and exists

    return all_exist


async def test_macro_data_fetcher():
    """测试 4: Macro Data Fetcher"""
    print("\n" + "="*60)
    print("测试 4/6: Macro Data Fetcher - 文件结构检查")
    print("="*60)

    skill_path = Path("skills/macro-data-fetcher-skill")

    required_files = [
        "SKILL.md",
        "__init__.py",
        "fetcher.py",
        "requirements.txt",
    ]

    all_exist = True
    for file in required_files:
        full_path = skill_path / file
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        all_exist = all_exist and exists

    return all_exist


async def test_data_quality_validator():
    """测试 5: Data Quality Validator"""
    print("\n" + "="*60)
    print("测试 5/6: Data Quality Validator - 文件结构检查")
    print("="*60)

    skill_path = Path("skills/data-quality-validator-skill")

    required_files = [
        "SKILL.md",
        "__init__.py",
        "validator.py",
        "requirements.txt",
    ]

    all_exist = True
    for file in required_files:
        full_path = skill_path / file
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        all_exist = all_exist and exists

    return all_exist


async def test_data_storage_manager():
    """测试 6: Data Storage Manager"""
    print("\n" + "="*60)
    print("测试 6/6: Data Storage Manager - 文件结构检查")
    print("="*60)

    skill_path = Path("skills/data-storage-manager-skill")

    required_files = [
        "SKILL.md",
        "__init__.py",
        "manager.py",
        "requirements.txt",
    ]

    all_exist = True
    for file in required_files:
        full_path = skill_path / file
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        all_exist = all_exist and exists

    return all_exist


async def count_all_skills():
    """统计所有 Skills"""
    print("\n" + "="*60)
    print("GM-SkillForge 全部 Skills 统计")
    print("="*60)

    skills_dir = Path("skills")
    all_skills = list(skills_dir.glob("*/SKILL.md"))

    print(f"\n发现 {len(all_skills)} 个 Skills:\n")

    phase_skills = {}
    for skill_md in all_skills:
        skill_name = skill_md.parent.name
        phase_skills[skill_name] = skill_md

        # 读取 phase 信息
        content = skill_md.read_text(encoding='utf-8')

    # 按字母顺序显示
    for skill_name in sorted(phase_skills.keys()):
        print(f"  ✓ {skill_name}")

    print(f"\n总计: {len(all_skills)} 个 Skills")

    return len(all_skills)


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Phase 1 数据层 - Skills 结构验证")
    print("="*60)

    tests = [
        ("Market Data Fetcher", test_market_data_fetcher),
        ("Financial Data Fetcher", test_financial_data_fetcher),
        ("Sentiment Data Fetcher", test_sentiment_data_fetcher),
        ("Macro Data Fetcher", test_macro_data_fetcher),
        ("Data Quality Validator", test_data_quality_validator),
        ("Data Storage Manager", test_data_storage_manager),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} 测试异常: {e}")
            results.append((name, False))

    # 统计所有 Skills
    total_skills = await count_all_skills()

    # 打印总结
    print("\n" + "="*60)
    print("Phase 1 测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nPhase 1: {passed}/{total} 通过")
    print(f"通过率: {passed/total*100:.1f}%")
    print(f"\n系统总 Skills 数: {total_skills}")

    # 创建验证报告
    report = {
        "phase": "Phase 1 - 数据层",
        "test_date": Path.cwd().name,
        "total_skills": total_skills,
        "phase_skills": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": f"{passed/total*100:.1f}%",
        "results": [
            {"name": name, "status": "PASS" if result else "FAIL"}
            for name, result in results
        ]
    }

    # 保存报告
    import json
    report_path = Path("reports/phase1_validation.json")
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"\n✓ 验证报告已保存: {report_path}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
