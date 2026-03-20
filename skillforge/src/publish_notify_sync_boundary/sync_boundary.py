"""
Sync Boundary Definition

定义同步动作的边界规则。
只定义边界接口，不实现同步逻辑。
"""

from abc import ABC, abstractmethod

from .boundary_interface import (
    BoundaryCheckResult,
    SyncRequest,
    SyncResult,
)


class SyncBoundaryInterface(ABC):
    """
    同步边界接口

    只定义同步边界接口，不实现同步逻辑。
    """

    @abstractmethod
    def check_sync_request(self, request: SyncRequest) -> BoundaryCheckResult:
        """
        检查同步请求

        只定义检查接口，不实现检查逻辑。
        """
        pass

    @abstractmethod
    def validate_sync_permit(self, permit_ref: str) -> bool:
        """
        验证同步 permit

        只定义验证接口，不实现验证逻辑。
        委托给 E4 的 permit 校验。
        """
        pass

    @abstractmethod
    def check_sync_target(self, target_system: str) -> bool:
        """
        检查同步目标

        只定义检查接口，不实现检查逻辑。
        """
        pass


class SyncBoundary(SyncBoundaryInterface):
    """
    同步边界实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化同步边界（仅骨架）"""
        # 不维护真实状态
        pass

    def check_sync_request(self, request: SyncRequest) -> BoundaryCheckResult:
        """
        检查同步请求（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("SyncBoundary 检查功能待实现")

    def validate_sync_permit(self, permit_ref: str) -> bool:
        """
        验证同步 permit（仅骨架）

        当前阶段不实现验证逻辑。
        委托给 E4 的 permit 校验。
        """
        # 不实现真实验证
        raise NotImplementedError("SyncBoundary permit 验证功能待实现")

    def check_sync_target(self, target_system: str) -> bool:
        """
        检查同步目标（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("SyncBoundary 目标检查功能待实现")
