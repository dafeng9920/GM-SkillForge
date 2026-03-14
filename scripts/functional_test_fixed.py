"""
GM-SkillForge 功能测试脚本 (修复版)

修复了回测引擎的导入问题
"""

import asyncio
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import importlib.util

# 添加 skills 目录到路径
skills_path = Path(__file__).parent.parent / "skills"
sys.path.insert(0, str(skills_path))


async def test_backtest_engine():
    """测试 Phase 2: Backtest Engine (修复版)"""
    print("\n" + "="*60)
    print("功能测试: Backtest Engine (修复版)")
    print("="*60)

    try:
        # 首先导入 order 模块（建立包上下文）
        order_path = skills_path / "backtest-engine-skill" / "order.py"
        order_spec = importlib.util.spec_from_file_location(
            "backtest_engine_skill.order",
            order_path,
        )
        order_module = importlib.util.module_from_spec(order_spec)
        order_spec.loader.exec_module(order_module)

        # 将模块添加到 sys.modules
        sys.modules['backtest_engine_skill.order'] = order_module

        # 现在导入 engine 模块
        engine_path = skills_path / "backtest-engine-skill" / "engine.py"
        engine_spec = importlib.util.spec_from_file_location(
            "backtest_engine_skill.engine",
            engine_path,
        )
        engine_module = importlib.util.module_from_spec(engine_spec)
        engine_spec.loader.exec_module(engine_module)

        BacktestEngine = engine_module.BacktestEngine

        # 创建回测引擎
        engine = BacktestEngine(initial_capital=100000)
        print("  ✓ 回测引擎创建成功")
        print(f"    初始资金: ${engine.initial_capital:,.0f}")
        print(f"    当前现金: ${engine.portfolio.cash:,.0f}")

        # 测试基本功能
        print("\n  测试基本功能:")

        # 检查订单类型
        OrderType = order_module.OrderType
        OrderSide = order_module.OrderSide
        OrderStatus = order_module.OrderStatus

        print(f"  ✓ 订单类型: {[t.value for t in OrderType]}")
        print(f"  ✓ 订单方向: {[s.value for s in OrderSide]}")
        print(f"  ✓ 订单状态: {[s.value for s in OrderStatus]}")

        # 检查投资组合
        print(f"  ✓ 现金: ${engine.portfolio.cash:,.2f}")
        print(f"  ✓ 持仓: {engine.portfolio.positions}")

        # 检查订单列表
        print(f"  ✓ 待成交订单: {len(engine.portfolio.pending_orders)}")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_indicator_calculator():
    """测试 Phase 2: Indicator Calculator"""
    print("\n" + "="*60)
    print("功能测试: Indicator Calculator")
    print("="*60)

    try:
        import importlib.util

        calc_path = skills_path / "indicator-calculator-skill" / "calculator.py"
        spec = importlib.util.spec_from_file_location("calculator", calc_path)
        calc_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(calc_module)

        IndicatorCalculator = calc_module.IndicatorCalculator

        # 创建测试数据
        print("  创建测试数据 (模拟股价)...")
        dates = pd.date_range("2024-01-01", periods=50, freq="D")
        np.random.seed(42)

        test_data = pd.DataFrame({
            "timestamp": dates,
            "open": 100 + np.cumsum(np.random.randn(50)),
            "high": 100 + np.cumsum(np.random.randn(50)) + 2,
            "low": 100 + np.cumsum(np.random.randn(50)) - 2,
            "close": 100 + np.cumsum(np.random.randn(50)),
            "volume": np.random.randint(1000000, 10000000, 50),
        })
        test_data = test_data.set_index("timestamp")

        calculator = IndicatorCalculator()

        # 计算指标
        print("  计算技术指标...")

        # SMA
        sma_20 = await calculator._sma(test_data, 20)
        print(f"  ✓ SMA(20) 最新值: {sma_20.iloc[-1]:.2f}")

        # RSI
        rsi_14 = await calculator._rsi(test_data, 14)
        print(f"  ✓ RSI(14) 最新值: {rsi_14.iloc[-1]:.2f}")

        # MACD
        macd = await calculator._macd(test_data, 12, 26, 9)
        print(f"  ✓ MACD: macd={macd['macd'].iloc[-1]:.4f}, signal={macd['signal'].iloc[-1]:.4f}")

        # 布林带
        bb = await calculator._bollinger_bands(test_data, 20, 2)
        print(f"  ✓ 布林带: upper={bb['upper'].iloc[-1]:.2f}, lower={bb['lower'].iloc[-1]:.2f}")

        # ATR
        atr = await calculator._atr(test_data, 14)
        print(f"  ✓ ATR(14): {atr.iloc[-1]:.4f}")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_signal_generator():
    """测试 Phase 2: Signal Generator"""
    print("\n" + "="*60)
    print("功能测试: Signal Generator")
    print("="*60)

    try:
        import importlib.util

        gen_path = skills_path / "signal-generator-skill" / "generator.py"
        spec = importlib.util.spec_from_file_location("generator", gen_path)
        gen_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gen_module)

        SignalGenerator = gen_module.SignalGenerator
        SignalType = gen_module.SignalType
        Signal = gen_module.Signal

        generator = SignalGenerator()
        print("  ✓ 信号生成器创建成功")

        # 创建测试数据
        dates = pd.date_range("2024-01-01", periods=20, freq="D")
        test_data = pd.DataFrame({
            "timestamp": dates,
            "close": 100 + np.cumsum(np.random.randn(20)),
        })
        test_data = test_data.set_index("timestamp")

        # 添加一些指标用于信号生成
        test_data["SMA_fast"] = test_data["close"].rolling(5).mean()
        test_data["SMA_slow"] = test_data["close"].rolling(10).mean()
        test_data = test_data.ffill()  # 兼容新版 pandas

        print("  ✓ 测试数据准备完成")

        # 生成信号
        rules = [
            {"type": "crossover", "fast": "SMA_fast", "slow": "SMA_slow", "direction": "bullish"}
        ]

        signal = await generator.generate(test_data, "AAPL", rules)

        print(f"  ✓ 信号生成成功:")
        print(f"    - 类型: {signal.signal_type.value}")
        print(f"    - 强度: {signal.strength:.2f}")
        print(f"    - 置信度: {signal.confidence:.2f}")
        print(f"    - 理由: {signal.reasons}")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multi_strategy_portfolio():
    """测试 Phase 5: Multi-Strategy Portfolio"""
    print("\n" + "="*60)
    print("功能测试: Multi-Strategy Portfolio")
    print("="*60)

    try:
        import importlib.util

        portfolio_path = skills_path / "multi-strategy-portfolio-skill" / "portfolio.py"
        spec = importlib.util.spec_from_file_location("portfolio", portfolio_path)
        portfolio_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(portfolio_module)

        MultiStrategyPortfolio = portfolio_module.MultiStrategyPortfolio

        portfolio = MultiStrategyPortfolio()
        print("  ✓ 多策略组合创建成功")

        # 创建策略收益数据
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        np.random.seed(42)

        # 策略1: 动量策略
        returns1 = pd.Series(np.random.randn(100) * 0.01, index=dates)

        # 策略2: 均值策略
        returns2 = pd.Series(np.random.randn(100) * 0.008, index=dates)

        # 策略3: 趋势策略
        returns3 = pd.Series(np.random.randn(100) * 0.012, index=dates)

        # 添加策略
        await portfolio.add_strategy("Momentum", returns1, 0.4)
        await portfolio.add_strategy("MeanReversion", returns2, 0.3)
        await portfolio.add_strategy("Trend", returns3, 0.3)

        print(f"  ✓ 添加了 3 个策略")

        # 优化权重
        print("  优化权重分配...")

        # 等权重
        equal_weights = await portfolio.optimize_weights(method="equal_weight")
        print(f"  ✓ 等权重优化: {equal_weights}")

        # 计算组合指标
        metrics = await portfolio.get_portfolio_metrics(equal_weights)
        print(f"  ✓ 组合指标:")
        print(f"    - 年化收益: {metrics['annual_return']:.2%}")
        print(f"    - 年化波动: {metrics['annual_volatility']:.2%}")
        print(f"    - 夏普比率: {metrics['sharpe_ratio']:.2f}")

        # 计算相关性矩阵
        corr_matrix = await portfolio.calculate_correlation_matrix()
        print(f"  ✓ 相关性矩阵:")
        print(f"    {corr_matrix.to_string()}")

        return True

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_data_quality_validator():
    """测试 Phase 1: Data Quality Validator"""
    print("\n" + "="*60)
    print("功能测试: Data Quality Validator")
    print("="*60)

    try:
        import importlib.util

        validator_path = skills_path / "data-quality-validator-skill" / "validator.py"
        spec = importlib.util.spec_from_file_location("validator", validator_path)
        validator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator_module)

        DataQualityValidator = validator_module.DataQualityValidator

        # 创建测试数据（包含一些错误）
        print("  创建测试数据...")
        test_data = pd.DataFrame({
            "open": [100, 102, 105, 98, 103],  # 正常
            "high": [102, 105, 100, 108, 106],  # 正常
            "low": [98, 100, 95, 103, 101],  # 正常
            "close": [101, 103, 99, 106, 104],  # 正常
            "volume": [1000000, 1200000, 900000, 1500000, 1100000],  # 正常
        })

        validator = DataQualityValidator()

        # 添加规则
        validator.add_rule("price_positive", validator.check_price_positive, "high")
        validator.add_rule("volume_non_negative", validator.check_volume_non_negative, "medium")
        validator.add_rule("ohlc_consistency", validator.check_ohlc_consistency, "high")
        validator.add_rule("no_duplicates", validator.check_no_duplicates, "medium")

        print("  执行数据验证...")
        result = validator.validate(test_data)

        print(f"  ✓ 验证完成:")
        print(f"    - 状态: {result['status']}")
        print(f"    - 总行数: {result['total_rows']}")
        print(f"    - 有效行数: {result['valid_rows']}")
        print(f"    - 无效行数: {result['invalid_rows']}")

        if result['issues']:
            print(f"    - 发现问题: {len(result['issues'])}")
            for issue in result['issues']:
                print(f"      * {issue['type']}: {issue['count']} 行")

        return result['status'] == "PASSED"

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有功能测试"""
    print("\n" + "="*60)
    print("GM-SkillForge 功能测试 (修复版)")
    print("="*60)

    tests = [
        ("Data Quality Validator", test_data_quality_validator),
        ("Indicator Calculator", test_indicator_calculator),
        ("Backtest Engine", test_backtest_engine),
        ("Signal Generator", test_signal_generator),
        ("Multi-Strategy Portfolio", test_multi_strategy_portfolio),
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
    print("功能测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")
    print(f"通过率: {passed/total*100:.1f}%")

    # 保存测试报告
    import json
    report = {
        "test_date": datetime.now().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": f"{passed/total*100:.1f}%",
        "all_passed": passed == total,
        "results": [
            {"name": name, "status": "PASS" if result else "FAIL"}
            for name, result in results
        ]
    }

    report_path = Path("reports/functional_test_results.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n✓ 测试报告已保存: {report_path}")

    # 如果全部通过，创建成功标志
    if passed == total:
        success_flag = Path("reports/ALL_TESTS_PASSED.flag")
        success_flag.write_text(datetime.now().isoformat())
        print(f"\n🎉 所有测试通过！成功标志已创建: {success_flag}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
