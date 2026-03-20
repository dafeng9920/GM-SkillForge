"""
Connector Contract Types

定义外部连接接口契约的类型结构。
只定义接口，不实现连接。

Contract: EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1
Task: E1 - connector contract 子面准备
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class FrozenDependencyDeclaration:
    """
    Frozen 依赖声明

    硬约束：
    - 所有 frozen 依赖必须显式声明
    - 所有访问必须是只读的
    - 不得隐式依赖 frozen 对象

    Attributes:
        module: frozen 模块路径
        object_type: frozen 对象类型
        access_pattern: 访问模式（只读）: "read" | "reference" | "query"
        purpose: 使用目的
    """

    module: str
    object_type: str
    access_pattern: str  # "read" | "reference" | "query"
    purpose: str


@dataclass(frozen=True)
class PermitRequirementDeclaration:
    """
    Permit 需求声明

    硬约束：
    - 只声明需求，不生成 permit
    - 不处理 permit 验证
    - 不处理 permit 续期
    - permit 类型由 Governor 定义

    Attributes:
        permit_type: permit 类型（引用 Governor 定义）
        required_for: 用途说明
        validation_rule: 验证规则描述（可选，不实现）
    """

    permit_type: str
    required_for: str
    validation_rule: Optional[str] = None


@dataclass(frozen=True)
class EvidenceReferenceDeclaration:
    """
    Evidence 引用声明

    硬约束：
    - 只读引用，不修改
    - 搬运副本，不移动原始对象
    - Evidence/AuditPack 由内核生成

    Attributes:
        evidence_type: 证据类型: "gate_decision" | "validation_report" | "audit_pack"
        access_pattern: 访问模式: "read" | "upload" | "notify"
        purpose: 使用目的
    """

    evidence_type: str  # "gate_decision" | "validation_report" | "audit_pack"
    access_pattern: str  # "read" | "upload" | "notify"
    purpose: str


@dataclass(frozen=True)
class ExternalConnectionContract:
    """
    外部连接接口契约定义

    硬约束：
    - 只定义接口，不实现连接
    - 只声明 permit 依赖，不生成 permit
    - 只声明 frozen 依赖，不修改 frozen 对象
    - 契约对象不可变 (frozen=True)
    - 不进入 runtime

    Attributes:
        connection_id: 连接唯一标识符
        connection_type: 连接类型分类: "git" | "webhook" | "api" | "registry" | "storage" | "notification"
        target: 连接目标标识（不包含敏感信息）
        required_permits: 需要的 permit 类型列表（声明，不生成）
        frozen_dependencies: frozen 主线依赖声明（只读）
        request_schema: 请求数据结构规范
        response_schema: 响应数据结构规范
        error_classes: 错误分类定义
        contract_type: 契约类型标识
        boundary_note: 边界声明
    """

    connection_id: str
    connection_type: str  # "git" | "webhook" | "api" | "registry" | "storage" | "notification"
    target: str
    required_permits: List[str]
    frozen_dependencies: List[FrozenDependencyDeclaration]
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    error_classes: Dict[str, str]
    contract_type: str = "ExternalConnectionContract"
    boundary_note: str = (
        "此契约只定义接口，不实现连接。真实连接由 Integration Gateway 执行。"
    )

    def get_frozen_dependency_summary(self) -> List[str]:
        """
        获取 frozen 依赖摘要

        Returns:
            frozen 模块路径列表
        """
        return [dep.module for dep in self.frozen_dependencies]


@dataclass(frozen=True)
class ConnectorRequest:
    """
    Connector 请求定义

    用于 Integration Gateway 向 Connector 传递请求。
    只定义结构，不实现请求逻辑。

    Attributes:
        connector_type: connector 类型
        action: 执行动作
        payload: 载荷数据
        permit_ref: permit 引用（由 Governor 生成）
        metadata: 元数据（用于追踪和审计）
    """

    connector_type: str
    action: str
    payload: Dict[str, Any]
    permit_ref: Optional[str] = None
    metadata: Dict[str, Any] | None = None


@dataclass(frozen=True)
class ConnectorResult:
    """
    Connector 结果定义

    用于 Connector 向 Integration Gateway 返回结果。
    只定义结构，不实现结果处理逻辑。

    Attributes:
        success: 操作是否成功
        result_ref: 结果引用标识
        output: 输出数据
        error_code: 错误代码（如有）
        evidence_ref: Evidence 引用（由内核生成）
    """

    success: bool
    result_ref: str
    output: Dict[str, Any] | None = None
    error_code: str | None = None
    evidence_ref: str | None = None


# 预定义连接契约示例（通用、协议无关）

GENERIC_CONNECTION_CONTRACT = ExternalConnectionContract(
    contract_type="ExternalConnectionContract",
    connection_id="generic_connection_default",
    connection_type="generic",
    target="external_system",
    required_permits=["external.action.execute"],
    frozen_dependencies=[
        FrozenDependencyDeclaration(
            module="skillforge.src.contracts.normalized_skill_spec",
            object_type="NormalizedSkillSpec",
            access_pattern="read",
            purpose="获取技能规范用于外部操作",
        ),
    ],
    # 通用请求结构（协议无关）
    request_schema={
        "type": "object",
        "properties": {
            "target_ref": {
                "type": "string",
                "description": "目标引用标识（协议无关）",
            },
            "action_type": {
                "type": "string",
                "description": "动作类型（协议无关）",
            },
            "payload": {
                "type": "object",
                "description": "载荷数据（具体协议内容由 Integration Gateway 处理）",
            },
            "metadata": {
                "type": "object",
                "description": "元数据（用于追踪和审计）",
            },
        },
    },
    # 通用响应结构（协议无关）
    response_schema={
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "操作是否成功",
            },
            "result_ref": {
                "type": "string",
                "description": "结果引用标识（协议无关）",
            },
            "error_code": {
                "type": "string",
                "description": "错误代码（如有）",
            },
        },
    },
    error_classes={
        "PERMIT_MISSING": "缺少操作许可",
        "TARGET_UNREACHABLE": "目标不可达",
        "PAYLOAD_INVALID": "载荷无效",
    },
)


# 导出公共 API
__all__ = [
    "FrozenDependencyDeclaration",
    "PermitRequirementDeclaration",
    "EvidenceReferenceDeclaration",
    "ExternalConnectionContract",
    "ConnectorRequest",
    "ConnectorResult",
    "GENERIC_CONNECTION_CONTRACT",
]
