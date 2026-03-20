"""
External Connection Contract Type Definitions

定义外部连接接口契约的类型结构。
只定义接口，不实现连接。
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
    """

    module: str
    """frozen 模块路径"""

    object_type: str
    """frozen 对象类型"""

    access_pattern: str  # "read" | "reference" | "query"
    """访问模式（只读）"""

    purpose: str
    """使用目的"""


@dataclass(frozen=True)
class ExternalConnectionContract:
    """
    外部连接接口契约定义

    硬约束：
    - 只定义接口，不实现连接
    - 只声明 permit 依赖，不生成 permit
    - 只声明 frozen 依赖，不修改 frozen 对象
    - 契约对象不可变 (frozen=True)
    """

    connection_id: str
    """连接唯一标识符"""

    connection_type: str  # "git" | "webhook" | "api" | "registry" | "storage" | "notification"
    """连接类型分类"""

    target: str
    """连接目标标识（不包含敏感信息）"""

    required_permits: List[str]
    """需要的 permit 类型列表（声明，不生成）"""

    frozen_dependencies: List[FrozenDependencyDeclaration]
    """frozen 主线依赖声明（只读）"""

    request_schema: Dict[str, Any]
    """请求数据结构规范"""

    response_schema: Dict[str, Any]
    """响应数据结构规范"""

    error_classes: Dict[str, str]
    """错误分类定义"""

    contract_type: str = "ExternalConnectionContract"
    """契约类型标识"""

    boundary_note: str = (
        "此契约只定义接口，不实现连接。真实连接由 Integration Gateway 执行。"
    )
    """边界声明"""

    def get_frozen_dependency_summary(self) -> List[str]:
        """
        获取 frozen 依赖摘要

        Returns:
            frozen 模块路径列表
        """
        return [dep.module for dep in self.frozen_dependencies]


@dataclass(frozen=True)
class EvidenceReferenceDeclaration:
    """
    Evidence 引用声明

    硬约束：
    - 只读引用，不修改
    - 搬运副本，不移动原始对象
    """

    evidence_type: str  # "gate_decision" | "validation_report" | "audit_pack"
    """证据类型"""

    access_pattern: str  # "read" | "upload" | "notify"
    """访问模式"""

    purpose: str
    """使用目的"""


@dataclass(frozen=True)
class PermitRequirementDeclaration:
    """
    Permit 需求声明

    硬约束：
    - 只声明需求，不生成 permit
    - 不处理 permit 续期
    """

    permit_type: str
    """permit 类型"""

    required_for: str
    """用途说明"""

    validation_rule: Optional[str] = None
    """验证规则（可选）"""


# 预定义连接契约示例（通用、协议无关）

# 注意：Connector Contract 只定义通用、协议无关的接口结构。
# 具体协议（Git、Webhook 等）的专用字段由 Integration Gateway 处理。

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
            purpose="获取技能规范用于外部操作"
        ),
    ],
    # 通用请求结构（协议无关）
    request_schema={
        "type": "object",
        "properties": {
            "target_ref": {
                "type": "string",
                "description": "目标引用标识（协议无关）"
            },
            "action_type": {
                "type": "string",
                "description": "动作类型（协议无关）"
            },
            "payload": {
                "type": "object",
                "description": "载荷数据（具体协议内容由 Integration Gateway 处理）"
            },
            "metadata": {
                "type": "object",
                "description": "元数据（用于追踪和审计）"
            },
        },
    },
    # 通用响应结构（协议无关）
    response_schema={
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "操作是否成功"
            },
            "result_ref": {
                "type": "string",
                "description": "结果引用标识（协议无关）"
            },
            "error_code": {
                "type": "string",
                "description": "错误代码（如有）"
            },
        },
    },
    error_classes={
        "PERMIT_MISSING": "缺少操作许可",
        "TARGET_UNREACHABLE": "目标不可达",
        "PAYLOAD_INVALID": "载荷无效",
    },
)
