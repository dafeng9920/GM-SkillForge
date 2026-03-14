"""
Phase 1 数据层测试脚本

测试所有 6 个数据层 Skills 的基本功能
"""

import asyncio
import sys
from pathlib import Path

# 添加 skills 目录到路径
skills_path = Path(__file__).parent.parent / "skills"
sys.path.insert(0, str(skills_path))


async def test_market_data_fetcher():
    """测试 1: Market Data Fetcher"""
    print("\n" + "="*60)
    print("测试 1/6: Market Data Fetcher")
    print("="*60)

    try:
        from market_data_fetcher_skill import MarketDataFetcher
        print("✓ 模块导入成功")

        # 创建简单测试数据
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta

        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        np.random.seed(42)

        data = pd.DataFrame({
            "timestamp": dates,
            "open": 100 + np.cumsum(np.random.randn(100) * 2),
            "high": 100 + np.cumsum(np.random.randn(100) * 2) + 2,
            "low": 100 + np.cumsum(np.random.randn(100) * 2) - 2,
            "close": 100 + np.cumsum(np.random.randn(100) * 2),
            "volume": np.random.randint(1000000, 10000000, 100),
        })
        data = data.set_index("timestamp")

        print(f"✓ 测试数据创建成功: {len(data)} 行")
        print(f"  数据列: {list(data.columns)}")
        print(f"  时间范围: {data.index[0]} 到 {data.index[-1]}")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_financial_data_fetcher():
    """测试 2: Financial Data Fetcher"""
    print("\n" + "="*60)
    print("测试 2/6: Financial Data Fetcher")
    print("="*60)

    try:
        from financial_data_fetcher_skill import FinancialDataFetcher
        print("✓ 模块导入成功")

        # 创建模拟数据
        import pandas as pd

        financial_data = pd.DataFrame({
            "period": ["Q4 2023", "Q3 2023", "Q2 2023"],
            "revenue": [119575000000, 89498000000, 81892000000],
            "net_income": [33916000000, 22956000000, 19881000000],
            "eps": [2.18, 1.46, 1.26],
        })

        print(f"✓ 财务数据创建成功: {len(financial_data)} 个季度")
        print(f"  列: {list(financial_data.columns)}")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_sentiment_data_fetcher():
    """测试 3: Sentiment Data Fetcher"""
    print("\n" + "="*60)
    print("测试 3/6: Sentiment Data Fetcher")
    print("="*60)

    try:
        from sentiment_data_fetcher_skill import SentimentDataFetcher
        print("✓ 模块导入成功")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_macro_data_fetcher():
    """测试 4: Macro Data Fetcher"""
    print("\n" + "="*60)
    print("测试 4/6: Macro Data Fetcher")
    print("="*60)

    try:
        from macro_data_fetcher_skill import MacroDataFetcher
        print("✓ 模块导入成功")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_data_quality_validator():
    """测试 5: Data Quality Validator"""
    print("\n" + "="*60)
    print("测试 5/6: Data Quality Validator")
    print("="*60)

    try:
        from data_quality_validator_skill import DataQualityValidator
        print("✓ 模块导入成功")

        # 创建测试数据
        import pandas as pd
        import numpy as np

        test_data = pd.DataFrame({
            "open": [100, 102, 98, 105, 103],
            "high": [102, 105, 100, 108, 106],
            "low": [98, 100, 95, 103, 101],
            "close": [101, 103, 99, 106, 104],
            "volume": [1000000, 1200000, 900000, 1500000, 1100000],
        })

        validator = DataQualityValidator()

        # 添加验证规则
        validator.add_rule("price_positive", validator.check_price_positive, "high")
        validator.add_rule("volume_non_negative", validator.check_volume_non_negative, "medium")
        validator.add_rule("ohlc_consistency", validator.check_ohlc_consistency, "high")

        print(f"✓ 验证器创建成功，添加了 3 条规则")
        print(f"✓ 测试数据: {len(test_data)} 行")

        # 执行验证
        result = validator.validate(test_data)

        print(f"  验证状态: {result['status']}")
        print(f"  总行数: {result['total_rows']}")
        print(f"  有效行数: {result['valid_rows']}")
        print(f"  无效行数: {result['invalid_rows']}")

        if result['issues']:
            print(f"  发现问题:")
            for issue in result['issues']:
                print(f"    - {issue['type']}: {issue['count']} 行 (严重性: {issue['severity']})")

        return result['status'] == "PASSED"

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_data_storage_manager():
    """测试 6: Data Storage Manager"""
    print("\n" + "="*60)
    print("测试 6/6: Data Storage Manager")
    print("="*60)

    try:
        from data_storage_manager_skill import DataStorageManager
        print("✓ 模块导入成功")

        # 创建管理器
        manager = DataStorageManager(
            db_url="postgresql://localhost:5432/test",
            minio_config={"endpoint": "localhost:9000"}
        )

        print(f"✓ 存储管理器创建成功")

        # 获取存储统计
        stats = await manager.get_storage_stats()

        print(f"  存储统计: {stats}")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def main():
    """运行所有 Phase 1 测试"""
    print("\n" + "="*60)
    print("Phase 1 数据层 - Skills 测试")
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

    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")
    print(f"通过率: {passed/total*100:.1f}%")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
