"""
完整周期测试 - Phase 4 系统

测试场景：
1. 假突破：横盘 → 突破 → 回落 → 验证失败 → 止损
2. 真突破：横盘 → 突破 → 持续上涨 → 验证成功 → 继续持有
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine


def generate_fake_breakout_data():
    """
    假突破场景：横盘 → 突破 → 快速回落
    预期：买入 → 验证失败 → 止损离场
    """
    events = []
    current_time = datetime.now() - timedelta(hours=100)

    # 阶段1: 横盘整理（25个点）
    for i in range(25):
        event = TickEvent(
            symbol="FAKE",
            timestamp=current_time,
            price=100.0,
            volume=500000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段2: 假突破（价格100.0 → 100.6 → 101.2 → 101.8）
    for i in range(3):
        price = 100.0 + (i + 1) * 0.6
        volume = 900000  # 放量

        event = TickEvent(
            symbol="FAKE",
            timestamp=current_time,
            price=price,
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段3: 验证失败（价格回落到100.5以下）
    # 这应该触发验证点失败机制，立即止损
    for i in range(10):
        price = 101.8 - (i + 1) * 0.3  # 快速回落：101.5, 101.2, 100.9, 100.6, 100.3, 100.0...
        volume = 400000

        event = TickEvent(
            symbol="FAKE",
            timestamp=current_time,
            price=max(price, 99.0),  # 最低99
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    return events


def generate_real_breakout_data():
    """
    真突破场景：横盘 → 突破 → 持续上涨
    预期：买入 → 验证成功 → 继续持有
    """
    events = []
    current_time = datetime.now() - timedelta(hours=100)

    # 阶段1: 横盘整理（25个点）
    for i in range(25):
        event = TickEvent(
            symbol="REAL",
            timestamp=current_time,
            price=100.0,
            volume=500000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段2: 真突破（价格100.0 → 100.6 → 101.2 → 101.8 → 102.4 → 103.0）
    for i in range(5):
        price = 100.0 + (i + 1) * 0.6
        volume = 900000  # 放量

        event = TickEvent(
            symbol="REAL",
            timestamp=current_time,
            price=price,
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段3: 验证成功（价格继续上涨到105）
    for i in range(15):
        price = 103.0 + i * 0.15  # 缓慢上涨
        volume = 700000

        event = TickEvent(
            symbol="REAL",
            timestamp=current_time,
            price=price,
            volume=volume,
            bid=price * 0.999,
            ask=price * 1.001,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    return events


def run_test(name: str, data: list[TickEvent], config: dict):
    """运行单个测试"""
    print(f"\n{'=' * 60}")
    print(f"测试: {name}")
    print(f"{'=' * 60}")

    print(f"数据点数: {len(data)}")
    print(f"价格范围: ${min(d.price for d in data):.2f} - ${max(d.price for d in data):.2f}")

    # 创建 Phase 4 引擎
    phase4 = Phase4Engine(config=config)

    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )

    # 运行回测
    metrics = engine.run(data)

    # 打印结果
    print(f"\n【回测结果】")
    print(f"  订单数: {engine.order_count}")
    print(f"  成交数: {engine.fill_count}")
    print(f"  完成交易: {metrics.total_trades}")
    print(f"  最终现金: ${engine.portfolio.cash:,.2f}")
    print(f"  持仓市值: ${sum(pos.market_value(engine.current_prices.get(pos.symbol, 0)) for pos in engine.portfolio.positions.values()):,.2f}")
    print(f"  总权益: ${metrics.final_capital:,.2f}")
    print(f"  总收益率: {metrics.total_return:.2%}")
    print(f"  夏普比率: {metrics.sharpe_ratio:.2f}")
    print(f"  最大回撤: {metrics.max_drawdown:.2%}")
    print(f"  胜率: {metrics.win_rate:.2%}")

    # 打印交易详情
    if metrics.trades:
        print(f"\n【交易详情】")
        for i, trade in enumerate(metrics.trades, 1):
            print(f"  交易 {i}: {trade.symbol}")
            print(f"    买入: ${trade.entry_price:.2f} at {trade.entry_time.strftime('%H:%M')}")
            print(f"    卖出: ${trade.exit_price:.2f} at {trade.exit_time.strftime('%H:%M')}")
            print(f"    盈亏: ${trade.pnl:,.2f} ({trade.return_pct:.2%})")
    else:
        print(f"\n【当前持仓】")
        for symbol, pos in engine.portfolio.positions.items():
            current_price = engine.current_prices.get(symbol, pos.entry_price)
            unrealized_pnl = pos.unrealized_pnl(current_price)
            print(f"  {symbol}:")
            print(f"    数量: {pos.quantity}")
            print(f"    成本: ${pos.entry_price:.2f}")
            print(f"    现价: ${current_price:.2f}")
            print(f"    浮盈: ${unrealized_pnl:,.2f} ({unrealized_pnl / (pos.entry_price * pos.quantity):.2%})")

    return engine, metrics


def main():
    print("=" * 60)
    print("Phase 4 完整周期测试")
    print("=" * 60)

    # 测试配置
    config = {
        'min_breakout_amp': 0.005,   # 0.5% 突破
        'min_volume_ratio': 1.2,      # 1.2倍放量
        'min_resonance': 1,           # 至少1个信号
        'resistance_lookback': 20,
        'validation_target_gain': 0.005,  # 0.5% 目标
        'validation_time_window': 5,      # 5小时窗口
    }

    print(f"\n【测试配置】")
    print(f"  最小突破幅度: {config['min_breakout_amp']:.1%}")
    print(f"  最小放量倍数: {config['min_volume_ratio']}x")
    print(f"  最小共振信号: {config['min_resonance']}个")
    print(f"  验证点目标: {config['validation_target_gain']:.1%}")
    print(f"  验证时间窗口: {config['validation_time_window']}小时")

    # 测试1: 假突破
    fake_data = generate_fake_breakout_data()
    fake_engine, fake_metrics = run_test("假突破（应止损）", fake_data, config)

    # 测试2: 真突破
    real_data = generate_real_breakout_data()
    real_engine, real_metrics = run_test("真突破（应持有）", real_data, config)

    # 总结
    print(f"\n{'=' * 60}")
    print("测试总结")
    print(f"{'=' * 60}")
    print(f"\n假突破场景:")
    print(f"  订单/成交/交易: {fake_engine.order_count}/{fake_engine.fill_count}/{fake_metrics.total_trades}")
    print(f"  最终权益: ${fake_metrics.final_capital:,.2f}")
    print(f"  收益率: {fake_metrics.total_return:.2%}")

    print(f"\n真突破场景:")
    print(f"  订单/成交/交易: {real_engine.order_count}/{real_engine.fill_count}/{real_metrics.total_trades}")
    print(f"  最终权益: ${real_metrics.final_capital:,.2f}")
    print(f"  收益率: {real_metrics.total_return:.2%}")

    # 验证预期
    print(f"\n【预期验证】")
    print(f"  假突破: 应该有1笔完整交易（买入+止损卖出）")
    if fake_metrics.total_trades >= 1:
        print(f"    ✅ 通过 - 有{fake_metrics.total_trades}笔交易")
    else:
        print(f"    ❌ 失败 - 没有{fake_metrics.total_trades}笔交易")

    print(f"  真突破: 应该持有仓位（0笔完整交易，有浮盈）")
    if real_metrics.total_trades == 0 and len(real_engine.portfolio.positions) > 0:
        print(f"    ✅ 通过 - 持有{len(real_engine.portfolio.positions)}个仓位")
    else:
        print(f"    ❌ 失败 - 交易数:{real_metrics.total_trades}, 持仓数:{len(real_engine.portfolio.positions)}")


if __name__ == "__main__":
    main()
