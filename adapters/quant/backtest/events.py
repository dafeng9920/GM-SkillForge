"""
回测引擎事件定义

支持的事件类型：
- TickEvent: 价格/成交量更新
- SignalEvent: 交易信号生成
- OrderEvent: 订单执行
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class EventType(str, Enum):
    """事件类型"""
    TICK = "tick"
    SIGNAL = "signal"
    ORDER = "order"
    FILL = "fill"


@dataclass
class TickEvent:
    """
    Tick 事件 - 市场数据更新

    这是回测引擎的基础事件，所有策略基于此事件运行
    """
    symbol: str
    timestamp: datetime
    price: float
    volume: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None

    def __post_init__(self):
        """事件类型标识"""
        self.type = EventType.TICK


@dataclass
class SignalEvent:
    """
    信号事件 - 交易信号

    由策略生成，经过确认后转化为订单
    """
    symbol: str
    timestamp: datetime
    signal_type: str  # BUY, SELL, HOLD
    confidence: float  # 0-1
    price: Optional[float] = None
    reason: str = ""
    metadata: dict = None

    def __post_init__(self):
        """事件类型标识"""
        self.type = EventType.SIGNAL
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OrderEvent:
    """
    订单事件 - 订单请求

    由信号事件转化而来，提交给订单管理系统
    """
    symbol: str
    timestamp: datetime
    order_type: str  # MARKET, LIMIT, STOP
    direction: str  # BUY, SELL
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    reason: str = ""
    signal_id: Optional[str] = None

    def __post_init__(self):
        """事件类型标识"""
        self.type = EventType.ORDER


@dataclass
class FillEvent:
    """
    成交事件 - 订单成交

    订单执行后的结果，更新持仓和资金
    """
    symbol: str
    timestamp: datetime
    direction: str  # BUY, SELL
    quantity: int
    price: float
    commission: float = 0.0
    order_id: Optional[str] = None

    def __post_init__(self):
        """事件类型标识"""
        self.type = EventType.FILL

    @property
    def value(self) -> float:
        """成交金额"""
        return self.quantity * self.price
