"""
Retry Policy Definition

重试策略定义，只定义策略接口，不实现重试逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

from .boundary_interface import FailureEvent, FailureType, RetryType


@dataclass
class RetryCondition:
    """
    重试条件

    只定义条件结构，不实现条件判断。
    """
    failure_type: FailureType  # 失败类型
    error_code_pattern: str     # 错误码模式
    max_attempts: int          # 最大尝试次数
    retry_window: int          # 重试窗口（秒）


@dataclass
class RetrySchedule:
    """
    重试调度

    只定义调度结构，不实现调度逻辑。
    """
    retry_type: RetryType      # 重试类型
    initial_delay: int         # 初始延迟（秒）
    max_delay: int             # 最大延迟（秒）
    backoff_multiplier: float  # 退避乘数


class RetryPolicyInterface(ABC):
    """
    重试策略接口

    只定义策略接口，不实现策略逻辑。
    """

    @abstractmethod
    def should_retry(self, event: FailureEvent) -> bool:
        """
        判断是否应该重试

        只定义判断接口，不实现判断逻辑。
        """
        pass

    @abstractmethod
    def get_retry_type(self, event: FailureEvent) -> RetryType:
        """
        获取重试类型

        只定义获取接口，不实现获取逻辑。
        """
        pass

    @abstractmethod
    def calculate_retry_delay(self, event: FailureEvent, attempt: int) -> int:
        """
        计算重试延迟

        只定义计算接口，不实现计算逻辑。
        """
        pass

    @abstractmethod
    def get_max_retries(self, event: FailureEvent) -> int:
        """
        获取最大重试次数

        只定义获取接口，不实现获取逻辑。
        """
        pass

    @abstractmethod
    def explain_retry_policy(self, event: FailureEvent) -> str:
        """
        说明重试策略

        只定义说明接口，不实现说明逻辑。
        """
        pass


class RetryPolicy(RetryPolicyInterface):
    """
    重试策略实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化重试策略（仅骨架）"""
        # 不维护真实状态
        pass

    def should_retry(self, event: FailureEvent) -> bool:
        """
        判断是否应该重试（仅骨架）

        当前阶段不实现判断逻辑。
        """
        # 不实现真实判断
        raise NotImplementedError("RetryPolicy 判断功能待实现")

    def get_retry_type(self, event: FailureEvent) -> RetryType:
        """
        获取重试类型（仅骨架）

        当前阶段不实现获取逻辑。
        """
        # 不实现真实获取
        raise NotImplementedError("RetryPolicy 类型获取功能待实现")

    def calculate_retry_delay(self, event: FailureEvent, attempt: int) -> int:
        """
        计算重试延迟（仅骨架）

        当前阶段不实现计算逻辑。
        """
        # 不实现真实计算
        raise NotImplementedError("RetryPolicy 延迟计算功能待实现")

    def get_max_retries(self, event: FailureEvent) -> int:
        """
        获取最大重试次数（仅骨架）

        当前阶段不实现获取逻辑。
        """
        # 不实现真实获取
        raise NotImplementedError("RetryPolicy 最大重试次数获取功能待实现")

    def explain_retry_policy(self, event: FailureEvent) -> str:
        """
        说明重试策略（仅骨架）

        当前阶段不实现说明逻辑。
        """
        # 不实现真实说明
        raise NotImplementedError("RetryPolicy 策略说明功能待实现")
