"""
调试确认层逻辑
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from adapters.quant.phase4.engine import Phase4Engine


def test_confirmation():
    """测试确认层"""
    print("=" * 60)
    print("测试确认层")
    print("=" * 60)

    phase4 = Phase4Engine(config={
        'min_breakout_amp': 0.005,
        'min_volume_ratio': 1.1,
        'min_resonance': 1,
        'resistance_lookback': 10,
    })

    # 先添加历史数据
    current_time = datetime.now()
    for i in range(15):
        tick_data = {
            "symbol": "AAPL",
            "timestamp": current_time,
            "price": 100.0,
            "volume": 500000,
        }
        phase4._update_history("AAPL", tick_data)
        current_time += timedelta(hours=1)

    # 现在测试突破
    tick_data = {
        "symbol": "AAPL",
        "timestamp": current_time,
        "price": 100.50,
        "volume": 700000,
    }

    # 更新历史
    phase4._update_history("AAPL", tick_data)

    # 获取原始信号
    raw_signals = phase4._perceive(tick_data)
    print("\n原始信号:")
    for key, value in raw_signals.items():
        print(f"  {key}: {value}")

    # 测试确认条件
    print("\n确认条件检查:")
    conditions = {
        'breakout_up': raw_signals.get('breakout_up', False),
        'volume_surge': raw_signals.get('volume_surge', False),
        'resonance_ok': raw_signals.get('resonance_count', 0) >= phase4.min_resonance,
    }

    for name, result in conditions.items():
        status = "✓" if result else "✗"
        print(f"  {status} {name}: {result}")

    print(f"\n需要全部满足才能买入: {all(conditions.values())}")

    # 执行确认
    confirmed = phase4._confirm(raw_signals, tick_data)
    print(f"\n确认结果: {confirmed}")


if __name__ == "__main__":
    test_confirmation()
