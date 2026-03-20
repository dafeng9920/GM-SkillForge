"""
Boundary Interface Definition

定义 publish/notify/sync 边界接口契约，不实现具体逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from enum import Enum


class BoundaryType(Enum):
    """
    边界类型
    """
    PUBLISH = "PUBLISH"
    NOTIFY = "NOTIFY"
    SYNC = "SYNC"


@dataclass
class BoundaryCheckResult:
    """
    边界检查结果

    只定义结果结构，不实现检查逻辑。
    """
    action: str                    # 动作名称
    boundary_type: BoundaryType    # 边界类型
    allowed: bool                  # 是否允许
    block_reason: str | None       # 阻断原因
    permit_required: bool          # 是否需要 permit
    permit_check_result: Any | None  # Permit 校验结果（来自 E4）


@dataclass
class PublishRequest:
    """
    发布请求

    只定义请求结构，不实现发布逻辑。
    """
    skill_id: str                  # Skill ID
    target_system: str             # 目标系统
    payload: dict[str, Any]        # 载荷
    permit_ref: str                # Permit 引用


@dataclass
class PublishResult:
    """
    发布结果

    只定义结果结构，不实现发布逻辑。
    """
    request_id: str                # 请求 ID
    status: str                    # 状态
    output: dict[str, Any]         # 输出
    error: str | None              # 错误信息


@dataclass
class NotifyRequest:
    """
    通知请求

    只定义请求结构，不实现通知逻辑。
    """
    notification_type: str         # 通知类型
    target: str                    # 通知目标
    payload: dict[str, Any]        # 载荷
    permit_ref: str                # Permit 引用


@dataclass
class NotifyResult:
    """
    通知结果

    只定义结果结构，不实现通知逻辑。
    """
    request_id: str                # 请求 ID
    status: str                    # 状态
    output: dict[str, Any]         # 输出
    error: str | None              # 错误信息


@dataclass
class SyncRequest:
    """
    同步请求

    只定义请求结构，不实现同步逻辑。
    """
    sync_type: str                 # 同步类型
    target_system: str             # 目标系统
    payload: dict[str, Any]        # 载荷
    permit_ref: str                # Permit 引用


@dataclass
class SyncResult:
    """
    同步结果

    只定义结果结构，不实现同步逻辑。
    """
    request_id: str                # 请求 ID
    status: str                    # 状态
    output: dict[str, Any]         # 输出
    error: str | None              # 错误信息


class BoundaryInterface(ABC):
    """
    边界接口

    定义边界职责，不实现具体逻辑。
    当前阶段只定义接口签名。
    """

    @abstractmethod
    def check_boundary(self, action: str, permit_ref: str, payload: dict[str, Any]) -> BoundaryCheckResult:
        """
        检查边界

        只定义检查接口，不实现检查逻辑。
        委托给 E4 的 permit 校验。
        """
        pass

    @abstractmethod
    def validate_permit_ref(self, permit_ref: str) -> bool:
        """
        验证 permit 引用格式

        只定义验证接口，不实现验证逻辑。
        委托给 E4 的 permit 校验。
        """
        pass

    @abstractmethod
    def check_permit_type_match(self, action: str, permit_ref: str) -> bool:
        """
        检查 permit 类型是否匹配动作类型

        只定义检查接口，不实现检查逻辑。
        """
        pass

    @abstractmethod
    def check_publish_permit(self, request: PublishRequest) -> BoundaryCheckResult:
        """
        检查发布 permit

        只定义检查接口，不实现检查逻辑。
        """
        pass

    @abstractmethod
    def check_notify_permit(self, request: NotifyRequest) -> BoundaryCheckResult:
        """
        检查通知 permit

        只定义检查接口，不实现检查逻辑。
        """
        pass

    @abstractmethod
    def check_sync_permit(self, request: SyncRequest) -> BoundaryCheckResult:
        """
        检查同步 permit

        只定义检查接口，不实现检查逻辑。
        """
        pass


class BoundaryError(Exception):
    """
    边界异常基类

    只定义异常类型，不实现异常处理。
    """
    def __init__(self, error_code: str, error_message: str, context: dict[str, Any] | None = None):
        self.error_code = error_code
        self.error_message = error_message
        self.context = context or {}
        super().__init__(f"[{error_code}] {error_message}")


class BoundaryErrorCode:
    """
    边界错误码

    只定义错误码，不实现错误处理。
    """
    INVALID_REQUEST = "BOUNDARY_001"           # 无效的请求
    MISSING_PERMIT = "BOUNDARY_002"            # 缺少 permit
    INVALID_PERMIT_REF = "BOUNDARY_003"        # 无效的 permit 引用
    PERMIT_TYPE_MISMATCH = "BOUNDARY_004"      # Permit 类型不匹配
    ACTION_NOT_ALLOWED = "BOUNDARY_005"        # 动作不允许
    TARGET_SYSTEM_INVALID = "BOUNDARY_006"     # 目标系统无效
    CHECK_FAILED = "BOUNDARY_007"              # 边界检查失败
