"""
Order Router - 订单路由

Skill 类型: 执行层
职责: 订单路由，支持 Mock/Live 模式

输入: 交易意图 (已通过 Gate 检查)
输出: 路由结果 (order_id, status, venue)

Mock 模式: 记录日志，不执行
Live 模式: 调用交易接口
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ..audit_event_writer import write_gate_finish_event

SKILL_NAME = "order_router"
SKILL_VERSION = "1.0.0"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ROUTED = "ROUTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class RoutingMode(str, Enum):
    MOCK = "MOCK"       # 模拟模式
    PAPER = "PAPER"     # 模拟盘
    LIVE = "LIVE"       # 实盘


@dataclass
class Order:
    """订单"""
    order_id: str
    symbol: str
    action: str         # BUY/SELL
    quantity: int
    price: Optional[float]
    status: OrderStatus
    venue: str
    created_at: str
    filled_at: Optional[str] = None
    filled_price: Optional[float] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "status": self.status.value,
            "venue": self.venue,
            "created_at": self.created_at,
            "filled_at": self.filled_at,
            "filled_price": self.filled_price,
            "message": self.message,
        }


class OrderRouter:
    """订单路由器"""

    def __init__(self, mode: RoutingMode = RoutingMode.MOCK):
        self.mode = mode
        self._orders: Dict[str, Order] = {}

    def _generate_order_id(self) -> str:
        return f"ORD-{uuid.uuid4().hex[:12].upper()}"

    def _get_timestamp(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """验证输入"""
        errors = []

        if input_data.get("action") not in ["BUY", "SELL"]:
            errors.append("action 必须是 BUY 或 SELL")

        if input_data.get("quantity", 0) <= 0:
            errors.append("quantity 必须大于 0")

        if not input_data.get("symbol"):
            errors.append("symbol 不能为空")

        return errors

    def route(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Order:
        """路由订单"""
        context = context or {}

        # 1. 验证输入
        errors = self.validate_input(input_data)
        if errors:
            return Order(
                order_id=self._generate_order_id(),
                symbol=input_data.get("symbol", "UNKNOWN"),
                action=input_data.get("action", "BUY"),
                quantity=input_data.get("quantity", 0),
                price=input_data.get("price"),
                status=OrderStatus.REJECTED,
                venue="NONE",
                created_at=self._get_timestamp(),
                message="; ".join(errors)
            )

        # 2. 创建订单
        order = Order(
            order_id=self._generate_order_id(),
            symbol=input_data["symbol"],
            action=input_data["action"],
            quantity=input_data["quantity"],
            price=input_data.get("price"),
            status=OrderStatus.PENDING,
            venue=self._get_venue(),
            created_at=self._get_timestamp()
        )

        # 3. 根据模式处理
        if self.mode == RoutingMode.MOCK:
            order = self._process_mock(order, input_data)
        elif self.mode == RoutingMode.PAPER:
            order = self._process_paper(order, input_data)
        else:
            order = self._process_live(order, input_data)

        # 4. 记录
        self._orders[order.order_id] = order

        write_gate_finish_event(
            job_id=context.get("job_id", "unknown"),
            gate_node=SKILL_NAME,
            decision="PASS" if order.status in [OrderStatus.ROUTED, OrderStatus.FILLED] else "FAIL",
            metadata=order.to_dict()
        )

        return order

    def _get_venue(self) -> str:
        """获取交易场所"""
        if self.mode == RoutingMode.MOCK:
            return "MOCK"
        elif self.mode == RoutingMode.PAPER:
            return "PAPER"
        return "LIVE"

    def _process_mock(self, order: Order, input_data: Dict[str, Any]) -> Order:
        """Mock 模式: 立即成交"""
        order.status = OrderStatus.FILLED
        order.filled_at = self._get_timestamp()
        order.filled_price = order.price or input_data.get("estimated_price", 100.0)
        order.venue = "MOCK"
        order.message = "Mock order filled immediately"
        return order

    def _process_paper(self, order: Order, input_data: Dict[str, Any]) -> Order:
        """模拟盘: 记录但不真实执行"""
        order.status = OrderStatus.ROUTED
        order.venue = "PAPER"
        order.message = "Paper order routed (not executed)"
        return order

    def _process_live(self, order: Order, input_data: Dict[str, Any]) -> Order:
        """实盘: 调用真实交易接口"""
        # TODO: 接入 VeighNa 或其他交易接口
        order.status = OrderStatus.PENDING
        order.venue = "LIVE"
        order.message = "Live order pending execution (VeighNa not connected)"
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """查询订单"""
        return self._orders.get(order_id)

    def list_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """列出订单"""
        orders = list(self._orders.values())
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return orders


def order_router(
    action: str,
    symbol: str,
    quantity: int,
    price: Optional[float] = None,
    mode: str = "MOCK",
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """函数式接口"""
    router = OrderRouter(mode=RoutingMode(mode))

    order = router.route({
        "action": action,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
    }, context)

    return order.to_dict()
