"""
验证点管理器 - Phase 4 确认层核心

买入不是结束，而是验证的开始。
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional


@dataclass
class ValidationPoint:
    """验证点数据结构"""
    symbol: str
    entry_price: float
    entry_time: datetime
    target_price: float
    deadline: datetime
    status: str  # pending, passed, failed

    @property
    def elapsed_minutes(self) -> float:
        """已过时间（分钟）"""
        return (datetime.now() - self.entry_time).total_seconds() / 60

    @property
    def remaining_minutes(self) -> float:
        """剩余时间（分钟）"""
        return max(0, (self.deadline - datetime.now()).total_seconds() / 60)


@dataclass
class ValidationResult:
    """验证结果"""
    status: str  # pending, passed, failed, no_validation_point
    action: str = 'hold'  # hold, exit
    reason: str = ''
    confidence: float = 0.0


class ValidationPointManager:
    """
    验证点管理器

    核心功能：
    1. 买入后立即创建验证点
    2. 每个tick检查验证状态
    3. 未达成即离场
    """

    def __init__(
        self,
        target_gain: float = 0.01,  # 目标涨幅1%
        time_window: int = 30,       # 时间窗口30分钟
    ):
        self.target_gain = target_gain
        self.time_window = time_window
        self.validation_points: Dict[str, ValidationPoint] = {}

    def create_validation_point(
        self,
        symbol: str,
        entry_price: float,
        entry_time: datetime,
    ) -> ValidationPoint:
        """
        创建验证点 - 买入后立即调用

        验证逻辑：
        - 30分钟内价格需要上涨1%
        - 如果达成，验证通过，继续持有
        - 如果未达成，验证失败，立即离场
        """
        vp = ValidationPoint(
            symbol=symbol,
            entry_price=entry_price,
            entry_time=entry_time,
            target_price=entry_price * (1 + self.target_gain),
            deadline=entry_time + timedelta(minutes=self.time_window),
            status='pending'
        )
        self.validation_points[symbol] = vp
        return vp

    def check_validation(
        self,
        symbol: str,
        current_price: float,
        current_time: datetime,
    ) -> ValidationResult:
        """
        检查验证点状态 - 每个tick都调用

        返回行动建议：
        - hold: 继续持有（验证中或已通过）
        - exit: 立即离场（验证失败）
        """
        if symbol not in self.validation_points:
            return ValidationResult(status='no_validation_point')

        vp = self.validation_points[symbol]

        # 检查是否超时
        if current_time > vp.deadline:
            if current_price < vp.target_price:
                # 超时且未达标，验证失败
                vp.status = 'failed'
                gain = self._calc_gain(vp.entry_price, current_price)
                return ValidationResult(
                    status='failed',
                    action='exit',
                    reason=f'验证点未达成: 要求{self.time_window}分钟内涨{self.target_gain:.1%}, 实际{gain:.2%}',
                    confidence=0.8
                )
            else:
                # 超时但已达标，验证通过
                vp.status = 'passed'
                return ValidationResult(
                    status='passed',
                    action='hold',
                    reason='验证点已达成',
                    confidence=0.9
                )

        # 检查是否已达标
        if current_price >= vp.target_price:
            vp.status = 'passed'
            gain = self._calc_gain(vp.entry_price, current_price)
            return ValidationResult(
                status='passed',
                action='hold',
                reason=f'验证点达成: {gain:.2%}',
                confidence=0.9
            )

        # 还在验证中
        time_remaining = (vp.deadline - current_time).total_seconds() / 60
        gain = self._calc_gain(vp.entry_price, current_price)
        return ValidationResult(
            status='pending',
            action='hold',
            reason=f'验证中: 剩余{time_remaining:.1f}分钟, 当前{gain:.2%}',
            confidence=0.5
        )

    def remove_validation_point(self, symbol: str):
        """移除验证点（卖出时调用）"""
        self.validation_points.pop(symbol, None)

    def _calc_gain(self, entry_price: float, current_price: float) -> float:
        """计算涨幅"""
        return (current_price - entry_price) / entry_price
