"""
执行监控器
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import asyncio


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AlertSeverity(Enum):
    """警报级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """警报"""
    type: str
    message: str
    severity: AlertSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    order_id: Optional[str] = None


@dataclass
class OrderState:
    """订单状态"""
    order_id: str
    status: OrderStatus
    filled_quantity: float = 0
    remaining_quantity: float = 0
    avg_fill_price: float = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    fills: List[Dict] = field(default_factory=list)


@dataclass
class MonitoringRule:
    """监控规则"""
    type: str
    threshold: float
    action: str = "alert"  # alert, cancel, retry


class ExecutionMonitor:
    """
    执行监控器

    负责订单状态跟踪、成交确认、异常检测
    """

    def __init__(self):
        self._monitored_orders: Dict[str, OrderState] = {}
        self._alerts: List[Alert] = []
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._callbacks: Dict[str, List[Callable]] = {}

    async def monitor_order(
        self,
        order_id: str,
        venue: str,
        symbol: str,
        side: str,
        quantity: float,
        expected_price: float,
        rules: List[MonitoringRule],
    ) -> OrderState:
        """
        开始监控订单

        Args:
            order_id: 订单ID
            venue: 交易通道
            symbol: 标的代码
            side: 买卖方向
            quantity: 数量
            expected_price: 预期价格
            rules: 监控规则

        Returns:
            订单状态
        """
        # 创建订单状态
        state = OrderState(
            order_id=order_id,
            status=OrderStatus.PENDING,
            remaining_quantity=quantity,
        )

        self._monitored_orders[order_id] = state

        # 启动监控任务
        task = asyncio.create_task(
            self._monitoring_loop(order_id, rules)
        )
        self._monitoring_tasks[order_id] = task

        return state

    async def _monitoring_loop(
        self, order_id: str, rules: List[MonitoringRule]
    ):
        """监控循环"""
        while order_id in self._monitored_orders:
            state = self._monitored_orders[order_id]

            # 检查订单是否已完成
            if state.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]:
                break

            # 应用监控规则
            for rule in rules:
                alert = await self._apply_rule(state, rule)
                if alert:
                    self._alerts.append(alert)
                    await self._trigger_callbacks(alert)

            # 等待下次检查
            await asyncio.sleep(1)

        # 清理
        if order_id in self._monitoring_tasks:
            del self._monitoring_tasks[order_id]

    async def _apply_rule(
        self, state: OrderState, rule: MonitoringRule
    ) -> Optional[Alert]:
        """应用监控规则"""
        rule_type = rule.type

        if rule_type == "fill_timeout":
            return await self._check_fill_timeout(state, rule)
        elif rule_type == "price_deviation":
            return await self._check_price_deviation(state, rule)
        elif rule_type == "partial_fill":
            return await self._check_partial_fill(state, rule)
        elif rule_type == "rejection":
            return await self._check_rejection(state, rule)

        return None

    async def _check_fill_timeout(
        self, state: OrderState, rule: MonitoringRule
    ) -> Optional[Alert]:
        """检查成交超时"""
        elapsed = (datetime.now() - state.created_at).total_seconds()

        if elapsed > rule.threshold:
            if state.status == OrderStatus.PENDING:
                return Alert(
                    type="fill_timeout",
                    message=f"订单 {state.order_id} 成交超时（{elapsed:.0f}秒）",
                    severity=AlertSeverity.WARNING,
                    order_id=state.order_id,
                )

        return None

    async def _check_price_deviation(
        self, state: OrderState, rule: MonitoringRule
    ) -> Optional[Alert]:
        """检查价格偏离（需要传入当前市场价格）"""
        # 简化版：实际需要获取实时价格
        if state.avg_fill_price > 0:
            # 这里需要预期价格，暂时跳过
            pass

        return None

    async def _check_partial_fill(
        self, state: OrderState, rule: MonitoringRule
    ) -> Optional[Alert]:
        """检查部分成交异常"""
        if state.status == OrderStatus.PARTIALLY_FILLED:
            fill_pct = state.filled_quantity / (state.filled_quantity + state.remaining_quantity)

            if fill_pct < rule.threshold:
                # 部分成交但比例过小
                elapsed = (datetime.now() - state.created_at).total_seconds()
                if elapsed > 300:  # 5分钟后
                    return Alert(
                        type="partial_fill",
                        message=f"订单 {state.order_id} 部分成交比例过低（{fill_pct:.1%}）",
                        severity=AlertSeverity.WARNING,
                        order_id=state.order_id,
                    )

        return None

    async def _check_rejection(
        self, state: OrderState, rule: MonitoringRule
    ) -> Optional[Alert]:
        """检查订单拒绝"""
        if state.status == OrderStatus.REJECTED:
            return Alert(
                type="rejection",
                message=f"订单 {state.order_id} 被拒绝",
                severity=AlertSeverity.ERROR,
                order_id=state.order_id,
            )

        return None

    async def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        filled_quantity: Optional[float] = None,
        fill_price: Optional[float] = None,
    ):
        """
        更新订单状态

        由外部系统调用（如收到交易所回报）
        """
        if order_id not in self._monitored_orders:
            return

        state = self._monitored_orders[order_id]

        # 更新状态
        state.status = status
        state.updated_at = datetime.now()

        if filled_quantity is not None:
            new_fill = filled_quantity - state.filled_quantity

            if new_fill > 0:
                state.fills.append({
                    "quantity": new_fill,
                    "price": fill_price,
                    "timestamp": datetime.now(),
                })

            state.filled_quantity = filled_quantity
            state.remaining_quantity -= new_fill

        if fill_price is not None:
            # 更新平均成交价
            total_value = sum(f["quantity"] * f["price"] for f in state.fills)
            state.avg_fill_price = total_value / state.filled_quantity

        # 触发回调
        await self._trigger_callbacks(Alert(
            type="status_update",
            message=f"订单 {order_id} 状态更新为 {status.value}",
            severity=AlertSeverity.INFO,
            order_id=order_id,
        ))

    async def _trigger_callbacks(self, alert: Alert):
        """触发回调"""
        for callback in self._callbacks.get(alert.type, []):
            try:
                await callback(alert)
            except Exception as e:
                print(f"Callback error: {e}")

    def register_callback(self, alert_type: str, callback: Callable):
        """注册回调函数"""
        if alert_type not in self._callbacks:
            self._callbacks[alert_type] = []
        self._callbacks[alert_type].append(callback)

    def get_order_state(self, order_id: str) -> Optional[OrderState]:
        """获取订单状态"""
        return self._monitored_orders.get(order_id)

    def get_all_states(self) -> Dict[str, OrderState]:
        """获取所有订单状态"""
        return self._monitored_orders.copy()

    def get_alerts(
        self, order_id: Optional[str] = None, severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """获取警报"""
        alerts = self._alerts

        if order_id:
            alerts = [a for a in alerts if a.order_id == order_id]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    async def cancel_monitoring(self, order_id: str):
        """取消监控"""
        if order_id in self._monitoring_tasks:
            self._monitoring_tasks[order_id].cancel()
            del self._monitoring_tasks[order_id]

    async def calculate_execution_quality(
        self, order_id: str
    ) -> Optional[Dict]:
        """计算执行质量"""
        state = self._monitored_orders.get(order_id)
        if not state:
            return None

        if state.status != OrderStatus.FILLED:
            return None

        # 执行质量指标
        fill_rate = state.filled_quantity / (state.filled_quantity + state.remaining_quantity)
        execution_time = (state.updated_at - state.created_at).total_seconds()

        return {
            "order_id": order_id,
            "fill_rate": fill_rate,
            "avg_fill_price": state.avg_fill_price,
            "execution_time_seconds": execution_time,
            "fill_count": len(state.fills),
        }
