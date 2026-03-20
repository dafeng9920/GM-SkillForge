"""
Compensation Advisor Definition

补偿建议定义，只定义建议接口，不实现补偿逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

from .boundary_interface import FailureEvent, FailureType, CompensationType


@dataclass
class CompensationImpact:
    """
    补偿影响评估

    只定义影响评估结构，不实现评估逻辑。
    """
    affected_scope: str        # 影响范围
    affected_resources: list[str]  # 受影响的资源
    rollback_feasibility: str   # 回滚可行性
    estimated_cost: str         # 预估成本


@dataclass
class CompensationPlan:
    """
    补偿计划

    只定义计划结构，不实现计划生成逻辑。
    """
    compensation_type: CompensationType  # 补偿类型
    compensation_steps: list[str]        # 补偿步骤
    required_resources: list[str]        # 所需资源
    estimated_duration: int              # 预估时长（秒）
    risk_level: str                      # 风险等级


class CompensationAdvisorInterface(ABC):
    """
    补偿建议接口

    只定义建议接口，不实现建议逻辑。
    """

    @abstractmethod
    def should_compensate(self, event: FailureEvent) -> bool:
        """
        判断是否应该补偿

        只定义判断接口，不实现判断逻辑。
        """
        pass

    @abstractmethod
    def get_compensation_type(self, event: FailureEvent) -> CompensationType:
        """
        获取补偿类型

        只定义获取接口，不实现获取逻辑。
        """
        pass

    @abstractmethod
    def assess_compensation_impact(self, event: FailureEvent) -> CompensationImpact:
        """
        评估补偿影响

        只定义评估接口，不实现评估逻辑。
        """
        pass

    @abstractmethod
    def generate_compensation_plan(self, event: FailureEvent) -> CompensationPlan:
        """
        生成补偿计划

        只定义生成接口，不实现生成逻辑。
        """
        pass

    @abstractmethod
    def explain_compensation_advice(self, event: FailureEvent) -> str:
        """
        说明补偿建议

        只定义说明接口，不实现说明逻辑。
        """
        pass

    @abstractmethod
    def check_compensation_feasibility(self, event: FailureEvent) -> tuple[bool, str]:
        """
        检查补偿可行性

        只定义检查接口，不实现检查逻辑。

        Returns:
            (feasible, reason) tuple
        """
        pass


class CompensationAdvisor(CompensationAdvisorInterface):
    """
    补偿建议实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化补偿建议（仅骨架）"""
        # 不维护真实状态
        pass

    def should_compensate(self, event: FailureEvent) -> bool:
        """
        判断是否应该补偿（仅骨架）

        当前阶段不实现判断逻辑。
        """
        # 不实现真实判断
        raise NotImplementedError("CompensationAdvisor 判断功能待实现")

    def get_compensation_type(self, event: FailureEvent) -> CompensationType:
        """
        获取补偿类型（仅骨架）

        当前阶段不实现获取逻辑。
        """
        # 不实现真实获取
        raise NotImplementedError("CompensationAdvisor 类型获取功能待实现")

    def assess_compensation_impact(self, event: FailureEvent) -> CompensationImpact:
        """
        评估补偿影响（仅骨架）

        当前阶段不实现评估逻辑。
        """
        # 不实现真实评估
        raise NotImplementedError("CompensationAdvisor 影响评估功能待实现")

    def generate_compensation_plan(self, event: FailureEvent) -> CompensationPlan:
        """
        生成补偿计划（仅骨架）

        当前阶段不实现生成逻辑。
        """
        # 不实现真实生成
        raise NotImplementedError("CompensationAdvisor 计划生成功能待实现")

    def explain_compensation_advice(self, event: FailureEvent) -> str:
        """
        说明补偿建议（仅骨架）

        当前阶段不实现说明逻辑。
        """
        # 不实现真实说明
        raise NotImplementedError("CompensationAdvisor 建议说明功能待实现")

    def check_compensation_feasibility(self, event: FailureEvent) -> tuple[bool, str]:
        """
        检查补偿可行性（仅骨架）

        当前阶段不实现检查逻辑。
        """
        # 不实现真实检查
        raise NotImplementedError("CompensationAdvisor 可行性检查功能待实现")
