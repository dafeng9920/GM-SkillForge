"""
Base Service Implementation

提供 Service 层的最小实现（仅用于承接，不执行业务逻辑）。
"""

from __future__ import annotations

from typing import Any, Dict, List
from .service_interface import ServiceInterface


class BaseService(ServiceInterface):
    """
    Service 层基础实现。

    硬约束：
    - NO real business logic implementation
    - NO external calls
    - NO runtime control
    - READ-ONLY access to frozen objects
    """

    # Service 元信息
    _SERVICE_NAME = "BaseService"
    _SERVICE_TYPE = "internal_service"

    # 只读依赖的 frozen 主线模块（示例）
    _FROZEN_DEPENDENCIES: List[str] = [
        # frozen 主线模块将在实际实现时添加
    ]

    def get_service_info(self) -> Dict[str, Any]:
        """
        返回服务元信息。
        """
        return {
            "service_name": self._SERVICE_NAME,
            "service_type": self._SERVICE_TYPE,
            "accepts_context": True,
            "reads_frozen_only": True,
            "has_business_logic": False,  # 最小骨架，无业务逻辑
        }

    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        验证来自 orchestrator 的上下文结构。

        检查项：
        1. request_id 存在且非空
        2. route_target 存在
        3. routing_decision 存在
        """
        reasons: List[str] = []

        # 检查 request_id
        if "request_id" not in context or not context.get("request_id"):
            reasons.append("missing or empty request_id")

        # 检查 route_target
        if "route_target" not in context:
            reasons.append("missing route_target")

        # 检查 routing_decision
        if "routing_decision" not in context:
            reasons.append("missing routing_decision")

        return (len(reasons) == 0, reasons)

    def get_read_dependencies(self) -> List[str]:
        """
        返回只读依赖的 frozen 主线模块列表。
        """
        return list(self._FROZEN_DEPENDENCIES)
