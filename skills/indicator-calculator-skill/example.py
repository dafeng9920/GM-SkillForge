"""
Indicator Calculator - 使用示例
"""

import asyncio
import pandas as pd
import numpy as np
from indicator_calculator_skill import IndicatorCalculator


async def main():
    """示例：计算技术指标"""

    # 创建示例数据
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    np.random.seed(42)

    # 模拟价格数据（随机游走）
    close = 100 + np.cumsum(np.random.randn(100) * 2)

    data = pd.DataFrame({
        "timestamp": dates,
        "open": close * (1 + np.random.randn(100) * 0.01),
        "high": close * (1 + abs(np.random.randn(100)) * 0.02),
        "low": close * (1 - abs(np.random.randn(100)) * 0.02),
        "close": close,
        "volume": np.random.randint(1000000, 10000000, 100),
    })
    data = data.set_index("timestamp")

    # 初始化指标计算器
    calculator = IndicatorCalculator()

    # 计算指标
    indicators_config = [
        {"name": "SMA", "params": {"period": 20}},
        {"name": "EMA", "params": {"period": 12}},
        {"name": "RSI", "params": {"period": 14}},
        {"name": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}},
        {"name": "BOLLINGER_BANDS", "params": {"period": 20, "std_dev": 2}},
    ]

    results = await calculator.calculate(data, indicators_config)

    # 打印结果
    print("技术指标计算结果:")
    print("=" * 60)

    for name, values in results.items():
        if isinstance(values, dict):
            print(f"\n{name}:")
            for key, val in values.items():
                print(f"  {key}: {val.iloc[-1]:.4f}")
        else:
            print(f"\n{name}: {values.iloc[-1]:.4f}")

    # 或者一次性计算所有指标
    print("\n\n" + "=" * 60)
    print("所有指标计算结果:")
    all_indicators = await calculator.calculate_all(data)
    print(all_indicators.tail())


if __name__ == "__main__":
    asyncio.run(main())
