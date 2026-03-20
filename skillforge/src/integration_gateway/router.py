"""
Router Definition

路由执行意图到正确的连接器。
只定义路由接口，不实现路由逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

from .gateway_interface import ExecutionIntent, RoutingResult


@dataclass
class ConnectorRegistration:
    """
    连接器注册信息

    只定义注册结构，不维护真实注册表。
    """
    connector_type: str       # 连接器类型
    connector_id: str         # 连接器 ID
    supported_actions: list[str]  # 支持的动作类型
    config: Dict[str, Any]    # 配置


@dataclass
class RoutingRule:
    """
    路由规则

    只定义规则结构，不实现路由规则。
    """
    action_type: str          # 动作类型
    target_connector: str     # 目标连接器
    priority: int             # 优先级
    conditions: Dict[str, Any]  # 路由条件


class RouterInterface(ABC):
    """
    路由器接口

    只定义路由接口，不实现路由逻辑。
    """

    @abstractmethod
    def register_connector(self, registration: ConnectorRegistration) -> bool:
        """
        注册连接器

        只定义注册接口，不维护真实注册表。
        """
        pass

    @abstractmethod
    def add_routing_rule(self, rule: RoutingRule) -> bool:
        """
        添加路由规则

        只定义规则接口，不维护真实规则表。
        """
        pass

    @abstractmethod
    def route(self, intent: ExecutionIntent) -> RoutingResult:
        """
        路由执行意图

        只定义路由接口，不实现路由逻辑。
        """
        pass

    @abstractmethod
    def get_connector_for_action(self, action_type: str) -> Optional[str]:
        """
        获取动作对应的连接器

        只定义查询接口，不实现查询逻辑。
        """
        pass


class Router(RouterInterface):
    """
    路由器实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化路由器（仅骨架）"""
        # 不维护真实状态
        self._registrations: Dict[str, ConnectorRegistration] = {}
        self._rules: list[RoutingRule] = []

    def register_connector(self, registration: ConnectorRegistration) -> bool:
        """
        注册连接器（仅骨架）

        当前阶段不实现注册逻辑。
        """
        # 不实现真实注册
        raise NotImplementedError("Router 注册功能待实现")

    def add_routing_rule(self, rule: RoutingRule) -> bool:
        """
        添加路由规则（仅骨架）

        当前阶段不实现规则添加逻辑。
        """
        # 不实现真实规则添加
        raise NotImplementedError("Router 规则添加功能待实现")

    def route(self, intent: ExecutionIntent) -> RoutingResult:
        """
        路由执行意图（仅骨架）

        当前阶段不实现路由逻辑。
        """
        # 不实现真实路由
        raise NotImplementedError("Router 路由功能待实现")

    def get_connector_for_action(self, action_type: str) -> Optional[str]:
        """
        获取动作对应的连接器（仅骨架）

        当前阶段不实现查询逻辑。
        """
        # 不实现真实查询
        raise NotImplementedError("Router 查询功能待实现")
