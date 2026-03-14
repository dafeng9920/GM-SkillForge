"""
Phase 4 参数优化测试

系统测试不同的验证点参数组合，找出最优配置
"""

import sys
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """测试配置"""
    name: str
    target_gain: float
    time_window: int
    min_resonance: int
    min_breakout_amp: float
    min_volume_ratio: float


@dataclass
class TestResult:
    """测试结果"""
    config: TestConfig
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    win_rate: float
    final_capital: float


def generate_test_data() -> List[TickEvent]:
    """
    生成标准测试数据

    场景：横盘后突破，部分验证成功
    """
    events = []
    current_time = datetime.now() - timedelta(hours=100)

    # 阶段1: 横盘整理（30个点，价格100）
    for i in range(30):
        event = TickEvent(
            symbol="AAPL",
            timestamp=current_time,
            price=100.0,
            volume=500000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段2: 突破上涨（价格100.0 → 102.0）
    # 第一个tick就需要触发突破，至少0.6% (100.6)
    for i in range(5):
        price = 100.0 + (i + 1) * 0.6  # 100.6, 101.2, 101.8, 102.4, 103.0
        volume = 800000  # 放量（1.6倍）

        event = TickEvent(
            symbol="AAPL",
            timestamp=current_time,
            price=price,
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段3: 验证期 - 部分成功（价格继续上涨）
    for i in range(8):
        price = 103.0 + i * 0.1  # 从103.0继续缓慢上涨
        volume = 700000

        event = TickEvent(
            symbol="AAPL",
            timestamp=current_time,
            price=price,
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    return events


def create_test_configs() -> List[TestConfig]:
    """
    创建测试配置组合

    测试不同的参数组合：
    - 目标涨幅: 0.5%, 1%, 2%
    - 时间窗口: 5小时, 30小时, 60小时
    - 共振要求: 1个信号, 2个信号, 3个信号
    """
    configs = []

    # 基础配置：保守 vs 激进
    configs.append(TestConfig(
        name="保守-短期-低目标",
        target_gain=0.005,  # 0.5%
        time_window=5,      # 5小时
        min_resonance=1,
        min_breakout_amp=0.005,
        min_volume_ratio=1.2,
    ))

    configs.append(TestConfig(
        name="保守-长期-低目标",
        target_gain=0.005,  # 0.5%
        time_window=60,     # 60小时
        min_resonance=1,
        min_breakout_amp=0.005,
        min_volume_ratio=1.2,
    ))

    configs.append(TestConfig(
        name="平衡-中期-中目标",
        target_gain=0.01,   # 1%
        time_window=30,     # 30小时
        min_resonance=2,
        min_breakout_amp=0.01,
        min_volume_ratio=1.5,
    ))

    configs.append(TestConfig(
        name="激进-短期-高目标",
        target_gain=0.02,   # 2%
        time_window=5,      # 5小时
        min_resonance=3,
        min_breakout_amp=0.01,
        min_volume_ratio=1.5,
    ))

    configs.append(TestConfig(
        name="激进-长期-高目标",
        target_gain=0.02,   # 2%
        time_window=60,     # 60小时
        min_resonance=2,
        min_breakout_amp=0.01,
        min_volume_ratio=1.5,
    ))

    return configs


def run_backtest(config: TestConfig, data: List[TickEvent]) -> TestResult:
    """运行单次回测"""
    phase4_config = {
        'min_breakout_amp': config.min_breakout_amp,
        'min_volume_ratio': config.min_volume_ratio,
        'min_resonance': config.min_resonance,
        'resistance_lookback': 20,
        'validation_target_gain': config.target_gain,
        'validation_time_window': config.time_window,
    }

    phase4 = Phase4Engine(config=phase4_config)

    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )

    metrics = engine.run(data)

    # 提取验证点状态
    validation_status = "N/A"
    if phase4.validation_manager.validation_points:
        vp = list(phase4.validation_manager.validation_points.values())[0]
        validation_status = vp.status

    return TestResult(
        config=config,
        total_return=metrics.total_return,
        sharpe_ratio=metrics.sharpe_ratio,
        max_drawdown=metrics.max_drawdown,
        total_trades=metrics.total_trades,
        win_rate=metrics.win_rate,
        final_capital=metrics.final_capital,
    )


def print_comparison_table(results: List[TestResult]):
    """打印对比表格"""
    print("\n" + "=" * 80)
    print(f"{'配置':<25} {'收益率':<12} {'夏普':<10} {'最大回撤':<12} {'交易数':<8} {'胜率':<10} {'验证点':<10}")
    print("-" * 80)

    for r in results:
        print(f"{r.config.name:<25} "
              f"{r.total_return:>10.2%}  "
              f"{r.sharpe_ratio:>8.2f}  "
              f"{r.max_drawdown:>10.2%}  "
              f"{r.total_trades:>6}  "
              f"{r.win_rate:>8.2%}  "
              f"${r.final_capital:>9,.2f}")

    print("-" * 80)

    # 找出最优配置
    best_return = max(results, key=lambda x: x.total_return)
    best_sharpe = max(results, key=lambda x: x.sharpe_ratio)
    best_drawdown = min(results, key=lambda x: x.max_drawdown)

    print(f"\n【最优配置】")
    print(f"  最高收益: {best_return.config.name} ({best_return.total_return:.2%})")
    print(f"  最高夏普: {best_sharpe.config.name} ({best_sharpe.sharpe_ratio:.2f})")
    print(f"  最小回撤: {best_drawdown.config.name} ({best_drawdown.max_drawdown:.2%})")

    # 分析
    print(f"\n【参数分析】")
    print(f"  目标涨幅影响:")
    for r in results:
        print(f"    {r.config.name}: {r.total_return:.2%}")

    print(f"\n  时间窗口影响:")
    for r in results:
        if r.config.target_gain == 0.01:  # 固定1%目标，比较不同时间窗口
            print(f"    {r.config.name}: {r.total_return:.2%}, 夏普={r.sharpe_ratio:.2f}")

    print(f"\n  共振要求影响:")
    for r in results:
        if r.config.time_window == 30:  # 固定30小时窗口，比较不同共振要求
            print(f"    {r.config.name}: {r.total_return:.2%}, 交易={r.total_trades}笔")


def run_parameter_optimization():
    """运行完整的参数优化测试"""
    print("=" * 80)
    print("Phase 4 参数优化测试")
    print("=" * 80)

    print("\n【测试场景】")
    data = generate_test_data()
    print(f"  Tick数量: {len(data)}")
    print(f"  价格范围: ${min(d.price for d in data):.2f} - ${max(d.price for d in data):.2f}")
    print(f"  场景: 横盘 → 突破上涨 → 部分验证成功")

    # 创建测试配置
    configs = create_test_configs()

    print(f"\n【测试配置】")
    print(f"  测试组合数: {len(configs)}")

    # 运行所有测试
    results = []
    for i, config in enumerate(configs):
        print(f"\n测试 {i+1}/{len(configs)}: {config.name}")
        result = run_backtest(config, data)
        results.append(result)

        # 打印关键指标
        print(f"  总收益率: {result.total_return:.2%}")
        print(f"  夏普比率: {result.sharpe_ratio:.2f}")
        print(f"  最大回撤: {result.max_drawdown:.2%}")
        print(f"  交易次数: {result.total_trades}")
        print(f"  最终资金: ${result.final_capital:,.2f}")

    # 打印对比表格
    print_comparison_table(results)

    return results


def run_multi_scenario_test():
    """多场景参数测试"""
    print("\n" + "=" * 80)
    print("多场景参数测试")
    print("=" * 80)

    # 测试场景1：假突破（突破后回落）
    print("\n【场景1: 假突破】")
    print("  横盘 → 突破 → 快速回落")

    # 生成假突破数据
    events = []
    current_time = datetime.now() - timedelta(hours=50)

    # 横盘
    for i in range(20):
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=100.0,
            volume=500000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 假突破（100.6, 100.9, 101.2 - 0.5%突破后会回落）
    for i in range(3):
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=100.0 + (i + 1) * 0.3,  # 100.3, 100.6, 100.9
            volume=900000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 快速回落
    for i in range(10):
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=100.0 - i * 0.05,
            volume=400000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 测试不同配置
    configs = [
        TestConfig("宽松-快速", 0.01, 5, 1, 0.005, 1.2),
        TestConfig("严格-慢速", 0.01, 30, 2, 0.01, 1.5),
    ]

    print(f"\n测试配置: {len(configs)}")
    results = []
    for config in configs:
        result = run_backtest(config, events)
        results.append(result)
        print(f"  {config.name}: 收益={result.total_return:.2%}, 夏普={result.sharpe_ratio:.2f}, 交易={result.total_trades}")

    # 测试场景2：真突破（突破后持续）
    print("\n【场景2: 真突破】")
    print("  横盘 → 突破 → 持续上涨")

    # 生成真突破数据
    events = []
    current_time = datetime.now() - timedelta(hours=50)

    # 横盘
    for i in range(20):
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=100.0,
            volume=500000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 真突破（100.6, 101.2, 101.8, 102.4, 103.0）
    for i in range(5):
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=100.0 + (i + 1) * 0.6,  # 0.6% increments
            volume=900000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 持续上涨
    for i in range(15):
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=103.0 + i * 0.1,  # 继续上涨
            volume=700000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 测试不同配置
    print(f"\n测试配置: {len(configs)}")
    results = []
    for config in configs:
        result = run_backtest(config, events)
        results.append(result)
        print(f"  {config.name}: 收益={result.total_return:.2%}, 夏普={result.sharpe_ratio:.2f}, 交易={result.total_trades}")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    # 运行参数优化测试
    results = run_parameter_optimization()

    # 运行多场景测试
    run_multi_scenario_test()

    print("\n所有测试完成!")
