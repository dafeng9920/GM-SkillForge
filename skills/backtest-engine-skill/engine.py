"""
回测引擎
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

# 支持动态加载的导入
try:
    from .order import Order, OrderType, OrderSide, OrderStatus
except (ImportError, ValueError):
    # 动态加载时的回退方案
    # 尝试从已注册的模块中获取
    import sys
    if 'backtest_engine_skill.order' in sys.modules:
        order_module = sys.modules['backtest_engine_skill.order']
        Order = order_module.Order
        OrderType = order_module.OrderType
        OrderSide = order_module.OrderSide
        OrderStatus = order_module.OrderStatus
    else:
        # 最后的回退：直接从文件导入
        import importlib.util
        import pathlib
        current_file = pathlib.Path(__file__)
        order_path = current_file.parent / 'order.py'
        spec = importlib.util.spec_from_file_location("backtest_engine_skill.order", order_path)
        if spec and spec.loader:
            order_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(order_module)
            Order = order_module.Order
            OrderType = order_module.OrderType
            OrderSide = order_module.OrderSide
            OrderStatus = order_module.OrderStatus
        else:
            raise ImportError("Cannot import order module")


@dataclass
class Portfolio:
    """投资组合"""
    cash: float
    positions: Dict[str, float]  # symbol -> quantity
    pending_orders: List[Order]

    @property
    def equity(self) -> float:
        """总权益（需要结合当前价格计算）"""
        return self.cash  # 简化版

    @property
    def total_value(self, current_prices: Dict[str, float]) -> float:
        """总资产"""
        value = self.cash
        for symbol, quantity in self.positions.items():
            if symbol in current_prices:
                value += quantity * current_prices[symbol]
        return value


@dataclass
class Trade:
    """交易记录"""
    symbol: str
    side: OrderSide
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    return_pct: Optional[float]
    return_amt: Optional[float]


@dataclass
class BacktestResult:
    """回测结果"""
    equity_curve: pd.Series
    trades: List[Trade]
    metrics: Dict[str, float]


class BacktestEngine:
    """
    回测引擎

    支持：
    - 历史数据回放
    - 订单模拟（市价、限价、止损）
    - 持仓管理
    - 绩效计算
    """

    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0001,
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        # 投资组合
        self.portfolio = Portfolio(
            cash=initial_capital,
            positions={},
            pending_orders=[],
        )

        # 交易记录
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []

        # 当前状态
        self.current_date: Optional[datetime] = None
        self.current_prices: Dict[str, float] = {}

    async def run(
        self,
        data: pd.DataFrame,
        strategy: Callable,
        strategy_params: Dict = None,
    ) -> BacktestResult:
        """
        运行回测

        Args:
            data: 历史数据（包含 OHLCV）
            strategy: 策略函数
            strategy_params: 策略参数

        Returns:
            回测结果
        """
        if strategy_params is None:
            strategy_params = {}

        # 重置状态
        self._reset()

        # 遍历历史数据
        for i in range(len(data)):
            row = data.iloc[i]
            self.current_date = row.name
            self.current_prices = self._get_current_prices(data, i)

            # 更新权益曲线
            self._update_equity_curve()

            # 处理待成交订单
            await self._process_pending_orders(row)

            # 生成交易信号
            signals = await strategy(
                data.iloc[:i+1],
                self.portfolio,
                strategy_params,
            )

            # 执行信号
            await self._execute_signals(signals, row)

        # 计算最终结果
        return self._calculate_result()

    def _reset(self):
        """重置状态"""
        self.portfolio = Portfolio(
            cash=self.initial_capital,
            positions={},
            pending_orders=[],
        )
        self.trades = []
        self.equity_curve = []

    def _get_current_prices(self, data: pd.DataFrame, index: int) -> Dict[str, float]:
        """获取当前价格"""
        row = data.iloc[index]
        return {"close": row["close"]}

    async def _process_pending_orders(self, row: pd.Series):
        """处理待成交订单"""
        for order in self.portfolio.pending_orders[:]:
            if order.symbol not in self.current_prices:
                continue

            current_price = self.current_prices[order.symbol]
            filled = False
            fill_price = current_price

            # 市价单直接成交
            if order.order_type == OrderType.MARKET:
                # 应用滑点
                if order.side in [OrderSide.BUY, OrderSide.COVER]:
                    fill_price = current_price * (1 + self.slippage)
                else:
                    fill_price = current_price * (1 - self.slippage)
                filled = True

            # 限价单
            elif order.order_type == OrderType.LIMIT:
                if order.side in [OrderSide.BUY, OrderSide.COVER]:
                    if current_price <= order.price:
                        fill_price = order.price
                        filled = True
                else:
                    if current_price >= order.price:
                        fill_price = order.price
                        filled = True

            # 止损单
            elif order.order_type == OrderType.STOP:
                if order.side in [OrderSide.BUY, OrderSide.COVER]:
                    if current_price >= order.stop_price:
                        fill_price = current_price * (1 + self.slippage)
                        filled = True
                else:
                    if current_price <= order.stop_price:
                        fill_price = current_price * (1 - self.slippage)
                        filled = True

            if filled:
                await self._fill_order(order, fill_price)

    async def _fill_order(self, order: Order, price: float):
        """成交订单"""
        # 计算手续费
        commission = order.quantity * price * self.commission

        # 更新持仓和现金
        if order.side in [OrderSide.BUY, OrderSide.COVER]:
            self.portfolio.cash -= order.quantity * price + commission
            self.portfolio.positions[order.symbol] = \
                self.portfolio.positions.get(order.symbol, 0) + order.quantity
        else:
            self.portfolio.cash += order.quantity * price - commission
            self.portfolio.positions[order.symbol] = \
                self.portfolio.positions.get(order.symbol, 0) - order.quantity

        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.filled_price = price
        order.commission = commission
        order.filled_at = self.current_date

        # 从待成交列表移除
        if order in self.portfolio.pending_orders:
            self.portfolio.pending_orders.remove(order)

        # 记录交易
        self._record_trade(order, price)

    async def _execute_signals(self, signals: List[Dict], row: pd.Series):
        """执行交易信号"""
        for signal in signals:
            order_type = OrderType(signal.get("type", "market").upper())
            side = OrderSide(signal["side"].upper())

            order = Order(
                symbol=signal["symbol"],
                side=side,
                order_type=order_type,
                quantity=signal["quantity"],
                price=signal.get("price"),
                stop_price=signal.get("stop_price"),
                created_at=self.current_date,
            )

            self.portfolio.pending_orders.append(order)

    def _record_trade(self, order: Order, fill_price: float):
        """记录交易"""
        # 简化版：暂不完整实现
        pass

    def _update_equity_curve(self):
        """更新权益曲线"""
        total_value = self.portfolio.total_value(self.current_prices)
        self.equity_curve.append(total_value)

    def _calculate_result(self) -> BacktestResult:
        """计算回测结果"""
        equity_series = pd.Series(self.equity_curve)

        # 计算收益率
        returns = equity_series.pct_change().dropna()

        # 计算绩效指标
        total_return = (equity_series.iloc[-1] / equity_series.iloc[0]) - 1

        # 夏普比率 (年化)
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        # 最大回撤
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        metrics = {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "final_equity": equity_series.iloc[-1],
        }

        return BacktestResult(
            equity_curve=equity_series,
            trades=self.trades,
            metrics=metrics,
        )
