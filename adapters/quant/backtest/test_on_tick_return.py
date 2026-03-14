"""
直接测试 on_tick 返回值
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.phase4.engine import Phase4Engine


def test_on_tick_return():
    """测试 on_tick 返回值"""
    print("=" * 60)
    print("测试 on_tick 返回值")
    print("=" * 60)

    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.005,
        'min_volume_ratio': 1.1,
        'min_resonance': 1,
        'resistance_lookback': 10,
    })

    portfolio_state = {
        "cash": 100000,
        "positions": {},  # 空仓
        "equity": 100000,
    }

    current_time = datetime.now()

    # 添加15个横盘数据点
    print("\n添加15个横盘数据点...")
    for i in range(15):
        tick_data = {
            "symbol": "AAPL",
            "timestamp": current_time,
            "price": 100.0,
            "volume": 500000,
        }
        signals = phase4.on_tick(tick_data, portfolio_state)
        current_time += timedelta(hours=1)

    print(f"历史数据: {len(phase4.price_history['AAPL'])} 个点")

    # 测试突破
    print("\n测试突破点...")
    tick_data = {
        "symbol": "AAPL",
        "timestamp": current_time,
        "price": 100.50,  # 突破
        "volume": 700000,  # 放量
    }

    signals = phase4.on_tick(tick_data, portfolio_state)

    print(f"价格: ${tick_data['price']:.2f}")
    print(f"成交量: {tick_data['volume']:,}")
    print(f"返回信号: {len(signals)} 个")

    if signals:
        for sig in signals:
            print(f"\n信号详情:")
            for key, value in sig.items():
                print(f"  {key}: {value}")
    else:
        print("没有返回信号!")

    # 调试：检查内部状态
    print(f"\n内部状态:")
    print(f"  历史数据点数: {len(phase4.price_history.get('AAPL', []))}")
    print(f"  成交量数据点数: {len(phase4.volume_history.get('AAPL', []))}")


if __name__ == "__main__":
    test_on_tick_return()
