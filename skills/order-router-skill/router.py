"""
订单路由器
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np


class RoutingStrategy(Enum):
    """路由策略"""
    SMART = "smart"
    VWAP = "vwap"
    TWAP = "twap"
    ICEBERG = "iceberg"
    BEST_PRICE = "best_price"


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


@dataclass
class Venue:
    """交易通道"""
    name: str
    priority: int
    fee_rate: float
    capacity: float = 1.0  # 容量利用率
    avg_fill_time: float = 1.0  # 平均成交时间（秒）


@dataclass
class Order:
    """原始订单"""
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    price: Optional[float] = None
    time_in_force: str = "DAY"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoutedOrder:
    """路由后的子订单"""
    venue: str
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    price: Optional[float] = None
    parent_order_id: Optional[str] = None
    status: str = "PENDING"


@dataclass
class RoutingResult:
    """路由结果"""
    status: str
    routed_orders: List[RoutedOrder]
    routing_summary: Dict


class OrderRouter:
    """
    订单路由器

    负责智能拆单、通道选择、订单分发
    """

    def __init__(self, venues: List[Venue]):
        self.venues = sorted(venues, key=lambda v: v.priority)
        self._routing_history = []

    async def route(
        self,
        order: Order,
        strategy: RoutingStrategy = RoutingStrategy.SMART,
        constraints: Dict = None,
    ) -> RoutingResult:
        """
        路由订单

        Args:
            order: 原始订单
            strategy: 路由策略
            constraints: 约束条件

        Returns:
            路由结果
        """
        if constraints is None:
            constraints = {}

        # 根据策略路由
        if strategy == RoutingStrategy.SMART:
            return await self._smart_route(order, constraints)
        elif strategy == RoutingStrategy.VWAP:
            return await self._vwap_route(order, constraints)
        elif strategy == RoutingStrategy.TWAP:
            return await self._twap_route(order, constraints)
        elif strategy == RoutingStrategy.ICEBERG:
            return await self._iceberg_route(order, constraints)
        elif strategy == RoutingStrategy.BEST_PRICE:
            return await self._best_price_route(order, constraints)
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")

    async def _smart_route(
        self, order: Order, constraints: Dict
    ) -> RoutingResult:
        """
        智能路由

        综合考虑：
        - 价格优先
        - 流动性
        - 交易成本
        - 通道容量
        """
        max_order_size = constraints.get("max_order_size", order.quantity)
        min_order_size = constraints.get("min_order_size", 100)
        venue_capacity = constraints.get("venue_capacity", 0.3)

        # 计算每个通道的分配
        routed_orders = []
        remaining_quantity = order.quantity

        # 按优先级排序通道
        sorted_venues = sorted(
            self.venues,
            key=lambda v: (v.priority, -v.capacity)
        )

        for venue in sorted_venues:
            if remaining_quantity <= 0:
                break

            # 计算该通道的容量
            venue_qty = min(
                max_order_size,
                int(order.quantity * venue_capacity),
                remaining_quantity,
            )

            if venue_qty >= min_order_size:
                routed_orders.append(RoutedOrder(
                    venue=venue.name,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=venue_qty,
                    order_type=OrderType.LIMIT,
                    price=order.price,  # 实际应根据市场数据计算
                ))
                remaining_quantity -= venue_qty

        # 如果还有剩余，分配给优先级最高的通道
        if remaining_quantity > 0:
            routed_orders.append(RoutedOrder(
                venue=sorted_venues[0].name,
                symbol=order.symbol,
                side=order.side,
                quantity=remaining_quantity,
                order_type=OrderType.LIMIT,
                price=order.price,
            ))

        # 计算路由摘要
        routing_summary = await self._calculate_summary(routed_orders, order)

        # 记录历史
        self._routing_history.append({
            "timestamp": datetime.now(),
            "order": order,
            "result": routing_summary,
        })

        return RoutingResult(
            status="SUCCESS",
            routed_orders=routed_orders,
            routing_summary=routing_summary,
        )

    async def _vwap_route(
        self, order: Order, constraints: Dict
    ) -> RoutingResult:
        """
        VWAP 拆单

        按成交量加权平均价格拆单
        """
        # 获取历史成交量分布
        volume_profile = await self._get_volume_profile(order.symbol)

        # 按成交量比例拆单
        total_volume = sum(volume_profile.values())
        routed_orders = []

        for venue, volume_pct in volume_profile.items():
            qty = int(order.quantity * volume_pct / total_volume)

            if qty > 0:
                routed_orders.append(RoutedOrder(
                    venue=venue,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=qty,
                    order_type=OrderType.LIMIT,
                    price=order.price,
                ))

        routing_summary = await self._calculate_summary(routed_orders, order)

        return RoutingResult(
            status="SUCCESS",
            routed_orders=routed_orders,
            routing_summary=routing_summary,
        )

    async def _twap_route(
        self, order: Order, constraints: Dict
    ) -> RoutingResult:
        """
        TWAP 拆单

        按时间加权平均价格拆单
        """
        time_slices = constraints.get("time_slices", 10)
        qty_per_slice = order.quantity / time_slices

        routed_orders = []
        for i in range(time_slices):
            # 轮流分配到不同通道
            venue = self.venues[i % len(self.venues)]

            routed_orders.append(RoutedOrder(
                venue=venue.name,
                symbol=order.symbol,
                side=order.side,
                quantity=qty_per_slice,
                order_type=OrderType.LIMIT,
                price=order.price,
            ))

        routing_summary = await self._calculate_summary(routed_orders, order)

        return RoutingResult(
            status="SUCCESS",
            routed_orders=routed_orders,
            routing_summary=routing_summary,
        )

    async def _iceberg_route(
        self, order: Order, constraints: Dict
    ) -> RoutingResult:
        """
        冰山订单

        隐藏大单，只显示部分数量
        """
        display_qty = constraints.get("display_quantity", 100)
        peak_size = constraints.get("peak_size", 1000)

        routed_orders = []
        remaining = order.quantity

        while remaining > 0:
            qty = min(display_qty, peak_size, remaining)

            # 轮换通道
            venue = self.venues[len(routed_orders) % len(self.venues)]

            routed_orders.append(RoutedOrder(
                venue=venue.name,
                symbol=order.symbol,
                side=order.side,
                quantity=qty,
                order_type=OrderType.LIMIT,
                price=order.price,
            ))

            remaining -= qty

        routing_summary = await self._calculate_summary(routed_orders, order)

        return RoutingResult(
            status="SUCCESS",
            routed_orders=routed_orders,
            routing_summary=routing_summary,
        )

    async def _best_price_route(
        self, order: Order, constraints: Dict
    ) -> RoutingResult:
        """
        最优价格路由

        寻找最优价格执行
        """
        # 比较各通道价格
        venue_prices = await self._get_venue_prices(order.symbol)

        # 按价格排序
        if order.side == OrderSide.BUY:
            sorted_venues = sorted(venue_prices.items(), key=lambda x: x[1])
        else:
            sorted_venues = sorted(venue_prices.items(), key=lambda x: x[1], reverse=True)

        # 全部分配给最优价格通道
        best_venue = sorted_venues[0][0]
        best_price = sorted_venues[0][1]

        routed_orders = [RoutedOrder(
            venue=best_venue,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            order_type=OrderType.LIMIT,
            price=best_price,
        )]

        routing_summary = await self._calculate_summary(routed_orders, order)

        return RoutingResult(
            status="SUCCESS",
            routed_orders=routed_orders,
            routing_summary=routing_summary,
        )

    async def _calculate_summary(
        self, routed_orders: List[RoutedOrder], original_order: Order
    ) -> Dict:
        """计算路由摘要"""
        total_quantity = sum(o.quantity for o in routed_orders)
        venues_used = len(set(o.venue for o in routed_orders))

        # 计算平均价格（如果有价格）
        prices = [o.price for o in routed_orders if o.price is not None]
        avg_price = sum(prices) / len(prices) if prices else None

        # 估算滑点
        estimated_slippage = 0.0
        if avg_price and original_order.price:
            estimated_slippage = abs(avg_price - original_order.price) / original_order.price

        return {
            "total_quantity": total_quantity,
            "venues_used": venues_used,
            "avg_price": avg_price,
            "estimated_slippage": estimated_slippage,
            "order_count": len(routed_orders),
        }

    async def _get_volume_profile(self, symbol: str) -> Dict[str, float]:
        """获取成交量分布（简化版）"""
        # 实际应从历史数据获取
        return {venue.name: np.random.uniform(0.2, 0.5) for venue in self.venues}

    async def _get_venue_prices(self, symbol: str) -> Dict[str, float]:
        """获取各通道价格（简化版）"""
        # 实际应从实时数据获取
        return {venue.name: 150.0 + np.random.uniform(-0.5, 0.5) for venue in self.venues}

    def get_routing_history(self) -> List[Dict]:
        """获取路由历史"""
        return self._routing_history
