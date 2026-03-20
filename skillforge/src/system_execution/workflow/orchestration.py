"""
Workflow Orchestration - 流程编排

> PREPARATION ONLY - 无运行时逻辑

职责:
- 连接 orchestrator → service → handler → API 各层
- 管理流程状态传递
- 不参与任何治理裁决
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol


class StageResult(Protocol):
    """阶段结果协议 - PREPARATION 级别定义"""

    stage_name: str
    status: str  # PREPARATION 级别只使用字符串，不引入枚举
    output: Optional[Dict[str, Any]]


class WorkflowOrchestrator:
    """
    工作流编排器 - PREPARATION 级别骨架

    只负责:
    1. 连接各层组件
    2. 传递状态和上下文
    3. 收集阶段结果

    不负责:
    1. 治理裁决 (由 Gate 层负责)
    2. 业务逻辑 (由 Service 层负责)
    3. 资源操作 (由 Handler 层负责)
    """

    def __init__(self) -> None:
        """初始化编排器 - PREPARATION 级别"""
        # 仅保留引用，不实例化任何运行时组件
        self._orchestrator_ref: Optional[str] = None
        self._service_refs: List[str] = []
        self._handler_refs: List[str] = []
        self._api_ref: Optional[str] = None

    def coordinate_stage(
        self,
        stage_name: str,
        context: Dict[str, Any],
        target_layer: str
    ) -> StageResult:
        """
        协调单个阶段的执行

        Args:
            stage_name: 阶段名称
            context: 执行上下文
            target_layer: 目标层级 (orchestrator|service|handler|api)

        Returns:
            阶段结果

        Raises:
            NotImplementedError: Runtime logic not implemented
        """
        # PREPARATION 级别: 只定义接口，不实现协调逻辑
        raise NotImplementedError("Stage coordination not implemented in preparation layer")

    def connect_to_orchestrator(self, orchestrator_path: str) -> None:
        """
        连接到编排器层

        Args:
            orchestrator_path: 编排器模块路径

        Note:
            PREPARATION 级别只记录路径引用，不建立运行时连接
        """
        self._orchestrator_ref = orchestrator_path

    def connect_to_service(self, service_path: str) -> None:
        """
        连接到服务层

        Args:
            service_path: 服务模块路径

        Note:
            PREPARATION 级别只记录路径引用，不建立运行时连接
        """
        self._service_refs.append(service_path)

    def connect_to_handler(self, handler_path: str) -> None:
        """
        连接到处理层

        Args:
            handler_path: 处理器模块路径

        Note:
            PREPARATION 级别只记录路径引用，不建立运行时连接
        """
        self._handler_refs.append(handler_path)

    def connect_to_api(self, api_path: str) -> None:
        """
        连接到 API 层

        Args:
            api_path: API 模块路径

        Note:
            PREPARATION 级别只记录路径引用，不建立运行时连接
        """
        self._api_ref = api_path


# 导出 - PREPARATION 级别
__all__ = [
    "StageResult",
    "WorkflowOrchestrator",
]
