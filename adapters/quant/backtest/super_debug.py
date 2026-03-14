"""
超级详细的调试测试
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine


class DebugPhase4Engine(Phase4Engine):
    """带调试输出的 Phase 4 引擎"""

    def on_tick(self, tick_data, portfolio_state):
        """处理tick - 带调试输出"""
        symbol = tick_data['symbol']
        price = tick_data['price']

        # 只调试关键点
        if price >= 100.4:
            print(f"\n[on_tick] {tick_data['timestamp'].strftime('%H:%M')} 价格=${price:.2f}")

            # 检查历史数据
            if symbol in self.price_history:
                history = self.price_history[symbol][:-1]  # 不包括当前
                if len(history) >= 10:
                    recent_high = max(history[-10:])
                    print(f"  阻力位: ${recent_high:.2f}")
                    print(f"  突破阈值: ${recent_high * 1.005:.2f}")
                    print(f"  当前价格: ${price:.2f}")
                    print(f"  是否突破: {price > recent_high * 1.005}")

            # 调用原始感知层
            raw_signals = self._perceive(tick_data)
            print(f"  感知结果: breakout={raw_signals.get('breakout_up')}, "
                  f"volume_surge={raw_signals.get('volume_surge')}, "
                  f"resonance={raw_signals.get('resonance_count')}")

            # 调用确认层
            confirmed = self._confirm(raw_signals, tick_data)
            print(f"  确认结果: buy_signal={confirmed.get('buy_signal')}, "
                  f"confidence={confirmed.get('confidence', 0):.2f}")

        # 调用原始方法
        return super().on_tick(tick_data, portfolio_state)


def create_test_data():
    """创建测试数据"""
    events = []
    current_time = datetime.now() - timedelta(hours=30)

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

    # 阶段2: 突破
    event = TickEvent(
        symbol="AAPL",
        timestamp=current_time,
        price=100.50,
        volume=700000,
        bid=100.4,
        ask=100.6,
    )
    events.append(event)
    current_time += timedelta(hours=1)

    # 阶段3: 验证期
    for i in range(5):
        event = TickEvent(
            symbol="AAPL",
            timestamp=current_time,
            price=100.6,
            volume=600000,
            bid=100.5,
            ask=100.7,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    return events


def main():
    print("=" * 60)
    print("超级详细调试")
    print("=" * 60)

    # 生成测试数据
    data = create_test_data()
    print(f"生成 {len(data)} 条Tick数据")

    # 初始化 Phase 4（带调试）
    phase4 = DebugPhase4Engine(config={
        'min_breakout_amp': 0.005,
        'min_volume_ratio': 1.1,
        'min_resonance': 1,
        'resistance_lookback': 15,
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

    print(f"\n\n最终结果:")
    print(f"  订单数: {engine.order_count}")
    print(f"  成交数: {engine.fill_count}")


if __name__ == "__main__":
    main()
