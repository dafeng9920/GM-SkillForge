"""
回测绩效指标计算

计算策略的关键绩效指标：
- 总收益率
- 年化收益率
- 夏普比率
- 最大回撤
- 胜率
- 盈亏比
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import math


@dataclass
class Trade:
    """单笔交易记录"""
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: int
    direction: str  # LONG, SHORT
    pnl: float
    commission: float = 0.0

    @property
    def return_pct(self) -> float:
        """收益率"""
        if self.direction == "LONG":
            return (self.exit_price - self.entry_price) / self.entry_price
        else:
            return (self.entry_price - self.exit_price) / self.entry_price

    @property
    def duration_hours(self) -> float:
        """持仓时长（小时）"""
        return (self.exit_time - self.entry_time).total_seconds() / 3600


@dataclass
class PerformanceMetrics:
    """
    策略绩效指标

    核心指标：
    - 总收益率
    - 年化收益率
    - 夏普比率
    - 最大回撤
    - 胜率
    - 盈亏比
    """
    # 基本信息
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float

    # 收益指标
    total_return: float = 0.0
    annual_return: float = 0.0
    annual_volatility: float = 0.0

    # 风险指标
    max_drawdown: float = 0.0
    max_drawdown_duration: float = 0.0  # 天数
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0

    # 交易指标
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0

    # 持仓指标
    avg_hold_time: float = 0.0  # 小时
    max_hold_time: float = 0.0
    min_hold_time: float = 0.0

    # 详细记录
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[tuple] = field(default_factory=list)  # (datetime, equity)

    def calculate_derived_metrics(self):
        """计算衍生指标"""
        # 收益率
        self.total_return = (self.final_capital - self.initial_capital) / self.initial_capital

        # 年化收益率
        days = (self.end_date - self.start_date).days
        if days > 0:
            self.annual_return = (1 + self.total_return) ** (365 / days) - 1

        # 交易指标
        if self.trades:
            self.total_trades = len(self.trades)
            self.winning_trades = sum(1 for t in self.trades if t.pnl > 0)
            self.losing_trades = sum(1 for t in self.trades if t.pnl < 0)

            if self.total_trades > 0:
                self.win_rate = self.winning_trades / self.total_trades

            wins = [t.pnl for t in self.trades if t.pnl > 0]
            losses = [t.pnl for t in self.trades if t.pnl < 0]

            if wins:
                self.avg_win = sum(wins) / len(wins)
            if losses:
                self.avg_loss = sum(losses) / len(losses)

            if self.avg_loss != 0:
                self.profit_factor = abs(self.avg_win / self.avg_loss)

            # 持仓时长
            hold_times = [t.duration_hours for t in self.trades]
            if hold_times:
                self.avg_hold_time = sum(hold_times) / len(hold_times)
                self.max_hold_time = max(hold_times)
                self.min_hold_time = min(hold_times)

        # 最大回撤
        if self.equity_curve:
            self.max_drawdown, self.max_drawdown_duration = self._calculate_drawdown()

        # 夏普比率（简化版，假设无风险利率为0）
        if self.equity_curve and len(self.equity_curve) > 1:
            self.sharpe_ratio = self._calculate_sharpe()

    def _calculate_drawdown(self) -> tuple[float, float]:
        """计算最大回撤和持续时长"""
        peak = self.initial_capital
        max_dd = 0.0
        max_dd_duration = 0.0
        peak_time = self.start_date

        for timestamp, equity in self.equity_curve:
            if equity > peak:
                peak = equity
                peak_time = timestamp
            else:
                dd = (peak - equity) / peak
                if dd > max_dd:
                    max_dd = dd
                    max_dd_duration = (timestamp - peak_time).total_seconds() / 86400

        return max_dd, max_dd_duration

    def _calculate_sharpe(self) -> float:
        """计算夏普比率"""
        if len(self.equity_curve) < 2:
            return 0.0

        # 计算日收益率
        returns = []
        for i in range(1, len(self.equity_curve)):
            _, equity_prev = self.equity_curve[i - 1]
            _, equity_curr = self.equity_curve[i]
            if equity_prev > 0:
                returns.append((equity_curr - equity_prev) / equity_prev)

        if not returns:
            return 0.0

        # 平均收益和标准差
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std = math.sqrt(variance)

        if std == 0:
            return 0.0

        # 年化夏普比率
        return avg_return / std * math.sqrt(252)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": f"{self.total_return:.2%}",
            "annual_return": f"{self.annual_return:.2%}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "max_drawdown_duration": f"{self.max_drawdown_duration:.1f} days",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "total_trades": self.total_trades,
            "win_rate": f"{self.win_rate:.2%}",
            "avg_win": f"${self.avg_win:.2f}",
            "avg_loss": f"${self.avg_loss:.2f}",
            "profit_factor": f"{self.profit_factor:.2f}",
            "avg_hold_time": f"{self.avg_hold_time:.1f} hours",
        }

    def print_report(self):
        """打印绩效报告"""
        print("\n" + "=" * 60)
        print("回测绩效报告".center(60))
        print("=" * 60)

        print(f"\n【基本信息】")
        print(f"  回测期间: {self.start_date.date()} 至 {self.end_date.date()}")
        print(f"  初始资金: ${self.initial_capital:,.2f}")
        print(f"  最终资金: ${self.final_capital:,.2f}")

        print(f"\n【收益指标】")
        print(f"  总收益率: {self.total_return:.2%}")
        print(f"  年化收益率: {self.annual_return:.2%}")

        print(f"\n【风险指标】")
        print(f"  最大回撤: {self.max_drawdown:.2%}")
        print(f"  最大回撤持续: {self.max_drawdown_duration:.1f} 天")
        print(f"  夏普比率: {self.sharpe_ratio:.2f}")

        print(f"\n【交易指标】")
        print(f"  总交易次数: {self.total_trades}")
        print(f"  胜率: {self.win_rate:.2%}")
        print(f"  盈利笔数: {self.winning_trades}")
        print(f"  亏损笔数: {self.losing_trades}")
        print(f"  平均盈利: ${self.avg_win:.2f}")
        print(f"  平均亏损: ${self.avg_loss:.2f}")
        print(f"  盈亏比: {self.profit_factor:.2f}")

        print(f"\n【持仓指标】")
        print(f"  平均持仓时长: {self.avg_hold_time:.1f} 小时")
        print(f"  最长持仓: {self.max_hold_time:.1f} 小时")
        print(f"  最短持仓: {self.min_hold_time:.1f} 小时")

        print("\n" + "=" * 60)
