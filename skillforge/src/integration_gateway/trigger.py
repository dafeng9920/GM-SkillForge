"""
Trigger Definition

触发外部连接器执行。
只定义触发接口，不实现触发逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

from .gateway_interface import ExecutionIntent, PermitRef


@dataclass
class TriggerRequest:
    """
    触发请求

    只定义请求结构，不实现触发逻辑。
    """
    trigger_id: str           # 触发 ID
    connector_type: str       # 连接器类型
    action: str               # 动作
    payload: Dict[str, Any]   # 载荷
    permit_ref: str           # Permit 引用


@dataclass
class TriggerResult:
    """
    触发结果

    只定义结果结构，不实现结果处理。
    """
    trigger_id: str           # 触发 ID
    status: str               # 状态 (pending/success/failed)
    output: Dict[str, Any]    # 输出
    error: str                # 错误信息


class TriggerInterface(ABC):
    """
    触发器接口

    只定义触发接口，不实现触发逻辑。
    """

    @abstractmethod
    def trigger(self, request: TriggerRequest) -> TriggerResult:
        """
        触发连接器执行

        只定义触发接口，不实现触发逻辑。
        """
        pass

    @abstractmethod
    def check_permit_before_trigger(self, permit_ref: str) -> bool:
        """
        触发前检查 permit

        只定义检查接口，不实现检查逻辑。
        """
        pass

    @abstractmethod
    def record_trigger_attempt(self, request: TriggerRequest) -> str:
        """
        记录触发尝试

        只定义记录接口，不实现记录逻辑。
        """
        pass


class Trigger(TriggerInterface):
    """
    触发器实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化触发器（仅骨架）"""
        # 不维护真实状态
        pass

    def trigger(self, request: TriggerRequest) -> TriggerResult:
        """
        触发连接器执行（仅骨架）

        当前阶段不实现触发逻辑。
        """
        # 不实现真实触发
        raise NotImplementedError("Trigger 触发功能待实现")

    def check_permit_before_trigger(self, permit_ref: str) -> bool:
        """
        触发前检查 permit（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("Trigger permit 检查功能待实现")

    def record_trigger_attempt(self, request: TriggerRequest) -> str:
        """
        记录触发尝试（仅骨架）

        当前阶段不实现记录逻辑。
        """
        # 不实现真实记录
        raise NotImplementedError("Trigger 记录功能待实现")
