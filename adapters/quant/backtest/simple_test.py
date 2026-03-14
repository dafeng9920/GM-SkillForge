"""
简单回测测试 - 验证 Phase 4 交易信号
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine


def create_simple_test_data() -> list:
    """创建简单的测试数据"""
    events = []
    current_time = datetime.now() - timedelta(hours=30)

    # 阶段1: 横盘（15个点，价格100）
    for i in range(15):
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

    # 阶段2: 突破（价格涨到100.6，放量）
    for i in range(3):
        price = 100.2 + i * 0.2  # 100.2, 100.4, 100.6
        volume = 800000  # 放量

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

    # 阶段3: 验证期（价格维持在100.5-100.7之间）
    for i in range(10):
        import random
        price = 100.5 + random.random() * 0.2  # 100.5-100.7
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

    return events


def main():
    print("=" * 60)
    print("Phase 4 简单回测测试")
    print("=" * 60)

    # 生成测试数据
    data = create_simple_test_data()
    print(f"\n生成 {len(data)} 条Tick数据")

    # 初始化 Phase 4（放宽条件）
    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.005,     # 0.5%
        'min_volume_ratio': 1.1,       # 1.1倍
        'min_resonance': 1,            # 1个信号即可
        'resistance_lookback': 10,
        'validation_target_gain': 0.002, # 0.2% 目标（更容易达成）
        'validation_time_window': 5,    # 5小时验证
    })

    # 初始化回测引擎
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )

    # 运行回测
    print("\n运行回测...")
    metrics = engine.run(data)

    # 打印结果
    print(f"\n处理了 {len(data)} 个事件")
    print(f"生成 {engine.order_count} 个订单")
    print(f"成交 {engine.fill_count} 笔")

    if metrics.trades:
        print(f"\n交易明细:")
        for i, trade in enumerate(metrics.trades, 1):
            print(f"  {i}. ${trade.entry_price:.2f} → ${trade.exit_price:.2f} = ${trade.pnl:+.2f}")
    else:
        print("\n没有交易发生")

    metrics.print_report()


if __name__ == "__main__":
    main()
