"""
Publish / Notify / Sync Boundary Module

定义发布、通知、同步三类关键动作的边界规则。
只定义边界，不执行真实动作。

阶段: 准备阶段 - 只定义骨架，不进入 runtime
"""

from .boundary_interface import (
    BoundaryInterface,
    BoundaryType,
    BoundaryCheckResult,
    BoundaryError,
    BoundaryErrorCode,
)
from .publish_boundary import PublishBoundary
from .notify_boundary import NotifyBoundary
from .sync_boundary import SyncBoundary

__all__ = [
    "BoundaryInterface",
    "BoundaryType",
    "BoundaryCheckResult",
    "BoundaryError",
    "BoundaryErrorCode",
    "PublishBoundary",
    "NotifyBoundary",
    "SyncBoundary",
]
