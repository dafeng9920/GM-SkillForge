"""
订单模型
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"
    COVER = "cover"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """订单"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0
    filled_price: float = 0
    commission: float = 0
    created_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    order_id: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.order_id is None:
            self.order_id = f"{self.symbol}_{self.created_at.strftime('%Y%m%d%H%M%S')}"
