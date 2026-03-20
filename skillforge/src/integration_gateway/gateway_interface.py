"""
Integration Gateway Interface Definition

定义网关接口契约，不实现具体逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PermitRef:
    """
    Permit 引用

    只引用，不生成。
    """
    permit_id: str           # Permit ID
    governor_id: str         # 生成该 permit 的 Governor ID
    decision_ref: str        # 关联的 GateDecision 引用
    created_at: str          # 创建时间
    expires_at: str          # 过期时间
    scope: str               # 许可范围


@dataclass
class EvidenceRef:
    """
    Evidence 引用

    只引用，不生成。
    """
    evidence_id: str         # Evidence ID
    source_ref: str          # 生成源引用
    created_at: str          # 创建时间


@dataclass
class ExecutionIntent:
    """
    执行意图

    从 system_execution 接收的编排结果。
    只读取，不修改。
    """
    intent_id: str           # 意图 ID
    skill_id: str            # Skill ID
    action_type: str         # 动作类型 (publish/sync/notify/execute)
    payload: Dict[str, Any]  # 载荷
    permit_ref: str          # Permit 引用
    evidence_refs: list[str] # Evidence 引用列表


@dataclass
class RoutingResult:
    """
    路由结果

    只定义结构，不实现路由逻辑。
    """
    target_connector: str    # 目标连接器类型
    transformed_payload: Dict[str, Any]  # 转换后的载荷
    permit_ref: str          # 传递的 permit 引用


@dataclass
class GatewayErrorDetail:
    """
    网关错误详情

    只定义错误类型，不实现错误处理。
    """
    error_code: str          # 错误码
    error_message: str       # 错误消息
    context: Dict[str, Any]  # 错误上下文


class GatewayInterface(ABC):
    """
    网关接口

    定义网关职责，不实现具体逻辑。
    当前阶段只定义接口签名。
    """

    @abstractmethod
    def receive_intent(self, intent: ExecutionIntent) -> bool:
        """
        接收执行意图

        只定义接收接口，不实现接收逻辑。
        """
        pass

    @abstractmethod
    def validate_permit_ref(self, permit_ref: str) -> bool:
        """
        验证 permit 引用格式

        只定义验证接口，不实现验证逻辑。
        当前阶段只做格式检查，不做真实验证。
        """
        pass

    @abstractmethod
    def route_to_connector(self, intent: ExecutionIntent) -> RoutingResult:
        """
        路由到连接器

        只定义路由接口，不实现路由逻辑。
        """
        pass

    @abstractmethod
    def transport_payload(self, payload: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        搬运载荷

        只定义搬运接口，不实现搬运逻辑。
        """
        pass

    @abstractmethod
    def collect_evidence_refs(self, result: Any) -> list[EvidenceRef]:
        """
        收集 Evidence 引用

        只定义收集接口，不实现收集逻辑。
        只引用，不生成新的 Evidence。
        """
        pass


class GatewayException(Exception):
    """
    网关异常基类

    只定义异常类型，不实现异常处理。
    """
    def __init__(self, error_code: str, error_message: str, context: Dict[str, Any] | None = None):
        self.error_code = error_code
        self.error_message = error_message
        self.context = context or {}
        super().__init__(f"[{error_code}] {error_message}")


# 错误码定义
class GatewayErrorCode:
    """
    网关错误码

    只定义错误码，不实现错误处理。
    """
    INVALID_INTENT = "GATEWAY_001"           # 无效的执行意图
    MISSING_PERMIT = "GATEWAY_002"           # 缺少 permit
    INVALID_PERMIT_REF = "GATEWAY_003"       # 无效的 permit 引用
    ROUTING_FAILED = "GATEWAY_004"           # 路由失败
    TRANSPORT_FAILED = "GATEWAY_005"         # 搬运失败
    CONNECTOR_NOT_FOUND = "GATEWAY_006"      # 连接器未找到
