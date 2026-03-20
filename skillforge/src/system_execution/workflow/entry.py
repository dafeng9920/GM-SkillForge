"""
Workflow Entry Point - 入口编排

> PREPARATION ONLY - 无运行时逻辑

职责:
- 接收外部请求并路由到正确的处理路径
- 不做治理裁决
- 不实现业务逻辑
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Protocol


class WorkflowContext(Protocol):
    """工作流上下文协议 - PREPARATION 级别定义"""

    request_id: str
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]


class WorkflowEntry:
    """
    工作流入口 - PREPARATION 级别骨架

    只负责:
    1. 接收请求
    2. 路由分发
    3. 状态传递

    不负责:
    1. 治理裁决 (由 Gate 层负责)
    2. 业务执行 (由 Service 层负责)
    3. 资源操作 (由 Handler 层负责)
    """

    def __init__(self) -> None:
        """初始化工作流入口 - PREPARATION 级别"""
        # TODO: Runtime initialization (BLOCKED - preparation only)
        self._orchestrator_ref: Optional[str] = None  # 仅引用，不实例化
        self._service_ref: Optional[str] = None

    def route(self, context: WorkflowContext) -> str:
        """
        路由请求到正确的处理路径

        Args:
            context: 工作流上下文

        Returns:
            路由目标标识符 (PREPARATION 级别只返回字符串)

        Raises:
            NotImplementedError: Runtime logic not implemented
        """
        # PREPARATION 级别: 只定义接口，不实现路由逻辑
        raise NotImplementedError("Runtime routing not implemented in preparation layer")

    def dispatch_to_orchestrator(
        self, context: WorkflowContext
    ) -> Dict[str, Any]:
        """
        分发到编排器

        Args:
            context: 工作流上下文

        Returns:
            编排结果 (PREPARATION 级别只返回空字典)

        Raises:
            NotImplementedError: Runtime logic not implemented
        """
        # PREPARATION 级别: 只定义接口，不调用编排器
        raise NotImplementedError("Orchestrator dispatch not implemented in preparation layer")


# 导出 - PREPARATION 级别
__all__ = [
    "WorkflowContext",
    "WorkflowEntry",
]
