"""
调试 Phase 4 信号检测
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.phase4.engine import Phase4Engine


def test_signal_detection():
    """测试信号检测"""
    print("=" * 60)
    print("Phase 4 信号检测调试")
    print("=" * 60)

    # 初始化 Phase 4
    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.005,     # 0.5% 突破
        'min_volume_ratio': 1.1,       # 1.1倍放量
        'min_resonance': 1,            # 1个信号即可
        'resistance_lookback': 10,     # 10个点回看
        'validation_target_gain': 0.005,
        'validation_time_window': 10,
    })

    # 模拟数据：横盘后突破
    current_time = datetime.now()
    portfolio_state = {
        "cash": 100000,
        "positions": {},
        "equity": 100000,
    }

    # 阶段1: 横盘（10个点，价格100）
    print("\n阶段1: 横盘整理")
    for i in range(10):
        tick_data = {
            "symbol": "AAPL",
            "timestamp": current_time,
            "price": 100.0,
            "volume": 500000,
        }

        # 使用 on_tick 而不是直接调用 _perceive
        signals = phase4.on_tick(tick_data, portfolio_state)

        # 打印感知层的状态
        if "AAPL" in phase4.price_history:
            prices = phase4.price_history["AAPL"]
            volumes = phase4.volume_history["AAPL"]
            print(f"  点{i+1}: 价格={tick_data['price']:.2f}, "
                  f"历史数据={len(prices)}个, "
                  f"最高价=${max(prices):.2f}, "
                  f"平均量={sum(volumes[-10:]) / min(10, len(volumes)):,.0f}")

        current_time += timedelta(hours=1)

    # 阶段2: 突破（价格涨到101）
    print("\n阶段2: 突破上涨")
    for i in range(5):
        price = 100.0 + (i + 1) * 0.2  # 100.2, 100.4, 100.6, 100.8, 101.0
        volume = 600000 + i * 100000  # 放量

        tick_data = {
            "symbol": "AAPL",
            "timestamp": current_time,
            "price": price,
            "volume": volume,
        }

        signals = phase4.on_tick(tick_data, portfolio_state)

        # 打印信号状态
        print(f"  点{i+1}: 价格={price:.2f}, 成交量={volume:,}, 信号={len(signals)}个")
        if signals:
            for sig in signals:
                print(f"       {sig['signal_type']} - 置信度={sig['confidence']:.2f}, 原因={sig['reason']}")

        current_time += timedelta(hours=1)

    # 检查历史数据
    print("\n历史价格统计:")
    if "AAPL" in phase4.price_history:
        prices = phase4.price_history["AAPL"]
        print(f"  数据点数: {len(prices)}")
        print(f"  最近10个点: {prices[-10:]}")
        print(f"  最高价: ${max(prices):.2f}")
        print(f"  最低价: ${min(prices):.2f}")

    print("\n历史成交量统计:")
    if "AAPL" in phase4.volume_history:
        volumes = phase4.volume_history["AAPL"]
        print(f"  数据点数: {len(volumes)}")
        print(f"  最近10个点: {volumes[-10:]}")
        print(f"  平均量: {sum(volumes[-20:]) / min(20, len(volumes)):,.0f}")


if __name__ == "__main__":
    test_signal_detection()
