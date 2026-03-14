"""
A股实时交易系统 - Live A-Share Trading System

结合真实A股数据和模拟券商的完整交易系统

功能：
1. 获取实时A股行情
2. 运行多因子动量策略
3. 自动下单执行
4. 持仓管理
5. 风险控制

版本: 1.0.0
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.data.china_stock_fetcher import ChinaStockDataFetcher, get_popular_stocks
from adapters.quant.strategies.multi_factor_momentum import (
    MultiFactorMomentumStrategy,
    MarketData,
    StrategyConfig,
)
from adapters.quant.trading.simulated_broker import (
    SimulatedBroker,
    OrderSide,
    OrderType,
    OrderStatus,
)


# ============================================
# 自动交易系统
# ============================================

class AutoTradingSystem:
    """
    自动交易系统

    集成策略信号、风险管理、订单执行
    """

    def __init__(
        self,
        initial_capital: float = 1000000,
        symbols: Optional[List[str]] = None,
        config: Optional[StrategyConfig] = None
    ):
        """
        初始化交易系统

        Args:
            initial_capital: 初始资金
            symbols: 监控股票列表
            config: 策略配置
        """
        # 初始化模拟券商
        self.broker = SimulatedBroker(initial_capital=initial_capital)
        self.broker.connect_data_source()

        # 初始化策略
        self.strategy = MultiFactorMomentumStrategy(config=config)

        # 监控股票
        self.symbols = symbols or get_popular_stocks()[:5]

        # 历史数据缓存
        self.historical_data: Dict[str, List] = {
            "closes": {},
            "volumes": {}
        }

        # 风险控制
        self.max_positions = 3  # 最多持有3只股票
        self.max_single_position = 0.25  # 单只股票最大仓位25%

        print(f"\n✓ 自动交易系统初始化完成")
        print(f"  监控股票: {len(self.symbols)} 只")
        print(f"  初始资金: ¥{initial_capital:,.2f}")

    def load_historical_data(self, days: int = 120):
        """加载历史数据"""
        print(f"\n加载历史数据 ({days}天)...")

        end_date = datetime.now().strftime("%Y-%m-%d")

        for symbol in self.symbols:
            try:
                df = self.broker.data_fetcher.get_historical_data_for_strategy(
                    symbol, days=days, end_date=end_date
                )

                if not df.empty:
                    self.historical_data["closes"][symbol] = df["close"].tolist()
                    self.historical_data["volumes"][symbol] = df["volume"].tolist()
                    print(f"  ✓ {symbol}: {len(df)} 条数据")
                else:
                    print(f"  ✗ {symbol}: 无数据")

            except Exception as e:
                print(f"  ✗ {symbol}: {e}")

    def run_strategy(self):
        """运行策略分析"""
        print("\n" + "=" * 70)
        print("  策略分析")
        print("=" * 70)

        signals = {}

        for symbol in self.symbols:
            try:
                # 获取实时行情
                quotes = self.broker.data_fetcher.get_realtime_quotes([symbol])

                if symbol not in quotes:
                    print(f"  ⚠️  {symbol}: 未获取到行情")
                    continue

                quote = quotes[symbol]

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

                # 添加历史数据
                if symbol in self.historical_data["closes"]:
                    market_data.historical_closes = self.historical_data["closes"][symbol]
                    market_data.historical_volumes = self.historical_data["volumes"][symbol]

                # 生成信号
                signal = self.strategy.generate_signal(market_data)
                signals[symbol] = signal

                # 打印信号
                self._print_signal(signal, quote)

            except Exception as e:
                print(f"  ✗ {symbol}: {e}")

        return signals

    def execute_signals(self, signals: Dict):
        """执行交易信号"""
        print("\n" + "=" * 70)
        print("  执行交易")
        print("=" * 70)

        account = self.broker.get_account_info()

        for symbol, signal in signals.items():
            if signal.action == "BUY":
                self._execute_buy(symbol, signal, account)
            elif signal.action == "SELL":
                self._execute_sell(symbol, signal)

    def _execute_buy(self, symbol: str, signal, account: dict):
        """执行买入"""
        # 风险检查
        current_positions = len(self.broker.positions)

        if current_positions >= self.max_positions:
            print(f"  ⚠️  {symbol}: 持仓数量已达上限 ({self.max_positions})")
            return

        if symbol in self.broker.positions:
            print(f"  ⚠️  {symbol}: 已持有")
            return

        # 计算买入数量
        available_cash = account["cash"]
        max_investment = available_cash * self.max_single_position

        # 获取当前价格
        quotes = self.broker.data_fetcher.get_realtime_quotes([symbol])
        if symbol not in quotes:
            print(f"  ✗ {symbol}: 无法获取当前价格")
            return

        current_price = quotes[symbol].close
        max_quantity = int(max_investment / current_price)
        quantity = (max_quantity // 100) * 100  # 取整到100的倍数

        if quantity < 100:
            print(f"  ✗ {symbol}: 资金不足")
            return

        # 下单
        print(f"\n  🟢 {symbol} 买入信号")
        print(f"     价格: ¥{current_price:.2f}")
        print(f"     数量: {quantity} 股")
        print(f"     金额: ¥{quantity * current_price:,.2f}")
        print(f"     仓位建议: {signal.position_size:.0%}")
        print(f"     置信度: {signal.confidence:.0%}")

        order = self.broker.place_order(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=quantity
        )

        if order.status == OrderStatus.FILLED:
            print(f"     ✓ 买入成交: {order.filled_quantity}股 @ ¥{order.filled_price:.2f}")
        elif order.status == OrderStatus.REJECTED:
            print(f"     ✗ 买入被拒: {order.reason}")

    def _execute_sell(self, symbol: str, signal):
        """执行卖出"""
        if symbol not in self.broker.positions:
            print(f"  ⚠️  {symbol}: 无持仓")
            return

        position = self.broker.positions[symbol]

        # 下单（卖出全部）
        print(f"\n  🔴 {symbol} 卖出信号")
        print(f"     持仓: {position.quantity} 股")
        print(f"     成本: ¥{position.avg_price:.2f}")
        print(f"     浮盈: ¥{position.unrealized_pnl:+,.2f} ({position.unrealized_pnl_pct:+.1f}%)")

        order = self.broker.place_order(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=position.quantity
        )

        if order.status == OrderStatus.FILLED:
            print(f"     ✓ 卖出成交: {order.filled_quantity}股 @ ¥{order.filled_price:.2f}")
            pnl = (order.filled_price - position.avg_price) * order.filled_quantity
            print(f"     盈亏: ¥{pnl:+,.2f}")

    def _print_signal(self, signal, quote):
        """打印信号"""
        icons = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}
        icon = icons.get(signal.action, "❓")

        print(f"\n{icon} {signal.symbol} | {quote.name}")
        print(f"    价格: ¥{quote.close:.2f}")
        print(f"    信号: {signal.action:4} | 置信度: {signal.confidence:.0%}")
        print(f"    综合: {signal.factors['composite']:+.2f}")

        if signal.action != "HOLD":
            if signal.target_price:
                gain = (signal.target_price / quote.close - 1) * 100
                print(f"    目标: ¥{signal.target_price:.2f} (+{gain:.1f}%)")
            if signal.stop_loss:
                loss = (signal.stop_loss / quote.close - 1) * 100
                print(f"    止损: ¥{signal.stop_loss:.2f} ({loss:.1f}%)")

    def print_account_summary(self):
        """打印账户摘要"""
        print("\n" + "=" * 70)
        print("  账户摘要")
        print("=" * 70)

        account = self.broker.get_account_info()
        snapshot = self.broker.get_daily_snapshot()

        print(f"\n总资产: ¥{account['total_asset']:,.2f}")
        print(f"现金: ¥{account['cash']:,.2f}")
        print(f"持仓市值: ¥{account['market_value']:,.2f}")
        print(f"总盈亏: ¥{account['total_pnl']:+,.2f} ({account['total_pnl_pct']:+.2f}%)")

        if snapshot["positions"]:
            print(f"\n持仓明细:")
            for pos in snapshot["positions"]:
                print(f"  • {pos['symbol']}: {pos['quantity']}股 | "
                      f"成本¥{pos['avg_price']:.2f} | "
                      f"市值¥{pos['market_value']:,.2f} | "
                      f"盈亏{pos['unrealized_pnl_pct']:+.1f}%")
        else:
            print(f"\n当前无持仓")

        print(f"\n今日成交: {snapshot['today_trades']} 笔")
        print(f"挂单数量: {snapshot['pending_orders']} 单")

    def run_once(self):
        """运行一次完整的交易流程"""
        print("\n" + "=" * 70)
        print(f"  A股自动交易系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # 1. 运行策略
        signals = self.run_strategy()

        # 2. 执行交易
        if signals:
            self.execute_signals(signals)

        # 3. 更新持仓市值
        quotes = self.broker.data_fetcher.get_realtime_quotes(self.symbols)
        self.broker.update_positions(quotes)

        # 4. 打印账户摘要
        self.print_account_summary()

    def run_loop(self, interval_seconds: int = 60):
        """循环运行"""
        print(f"\n进入自动交易模式...")
        print(f"刷新间隔: {interval_seconds}秒")
        print("按 Ctrl+C 停止\n")

        try:
            while True:
                self.run_once()

                if interval_seconds > 0:
                    print(f"\n等待 {interval_seconds}秒后刷新...")
                    time.sleep(interval_seconds)
                else:
                    break

        except KeyboardInterrupt:
            print("\n\n交易系统已停止")


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    print("=" * 70)
    print("  A股实时交易系统")
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

    # 热门股票
    symbols = get_popular_stocks()[:5]

    # 创建交易系统
    trader = AutoTradingSystem(
        initial_capital=1000000,
        symbols=symbols,
        config=config
    )

    # 加载历史数据
    trader.load_historical_data(days=120)

    # 运行一次
    trader.run_once()

    print("\n✓ 交易完成！")


if __name__ == "__main__":
    main()
