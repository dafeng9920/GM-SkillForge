"""
Phase 4 量化系统快速测试脚本

运行此脚本以验证 Phase 4 系统是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_integration_tests():
    """运行集成测试"""
    print("\n" + "=" * 70)
    print("Phase 4 量化系统 - 集成测试")
    print("=" * 70)

    try:
        from adapters.quant.tests.test_phase4_integration import Phase4IntegrationTest

        tester = Phase4IntegrationTest()
        tester.run_all_tests()

        return True
    except Exception as e:
        print(f"\n❌ 测试运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_parameter_optimization():
    """运行参数优化测试"""
    print("\n" + "=" * 70)
    print("Phase 4 量化系统 - 参数优化")
    print("=" * 70)

    try:
        from adapters.quant.backtest.parameter_optimization import (
            run_parameter_optimization,
            run_multi_scenario_test,
        )

        # 运行参数优化
        results = run_parameter_optimization()

        # 运行多场景测试
        run_multi_scenario_test()

        return True
    except Exception as e:
        print(f"\n❌ 参数优化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_backtest_demo():
    """运行回测演示"""
    print("\n" + "=" * 70)
    print("Phase 4 量化系统 - 回测演示")
    print("=" * 70)

    try:
        from datetime import datetime, timedelta
        from adapters.quant.backtest.engine import BacktestEngine
        from adapters.quant.backtest.events import TickEvent
        from adapters.quant.phase4.engine import Phase4Engine

        # 创建Phase 4引擎
        config = {
            'min_breakout_amp': 0.02,
            'min_volume_ratio': 1.5,
            'min_resonance': 3,
            'validation_target_gain': 0.01,
            'validation_time_window': 30,
        }
        phase4 = Phase4Engine(config=config)

        # 生成测试数据
        events = []
        current_time = datetime.now() - timedelta(hours=100)

        # 阶段1: 横盘整理
        print("\n【阶段1: 横盘整理】")
        for i in range(30):
            event = TickEvent(
                symbol="DEMO",
                timestamp=current_time,
                price=100.0,
                volume=500000,
                bid=99.9,
                ask=100.1,
            )
            events.append(event)
            current_time += timedelta(hours=1)

        # 阶段2: 突破上涨
        print("【阶段2: 突破上涨】")
        for i in range(5):
            price = 100.0 + (i + 1) * 0.8
            volume = 800000
            event = TickEvent(
                symbol="DEMO",
                timestamp=current_time,
                price=price,
                volume=volume,
                bid=price * 0.999,
                ask=price * 1.001,
            )
            events.append(event)
            current_time += timedelta(hours=1)
            print(f"  价格: ${price:.2f}, 成交量: {volume:,}")

        # 阶段3: 验证期
        print("【阶段3: 验证期 - 价格继续上涨】")
        for i in range(8):
            price = 104.0 + i * 0.1
            event = TickEvent(
                symbol="DEMO",
                timestamp=current_time,
                price=price,
                volume=700000,
                bid=price * 0.999,
                ask=price * 1.001,
            )
            events.append(event)
            current_time += timedelta(hours=1)

        # 创建回测引擎
        engine = BacktestEngine(
            initial_capital=100000,
            commission=0.001,
            signal_handler=phase4.on_tick,
        )

        # 运行回测
        print("\n【运行回测】")
        metrics = engine.run(events)

        # 打印结果
        print("\n【回测结果】")
        print(f"  总收益率: {metrics.total_return:.2%}")
        print(f"  年化收益: {metrics.annual_return:.2%}")
        print(f"  夏普比率: {metrics.sharpe_ratio:.2f}")
        print(f"  最大回撤: {metrics.max_drawdown:.2%}")
        print(f"  交易次数: {metrics.total_trades}")
        print(f"  胜率: {metrics.win_rate:.2%}")
        print(f"  盈亏比: {metrics.profit_factor:.2f}")

        return True
    except Exception as e:
        print(f"\n❌ 回测演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("Phase 4 量化系统测试套件")
    print("=" * 70)
    print("\n请选择要运行的测试:")
    print("  1. 集成测试 (推荐)")
    print("  2. 参数优化测试")
    print("  3. 回测演示")
    print("  4. 运行所有测试")
    print("  0. 退出")

    choice = input("\n请输入选项 (0-4): ").strip()

    if choice == "1":
        run_integration_tests()
    elif choice == "2":
        run_parameter_optimization()
    elif choice == "3":
        run_backtest_demo()
    elif choice == "4":
        all_passed = True
        all_passed &= run_integration_tests()
        all_passed &= run_parameter_optimization()
        all_passed &= run_backtest_demo()

        if all_passed:
            print("\n" + "=" * 70)
            print("🎉 所有测试完成!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("⚠️  部分测试失败，请查看上面的错误信息")
            print("=" * 70)
    elif choice == "0":
        print("\n退出")
    else:
        print(f"\n无效选项: {choice}")


if __name__ == "__main__":
    main()
