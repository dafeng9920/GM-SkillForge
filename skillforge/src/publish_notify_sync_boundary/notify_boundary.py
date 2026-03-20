"""
Notify Boundary Definition

定义通知动作的边界规则。
只定义边界接口，不实现通知逻辑。
"""

from abc import ABC, abstractmethod

from .boundary_interface import (
    BoundaryCheckResult,
    NotifyRequest,
    NotifyResult,
)


class NotifyBoundaryInterface(ABC):
    """
    通知边界接口

    只定义通知边界接口，不实现通知逻辑。
    """

    @abstractmethod
    def check_notify_request(self, request: NotifyRequest) -> BoundaryCheckResult:
        """
        检查通知请求

        只定义检查接口，不实现检查逻辑。
        """
        pass

    @abstractmethod
    def validate_notify_permit(self, permit_ref: str) -> bool:
        """
        验证通知 permit

        只定义验证接口，不实现验证逻辑。
        委托给 E4 的 permit 校验。
        """
        pass

    @abstractmethod
    def check_notification_target(self, target: str) -> bool:
        """
        检查通知目标

        只定义检查接口，不实现检查逻辑。
        """
        pass


class NotifyBoundary(NotifyBoundaryInterface):
    """
    通知边界实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化通知边界（仅骨架）"""
        # 不维护真实状态
        pass

    def check_notify_request(self, request: NotifyRequest) -> BoundaryCheckResult:
        """
        检查通知请求（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("NotifyBoundary 检查功能待实现")

    def validate_notify_permit(self, permit_ref: str) -> bool:
        """
        验证通知 permit（仅骨架）

        当前阶段不实现验证逻辑。
        委托给 E4 的 permit 校验。
        """
        # 不实现真实验证
        raise NotImplementedError("NotifyBoundary permit 验证功能待实现")

    def check_notification_target(self, target: str) -> bool:
        """
        检查通知目标（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("NotifyBoundary 目标检查功能待实现")
