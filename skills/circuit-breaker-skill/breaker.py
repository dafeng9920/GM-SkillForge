"""
熔断器
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import asyncio


class BreakerLevel(Enum):
    """熔断级别"""
    WARNING = 1
    SUSPEND_NEW = 2
    SUSPEND_ALL = 3
    EMERGENCY = 4


class BreakerStatus(Enum):
    """熔断器状态"""
    CLOSED = "closed"  # 正常运行
    OPEN = "open"  # 熔断触发
    HALF_OPEN = "half_open"  # 半开（尝试恢复）


@dataclass
class BreakerCondition:
    """熔断条件"""
    type: str  # portfolio_loss, market_volatility, system_overload, etc.
    threshold: float
    time_window: int  # 秒
    level: BreakerLevel


@dataclass
class BreakerEvent:
    """熔断事件"""
    id: str
    level: BreakerLevel
    status: BreakerStatus
    reason: str
    triggered_at: datetime
    cooldown_until: Optional[datetime] = None
    auto_recovery: bool = False


class CircuitBreaker:
    """
    熔断器

    负责监控风险指标，在异常时触发熔断
    """

    def __init__(
        self,
        auto_recovery: bool = False,
        cooldown_period: int = 3600,
    ):
        self._conditions: List[BreakerCondition] = []
        self._current_status = BreakerStatus.CLOSED
        self._current_level = BreakerLevel.WARNING
        self._events: List[BreakerEvent] = []
        self._callbacks: List[Callable] = []
        self._auto_recovery = auto_recovery
        self._cooldown_period = cooldown_period
        self._monitoring_task = None

    def add_condition(self, condition: BreakerCondition):
        """添加熔断条件"""
        self._conditions.append(condition)

    def register_callback(self, callback: Callable):
        """注册回调函数"""
        self._callbacks.append(callback)

    async def start_monitoring(self):
        """开始监控"""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """停止监控"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None

    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            await self._check_conditions()
            await asyncio.sleep(1)  # 每秒检查一次

    async def _check_conditions(self):
        """检查所有条件"""
        for condition in self._conditions:
            triggered = await self._evaluate_condition(condition)
            if triggered:
                await self._trigger_breaker(condition)

    async def _evaluate_condition(self, condition: BreakerCondition) -> bool:
        """评估单个条件"""
        # 这里应该根据条件类型进行实际评估
        # 简化版：返回 False
        return False

    async def _trigger_breaker(self, condition: BreakerCondition):
        """触发熔断"""
        # 升级熔断级别
        if condition.level.value > self._current_level.value:
            self._current_level = condition.level
            self._current_status = BreakerStatus.OPEN

            # 创建熔断事件
            event = BreakerEvent(
                id=f"BRKR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                level=condition.level,
                status=self._current_status,
                reason=f"{condition.type} 触发: 超过阈值 {condition.threshold}",
                triggered_at=datetime.now(),
                cooldown_until=datetime.now() + timedelta(seconds=self._cooldown_period),
                auto_recovery=self._auto_recovery,
            )

            self._events.append(event)

            # 执行熔断动作
            await self._execute_breaker_action(condition.level)

            # 触发回调
            for callback in self._callbacks:
                try:
                    await callback(event)
                except Exception as e:
                    print(f"Callback error: {e}")

    async def _execute_breaker_action(self, level: BreakerLevel):
        """执行熔断动作"""
        if level == BreakerLevel.WARNING:
            await self._action_warning()
        elif level == BreakerLevel.SUSPEND_NEW:
            await self._action_suspend_new()
        elif level == BreakerLevel.SUSPEND_ALL:
            await self._action_suspend_all()
        elif level == BreakerLevel.EMERGENCY:
            await self._action_emergency()

    async def _action_warning(self):
        """警告级别动作"""
        print("WARNING: 风险指标接近阈值，请注意")

    async def _action_suspend_new(self):
        """暂停新开仓"""
        print("SUSPEND_NEW: 暂停新开仓，允许平仓")

    async def _action_suspend_all(self):
        """完全停止交易"""
        print("SUSPEND_ALL: 停止所有交易活动")

    async def _action_emergency(self):
        """紧急清算"""
        print("EMERGENCY: 启动紧急清算程序")

    async def manual_trigger(
        self,
        level: BreakerLevel,
        reason: str,
    ) -> BreakerEvent:
        """手动触发熔断"""
        self._current_level = level
        self._current_status = BreakerStatus.OPEN

        event = BreakerEvent(
            id=f"BRKR_MANUAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            level=level,
            status=self._current_status,
            reason=f"手动触发: {reason}",
            triggered_at=datetime.now(),
            cooldown_until=datetime.now() + timedelta(seconds=self._cooldown_period),
            auto_recovery=False,
        )

        self._events.append(event)

        await self._execute_breaker_action(level)

        return event

    async def reset(self):
        """重置熔断器"""
        self._current_status = BreakerStatus.CLOSED
        self._current_level = BreakerLevel.WARNING

    async def try_recover(self) -> bool:
        """尝试恢复"""
        if self._current_status != BreakerStatus.OPEN:
            return True

        # 检查冷却期是否结束
        latest_event = self._events[-1] if self._events else None
        if latest_event and latest_event.cooldown_until:
            if datetime.now() < latest_event.cooldown_until:
                return False

        # 尝试半开状态
        self._current_status = BreakerStatus.HALF_OPEN

        # 等待观察期
        await asyncio.sleep(60)

        # 如果没有再次触发，则恢复
        if self._current_status == BreakerStatus.HALF_OPEN:
            self._current_status = BreakerStatus.CLOSED
            self._current_level = BreakerLevel.WARNING
            return True

        return False

    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "status": self._current_status.value,
            "level": self._current_level.value,
            "auto_recovery": self._auto_recovery,
            "events_count": len(self._events),
            "latest_event": self._events[-1].__dict__ if self._events else None,
        }

    def get_events(
        self, limit: Optional[int] = None
    ) -> List[BreakerEvent]:
        """获取熔断事件历史"""
        events = self._events.copy()
        if limit:
            events = events[-limit:]
        return events

    async def check_trading_allowed(self, action: str) -> bool:
        """
        检查是否允许交易

        Args:
            action: "open_position" or "close_position"

        Returns:
            True if allowed
        """
        if self._current_status == BreakerStatus.CLOSED:
            return True

        if self._current_status == BreakerStatus.OPEN:
            if self._current_level == BreakerLevel.SUSPEND_NEW:
                return action == "close_position"
            elif self._current_level >= BreakerLevel.SUSPEND_ALL:
                return False

        if self._current_status == BreakerStatus.HALF_OPEN:
            # 半开状态谨慎允许
            return action == "close_position"

        return False
