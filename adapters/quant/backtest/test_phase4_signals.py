"""
Phase 4 信号测试脚本

生成明确的价格突破模式来测试 Phase 4 系统
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine


def generate_breakout_data() -> list:
    """
    生成包含明确突破的模拟数据

    模式：
    1. 前50个点：横盘整理（价格在100附近）
    2. 51-60个点：放量突破（价格涨到105）
    3. 61-100个点：验证期（价格在104-106之间）
    """
    events = []
    current_time = datetime.now() - timedelta(hours=100)

    # 阶段1: 横盘整理（50个点）
    for i in range(50):
        price = 100.0 + (i % 5 - 2) * 0.2  # 99.6 - 100.4 范围
        volume = 500000 + (i % 3) * 100000

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

    # 阶段2: 突破（10个点）
    for i in range(10):
        progress = i / 10
        price = 100.0 + progress * 5.0  # 100 -> 105
        volume = 1500000 + i * 100000  # 放量

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

    # 阶段3: 验证期（40个点）
    for i in range(40):
        # 价格在104-106之间波动
        price = 104.0 + (i % 3) * 0.5 + (i % 7) * 0.2
        volume = 800000 + (i % 5) * 100000

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


def test_phase4_breakout():
    """测试 Phase 4 突破信号"""
    print("=" * 60)
    print("Phase 4 突破信号测试")
    print("=" * 60)

    # 1. 生成突破数据
    print("\n1. 生成突破模式数据...")
    data = generate_breakout_data()
    print(f"   生成了 {len(data)} 条Tick数据")

    # 打印价格范围
    prices = [d.price for d in data]
    print(f"   价格范围: ${min(prices):.2f} - ${max(prices):.2f}")
    print(f"   开始价格: ${prices[0]:.2f}")
    print(f"   结束价格: ${prices[-1]:.2f}")
    print(f"   涨幅: {(prices[-1] - prices[0]) / prices[0]:.2%}")

    # 2. 初始化 Phase 4 引擎（降低阈值）
    print("\n2. 初始化 Phase 4 引擎...")
    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.01,      # 1% 突破
        'min_volume_ratio': 1.2,       # 1.2倍放量
        'min_resonance': 1,            # 只需1个信号
        'resistance_lookback': 20,     # 20个点回看
        'validation_target_gain': 0.005, # 0.5% 目标
        'validation_time_window': 20,   # 20小时验证
    })
    print("   Phase 4 引擎初始化完成")

    # 3. 初始化回测引擎
    print("\n3. 初始化回测引擎...")
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )
    print(f"   初始资金: ${engine.initial_capital:,.2f}")

    # 4. 运行回测
    print("\n4. 运行回测...")
    metrics = engine.run(data)
    print(f"   处理了 {len(data)} 个事件")
    print(f"   生成 {engine.order_count} 个订单")
    print(f"   成交 {engine.fill_count} 笔")

    # 5. 打印结果
    print("\n5. 回测结果:")
    metrics.print_report()

    # 6. 打印交易明细
    if metrics.trades:
        print("\n6. 交易明细:")
        for i, trade in enumerate(metrics.trades, 1):
            print(f"   {i}. {trade.entry_time.strftime('%Y-%m-%d %H:%M')} → "
                  f"{trade.exit_time.strftime('%Y-%m-%d %H:%M')} | "
                  f"${trade.entry_price:.2f} → ${trade.exit_price:.2f} | "
                  f"${trade.pnl:+.2f} ({trade.return_pct:+.2%})")
    else:
        print("\n6. 没有交易完成")

    # 7. 打印验证点状态
    print("\n7. 验证点状态:")
    if phase4.validation_manager.validation_points:
        for symbol, vp in phase4.validation_manager.validation_points.items():
            print(f"   {symbol}:")
            print(f"     入场: ${vp.entry_price:.2f}")
            print(f"     目标: ${vp.target_price:.2f}")
            print(f"     状态: {vp.status}")
    else:
        print("   无验证点")

    return metrics


def test_phase4_validation_failure():
    """测试 Phase 4 验证失败（买入后不涨）"""
    print("\n" + "=" * 60)
    print("Phase 4 验证失败测试")
    print("=" * 60)

    events = []
    current_time = datetime.now() - timedelta(hours=50)

    # 阶段1: 横盘（20个点）
    for i in range(20):
        price = 100.0 + (i % 3) * 0.1
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=price,
            volume=500000,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段2: 假突破（5个点）
    for i in range(5):
        price = 100.0 + i * 0.3  # 小幅突破
        volume = 1500000  # 放量
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=price,
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段3: 回落验证期（30个点）
    for i in range(30):
        price = 101.0 - i * 0.05  # 逐渐回落
        volume = 600000
        event = TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=price,
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    print(f"\n生成 {len(events)} 条数据（假突破场景）")

    # 运行回测
    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.005,     # 0.5% 即可
        'min_volume_ratio': 1.2,
        'min_resonance': 1,
        'resistance_lookback': 10,
        'validation_target_gain': 0.01,  # 要求1%
        'validation_time_window': 10,    # 10小时验证
    })

    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )

    metrics = engine.run(events)

    print(f"\n结果:")
    print(f"  总交易: {metrics.total_trades}")
    print(f"  最终资金: ${metrics.final_capital:,.2f}")
    print(f"  总收益: {metrics.total_return:.2%}")

    if metrics.trades:
        print(f"\n交易明细:")
        for i, trade in enumerate(metrics.trades, 1):
            print(f"  {i}. ${trade.entry_price:.2f} → ${trade.exit_price:.2f} = ${trade.pnl:+.2f}")


if __name__ == "__main__":
    # 测试突破信号
    test_phase4_breakout()

    # 测试验证失败
    test_phase4_validation_failure()

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)
