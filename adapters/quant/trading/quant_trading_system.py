"""
A股量化交易系统 - A-Share Quantitative Trading System

完整的A股量化交易系统，整合所有模块：
- 实时数据获取
- 多因子策略
- 模拟交易
- 风险管理
- 交易日志
- 实时监控

版本: 1.0.0
创建日期: 2026-03-09
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import json

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.data.china_stock_fetcher import (
    ChinaStockDataFetcher,
    get_popular_stocks
)
from adapters.quant.strategies.multi_factor_momentum import (
    MultiFactorMomentumStrategy,
    MarketData,
    StrategyConfig,
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


# ============================================
# 风险管理器
# ============================================

class RiskManager:
    """
    风险管理器

    提供风险控制功能：
    - 仓位控制
    - 止损/止盈
    - 最大回撤控制
    - 单日最大亏损限制
    """

    def __init__(
        self,
        max_positions: int = 5,            # 最大持仓数
        max_single_position: float = 0.2,   # 单只股票最大仓位
        max_daily_loss: float = 0.02,       # 单日最大亏损比例
        max_drawdown: float = 0.10,         # 最大回撤
        stop_loss_pct: float = 0.08,        # 默认止损比例
        take_profit_pct: float = 0.20       # 默认止盈比例
    ):
        self.max_positions = max_positions
        self.max_single_position = max_single_position
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

        self.daily_start_equity = None
        self.peak_equity = None

        print(f"✓ 风险管理器初始化完成")
        print(f"  最大持仓: {max_positions} 只")
        print(f"  单股最大仓位: {max_single_position:.0%}")
        print(f"  单日最大亏损: {max_daily_loss:.1%}")

    def check_entry(
        self,
        symbol: str,
        signal: TradingSignal,
        account: dict,
        positions: dict
    ) -> tuple[bool, str]:
        """
        检查是否可以入场

        Returns:
            (是否允许, 原因)
        """
        # 检查持仓数量
        if len(positions) >= self.max_positions:
            return False, f"持仓数量已达上限 ({self.max_positions})"

        # 检查是否已持有
        if symbol in positions:
            return False, f"已持有 {symbol}"

        # 检查单日亏损
        if self.daily_start_equity:
            daily_pnl_pct = (account['total_asset'] / self.daily_start_equity - 1)
            if daily_pnl_pct < -self.max_daily_loss:
                return False, f"今日亏损已达上限 ({daily_pnl_pct:.2%})"

        # 检查最大回撤
        if self.peak_equity and account['total_asset'] < self.peak_equity * (1 - self.max_drawdown):
            return False, f"最大回撤超限 ({((account['total_asset'] / self.peak_equity - 1)):.2%})"

        # 检查信号置信度
        if signal.confidence < 0.55:
            return False, f"信号置信度不足 ({signal.confidence:.0%})"

        return True, "通过"

    def check_exit(
        self,
        symbol: str,
        position: object,
        signal: TradingSignal
    ) -> tuple[bool, str]:
        """
        检查是否需要出场

        Returns:
            (是否出场, 原因)
        """
        # 检查止损
        if position.unrealized_pnl_pct < -self.stop_loss_pct * 100:
            return True, f"止损触发 ({position.unrealized_pnl_pct:.2%})"

        # 检查止盈
        if position.unrealized_pnl_pct > self.take_profit_pct * 100:
            return True, f"止盈触发 ({position.unrealized_pnl_pct:.2%})"

        # 检查卖出信号
        if signal.action == "SELL" and signal.confidence > 0.6:
            return True, f"策略卖出信号 (置信度{signal.confidence:.0%})"

        return False, "持有"

    def calculate_position_size(
        self,
        signal: TradingSignal,
        account: dict,
        current_price: float
    ) -> int:
        """
        计算仓位大小

        Returns:
            买入数量（100的整数倍）
        """
        # 基础仓位
        base_size = account['cash'] * self.max_single_position

        # 根据信号置信度调整
        size = base_size * (0.5 + signal.confidence)

        # 根据信号仓位建议调整
        size = account['cash'] * signal.position_size

        # 限制在最大仓位内
        size = min(size, account['cash'] * self.max_single_position)

        # 转换为股数（100的整数倍）
        quantity = int(size / current_price)
        quantity = (quantity // 100) * 100

        # 至少100股
        return max(quantity, 100)

    def update_daily_start(self, equity: float):
        """更新每日起始权益"""
        if self.daily_start_equity is None:
            self.daily_start_equity = equity
            self.peak_equity = equity

    def update_peak_equity(self, equity: float):
        """更新峰值权益"""
        if self.peak_equity is None or equity > self.peak_equity:
            self.peak_equity = equity


# ============================================
# 主交易系统
# ============================================

class QuantTradingSystem:
    """
    A股量化交易系统

    完整的量化交易系统，整合所有功能模块
    """

    def __init__(
        self,
        initial_capital: float = 1000000,
        symbols: Optional[List[str]] = None,
        data_dir: str = "trading_data",
        config: Optional[StrategyConfig] = None
    ):
        """
        初始化交易系统

        Args:
            initial_capital: 初始资金
            symbols: 监控股票列表
            data_dir: 数据保存目录
            config: 策略配置
        """
        print("=" * 80)
        print("  🚀 A股量化交易系统")
        print("=" * 80)

        # 初始化组件
        self.broker = SimulatedBroker(initial_capital=initial_capital)
        self.broker.connect_data_source()

        self.journal = TradeJournal(data_dir=data_dir)
        self.dashboard = TradingDashboard(self.broker, self.journal)
        self.risk_manager = RiskManager()

        # 初始化策略
        if config is None:
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

        self.strategy = MultiFactorMomentumStrategy(config=config)

        # 监控股票
        self.symbols = symbols or get_popular_stocks()[:10]

        # 历史数据缓存
        self.historical_data: Dict[str, List] = {
            "closes": {},
            "volumes": {}
        }

        # 系统状态
        self.is_running = False
        self.trade_count = 0
        self.last_signal_time = None

        print(f"\n✓ 交易系统初始化完成")
        print(f"  初始资金: ¥{initial_capital:,.2f}")
        print(f"  监控股票: {len(self.symbols)} 只")
        print(f"  数据目录: {data_dir}")

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

    def generate_signals(self) -> Dict[str, TradingSignal]:
        """生成交易信号"""
        signals = {}

        for symbol in self.symbols:
            try:
                # 获取实时行情
                quotes = self.broker.data_fetcher.get_realtime_quotes([symbol])

                if symbol not in quotes:
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

            except Exception as e:
                print(f"  ✗ {symbol}: {e}")

        return signals

    def execute_trades(self, signals: Dict[str, TradingSignal]):
        """执行交易"""
        account = self.broker.get_account_info()
        positions = self.broker.get_positions()

        # 更新风险管理器
        current_equity = account['total_asset']
        self.risk_manager.update_peak_equity(current_equity)

        for symbol, signal in signals.items():
            if signal.action == "BUY":
                self._execute_buy(symbol, signal, account, positions)
            elif signal.action == "SELL":
                self._execute_sell(symbol, signal, positions)

    def _execute_buy(self, symbol: str, signal: TradingSignal, account: dict, positions: dict):
        """执行买入"""
        # 风险检查
        allowed, reason = self.risk_manager.check_entry(symbol, signal, account, positions)
        if not allowed:
            return

        # 获取当前价格
        quotes = self.broker.data_fetcher.get_realtime_quotes([symbol])
        if symbol not in quotes:
            return

        current_price = quotes[symbol].close

        # 计算仓位
        quantity = self.risk_manager.calculate_position_size(signal, account, current_price)

        if quantity < 100:
            return

        # 下单
        order = self.broker.place_order(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=quantity
        )

        if order.status == OrderStatus.FILLED:
            self.trade_count += 1

            # 记录交易
            trade_record = {
                'trade_id': f'TRADE{self.trade_count:06d}',
                'order_id': order.order_id,
                'symbol': symbol,
                'side': 'BUY',
                'quantity': quantity,
                'price': order.filled_price,
                'commission': order.commission,
                'stamp_duty': 0,
                'trade_time': order.filled_at.isoformat(),
                'pnl': 0
            }
            self.journal.save_trade(trade_record)

            print(f"\n  ✓ 买入成交: {symbol} {quantity}股 @ ¥{order.filled_price:.2f}")

    def _execute_sell(self, symbol: str, signal: TradingSignal, positions: dict):
        """执行卖出"""
        if symbol not in positions:
            return

        position = positions[symbol]

        # 风险检查
        should_exit, reason = self.risk_manager.check_exit(symbol, position, signal)
        if not should_exit:
            return

        # 下单
        order = self.broker.place_order(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=position.quantity
        )

        if order.status == OrderStatus.FILLED:
            self.trade_count += 1

            # 计算盈亏
            pnl = (order.filled_price - position.avg_price) * order.filled_quantity

            # 记录交易
            trade_record = {
                'trade_id': f'TRADE{self.trade_count:06d}',
                'order_id': order.order_id,
                'symbol': symbol,
                'side': 'SELL',
                'quantity': order.filled_quantity,
                'price': order.filled_price,
                'commission': order.commission,
                'stamp_duty': order.filled_quantity * order.filled_price * self.broker.stamp_duty_rate,
                'trade_time': order.filled_at.isoformat(),
                'pnl': pnl
            }
            self.journal.save_trade(trade_record)

            print(f"\n  ✓ 卖出成交: {symbol} {order.filled_quantity}股 @ ¥{order.filled_price:.2f}")
            print(f"     盈亏: ¥{pnl:+,.2f} ({position.unrealized_pnl_pct:+.2f}%) | 原因: {reason}")

    def run_once(self):
        """运行一次完整的交易流程"""
        print("\n" + "=" * 80)
        print(f"  交易周期 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # 1. 更新持仓市值
        quotes = self.broker.data_fetcher.get_realtime_quotes(self.symbols)
        self.broker.update_positions(quotes)

        # 2. 生成交易信号
        print("\n生成交易信号...")
        signals = self.generate_signals()

        # 3. 更新仪表板信号
        self.dashboard.update_signals(signals)

        # 4. 执行交易
        print("\n执行交易...")
        self.execute_trades(signals)

        # 5. 保存快照
        snapshot = self.broker.get_daily_snapshot()
        self.journal.save_daily_snapshot(snapshot)

        # 6. 显示仪表板
        self.dashboard.render()

        return signals

    def run_auto(self, interval_seconds: int = 60):
        """自动运行模式"""
        self.is_running = True
        self.risk_manager.update_daily_start(self.broker.get_account_info()['total_asset'])

        print("\n开始自动交易...")
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

        # 最终保存
        self.dashboard.save_snapshot()
        self.journal.export_trade_report()

    def get_report(self) -> dict:
        """获取系统报告"""
        account = self.broker.get_account_info()
        performance = self.journal.get_performance_summary()

        return {
            'timestamp': datetime.now().isoformat(),
            'account': account,
            'performance': performance,
            'positions': len(self.broker.positions),
            'total_trades': self.trade_count,
            'symbols': self.symbols
        }


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='A股量化交易系统')
    parser.add_argument('--capital', type=float, default=1000000, help='初始资金')
    parser.add_argument('--symbols', type=str, nargs='+', help='监控股票代码')
    parser.add_argument('--interval', type=int, default=60, help='刷新间隔(秒)')
    parser.add_argument('--once', action='store_true', help='只运行一次')
    parser.add_argument('--data-dir', type=str, default='trading_data', help='数据目录')

    args = parser.parse_args()

    # 创建交易系统
    system = QuantTradingSystem(
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
