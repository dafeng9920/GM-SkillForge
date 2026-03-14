"""
回测引擎核心

事件驱动的回测引擎，支持：
1. 事件队列管理
2. 策略执行
3. 订单撮合
4. 绩效计算
5. Phase 4 系统集成
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Dict, Any
import logging

from .events import TickEvent, SignalEvent, OrderEvent, FillEvent, EventType
from .metrics import PerformanceMetrics, Trade

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: int
    entry_price: float
    entry_time: datetime
    direction: str = "LONG"  # LONG, SHORT

    def market_value(self, current_price: float) -> float:
        """当前市值"""
        return self.quantity * current_price

    def unrealized_pnl(self, current_price: float) -> float:
        """浮动盈亏"""
        if self.direction == "LONG":
            return (current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - current_price) * self.quantity


@dataclass
class Portfolio:
    """投资组合"""
    initial_capital: float
    cash: float = 0.0
    positions: Dict[str, Position] = field(default_factory=dict)

    def __post_init__(self):
        if self.cash == 0.0:
            self.cash = self.initial_capital

    def equity(self, prices: Dict[str, float]) -> float:
        """总权益"""
        total = self.cash
        for symbol, pos in self.positions.items():
            if symbol in prices:
                total += pos.market_value(prices[symbol])
        return total


class BacktestEngine:
    """
    回测引擎

    核心功能：
    1. 事件驱动执行
    2. 策略信号处理
    3. 订单撮合
    4. 持仓管理
    5. 绩效计算
    """

    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0,
        signal_handler: Optional[Callable] = None,
    ):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
            commission: 手续费率
            slippage: 滑点（比例）
            signal_handler: 信号处理函数 (Phase 4 系统入口)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.signal_handler = signal_handler

        # 事件队列
        self.events: deque = deque()

        # 投资组合
        self.portfolio = Portfolio(initial_capital=initial_capital)

        # 当前状态
        self.current_time: Optional[datetime] = None
        self.current_prices: Dict[str, float] = {}

        # 历史记录
        self.trades: List[Trade] = []
        self.equity_curve: List[tuple] = []  # (timestamp, equity)

        # 统计
        self.order_count = 0
        self.fill_count = 0

        logger.info(f"回测引擎初始化: 初始资金=${initial_capital:,.2f}")

    def run(self, data: List[TickEvent]) -> PerformanceMetrics:
        """
        运行回测

        Args:
            data: Tick数据列表

        Returns:
            PerformanceMetrics: 绩效指标
        """
        logger.info(f"开始回测: {len(data)} 条Tick数据")

        # 添加所有事件到队列
        for tick in data:
            self.events.append(tick)

        # 处理事件队列
        while self.events:
            event = self.events.popleft()
            self._on_event(event)

        # 生成绩效报告
        return self._generate_metrics()

    def _on_event(self, event):
        """处理单个事件"""
        if isinstance(event, TickEvent):
            self._on_tick(event)
        elif isinstance(event, SignalEvent):
            self._on_signal(event)
        elif isinstance(event, OrderEvent):
            self._on_order(event)
        elif isinstance(event, FillEvent):
            self._on_fill(event)

    def _on_tick(self, event: TickEvent):
        """
        处理Tick事件

        1. 更新当前状态
        2. 记录权益曲线
        3. 调用策略生成信号
        """
        self.current_time = event.timestamp
        self.current_prices[event.symbol] = event.price

        # 记录权益曲线（每根K线结束时）
        self._record_equity()

        # 调用Phase 4系统处理
        if self.signal_handler:
            tick_data = {
                "symbol": event.symbol,
                "timestamp": event.timestamp,
                "price": event.price,
                "volume": event.volume,
                "bid": event.bid,
                "ask": event.ask,
                "bid_size": event.bid_size,
                "ask_size": event.ask_size,
            }

            # 调用信号处理器（Phase 4系统）
            try:
                signals = self.signal_handler(tick_data, self._get_portfolio_state())
                for signal in signals:
                    # 将字典转换为 SignalEvent
                    if signal.get('signal_type') in ('BUY', 'SELL'):
                        signal_event = SignalEvent(
                            symbol=signal['symbol'],
                            timestamp=signal['timestamp'],
                            signal_type=signal['signal_type'],
                            confidence=signal.get('confidence', 0.5),
                            price=signal.get('price'),
                            reason=signal.get('reason', ''),
                        )
                        # 将信号插入队列前端，使其在下一个tick之前被处理
                        self.events.appendleft(signal_event)
            except Exception as e:
                logger.error(f"信号处理错误: {e}")

    def _on_signal(self, event: SignalEvent):
        """
        处理信号事件

        将信号转换为订单
        """
        # 将 signal_type 映射到 direction
        signal_to_direction = {
            "BUY": "BUY",
            "SELL": "SELL",
            "HOLD": "HOLD",
        }

        direction = signal_to_direction.get(event.signal_type)
        if not direction or direction == "HOLD":
            return

        # 计算订单数量（简化版：固定比例）
        quantity = self._calculate_order_quantity(
            event.symbol, direction, event.price or self.current_prices.get(event.symbol, 0)
        )

        if quantity <= 0:
            return

        # 创建订单
        order = OrderEvent(
            symbol=event.symbol,
            timestamp=event.timestamp,
            order_type="MARKET",
            direction=direction,
            quantity=quantity,
            price=event.price,
            reason=event.reason,
            signal_id=str(id(event)),
        )

        # 将订单插入队列前端，使其立即成交
        self.events.appendleft(order)
        self.order_count += 1

    def _on_order(self, event: OrderEvent):
        """
        处理订单事件

        简化版市价单：立即成交
        """
        # 获取成交价格（考虑滑点）
        base_price = event.price or self.current_prices.get(event.symbol, 0)
        if base_price == 0:
            logger.warning(f"无法获取 {event.symbol} 的价格，订单取消")
            return

        # 应用滑点
        slippage_factor = 1 + self.slippage if event.direction == "BUY" else 1 - self.slippage
        fill_price = base_price * slippage_factor

        # 创建成交事件
        fill = FillEvent(
            symbol=event.symbol,
            timestamp=event.timestamp,
            direction=event.direction,
            quantity=event.quantity,
            price=fill_price,
            commission=event.quantity * fill_price * self.commission,
            order_id=str(id(event)),
        )

        # 将成交事件插入队列前端，使其立即更新持仓
        self.events.appendleft(fill)

    def _on_fill(self, event: FillEvent):
        """
        处理成交事件

        更新持仓和资金
        """
        symbol = event.symbol
        direction = event.direction
        quantity = event.quantity
        price = event.price
        commission = event.commission

        if direction == "BUY":
            # 买入
            cost = quantity * price + commission
            if cost > self.portfolio.cash:
                logger.warning(f"资金不足: 需要 ${cost:.2f}, 可用 ${self.portfolio.cash:.2f}")
                return

            self.portfolio.cash -= cost

            # 更新或创建持仓
            if symbol in self.portfolio.positions:
                # 加仓（加权平均）
                pos = self.portfolio.positions[symbol]
                total_cost = pos.quantity * pos.entry_price + quantity * price
                pos.quantity += quantity
                pos.entry_price = total_cost / pos.quantity
            else:
                # 新建仓位
                self.portfolio.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    entry_time=event.timestamp,
                    direction="LONG",
                )

        else:
            # 卖出
            if symbol not in self.portfolio.positions:
                logger.warning(f"无持仓可卖: {symbol}")
                return

            pos = self.portfolio.positions[symbol]

            # 卖出数量检查
            sell_quantity = min(quantity, pos.quantity)
            proceeds = sell_quantity * price - commission

            self.portfolio.cash += proceeds

            # 记录交易
            trade = Trade(
                symbol=symbol,
                entry_time=pos.entry_time,
                exit_time=event.timestamp,
                entry_price=pos.entry_price,
                exit_price=price,
                quantity=sell_quantity,
                direction=pos.direction,
                pnl=(price - pos.entry_price) * sell_quantity - commission,
                commission=commission,
            )
            self.trades.append(trade)

            # 更新持仓
            pos.quantity -= sell_quantity
            if pos.quantity <= 0:
                del self.portfolio.positions[symbol]

        self.fill_count += 1

    def _calculate_order_quantity(self, symbol: str, direction: str, price: float) -> int:
        """
        计算订单数量

        简化版：每次使用固定比例的资金
        """
        if price <= 0:
            return 0

        # 使用可用资金的30%
        if direction == "BUY":
            available = self.portfolio.cash * 0.3
            quantity = int(available / price)
            return max(0, quantity)
        else:
            # 卖出全部持仓
            if symbol in self.portfolio.positions:
                return self.portfolio.positions[symbol].quantity
            return 0

    def _get_portfolio_state(self) -> Dict[str, Any]:
        """获取当前投资组合状态（供Phase 4系统使用）"""
        return {
            "cash": self.portfolio.cash,
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "entry_time": pos.entry_time.isoformat(),
                }
                for symbol, pos in self.portfolio.positions.items()
            },
            "equity": self.portfolio.equity(self.current_prices),
        }

    def _record_equity(self):
        """记录权益曲线"""
        if self.current_time:
            equity = self.portfolio.equity(self.current_prices)
            self.equity_curve.append((self.current_time, equity))

    def _generate_metrics(self) -> PerformanceMetrics:
        """生成绩效指标"""
        metrics = PerformanceMetrics(
            start_date=self.equity_curve[0][0] if self.equity_curve else datetime.now(),
            end_date=self.equity_curve[-1][0] if self.equity_curve else datetime.now(),
            initial_capital=self.initial_capital,
            final_capital=self.portfolio.equity(self.current_prices),
            trades=self.trades,
            equity_curve=self.equity_curve,
        )

        metrics.calculate_derived_metrics()
        return metrics
