"""
多因子动量策略回测测试

使用回测引擎验证策略表现
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import numpy as np

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.strategies.multi_factor_momentum import (
    MultiFactorMomentumStrategy,
    MarketData,
    TradingSignal,
    StrategyConfig,
    create_mock_data
)
from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.backtest.events import TickEvent


def create_realistic_price_series(
    days: int = 252,
    start_price: float = 100.0,
    drift: float = 0.0005,
    volatility: float = 0.015,
    seed: int = 42
) -> List[float]:
    """创建更真实的价格序列（几何布朗运动）"""
    np.random.seed(seed)

    prices = [start_price]
    for _ in range(days - 1):
        # 几何布朗运动
        dW = np.random.normal(0, 1)
        change = drift * prices[-1] + volatility * prices[-1] * dW
        new_price = max(prices[-1] + change, 1.0)  # 价格不能为负
        prices.append(new_price)

    return prices


def create_tick_events_from_prices(
    symbol: str,
    prices: List[float],
    start_date: datetime
) -> List[TickEvent]:
    """从价格序列创建Tick事件"""
    events = []
    for i, price in enumerate(prices):
        # 模拟日内波动
        high = price * (1 + np.random.uniform(0, 0.01))
        low = price * (1 - np.random.uniform(0, 0.01))
        open_price = np.random.uniform(low, high)
        close = price
        volume = np.random.normal(1000000, 200000)

        events.append(TickEvent(
            symbol=symbol,
            timestamp=start_date + timedelta(days=i),
            price=close,
            volume=int(max(volume, 10000)),
            bid=close * 0.999,
            ask=close * 1.001,
            bid_size=int(volume * 0.1),
            ask_size=int(volume * 0.1)
        ))

    return events


def run_backtest():
    """运行回测"""
    print("=" * 80)
    print("多因子动量策略回测")
    print("=" * 80)

    # 配置策略参数（更保守）
    config = StrategyConfig(
        momentum_weight=0.4,
        volatility_weight=0.2,
        volume_weight=0.2,
        rsi_weight=0.2,
        min_composite_score=0.25,      # 降低买入阈值
        max_composite_score=-0.25,     # 提高卖出阈值
        min_confidence=0.55,           # 降低置信度阈值
        max_position_size=0.25,
        base_position_size=0.1,
        stop_loss_pct=0.08,            # 8% 止损
        take_profit_pct=0.20           # 20% 止盈
    )

    # 创建策略
    strategy = MultiFactorMomentumStrategy(config=config)

    # 生成测试数据（1年交易日）
    print("\n生成测试数据...")
    start_date = datetime.now() - timedelta(days=252)
    prices = create_realistic_price_series(
        days=252,
        start_price=100.0,
        drift=0.0003,      # 轻微上涨趋势
        volatility=0.018,
        seed=42
    )

    tick_events = create_tick_events_from_prices("TEST", prices, start_date)
    print(f"生成 {len(tick_events)} 个Tick事件")
    print(f"价格范围: ${min(prices):.2f} - ${max(prices):.2f}")
    print(f"总收益: {(prices[-1]/prices[0] - 1)*100:.2f}%")

    # 手动回测（因为需要使用我们的策略）
    print("\n开始手动回测...")
    print("-" * 80)

    # 回测状态
    initial_capital = 100000
    cash = initial_capital
    position = 0  # 持仓数量
    entry_price = 0
    trades = []
    equity_curve = []

    # 策略信号历史
    signal_history = []

    for i, tick in enumerate(tick_events):
        # 更新策略历史数据
        market_data = MarketData(
            symbol=tick.symbol,
            timestamp=tick.timestamp,
            open=tick.price * 0.995,
            high=tick.price * 1.005,
            low=tick.price * 0.995,
            close=tick.price,
            volume=tick.volume
        )

        # 更新历史数据
        if i > 0:
            # 添加历史数据
            historical_prices = [t.price for t in tick_events[:i]]
            historical_volumes = [t.volume for t in tick_events[:i]]
            market_data.historical_closes = historical_prices
            market_data.historical_volumes = historical_volumes

        # 获取信号
        signal = strategy.generate_signal(market_data)
        signal_history.append(signal)

        # 计算当前权益
        current_equity = cash + position * tick.price
        equity_curve.append(current_equity)

        # 执行交易
        if signal.action == "BUY" and position == 0 and cash > 0:
            # 买入
            position_size = signal.position_size
            buy_amount = cash * position_size
            position = int(buy_amount / tick.price)
            cash -= position * tick.price
            entry_price = tick.price

            trades.append({
                "type": "BUY",
                "date": tick.timestamp,
                "price": tick.price,
                "quantity": position,
                "signal": signal
            })

            if len(trades) <= 3:  # 只打印前几个
                print(f"{tick.timestamp.strftime('%Y-%m-%d')} | "
                      f"BUY @ ${tick.price:.2f} | "
                      f"数量: {position} | "
                      f"综合得分: {signal.factors['composite']:.2f} | "
                      f"理由: {signal.reasoning}")

        elif signal.action == "SELL" and position > 0:
            # 卖出
            cash += position * tick.price
            pnl = (tick.price - entry_price) * position
            pnl_pct = (tick.price / entry_price - 1) * 100

            trades.append({
                "type": "SELL",
                "date": tick.timestamp,
                "price": tick.price,
                "quantity": position,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "signal": signal
            })

            if len(trades) <= 6:  # 只打印前几个
                print(f"{tick.timestamp.strftime('%Y-%m-%d')} | "
                      f"SELL @ ${tick.price:.2f} | "
                      f"盈亏: ${pnl:+.2f} ({pnl_pct:+.1f}%) | "
                      f"综合得分: {signal.factors['composite']:.2f}")

            position = 0
            entry_price = 0

        # 止损/止盈检查
        if position > 0:
            pnl_pct = (tick.price / entry_price - 1) * 100
            if pnl_pct <= -config.stop_loss_pct * 100:
                # 触发止损
                cash += position * tick.price
                pnl = (tick.price - entry_price) * position

                trades.append({
                    "type": "STOP_LOSS",
                    "date": tick.timestamp,
                    "price": tick.price,
                    "quantity": position,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct
                })

                print(f"{tick.timestamp.strftime('%Y-%m-%d')} | "
                      f"STOP_LOSS @ ${tick.price:.2f} | "
                      f"盈亏: ${pnl:+.2f} ({pnl_pct:+.1f}%)")

                position = 0
                entry_price = 0

            elif pnl_pct >= config.take_profit_pct * 100:
                # 触发止盈
                cash += position * tick.price
                pnl = (tick.price - entry_price) * position

                trades.append({
                    "type": "TAKE_PROFIT",
                    "date": tick.timestamp,
                    "price": tick.price,
                    "quantity": position,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct
                })

                print(f"{tick.timestamp.strftime('%Y-%m-%d')} | "
                      f"TAKE_PROFIT @ ${tick.price:.2f} | "
                      f"盈亏: ${pnl:+.2f} ({pnl_pct:+.1f}%)")

                position = 0
                entry_price = 0

    # 最终平仓
    if position > 0:
        final_price = tick_events[-1].price
        cash += position * final_price
        pnl = (final_price - entry_price) * position
        pnl_pct = (final_price / entry_price - 1) * 100

        trades.append({
            "type": "FINAL_CLOSE",
            "date": tick_events[-1].timestamp,
            "price": final_price,
            "quantity": position,
            "pnl": pnl,
            "pnl_pct": pnl_pct
        })

    # 计算最终结果
    final_equity = cash
    total_return = (final_equity / initial_capital - 1) * 100

    print("-" * 80)
    print("\n回测结果:")
    print(f"  初始资金: ${initial_capital:,.2f}")
    print(f"  最终资金: ${final_equity:,.2f}")
    print(f"  总收益率: {total_return:.2f}%")

    # 计算交易统计
    buy_trades = [t for t in trades if t["type"] in ["BUY", "SELL", "STOP_LOSS", "TAKE_PROFIT", "FINAL_CLOSE"]]
    completed_trades = []
    i = 0
    while i < len(trades):
        if trades[i]["type"] == "BUY":
            if i + 1 < len(trades) and trades[i + 1]["type"] in ["SELL", "STOP_LOSS", "TAKE_PROFIT", "FINAL_CLOSE"]:
                completed_trades.append({
                    "entry": trades[i],
                    "exit": trades[i + 1]
                })
                i += 2
            else:
                i += 1
        else:
            i += 1

    if completed_trades:
        win_trades = [t for t in completed_trades if t["exit"].get("pnl", 0) > 0]
        win_rate = len(win_trades) / len(completed_trades) * 100

        avg_pnl = np.mean([t["exit"].get("pnl", 0) for t in completed_trades])

        print(f"\n交易统计:")
        print(f"  完成交易: {len(completed_trades)} 笔")
        print(f"  获利交易: {len(win_trades)} 笔")
        print(f"  胜率: {win_rate:.1f}%")
        print(f"  平均盈亏: ${avg_pnl:.2f}")

        # 计算最大回撤
        equity_series = pd.Series(equity_curve)
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100

        print(f"\n风险指标:")
        print(f"  最大回撤: {max_drawdown:.2f}%")

        # 计算夏普比率
        returns = equity_series.pct_change().dropna()
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
            print(f"  夏普比率: {sharpe_ratio:.2f}")

    # 基准对比
    buy_hold_return = (prices[-1] / prices[0] - 1) * 100
    print(f"\n基准对比:")
    print(f"  买入持有收益: {buy_hold_return:.2f}%")
    print(f"  策略收益: {total_return:.2f}%")
    print(f"  超额收益: {total_return - buy_hold_return:.2f}%")

    print("\n" + "=" * 80)

    return {
        "final_equity": final_equity,
        "total_return": total_return,
        "trades": len(completed_trades) if completed_trades else 0
    }


if __name__ == "__main__":
    result = run_backtest()
