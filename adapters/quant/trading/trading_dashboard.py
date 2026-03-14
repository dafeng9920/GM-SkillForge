"""
实时交易监控仪表板 - Trading Dashboard

提供实时的交易系统监控，包括：
- 账户状态监控
- 持仓监控
- 订单状态监控
- 绩效指标监控
- 实时信号展示

版本: 1.0.0
创建日期: 2026-03-09
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.trading.simulated_broker import (
    SimulatedBroker,
    OrderSide,
    OrderType,
    OrderStatus,
    Position,
    Order
)
from adapters.quant.trading.trade_journal import TradeJournal
from adapters.quant.strategies.multi_factor_momentum import TradingSignal


# ============================================
# 仪表板数据模型
# ============================================

@dataclass
class DashboardState:
    """仪表板状态"""
    timestamp: datetime
    account_info: dict
    positions: List[Position]
    pending_orders: List[Order]
    recent_trades: List
    active_signals: Dict[str, TradingSignal]
    performance_metrics: dict


# ============================================
# 交易监控仪表板
# ============================================

class TradingDashboard:
    """
    交易监控仪表板

    实时展示交易系统的各项指标
    """

    def __init__(
        self,
        broker: SimulatedBroker,
        journal: TradeJournal
    ):
        """
        初始化仪表板

        Args:
            broker: 模拟券商实例
            journal: 交易日志实例
        """
        self.broker = broker
        self.journal = journal
        self.active_signals: Dict[str, TradingSignal] = {}
        self.last_update = None

        print("✓ 交易监控仪表板初始化完成")

    def update_signals(self, signals: Dict[str, TradingSignal]):
        """更新活跃信号"""
        self.active_signals = signals

    def get_state(self) -> DashboardState:
        """获取当前状态"""
        account_info = self.broker.get_account_info()
        positions = list(self.broker.get_positions().values())
        pending_orders = self.broker.get_orders(status=OrderStatus.PENDING)
        recent_trades = self.broker.get_trades(limit=20)

        return DashboardState(
            timestamp=datetime.now(),
            account_info=account_info,
            positions=positions,
            pending_orders=pending_orders,
            recent_trades=recent_trades,
            active_signals=self.active_signals,
            performance_metrics=self.journal.get_performance_summary()
        )

    def render(self):
        """渲染仪表板"""
        state = self.get_state()

        # 清屏（跨平台）
        self._clear_screen()

        # 标题
        self._print_header(state.timestamp)

        # 账户概览
        self._print_account_overview(state.account_info)

        # 持仓详情
        self._print_positions(state.positions)

        # 活跃信号
        self._print_active_signals(state.active_signals)

        # 挂单信息
        if state.pending_orders:
            self._print_pending_orders(state.pending_orders)

        # 绩效指标
        self._print_performance_metrics(state.performance_metrics)

        # 最近交易
        if state.recent_trades:
            self._print_recent_trades(state.recent_trades)

        self.last_update = datetime.now()

    def _clear_screen(self):
        """清屏"""
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')

    def _print_header(self, timestamp: datetime):
        """打印标题"""
        print("=" * 80)
        print("  🚀 A股量化交易系统 - 实时监控仪表板")
        print("=" * 80)
        print(f"  时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  市场状态: {'🟢 交易中' if self._is_market_open() else '⚫ 休市'}")
        print("=" * 80)

    def _is_market_open(self) -> bool:
        """判断市场是否开盘"""
        now = datetime.now()
        current_time = now.time()

        # A股交易时间：9:30-11:30, 13:00-15:00
        morning_start = datetime.strptime("09:30", "%H:%M").time()
        morning_end = datetime.strptime("11:30", "%H:%M").time()
        afternoon_start = datetime.strptime("13:00", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()

        # 检查是否是工作日
        if now.weekday() >= 5:  # 周六、周日
            return False

        # 检查时间
        return (morning_start <= current_time <= morning_end or
                afternoon_start <= current_time <= afternoon_end)

    def _print_account_overview(self, account: dict):
        """打印账户概览"""
        print("\n" + "─" * 80)
        print("  💼 账户概览")
        print("─" * 80)

        # 资金信息（ASCII条形图）
        total_width = 50
        cash_ratio = account['cash'] / account['total_asset']
        market_ratio = account['market_value'] / account['total_asset']

        cash_bar = "█" * int(cash_ratio * total_width)
        market_bar = "█" * int(market_ratio * total_width)

        print(f"\n  总资产: ¥{account['total_asset']:,.2f}")
        print(f"  现金:   ¥{account['cash']:,.2f}  [{cash_bar:<50}] {cash_ratio:.1%}")
        print(f"  持仓:   ¥{account['market_value']:,.2f}  [{market_bar:<50}] {market_ratio:.1%}")
        print(f"\n  总盈亏: ¥{account['total_pnl']:+,.2f} ({account['total_pnl_pct']:+.2f}%)")
        print(f"  持仓数: {account['positions']} 只")
        print(f"  冻结资金: ¥{account.get('frozen_cash', 0):,.2f}")

    def _print_positions(self, positions: List[Position]):
        """打印持仓详情"""
        print("\n" + "─" * 80)
        print("  📊 持仓详情")
        print("─" * 80)

        if not positions:
            print("\n  当前无持仓")
            return

        print(f"\n  {'代码':<12} {'数量':>8} {'成本价':>8} {'现价':>8} {'市值':>12} {'盈亏%':>8}")
        print("  " + "-" * 70)

        total_pnl = 0
        for pos in positions:
            pnl_sign = "+" if pos.unrealized_pnl >= 0 else ""
            print(f"  {pos.symbol:<12} {pos.quantity:>8} ¥{pos.avg_price:>7.2f} ¥{pos.current_price:>7.2f} "
                  f"¥{pos.market_value:>11,.2f} {pnl_sign}{pos.unrealized_pnl_pct:>7.2f}%")
            total_pnl += pos.unrealized_pnl

        print("  " + "-" * 70)
        print(f"  {'合计':<12} {'':>8} {'':>8} {'':>8} ¥{sum(p.market_value for p in positions):>11,.2f} "
              f"{'':>8}")

    def _print_active_signals(self, signals: Dict[str, TradingSignal]):
        """打印活跃信号"""
        print("\n" + "─" * 80)
        print("  🎯 策略信号")
        print("─" * 80)

        if not signals:
            print("\n  当前无活跃信号")
            return

        for symbol, signal in signals.items():
            icons = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}
            icon = icons.get(signal.action, "❓")

            print(f"\n  {icon} {symbol} - {signal.action}")
            print(f"     置信度: {signal.confidence:.0%} | 综合: {signal.factors['composite']:+.2f}")

            if signal.action == "BUY":
                if signal.target_price:
                    print(f"     目标: ¥{signal.target_price:.2f} | 止损: ¥{signal.stop_loss:.2f}")
                print(f"     仓位: {signal.position_size:.0%}")

    def _print_pending_orders(self, orders: List[Order]):
        """打印挂单信息"""
        print("\n" + "─" * 80)
        print("  📋 挂单信息")
        print("─" * 80)

        print(f"\n  {'订单ID':<20} {'代码':<12} {'方向':<4} {'类型':<6} {'数量':>8} {'价格':>8}")
        print("  " + "-" * 70)

        for order in orders:
            side_icon = "🟢" if order.side == OrderSide.BUY else "🔴"
            print(f"  {order.order_id:<20} {order.symbol:<12} {side_icon} {order.side.value:<3} "
                  f"{order.order_type.value:<6} {order.quantity:>8} @ ¥{order.price or 0:>7.2f}")

    def _print_performance_metrics(self, metrics: dict):
        """打印绩效指标"""
        print("\n" + "─" * 80)
        print("  📈 绩效指标")
        print("─" * 80)

        print(f"\n  总收益率: {metrics['total_return']:+.2f}%")
        print(f"  最大回撤: {metrics['max_drawdown']:.2f}%")
        print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
        print(f"  胜率: {metrics['win_rate']:.1f}%")
        print(f"  盈亏比: {metrics['profit_factor']:.2f}")
        print(f"  总交易: {metrics['total_trades']} 笔")

    def _print_recent_trades(self, trades: List):
        """打印最近交易"""
        print("\n" + "─" * 80)
        print("  🔄 最近交易")
        print("─" * 80)

        print(f"\n  {'时间':<16} {'代码':<12} {'方向':<4} {'数量':>8} {'价格':>8} {'手续费':>8}")
        print("  " + "-" * 65)

        for trade in trades[-10:]:  # 最近10笔
            side_icon = "🟢" if trade.side == OrderSide.BUY else "🔴"
            trade_time = trade.trade_time.strftime("%m-%d %H:%M") if hasattr(trade.trade_time, 'strftime') else str(trade.trade_time)
            print(f"  {trade_time:<16} {trade.symbol:<12} {side_icon} {trade.side.value:<3} "
                  f"{trade.quantity:>8} @ ¥{trade.price:>7.2f} ¥{trade.commission:>7.2f}")

    def save_snapshot(self):
        """保存当前快照到日志"""
        snapshot = self.broker.get_daily_snapshot()
        self.journal.save_daily_snapshot(snapshot)

    def start_monitoring(self, interval_seconds: int = 30):
        """开始监控循环"""
        print("\n开始实时监控...")
        print(f"刷新间隔: {interval_seconds} 秒")
        print("按 Ctrl+C 停止\n")

        try:
            while True:
                self.render()
                self.save_snapshot()

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n\n监控已停止")

            # 最终保存
            self.save_snapshot()
            print("✓ 最终快照已保存")


# ============================================
# CLI 测试
# ============================================

def main():
    """测试仪表板"""
    print("=" * 80)
    print("  交易监控仪表板测试")
    print("=" * 80)

    # 创建模拟券商
    broker = SimulatedBroker(initial_capital=1000000)
    broker.connect_data_source()

    # 创建交易日志
    journal = TradeJournal(data_dir="test_dashboard_data")

    # 创建仪表板
    dashboard = TradingDashboard(broker, journal)

    # 渲染一次
    dashboard.render()

    print("\n✓ 测试完成")


if __name__ == "__main__":
    main()
