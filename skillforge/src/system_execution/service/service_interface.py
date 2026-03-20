"""
Service Interface Definition

定义 Service 层的基础接口契约。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ServiceInterface(ABC):
    """
    Service 层基础接口。

    硬约束：
    - 不得实现真实业务逻辑
    - 不得执行外部调用
    - 不得进入 runtime 控制
    - 只读使用 frozen 主线数据
    """

    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        返回服务元信息（仅用于连接验证）。

        Returns:
            {
                "service_name": str,
                "service_type": str,
                "accepts_context": bool,
                "reads_frozen_only": bool,
            }
        """
        pass

    @abstractmethod
    def validate_context(self, context: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        验证来自 orchestrator 的上下文结构。

        仅检查结构完整性，不做业务判断。

        Args:
            context: 来自 orchestrator.prepare_context() 的上下文

        Returns:
            (valid, reasons) 元组
        """
        pass

    @abstractmethod
    def get_read_dependencies(self) -> list[str]:
        """
        返回只读依赖的 frozen 主线模块列表。

        Returns:
            frozen 模块路径列表，例如：
            ["skillforge.src.contracts.skill_spec", ...]
        """
        pass
