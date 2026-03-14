"""
回测引擎测试脚本

使用模拟数据测试回测引擎和 Phase 4 系统
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


def generate_mock_data(
    symbol: str = "TEST",
    days: int = 5,
    price: float = 100.0,
    volatility: float = 0.02,
    trend: float = 0.0001,
) -> list:
    """
    生成模拟Tick数据

    Args:
        symbol: 股票代码
        days: 天数
        price: 初始价格
        volatility: 波动率
        trend: 趋势（正数为上涨，负数为下跌）

    Returns:
        TickEvent列表
    """
    import random

    events = []
    current_time = datetime.now() - timedelta(days=days)
    current_price = price

    # 每天生成24个数据点（每小时）
    total_points = days * 24

    for i in range(total_points):
        # 价格随机游走
        change = random.gauss(trend, volatility / 24) * current_price
        current_price = max(current_price + change, 1.0)  # 价格不能低于1

        # 生成成交量
        volume = int(random.gauss(1000000, 200000))

        event = TickEvent(
            symbol=symbol,
            timestamp=current_time,
            price=current_price,
            volume=volume,
            bid=current_price * 0.999,  # 买价略低于当前价
            ask=current_price * 1.001,  # 卖价略高于当前价
        )
        events.append(event)

        # 移动到下一小时
        current_time += timedelta(hours=1)

    return events


def test_backtest():
    """测试回测引擎"""
    print("=" * 60)
    print("回测引擎测试")
    print("=" * 60)

    # 1. 生成模拟数据
    print("\n1. 生成模拟数据...")
    data = generate_mock_data(
        symbol="AAPL",
        days=10,
        price=150.0,
        volatility=0.02,
        trend=0.0001,  # 轻微上涨趋势
    )
    print(f"   生成了 {len(data)} 条Tick数据")
    print(f"   时间范围: {data[0].timestamp} 至 {data[-1].timestamp}")
    print(f"   价格范围: ${min(d.price for d in data):.2f} - ${max(d.price for d in data):.2f}")

    # 2. 初始化 Phase 4 引擎
    print("\n2. 初始化 Phase 4 引擎...")
    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.01,      # 降低阈值以便更容易触发
        'min_volume_ratio': 1.2,       # 降低阈值
        'min_resonance': 1,            # 降低阈值
        'validation_target_gain': 0.005, # 0.5% 目标涨幅
        'validation_time_window': 5,   # 5小时验证窗口
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
    print(f"   完成! 处理了 {len(data)} 个事件")

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
        print("\n6. 没有交易发生")

    return metrics


def test_validation_points():
    """测试验证点机制"""
    print("\n" + "=" * 60)
    print("验证点机制测试")
    print("=" * 60)

    from adapters.quant.phase4.validation import ValidationPointManager

    manager = ValidationPointManager(
        target_gain=0.01,  # 1% 目标
        time_window=30,    # 30分钟窗口
    )

    now = datetime.now()
    entry_price = 100.0

    # 创建验证点
    vp = manager.create_validation_point(
        symbol="TEST",
        entry_price=entry_price,
        entry_time=now,
    )
    print(f"\n验证点创建:")
    print(f"  入场价格: ${vp.entry_price:.2f}")
    print(f"  目标价格: ${vp.target_price:.2f}")
    print(f"  截止时间: {vp.deadline}")
    print(f"  状态: {vp.status}")

    # 测试场景1: 价格上涨超过目标
    print("\n场景1: 价格上涨到 $101.50")
    result = manager.check_validation("TEST", 101.50, now + timedelta(minutes=10))
    print(f"  状态: {result.status}")
    print(f"  行动: {result.action}")
    print(f"  原因: {result.reason}")
    print(f"  置信度: {result.confidence}")

    # 测试场景2: 超时未达标
    print("\n场景2: 30分钟后价格仍为 $100.50")
    result = manager.check_validation("TEST", 100.50, now + timedelta(minutes=31))
    print(f"  状态: {result.status}")
    print(f"  行动: {result.action}")
    print(f"  原因: {result.reason}")
    print(f"  置信度: {result.confidence}")


if __name__ == "__main__":
    # 测试回测引擎
    metrics = test_backtest()

    # 测试验证点机制
    test_validation_points()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
