"""
A股实时策略交易器 - Live A-Share Strategy Trader

使用真实A股数据运行多因子动量策略
支持实时行情获取和策略信号生成

版本: 1.0.0
创建日期: 2026-03-09
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import time

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.data.china_stock_fetcher import (
    ChinaStockDataFetcher,
    StockQuote,
    get_popular_stocks
)
from adapters.quant.strategies.multi_factor_momentum import (
    MultiFactorMomentumStrategy,
    MarketData,
    StrategyConfig,
    TradingSignal
)


# ============================================
# 实时交易器
# ============================================

class LiveAShareTrader:
    """
    A股实时策略交易器

    功能:
    1. 获取真实A股行情数据
    2. 运行多因子动量策略
    3. 生成实时交易信号
    4. 监控策略表现
    """

    def __init__(
        self,
        symbols: List[str],
        config: Optional[StrategyConfig] = None
    ):
        """
        初始化交易器

        Args:
            symbols: 监控的股票代码列表
            config: 策略配置
        """
        self.symbols = symbols
        self.strategy = MultiFactorMomentumStrategy(config=config)

        # 初始化数据获取器
        try:
            self.data_fetcher = ChinaStockDataFetcher(preferred_source="akshare")
            print("✓ A股数据源连接成功")
        except Exception as e:
            print(f"✗ 数据源连接失败: {e}")
            print("  请安装 akshare: pip install akshare")
            raise

        # 历史数据缓存
        self.historical_data: Dict[str, pd.DataFrame] = {}
        self.last_signals: Dict[str, TradingSignal] = {}

        # 加载历史数据
        print("\n加载历史数据...")
        self._load_historical_data()

    def _load_historical_data(self, days: int = 120):
        """加载历史数据用于策略计算"""
        end_date = datetime.now().strftime("%Y-%m-%d")

        for symbol in self.symbols:
            try:
                print(f"  加载 {symbol}...")
                df = self.data_fetcher.get_historical_data_for_strategy(
                    symbol,
                    days=days,
                    end_date=end_date
                )

                if not df.empty:
                    self.historical_data[symbol] = df

                    # 更新策略的历史数据
                    for _, row in df.iterrows():
                        market_data = MarketData(
                            symbol=symbol,
                            timestamp=row["date"],
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=float(row["volume"])
                        )
                        self.strategy.update_market_data(market_data)

                    print(f"    ✓ 已加载 {len(df)} 条数据")
                else:
                    print(f"    ✗ 未获取到数据")

            except Exception as e:
                print(f"    ✗ 加载失败: {e}")

    def get_realtime_quotes(self) -> Dict[str, StockQuote]:
        """获取实时行情"""
        try:
            quotes = self.data_fetcher.get_realtime_quotes(self.symbols)
            return quotes
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            return {}

    def generate_signals(self, quotes: Dict[str, StockQuote]) -> Dict[str, TradingSignal]:
        """生成交易信号"""
        signals = {}

        for symbol, quote in quotes.items():
            try:
                # 创建市场数据
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=quote.timestamp,
                    open=quote.open,
                    high=quote.high,
                    low=quote.low,
                    close=quote.close,
                    volume=quote.volume
                )

                # 获取历史数据
                if symbol in self.historical_data:
                    hist_df = self.historical_data[symbol]
                    market_data.historical_closes = hist_df["close"].tolist()
                    market_data.historical_volumes = hist_df["volume"].tolist()

                # 生成信号
                signal = self.strategy.generate_signal(market_data)
                signals[symbol] = signal

            except Exception as e:
                print(f"生成 {symbol} 信号失败: {e}")

        return signals

    def print_signal_card(self, signal: TradingSignal, quote: Optional[StockQuote] = None):
        """打印信号卡片"""
        icons = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}
        icon = icons.get(signal.action, "❓")

        print(f"\n{icon} {signal.symbol}")
        print("─" * 60)

        if quote:
            print(f"价格: ${quote.close:.2f} | 名称: {quote.name}")
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
                print(f"目标: ${signal.target_price:.2f} │ ", end="")
            if signal.stop_loss:
                print(f"止损: ${signal.stop_loss:.2f}")
        print(f"理由: {signal.reasoning}")

    def run_once(self):
        """运行一次策略分析"""
        print("\n" + "=" * 70)
        print(f"  A股策略分析 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # 获取实时行情
        print("\n获取实时行情...")
        quotes = self.get_realtime_quotes()

        if not quotes:
            print("未能获取到实时行情，使用历史数据的最新收盘价")
            # 使用历史数据的最新收盘价
            for symbol in self.symbols:
                if symbol in self.historical_data and not self.historical_data[symbol].empty:
                    latest = self.historical_data[symbol].iloc[-1]
                    quotes[symbol] = StockQuote(
                        symbol=symbol,
                        name=symbol,
                        timestamp=pd.to_datetime(latest["date"]),
                        open=float(latest["open"]),
                        high=float(latest["high"]),
                        low=float(latest["low"]),
                        close=float(latest["close"]),
                        volume=float(latest["volume"])
                    )

        print(f"获取到 {len(quotes)} 只股票的行情")

        # 生成信号
        print("\n生成交易信号...")
        signals = self.generate_signals(quotes)

        # 打印结果
        print("\n" + "=" * 70)
        print("  策略分析结果")
        print("=" * 70)

        for symbol in self.symbols:
            if symbol in signals:
                self.print_signal_card(signals[symbol], quotes.get(symbol))
                self.last_signals[symbol] = signals[symbol]

        # 统计汇总
        actions = [s.action for s in signals.values()]
        buy_count = actions.count("BUY")
        sell_count = actions.count("SELL")
        hold_count = actions.count("HOLD")

        print("\n" + "=" * 70)
        print("  信号汇总")
        print("=" * 70)
        print(f"  买入信号: {buy_count} │ 卖出信号: {sell_count} │ 观望: {hold_count}")

        if signals:
            avg_confidence = sum(s.confidence for s in signals.values()) / len(signals)
            print(f"  平均置信度: {avg_confidence:.1%}")

        # 找出综合得分最高的股票
        sorted_signals = sorted(
            signals.items(),
            key=lambda x: x[1].factors['composite'],
            reverse=True
        )

        if sorted_signals:
            best_symbol, best_signal = sorted_signals[0]
            print(f"\n  综合得分最高: {best_symbol} ({best_signal.factors['composite']:+.2f})")

        print("=" * 70)

        return signals

    def run_watch(self, interval_seconds: int = 60):
        """持续监控模式"""
        print("\n进入持续监控模式...")
        print(f"刷新间隔: {interval_seconds} 秒")
        print("按 Ctrl+C 停止\n")

        try:
            while True:
                self.run_once()

                if interval_seconds > 0:
                    print(f"\n等待 {interval_seconds} 秒后刷新...")
                    time.sleep(interval_seconds)
                else:
                    break

        except KeyboardInterrupt:
            print("\n\n监控已停止")


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    print("=" * 70)
    print("  A股实时策略交易器")
    print("=" * 70)

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

    # 获取热门股票
    symbols = get_popular_stocks()[:5]  # 只取前5只作为演示

    print(f"\n监控股票: {', '.join(symbols)}")

    try:
        # 创建交易器
        trader = LiveAShareTrader(symbols, config=config)

        # 运行一次分析
        trader.run_once()

        # 询问是否进入持续监控
        print("\n是否进入持续监控模式？")
        print("  [1] 是 - 每60秒刷新一次")
        print("  [2] 否 - 只运行一次后退出")

        # 在实际运行中，这里可以添加用户输入
        # 为了演示，我们只运行一次
        print("\n演示模式：只运行一次分析")

    except Exception as e:
        print(f"\n运行失败: {e}")
        print("\n请确保已安装 akshare:")
        print("  pip install akshare")


if __name__ == "__main__":
    main()
