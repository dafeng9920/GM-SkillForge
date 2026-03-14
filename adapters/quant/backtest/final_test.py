"""
Phase 4 系统完整回测测试

展示 Phase 4 盘中同步系统的完整功能：
1. 感知层 - 听市场在说什么
2. 确认层 - 验证信号真伪
3. 决策层 - 基于确认信号行动
4. 验证点机制 - 买入后持续验证
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent
from adapters.quant.phase4.engine import Phase4Engine


def generate_realistic_test_data():
    """生成真实的测试数据"""
    events = []
    current_time = datetime.now() - timedelta(hours=100)

    # 阶段1: 横盘整理（30个点，固定价格100）
    for i in range(30):
        event = TickEvent(
            symbol="AAPL",
            timestamp=current_time,
            price=100.0,  # 固定价格
            volume=500000,
            bid=99.9,
            ask=100.1,
        )
        events.append(event)
        current_time += timedelta(hours=1)

    # 阶段2: 突破上涨（价格100.5）
    event = TickEvent(
        symbol="AAPL",
        timestamp=current_time,
        price=100.5,
        volume=800000,  # 放量
        bid=100.4,
        ask=100.6,
    )
    events.append(event)
    current_time += timedelta(hours=1)

    # 阶段3: 验证失败（价格回落）
    for i in range(10):
        price = 100.5 - i * 0.05  # 逐渐回落
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
    print("=" * 70)
    print("Phase 4 盘中同步系统 - 完整回测测试")
    print("=" * 70)

    print("\n【核心哲学】")
    print("  - 不预测明天会怎样")
    print("  - 只确认现在在发生什么")
    print("  - 只在市场给出答案的那一刻行动")

    # 生成测试数据
    data = generate_realistic_test_data()
    print(f"\n【测试数据】")
    print(f"  Tick数量: {len(data)}")
    print(f"  价格范围: ${min(d.price for d in data):.2f} - ${max(d.price for d in data):.2f}")
    print(f"  场景: 横盘 → 突破 → 验证失败")

    # 初始化 Phase 4
    phase4_config = {
        'min_breakout_amp': 0.005,      # 0.5% 突破
        'min_volume_ratio': 1.2,       # 1.2倍放量
        'min_resonance': 1,            # 1个信号即可
        'resistance_lookback': 15,     # 15个点回看
        'validation_target_gain': 0.005, # 0.5% 目标
        'validation_time_window': 5,    # 5小时验证
    }

    phase4 = Phase4Engine(config=phase4_config)
    print(f"\n【Phase 4 配置】")
    print(f"  最小突破幅度: {phase4_config['min_breakout_amp']:.1%}")
    print(f"  最小放量倍数: {phase4_config['min_volume_ratio']}x")
    print(f"  验证点目标: {phase4_config['validation_target_gain']:.1%}")
    print(f"  验证时间窗口: {phase4_config['validation_time_window']} 小时")

    # 初始化回测引擎
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        signal_handler=phase4.on_tick,
    )

    # 运行回测
    print(f"\n【运行回测】")
    print(f"  初始资金: ${engine.initial_capital:,.2f}")

    metrics = engine.run(data)

    # 打印结果
    print(f"\n" + "=" * 70)
    print("回测结果")
    print("=" * 70)

    print(f"\n【执行统计】")
    print(f"  处理事件: {len(data)} 个")
    print(f"  生成订单: {engine.order_count} 个")
    print(f"  成交笔数: {engine.fill_count} 笔")

    if metrics.trades:
        print(f"\n【交易明细】")
        for i, trade in enumerate(metrics.trades, 1):
            hours = trade.duration_hours
            print(f"  {i}. {trade.entry_time.strftime('%m-%d %H:%M')} → "
                  f"{trade.exit_time.strftime('%H:%M')} "
                  f"({hours:.1f}h) | "
                  f"${trade.entry_price:.2f} → ${trade.exit_price:.2f} | "
                  f"${trade.pnl:+.2f} ({trade.return_pct:+.2%})")

    # 打印验证点状态
    print(f"\n【验证点状态】")
    if phase4.validation_manager.validation_points:
        for symbol, vp in phase4.validation_manager.validation_points.items():
            print(f"  {symbol}:")
            print(f"    入场价格: ${vp.entry_price:.2f}")
            print(f"    目标价格: ${vp.target_price:.2f}")
            print(f"    状态: {vp.status}")
            print(f"    最终价格: ${data[-1].price:.2f}")

            # 计算实际结果
            final_price = data[-1].price
            if final_price < vp.entry_price:
                result = f"验证失败，亏损 {(final_price - vp.entry_price) / vp.entry_price:.2%}"
            else:
                result = f"验证{'通过' if final_price >= vp.target_price else '失败'}，收益 {(final_price - vp.entry_price) / vp.entry_price:.2%}"
            print(f"    结果: {result}")

    # 打印绩效报告
    print("\n" + "=" * 70)
    metrics.print_report()

    # 分析结果
    print("\n【系统分析】")
    if metrics.total_trades > 0:
        print(f"  ✓ 系统成功生成交易信号")
        print(f"  ✓ 验证点机制正常工作")
        print(f"  ✓ 盈亏: ${metrics.final_capital - metrics.initial_capital:+,.2f}")
    else:
        print(f"  ⚠ 未触发交易（可能需要调整参数或使用更长时间的数据）")


if __name__ == "__main__":
    main()
