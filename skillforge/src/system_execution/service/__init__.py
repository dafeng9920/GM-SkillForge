"""
Service Layer - Internal Service承接层

System Execution Service 层职责：
- 承接来自 orchestrator 的内部服务请求
- 为业务逻辑提供最小服务接口定义
- 只读使用 frozen 主线数据

非职责：
- 不实现真实业务逻辑
- 不做外部调用
- 不进入 runtime 控制
"""

from __future__ import annotations

from .service_interface import ServiceInterface
from .base_service import BaseService

__all__ = [
    "ServiceInterface",
    "BaseService",
]
