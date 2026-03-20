"""
Publish Boundary Definition

定义发布动作的边界规则。
只定义边界接口，不实现发布逻辑。
"""

from abc import ABC, abstractmethod

from .boundary_interface import (
    BoundaryCheckResult,
    BoundaryInterface,
    PublishRequest,
    PublishResult,
)


class PublishBoundaryInterface(ABC):
    """
    发布边界接口

    只定义发布边界接口，不实现发布逻辑。
    """

    @abstractmethod
    def check_publish_request(self, request: PublishRequest) -> BoundaryCheckResult:
        """
        检查发布请求

        只定义检查接口，不实现检查逻辑。
        """
        pass

    @abstractmethod
    def validate_publish_permit(self, permit_ref: str) -> bool:
        """
        验证发布 permit

        只定义验证接口，不实现验证逻辑。
        委托给 E4 的 permit 校验。
        """
        pass

    @abstractmethod
    def check_target_system(self, target_system: str) -> bool:
        """
        检查目标系统

        只定义检查接口，不实现检查逻辑。
        """
        pass


class PublishBoundary(PublishBoundaryInterface):
    """
    发布边界实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化发布边界（仅骨架）"""
        # 不维护真实状态
        pass

    def check_publish_request(self, request: PublishRequest) -> BoundaryCheckResult:
        """
        检查发布请求（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("PublishBoundary 检查功能待实现")

    def validate_publish_permit(self, permit_ref: str) -> bool:
        """
        验证发布 permit（仅骨架）

        当前阶段不实现验证逻辑。
        委托给 E4 的 permit 校验。
        """
        # 不实现真实验证
        raise NotImplementedError("PublishBoundary permit 验证功能待实现")

    def check_target_system(self, target_system: str) -> bool:
        """
        检查目标系统（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("PublishBoundary 目标系统检查功能待实现")
