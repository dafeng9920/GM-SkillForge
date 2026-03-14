"""
详细调试 Phase 4 信号
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.phase4.engine import Phase4Engine


def test_detailed():
    """详细测试"""
    print("=" * 60)
    print("Phase 4 详细调试")
    print("=" * 60)

    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.005,
        'min_volume_ratio': 1.1,
        'min_resonance': 1,
        'resistance_lookback': 10,
    })

    # 先添加10个横盘数据点
    current_time = datetime.now()
    for i in range(10):
        tick_data = {
            "symbol": "AAPL",
            "timestamp": current_time,
            "price": 100.0,
            "volume": 500000,
        }
        phase4._update_history("AAPL", tick_data)
        current_time += timedelta(hours=1)

    print("\n横盘后历史数据:")
    print(f"  价格: {phase4.price_history['AAPL']}")
    print(f"  最高价: ${max(phase4.price_history['AAPL']):.2f}")

    # 现在测试突破
    print("\n测试突破:")

    # 测试价格100.50（应该突破）
    tick_data = {
        "symbol": "AAPL",
        "timestamp": current_time,
        "price": 100.50,  # 100 * 1.005 = 100.50
        "volume": 600000,
    }

    # 先更新历史（但不包括当前点）
    phase4._update_history("AAPL", tick_data)

    # 调用感知
    signals = phase4._perceive(tick_data)

    print(f"  当前价格: ${tick_data['price']:.2f}")
    print(f"  突破: {signals.get('breakout_up', False)}")
    print(f"  放量: {signals.get('volume_surge', False)}")
    print(f"  共振: {signals.get('resonance_count', 0)}")

    # 检查历史数据（当前价格已添加）
    print(f"\n历史数据（包括当前）:")
    print(f"  价格: {phase4.price_history['AAPL']}")
    print(f"  长度: {len(phase4.price_history['AAPL'])}")

    # 检查历史数据（不包括当前）
    history = phase4.price_history['AAPL'][:-1]
    print(f"  历史价格（不含当前）: {history}")
    print(f"  历史最高: ${max(history):.2f}")
    print(f"  突破阈值: ${max(history) * 1.005:.2f}")
    print(f"  当前价格: ${tick_data['price']:.2f}")
    print(f"  是否突破: {tick_data['price'] > max(history) * 1.005}")


if __name__ == "__main__":
    test_detailed()
