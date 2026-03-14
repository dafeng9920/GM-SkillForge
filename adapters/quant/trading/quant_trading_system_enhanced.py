"""
A股量化交易系统 - 增强版（技术面+机构面）

完整整合机构分析模块，实现"抱紧机构大腿"策略

版本: 2.0.0
创建日期: 2026-03-09
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.trading.fast_data_fetcher import FastDataFetcher
from adapters.quant.strategies.enhanced_multi_factor_strategy import (
    EnhancedMultiFactorStrategy,
    EnhancedStrategyConfig,
    TradingSignal
)
from adapters.quant.trading.simulated_broker import (
    SimulatedBroker,
    OrderSide,
    OrderType,
    OrderStatus
)
from adapters.quant.trading.trade_journal import TradeJournal
from adapters.quant.trading.trading_dashboard import TradingDashboard
from adapters.quant.data.china_stock_fetcher import get_popular_stocks


class EnhancedQuantTradingSystem:
    """
    增强版A股量化交易系统

    技术面 + 机构面共振策略
    """

    def __init__(
        self,
        initial_capital: float = 1000000,
        symbols: Optional[List[str]] = None,
        data_dir: str = "trading_data",
        config: Optional[EnhancedStrategyConfig] = None
    ):
        """初始化增强交易系统"""
        print("=" * 80)
        print("  🚀 A股量化交易系统 - 增强版（技术面+机构面）")
        print("=" * 80)

        # 使用高性能数据获取器
        self.data_fetcher = FastDataFetcher(preferred_source="akshare")

        # 初始化模拟券商
        self.broker = SimulatedBroker(initial_capital=initial_capital)
        self.broker.data_fetcher = self.data_fetcher.base_fetcher
        self.broker.connect_data_source()

        # 初始化增强策略
        if config is None:
            config = EnhancedStrategyConfig(
                # 技术面权重
                momentum_weight=0.25,
                volatility_weight=0.10,
                volume_weight=0.10,
                rsi_weight=0.05,

                # 机构面权重
                institution_holding_weight=0.15,
                dragon_tiger_weight=0.10,
                north_bound_weight=0.15,
                block_trade_weight=0.10,

                # 阈值
                min_composite_score=0.25,
                min_institution_score=0.3,
                min_confidence=0.55,

                # 仓位
                max_position_size=0.25,
                base_position_size=0.12,
                stop_loss_pct=0.08,
                take_profit_pct=0.20
            )

        self.strategy = EnhancedMultiFactorStrategy(config=config)

        # 其他组件
        self.journal = TradeJournal(data_dir=data_dir)
        self.dashboard = TradingDashboard(self.broker, self.journal)

        # 风险管理
        self.max_positions = 5
        self.max_single_position = 0.2

        # 监控股票
        self.symbols = symbols or get_popular_stocks()[:10]

        # 系统状态
        self.is_running = False
        self.trade_count = 0

        print(f"\n✓ 增强交易系统初始化完成")
        print(f"  初始资金: ¥{initial_capital:,.2f}")
        print(f"  监控股票: {len(self.symbols)} 只")
        print(f"  策略模式: 技术面 + 机构面共振")

    def load_historical_data(self, days: int = 120):
        """快速加载历史数据"""
        print(f"\n快速加载历史数据 ({days}天)...")

        start = time.time()
        hist_data = self.data_fetcher.get_historical_data_fast(self.symbols, days=days)
        elapsed = time.time() - start

        print(f"✓ 历史数据加载完成 ({elapsed:.1f}秒)")

    def generate_signals(self) -> Dict[str, TradingSignal]:
        """快速生成交易信号"""
        signals = {}

        # 批量获取实时行情
        start = time.time()
        quotes = self.data_fetcher.get_realtime_quotes_fast(self.symbols)
        elapsed = time.time() - start

        print(f"  获取实时行情: {len(quotes)} 只股票 ({elapsed:.2f}秒)")

        # 并发生成信号
        for symbol, quote in quotes.items():
            try:
                # 创建市场数据
                from adapters.quant.strategies.multi_factor_momentum import MarketData
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=quote.timestamp,
                    open=quote.open,
                    high=quote.high,
                    low=quote.low,
                    close=quote.close,
                    volume=quote.volume
                )

                # 生成信号（包含机构分析）
                signal = self.strategy.generate_signal(market_data)
                signals[symbol] = signal

            except Exception as e:
                print(f"  ✗ {symbol}: {e}")

        return signals

    def execute_trades(self, signals: Dict[str, TradingSignal]):
        """执行交易"""
        account = self.broker.get_account_info()
        positions = self.broker.get_positions()

        for symbol, signal in signals.items():
            if signal.action == "BUY":
                self._execute_buy(symbol, signal, account, positions)
            elif signal.action == "SELL":
                self._execute_sell(symbol, signal, positions)

    def _execute_buy(self, symbol: str, signal: TradingSignal, account: dict, positions: dict):
        """执行买入（增强版）"""
        # 快速风险检查
        if len(positions) >= self.max_positions:
            return
        if symbol in positions:
            return
        if signal.confidence < 0.55:
            return

        # 获取当前价格
        quotes = self.data_fetcher.get_realtime_quotes_fast([symbol])
        if symbol not in quotes:
            return

        current_price = quotes[symbol].close
        max_investment = account['cash'] * self.max_single_position
        quantity = int(max_investment / current_price)
        quantity = (quantity // 100) * 100

        if quantity < 100:
            return

        # 增强的买入信号显示
        print(f"\n  🟢 {symbol} 买入信号")
        print(f"     ════════════════════════════════════════════════════════")
        print(f"     价格: ¥{current_price:.2f}")
        print(f"     数量: {quantity} 股")
        print(f"     金额: ¥{quantity * current_price:,.2f}")
        print(f"     置信度: {signal.confidence:.0%}")
        print(f"     综合得分: {signal.factors['composite']:+.2f}")
        print(f"     ════════════════════════════════════════════════════════")

        # 技术面因子
        print(f"     【技术面分析】")
        print(f"       动量: {signal.factors['momentum']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['momentum'])

        print(f"       波动: {signal.factors['volatility']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['volatility'])

        print(f"       成交: {signal.factors['volume']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['volume'])

        print(f"       RSI:  {signal.factors['rsi']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['rsi'])

        # 机构面因子
        print(f"     ════════════════════════════════════════════════════════")
        print(f"     【机构面分析】")

        inst_score = signal.factors.get('institution_composite', 0)

        print(f"       机构持仓: {signal.factors['institution_holding']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['institution_holding'])

        print(f"       龙虎榜: {signal.factors['dragon_tiger']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['dragon_tiger'])

        print(f"       北向资金: {signal.factors['north_bound']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['north_bound'])

        print(f"       大宗交易: {signal.factors['block_trade']:+.2f}  │ ", end="")
        self._print_factor_bar(signal.factors['block_trade'])

        print(f"     ════════════════════════════════════════════════════════")
        print(f"     【机构评级】")

        # 机构评级
        if inst_score > 0.5:
            rating = "⭐⭐⭐⭐⭐ 强烈看好"
        elif inst_score > 0.3:
            rating = "⭐⭐⭐⭐ 机构加持"
        elif inst_score > 0:
            rating = "⭐⭐⭐ 中性偏好"
        elif inst_score > -0.2:
            rating = "⭐⭐ 关注度低"
        else:
            rating = "⭐ 机构撤离"

        print(f"       综合评级: {rating} ({inst_score:+.2f})")

        # 机构共振判断
        tech_good = signal.factors['momentum'] > 0.2 or signal.factors['volume'] > 0.2
        inst_good = inst_score > 0.3

        if tech_good and inst_good:
            print(f"       共振状态: ✅ 技术面+机构面共振，上涨概率高")
        elif tech_good:
            print(f"       共振状态: ⚠️  技术面好但机构关注度一般")
        elif inst_good:
            print(f"       共振状态: ⚠️  机构加持但技术面待观察")
        else:
            print(f"       共振状态: ❌ 暂无共振，等待确认")

        print(f"     ════════════════════════════════════════════════════════")
        print(f"     目标价: ¥{signal.target_price:.2f} (+{((signal.target_price / current_price - 1) * 100):.1f}%)")
        print(f"     止损价: ¥{signal.stop_loss:.2f} ({((signal.stop_loss / current_price - 1) * 100):.1f}%)")
        print(f"     买入理由: {signal.reasoning}")
        print(f"     ════════════════════════════════════════════════════════")

        # 下单
        order = self.broker.place_order(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=quantity
        )

        if order.status == OrderStatus.FILLED:
            self.trade_count += 1
            print(f"     ✓ 买入成交: {order.filled_quantity}股 @ ¥{order.filled_price:.2f}")

    def _print_factor_bar(self, score: float, max_len: int = 20):
        """打印因子条形图"""
        bar_len = int(abs(score) * max_len)
        if score > 0:
            bar = "🟢" * bar_len
        elif score < 0:
            bar = "🔴" * bar_len
        else:
            bar = "⚪" * max_len

        print(f"{bar}")

    def _execute_sell(self, symbol: str, signal: TradingSignal, positions: dict):
        """执行卖出"""
        if symbol not in positions:
            return

        position = positions[symbol]

        # 止损止盈检查
        if position.unrealized_pnl_pct < -8:
            reason = "止损"
        elif position.unrealized_pnl_pct > 20:
            reason = "止盈"
        elif signal.action == "SELL" and signal.confidence > 0.6:
            reason = "策略信号"
        else:
            return

        print(f"\n  🔴 {symbol} 卖出信号")
        print(f"     持仓: {position.quantity} 股")
        print(f"     理由: {reason}")
        print(f"     浮盈: {position.unrealized_pnl_pct:+.2f}%")

        # 下单
        order = self.broker.place_order(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=position.quantity
        )

        if order.status == OrderStatus.FILLED:
            pnl = (order.filled_price - position.avg_price) * order.filled_quantity
            print(f"     ✓ 卖出成交: {order.filled_quantity}股 @ ¥{order.filled_price:.2f}")
            print(f"     盈亏: ¥{pnl:+,.2f}")

    def run_once(self):
        """运行一次完整的交易流程"""
        total_start = time.time()

        print("\n" + "=" * 80)
        print(f"  增强交易周期 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # 1. 更新持仓市值
        start = time.time()
        quotes = self.data_fetcher.get_realtime_quotes_fast(self.symbols)
        self.broker.update_positions(quotes)
        print(f"  更新持仓: {time.time() - start:.2f}秒")

        # 2. 生成交易信号
        start = time.time()
        signals = self.generate_signals()
        print(f"  生成信号: {time.time() - start:.2f}秒")

        # 3. 更新仪表板信号
        self.dashboard.update_signals(signals)

        # 4. 执行交易
        start = time.time()
        self.execute_trades(signals)
        print(f"  执行交易: {time.time() - start:.2f}秒")

        # 5. 保存快照
        snapshot = self.broker.get_daily_snapshot()
        self.journal.save_daily_snapshot(snapshot)

        # 6. 显示账户摘要
        self._print_account_summary()

        total_time = time.time() - total_start
        print(f"\n⚡ 总耗时: {total_time:.2f}秒")

        return signals

    def _print_account_summary(self):
        """打印账户摘要"""
        account = self.broker.get_account_info()

        print("\n" + "=" * 80)
        print("  📊 账户摘要")
        print("=" * 80)
        print(f"\n总资产: ¥{account['total_asset']:,.2f}")
        print(f"现金: ¥{account['cash']:,.2f}")
        print(f"持仓市值: ¥{account['market_value']:,.2f}")
        print(f"总盈亏: ¥{account['total_pnl']:+,.2f} ({account['total_pnl_pct']:+.2f}%)")
        print(f"持仓数: {account['positions']}")
        print("=" * 80)

    def run_auto(self, interval_seconds: int = 30):
        """自动运行模式"""
        self.is_running = True

        print("\n开始增强自动交易...")
        print(f"刷新间隔: {interval_seconds} 秒")
        print("按 Ctrl+C 停止\n")

        try:
            while self.is_running:
                self.run_once()

                if interval_seconds > 0:
                    print(f"\n等待 {interval_seconds} 秒后刷新...")
                    time.sleep(interval_seconds)
                else:
                    break

        except KeyboardInterrupt:
            print("\n\n交易系统已停止")
            self.is_running = False


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='A股量化交易系统 - 增强版')
    parser.add_argument('--capital', type=float, default=1000000, help='初始资金')
    parser.add_argument('--symbols', type=str, nargs='+', help='监控股票代码')
    parser.add_argument('--interval', type=int, default=30, help='刷新间隔(秒)')
    parser.add_argument('--once', action='store_true', help='只运行一次')
    parser.add_argument('--data-dir', type=str, default='trading_data', help='数据目录')

    args = parser.parse_args()

    # 创建增强交易系统
    system = EnhancedQuantTradingSystem(
        initial_capital=args.capital,
        symbols=args.symbols,
        data_dir=args.data_dir
    )

    # 加载历史数据
    system.load_historical_data(days=120)

    # 运行
    if args.once:
        system.run_once()
    else:
        system.run_auto(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
