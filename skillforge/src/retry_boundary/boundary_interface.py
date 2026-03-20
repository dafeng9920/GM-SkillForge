"""
Boundary Interface Definition

定义失败分析与建议的边界接口契约，不实现具体逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class FailureType(Enum):
    """失败类型"""
    CONNECTION_FAILED = "connection_failed"      # 连接失败
    BUSINESS_LOGIC_FAILED = "business_logic_failed"  # 业务逻辑失败
    GOVERNANCE_FAILED = "governance_failed"      # 治理失败
    PERMISSION_DENIED = "permission_denied"      # 权限不足
    RESOURCE_UNAVAILABLE = "resource_unavailable"  # 资源不可用
    TIMEOUT = "timeout"                          # 超时
    UNKNOWN = "unknown"                          # 未知


class RetryType(Enum):
    """重试类型"""
    IMMEDIATE = "immediate"      # 立即重试
    DELAYED = "delayed"          # 延迟重试
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # 指数退避
    NO_RETRY = "no_retry"        # 不重试


class CompensationType(Enum):
    """补偿类型"""
    ROLLBACK = "rollback"        # 回滚
    REDO = "redo"                # 重做
    MANUAL_INTERVENTION = "manual_intervention"  # 人工介入
    NO_COMPENSATION = "no_compensation"  # 不补偿


@dataclass
class FailureEvent:
    """
    失败事件

    从 system_execution 或 integration_gateway 接收的失败通知。
    只读取，不修改。
    """
    event_id: str              # 事件 ID
    execution_id: str          # 执行 ID
    failure_type: FailureType  # 失败类型
    error_code: str            # 错误码
    error_message: str         # 错误消息
    error_context: Dict[str, Any]  # 错误上下文
    evidence_ref: str          # Evidence 引用
    gate_decision_ref: str     # GateDecision 引用
    permit_ref: Optional[str]  # Permit 引用（如有）
    timestamp: str             # 失败时间戳


@dataclass
class RetryAdvice:
    """
    重试建议

    只提供建议，不自动执行。
    """
    should_retry: bool         # 是否建议重试
    retry_type: RetryType      # 重试类型
    retry_interval: int        # 重试间隔（秒）
    max_retries: int           # 最大重试次数
    required_permit_type: str  # 需要的 permit 类型
    reason: str                # 建议理由


@dataclass
class CompensationAdvice:
    """
    补偿建议

    只提供建议，不自动执行。
    """
    should_compensate: bool        # 是否建议补偿
    compensation_type: CompensationType  # 补偿类型
    compensation_scope: str        # 补偿范围
    compensation_priority: str     # 补偿优先级
    required_permit_type: str      # 需要的 permit 类型
    reason: str                    # 建议理由


@dataclass
class FailureAnalysis:
    """
    失败分析结果

    只提供分析结果和建议，不自动执行。
    """
    analysis_id: str                # 分析 ID
    event_id: str                   # 关联的事件 ID
    failure_type: FailureType       # 失败类型
    failure_reason: str             # 失败原因
    failure_impact: str             # 失败影响
    retry_advice: Optional[RetryAdvice]      # 重试建议
    compensation_advice: Optional[CompensationAdvice]  # 补偿建议
    requires_governor_decision: bool  # 是否需要 Governor 决策


@dataclass
class PermitRequirement:
    """
    Permit 需求说明

    只说明需要的 permit 类型，不生成 permit。
    """
    action_type: str          # 动作类型 (retry/compensation/override)
    required_permit_type: str # 需要的 permit 类型
    source: str               # permit 来源 (Governor)
    scope: str                # permit 范围说明


class BoundaryInterface(ABC):
    """
    边界接口

    定义失败分析与建议的职责，不实现具体逻辑。
    当前阶段只定义接口签名。
    """

    @abstractmethod
    def observe_failure(self, event: FailureEvent) -> bool:
        """
        观察失败事件

        只定义观察接口，不实现观察逻辑。
        """
        pass

    @abstractmethod
    def analyze_failure(self, event: FailureEvent) -> FailureAnalysis:
        """
        分析失败事件

        只定义分析接口，不实现分析逻辑。
        """
        pass

    @abstractmethod
    def provide_retry_advice(self, event: FailureEvent) -> Optional[RetryAdvice]:
        """
        提供重试建议

        只定义建议接口，不实现建议逻辑。
        """
        pass

    @abstractmethod
    def provide_compensation_advice(self, event: FailureEvent) -> Optional[CompensationAdvice]:
        """
        提供补偿建议

        只定义建议接口，不实现建议逻辑。
        """
        pass

    @abstractmethod
    def explain_permit_requirement(self, advice: RetryAdvice | CompensationAdvice) -> PermitRequirement:
        """
        说明 permit 需求

        只定义说明接口，不实现说明逻辑。
        """
        pass


class BoundaryException(Exception):
    """
    边界异常基类

    只定义异常类型，不实现异常处理。
    """
    def __init__(self, error_code: str, error_message: str, context: Dict[str, Any] | None = None):
        self.error_code = error_code
        self.error_message = error_message
        self.context = context or {}
        super().__init__(f"[{error_code}] {error_message}")


# 错误码定义
class BoundaryErrorCode:
    """
    边界错误码

    只定义错误码，不实现错误处理。
    """
    INVALID_EVENT = "BOUNDARY_001"           # 无效的失败事件
    MISSING_EVIDENCE_REF = "BOUNDARY_002"    # 缺少 evidence 引用
    MISSING_DECISION_REF = "BOUNDARY_003"    # 缺少决策引用
    ANALYSIS_FAILED = "BOUNDARY_004"         # 分析失败
    ADVICE_GENERATION_FAILED = "BOUNDARY_005"  # 建议生成失败
    PERMIT_REQUIREMENT_FAILED = "BOUNDARY_006"  # permit 需求说明失败
