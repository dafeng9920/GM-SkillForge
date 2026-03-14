"""
A股策略演示 - Demo A-Share Strategy

使用模拟的A股数据运行多因子动量策略
演示策略在真实市场环境下的表现

版本: 1.0.0
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.strategies.multi_factor_momentum import (
    MultiFactorMomentumStrategy,
    MarketData,
    StrategyConfig,
    create_mock_data
)


# ============================================
# A股热门股票数据（模拟）
# ============================================

def get_realistic_a_share_data(symbol: str, days: int = 120) -> list:
    """
    生成真实的A股模拟数据

    基于A股特征：
    - 涨跌停限制（±10%）
    - T+1 交易制度
    - 日内波动有限
    - 市场情绪影响
    """
    # 不同股票的特征参数
    stock_profiles = {
        "600519.SH": {"name": "贵州茅台", "base_price": 1700, "volatility": 0.015, "trend": 0.002},
        "000001.SZ": {"name": "平安银行", "base_price": 12, "volatility": 0.025, "trend": 0.000},
        "000002.SZ": {"name": "万科A", "base_price": 8, "volatility": 0.03, "trend": -0.001},
        "600030.SH": {"name": "中信证券", "base_price": 22, "volatility": 0.028, "trend": 0.001},
        "300750.SZ": {"name": "宁德时代", "base_price": 180, "volatility": 0.035, "trend": 0.003},
        "002594.SZ": {"name": "比亚迪", "base_price": 220, "volatility": 0.032, "trend": 0.002},
    }

    profile = stock_profiles.get(symbol, {
        "name": "股票",
        "base_price": 100,
        "volatility": 0.02,
        "trend": 0.000
    })

    return create_mock_data(
        symbol=symbol,
        days=days,
        start_price=profile["base_price"],
        trend=profile["trend"],
        volatility=profile["volatility"],
        seed=hash(symbol) % 10000
    )


# ============================================
# A股策略演示
# ============================================

def run_a_share_strategy_demo():
    """运行A股策略演示"""
    print("=" * 80)
    print("  A股多因子动量策略演示")
    print("  模拟真实A股市场环境")
    print("=" * 80)

    # 创建策略配置
    config = StrategyConfig(
        momentum_weight=0.5,
        volatility_weight=0.2,
        volume_weight=0.15,
        rsi_weight=0.15,
        min_composite_score=0.15,
        max_composite_score=-0.15,
        min_confidence=0.55,
        max_position_size=0.25,
        base_position_size=0.12,
        stop_loss_pct=0.08,
        take_profit_pct=0.20
    )

    # 创建策略
    strategy = MultiFactorMomentumStrategy(config=config)

    # A股热门股票
    a_share_stocks = [
        "600519.SH",  # 贵州茅台
        "000001.SZ",  # 平安银行
        "000002.SZ",  # 万科A
        "600030.SH",  # 中信证券
        "300750.SZ",  # 宁德时代
        "002594.SZ",  # 比亚迪
    ]

    print(f"\n监控股票: {len(a_share_stocks)} 只")
    for stock in a_share_stocks:
        print(f"  • {stock}")

    # 分析每只股票
    print("\n" + "=" * 80)
    print("  加载历史数据并分析...")
    print("=" * 80)

    results = []

    for i, symbol in enumerate(a_share_stocks):
        print(f"\n[{i+1}/{len(a_share_stocks)}] 分析 {symbol}...")

        # 重置策略
        strategy = MultiFactorMomentumStrategy(config=config)

        # 获取历史数据
        historical_data = get_realistic_a_share_data(symbol, days=120)

        # 加载历史数据到策略
        for data in historical_data[:-1]:
            strategy.update_market_data(data)

        # 分析最新数据
        signal = strategy.process_tick(historical_data[-1])

        # 获取股票信息
        latest = historical_data[-1]
        price_change = (latest.close - historical_data[0].close) / historical_data[0].close * 100

        results.append({
            "symbol": symbol,
            "signal": signal,
            "price": latest.close,
            "change": price_change
        })

        # 打印信号
        print_signal_card(signal, latest.close, price_change)

    # 统计汇总
    print("\n" + "=" * 80)
    print("  策略分析汇总")
    print("=" * 80)

    # 按信号分组
    buy_signals = [r for r in results if r["signal"].action == "BUY"]
    sell_signals = [r for r in results if r["signal"].action == "SELL"]
    hold_signals = [r for r in results if r["signal"].action == "HOLD"]

    print(f"\n信号分布:")
    print(f"  🟢 买入: {len(buy_signals)} 只")
    print(f"  🔴 卖出: {len(sell_signals)} 只")
    print(f"  ⚪ 观望: {len(hold_signals)} 只")

    # 买入信号详情
    if buy_signals:
        print(f"\n推荐买入股票:")
        for r in buy_signals:
            signal = r["signal"]
            print(f"  • {r['symbol']}")
            print(f"    价格: ¥{r['price']:.2f} | 近期涨跌: {r['change']:+.1f}%")
            print(f"    综合得分: {signal.factors['composite']:+.2f} | 置信度: {signal.confidence:.0%}")
            if signal.target_price:
                print(f"    目标价位: ¥{signal.target_price:.2f} (+{((signal.target_price/r['price']-1)*100):.1f}%)")
            if signal.stop_loss:
                print(f"    止损价位: ¥{signal.stop_loss:.2f} ({((signal.stop_loss/r['price']-1)*100):.1f}%)")

    # 按综合得分排序
    print(f"\n综合得分排名:")
    sorted_results = sorted(results, key=lambda x: x["signal"].factors['composite'], reverse=True)
    for i, r in enumerate(sorted_results, 1):
        action_icon = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}[r["signal"].action]
        print(f"  {i}. {action_icon} {r['symbol']} | 得分: {r['signal'].factors['composite']:+.2f} | 涨跌: {r['change']:+.1f}%")

    # 风险提示
    print("\n" + "=" * 80)
    print("  ⚠️  风险提示")
    print("=" * 80)
    print("""
  1. 本演示使用模拟数据，实际市场表现可能有所不同
  2. A股市场有涨跌停限制（±10%），实际交易需注意
  3. 策略基于历史数据，不保证未来收益
  4. 投资有风险，入市需谨慎
  5. 建议结合基本面分析和市场环境综合判断
    """)

    print("=" * 80)

    return results


def print_signal_card(signal, price: float, change_pct: float):
    """打印信号卡片"""
    icons = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}
    icon = icons.get(signal.action, "❓")

    print(f"\n{icon} {signal.symbol}")
    print("─" * 60)
    print(f"价格: ¥{price:.2f} | 涨跌: {change_pct:+.1f}%")
    print(f"信号: {signal.action:4} | 置信度: {signal.confidence:.0%}")
    print("─" * 60)

    # 因子条形图
    factors = [
        ("动量", signal.factors['momentum']),
        ("波动", signal.factors['volatility']),
        ("成交", signal.factors['volume']),
        ("RSI", signal.factors['rsi']),
    ]
    for name, score in factors:
        bar_len = int(abs(score) * 20)
        bar = "█" * bar_len
        sign = "+" if score > 0 else ""
        print(f"  {name:4} │{sign}{score:.2f}│ {bar}")

    print("─" * 60)
    print(f"综合: {signal.factors['composite']:+.2f} │ 仓位: {signal.position_size:.0%}")

    if signal.action != "HOLD":
        if signal.target_price:
            target_gain = (signal.target_price / price - 1) * 100
            print(f"目标: ¥{signal.target_price:.2f} (+{target_gain:.1f}%)")
        if signal.stop_loss:
            stop_loss = (signal.stop_loss / price - 1) * 100
            print(f"止损: ¥{signal.stop_loss:.2f} ({stop_loss:.1f}%)")
    print(f"理由: {signal.reasoning}")


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    try:
        results = run_a_share_strategy_demo()

        print("\n✓ 演示完成！")
        print("\n下一步:")
        print("  1. 安装真实数据源: pip install akshare")
        print("  2. 运行实时分析: python adapters/quant/strategies/live_a_share_trader.py")
        print("  3. 查看策略文档: docs/QUANT_STRATEGY_GUIDE.md")

    except Exception as e:
        print(f"\n✗ 运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
