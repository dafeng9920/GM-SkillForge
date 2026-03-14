"""
使用回测引擎测试 Phase 4
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine


def create_test_data_with_signal():
    """创建包含明确信号的测试数据"""
    events = []
    current_time = datetime.now() - timedelta(hours=40)

    # 阶段1: 横盘（20个点，价格100）
    for i in range(20):
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

    # 阶段2: 突破（价格100.5，放量）
    event = TickEvent(
        symbol="AAPL",
        timestamp=current_time,
        price=100.5,  # 0.5% 突破
        volume=700000,  # 1.4倍放量
        bid=100.4,
        ask=100.6,
    )
    events.append(event)
    current_time += timedelta(hours=1)

    # 阶段3: 验证期（价格维持）
    for i in range(10):
        import random
        price = 100.4 + random.random() * 0.3  # 100.4-100.7
        event = TickEvent(
            symbol="AAPL",
            timestamp=current_time,
            price=price,
            volume=600000,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    return events


def main():
    print("=" * 60)
    print("回测引擎测试 Phase 4")
    print("=" * 60)

    # 生成测试数据
    data = create_test_data_with_signal()
    print(f"\n生成 {len(data)} 条Tick数据")

    # 初始化 Phase 4
    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.005,
        'min_volume_ratio': 1.1,
        'min_resonance': 1,
        'resistance_lookback': 15,  # 需要15个点来计算阻力位
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
    print(f"\n处理 {len(data)} 个事件")
    print(f"生成 {engine.order_count} 个订单")
    print(f"成交 {engine.fill_count} 笔")

    if metrics.trades:
        print(f"\n交易明细:")
        for i, trade in enumerate(metrics.trades, 1):
            print(f"  {i}. ${trade.entry_price:.2f} → ${trade.exit_price:.2f} = ${trade.pnl:+.2f} ({trade.return_pct:+.2%})")

    metrics.print_report()


if __name__ == "__main__":
    main()
