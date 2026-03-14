"""
调试验证点机制

追踪验证点的创建、检查和触发
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine
from adapters.quant.phase4.validation import ValidationPoint


def test_validation_mechanism():
    """测试验证点机制"""
    print("=" * 60)
    print("验证点机制调试")
    print("=" * 60)

    # 创建测试数据：假突破
    events = []
    current_time = datetime.now() - timedelta(hours=50)

    # 横盘（25个点）
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

    # 记录突破开始时间
    breakout_start_time = current_time

    # 突破（3个点）
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

    # 回落（10个点）- 这应该触发验证失败
    for i in range(10):
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

    print(f"\n数据准备完成:")
    print(f"  总Tick数: {len(events)}")
    print(f"  横盘结束: tick 25, 价格 100.0")
    print(f"  突破开始: tick 26, 时间 {events[25].timestamp.strftime('%H:%M')}")
    print(f"  回落开始: tick 29, 时间 {events[28].timestamp.strftime('%H:%M')}")

    # 配置验证窗口为5小时
    config = {
        'min_breakout_amp': 0.005,
        'min_volume_ratio': 1.2,
        'min_resonance': 1,
        'resistance_lookback': 20,
        'validation_target_gain': 0.005,
        'validation_time_window': 5,  # 5小时
    }

    # 创建带有调试输出的引擎
    class DebugPhase4Engine(Phase4Engine):
        def __init__(self, config=None):
            super().__init__(config)
            self.buy_tick = None
            self.buy_price = None
            self.buy_time = None

        def on_tick(self, tick_data, portfolio_state):
            signals = super().on_tick(tick_data, portfolio_state)

            # 检测买入
            for signal in signals:
                if signal.get('signal_type') == 'BUY':
                    self.buy_tick = len([e for e in events if e.timestamp <= tick_data['timestamp']])
                    self.buy_price = signal['price']
                    self.buy_time = tick_data['timestamp']
                    print(f"\n✅ 买入信号触发!")
                    print(f"   Tick: {self.buy_tick}")
                    print(f"   价格: ${self.buy_price:.2f}")
                    print(f"   时间: {self.buy_time.strftime('%H:%M')}")
                    print(f"   原因: {signal['reason']}")

                    # 检查验证点是否创建
                    if 'TEST' in self.validation_manager.validation_points:
                        vp = self.validation_manager.validation_points['TEST']
                        print(f"\n📍 验证点已创建:")
                        print(f"   入场价: ${vp.entry_price:.2f}")
                        print(f"   目标价: ${vp.target_price:.2f}")
                        print(f"   入场时间: {vp.entry_time.strftime('%H:%M')}")
                        print(f"   截止时间: {vp.deadline.strftime('%H:%M')}")
                        print(f"   时间窗口: {vp.deadline - vp.entry_time}")

                elif signal.get('signal_type') == 'SELL':
                    elapsed = (tick_data['timestamp'] - self.buy_time).total_seconds() / 3600 if self.buy_time else 0
                    print(f"\n❌ 卖出信号触发!")
                    print(f"   价格: ${signal['price']:.2f}")
                    print(f"   原因: {signal['reason']}")
                    print(f"   买入后时间: {elapsed:.1f}小时")

            return signals

    phase4 = DebugPhase4Engine(config=config)

    # 运行回测
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )

    print(f"\n开始回测...")
    metrics = engine.run(events)

    # 分析结果
    print(f"\n{'=' * 60}")
    print("回测结果分析")
    print(f"{'=' * 60}")

    print(f"\n订单数: {engine.order_count}")
    print(f"成交数: {engine.fill_count}")
    print(f"完成交易: {metrics.total_trades}")

    # 检查验证点状态
    if 'TEST' in phase4.validation_manager.validation_points:
        vp = phase4.validation_manager.validation_points['TEST']
        print(f"\n验证点最终状态:")
        print(f"  状态: {vp.status}")
        print(f"  入场价: ${vp.entry_price:.2f}")
        print(f"  目标价: ${vp.target_price:.2f}")

    # 检查持仓
    if 'TEST' in engine.portfolio.positions:
        pos = engine.portfolio.positions['TEST']
        current_price = engine.current_prices.get('TEST', pos.entry_price)
        pnl = pos.unrealized_pnl(current_price)
        print(f"\n当前持仓:")
        print(f"  数量: {pos.quantity}")
        print(f"  成本: ${pos.entry_price:.2f}")
        print(f"  现价: ${current_price:.2f}")
        print(f"  浮盈: ${pnl:,.2f}")

    # 计算买入后的时间
    if phase4.buy_time:
        final_time = events[-1].timestamp
        elapsed = (final_time - phase4.buy_time).total_seconds() / 3600
        print(f"\n时间分析:")
        print(f"  买入时间: {phase4.buy_time.strftime('%H:%M')}")
        print(f"  最终时间: {final_time.strftime('%H:%M')}")
        print(f"  已过时间: {elapsed:.1f}小时")
        print(f"  验证窗口: {config['validation_time_window']}小时")

        if elapsed > config['validation_time_window']:
            print(f"\n⚠️  验证窗口已过，应该触发验证检查!")
            current_price = engine.current_prices.get('TEST', phase4.buy_price)
            target_price = phase4.buy_price * (1 + config['validation_target_gain'])
            print(f"   当前价: ${current_price:.2f}")
            print(f"   目标价: ${target_price:.2f}")
            if current_price < target_price:
                print(f"   ❌ 未达标，应该触发止损!")
            else:
                print(f"   ✅ 已达标，应该继续持有")


if __name__ == "__main__":
    test_validation_mechanism()
