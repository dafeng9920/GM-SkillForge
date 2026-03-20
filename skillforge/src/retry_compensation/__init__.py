"""
Retry / Compensation Boundary Module

失败后的重试策略与补偿建议边界。
只定义边界接口与策略草案，不实现自动重试与补偿执行。

阶段: 准备阶段 - 只定义骨架，不进入 runtime
"""

from .boundary_interface import BoundaryInterface
from .retry_policy import RetryPolicy
from .compensation_advisor import CompensationAdvisor

__all__ = [
    "BoundaryInterface",
    "RetryPolicy",
    "CompensationAdvisor",
]
