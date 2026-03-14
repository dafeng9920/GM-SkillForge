"""
调试订单流程 - 追踪信号到订单的转换
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from collections import deque
from adapters.quant.backtest.engine import BacktestEngine, Portfolio, Position
from adapters.quant.backtest.events import TickEvent, SignalEvent, OrderEvent, FillEvent
from adapters.quant.phase4.engine import Phase4Engine


class DebugBacktestEngine(BacktestEngine):
    """带有调试输出的回测引擎"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signal_count = 0
        self.buy_signal_count = 0
        self.sell_signal_count = 0

    def _on_signal(self, event: SignalEvent):
        """处理信号事件"""
        self.signal_count += 1
        if event.signal_type == "BUY":
            self.buy_signal_count += 1
        elif event.signal_type == "SELL":
            self.sell_signal_count += 1

        print(f"\n  🔔 收到{event.signal_type}信号 #{self.signal_count}")
        print(f"     Symbol: {event.symbol}")
        print(f"     Price: ${event.price:.2f}")
        print(f"     Reason: {event.reason}")

        # 将 signal_type 映射到 direction
        signal_to_direction = {
            "BUY": "BUY",
            "SELL": "SELL",
            "HOLD": "HOLD",
        }

        direction = signal_to_direction.get(event.signal_type)
        if not direction or direction == "HOLD":
            print(f"     ⚠️  信号被忽略 (direction={direction})")
            return

        # 计算订单数量
        price = event.price or self.current_prices.get(event.symbol, 0)
        quantity = self._calculate_order_quantity(event.symbol, direction, price)

        print(f"     计算订单数量: {quantity}")
        print(f"     可用现金: ${self.portfolio.cash:,.2f}")
        if event.symbol in self.portfolio.positions:
            print(f"     当前持仓: {self.portfolio.positions[event.symbol].quantity}")
        else:
            print(f"     当前持仓: 0")

        if quantity <= 0:
            print(f"     ⚠️  订单数量为0，跳过")
            return

        # 创建订单
        order = OrderEvent(
            symbol=event.symbol,
            timestamp=event.timestamp,
            order_type="MARKET",
            direction=direction,
            quantity=quantity,
            price=event.price,
            reason=event.reason,
            signal_id=str(id(event)),
        )

        print(f"     ✅ 订单已创建: {direction} {quantity}股 @ ${price:.2f}")

        self.events.append(order)
        self.order_count += 1

    def _on_order(self, event: OrderEvent):
        """处理订单事件"""
        print(f"\n  📋 处理订单: {event.direction} {event.quantity}股 {event.symbol}")
        super()._on_order(event)

    def _on_fill(self, event: FillEvent):
        """处理成交事件"""
        print(f"     💰 成交: {event.direction} {event.quantity}股 @ ${event.fill_price:.2f}")
        print(f"        现金: ${self.portfolio.cash:,.2f}")
        if event.symbol in self.portfolio.positions:
            pos = self.portfolio.positions[event.symbol]
            print(f"        持仓: {pos.quantity}股")
        super()._on_fill(event)


def test_order_flow():
    """测试订单流程"""
    print("=" * 60)
    print("订单流程调试")
    print("=" * 60)

    # 创建测试数据
    events = []
    current_time = datetime.now() - timedelta(hours=50)

    # 横盘
    for i in range(25):
        events.append(TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=100.0,
            volume=500000,
            bid=99.9,
            ask=100.1,
        ))
        current_time += timedelta(hours=1)

    # 突破
    for i in range(3):
        price = 100.0 + (i + 1) * 0.6
        events.append(TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=price,
            volume=900000,
            bid=price * 0.999,
            ask=price * 1.001,
        ))
        current_time += timedelta(hours=1)

    # 回落
    for i in range(5):
        price = 101.8 - (i + 1) * 0.3
        events.append(TickEvent(
            symbol="TEST",
            timestamp=current_time,
            price=max(price, 99.0),
            volume=400000,
            bid=price * 0.999,
            ask=price * 1.001,
        ))
        current_time += timedelta(hours=1)

    print(f"数据点数: {len(events)}")

    # 创建引擎
    config = {
        'min_breakout_amp': 0.005,
        'min_volume_ratio': 1.2,
        'min_resonance': 1,
        'resistance_lookback': 20,
        'validation_target_gain': 0.005,
        'validation_time_window': 5,
    }

    phase4 = Phase4Engine(config=config)
    engine = DebugBacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )

    # 运行回测
    print(f"\n开始回测...")
    metrics = engine.run(events)

    # 分析结果
    print(f"\n{'=' * 60}")
    print("结果分析")
    print(f"{'=' * 60}")
    print(f"信号总数: {engine.signal_count}")
    print(f"买入信号: {engine.buy_signal_count}")
    print(f"卖出信号: {engine.sell_signal_count}")
    print(f"订单数: {engine.order_count}")
    print(f"成交数: {engine.fill_count}")
    print(f"完成交易: {metrics.total_trades}")
    print(f"最终权益: ${metrics.final_capital:,.2f}")

    if 'TEST' in engine.portfolio.positions:
        pos = engine.portfolio.positions['TEST']
        print(f"\n最终持仓:")
        print(f"  数量: {pos.quantity}")
        print(f"  成本: ${pos.entry_price:.2f}")


if __name__ == "__main__":
    test_order_flow()
