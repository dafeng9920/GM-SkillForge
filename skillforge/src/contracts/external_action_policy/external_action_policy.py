"""
External Action Policy - 外部动作策略

定义关键动作/非关键动作分类，以及 permit 校验规则。

遵循 permit_contract_v1.yml 和 gate_permit.py 的错误码映射。

Task ID: E4
Executor: Kior-B
Date: 2026-03-19
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from .classification import ActionCategory, classify_action
from .permit_check import check_permit_for_action, PermitCheckResult


# 不可变关键动作集合 - 禁止运行时修改
CRITICAL_ACTIONS: frozenset[str] = frozenset({
    "PUBLISH_LISTING",
    "EXECUTE_VIA_N8N",
    "EXPORT_WHITELIST",
    "UPGRADE_REPLACE_ACTIVE",
    "TRIGGER_EXTERNAL_CONNECTOR",
    "WRITE_EXTERNAL_STATE",
    "MODIFY_EXTERNAL_RESOURCE",
    "DELETE_EXTERNAL_RESOURCE",
})


class ExecutionBlockReason(Enum):
    """执行阻断原因"""
    PERMIT_REQUIRED = "PERMIT_REQUIRED"
    PERMIT_INVALID = "PERMIT_INVALID"
    PERMIT_EXPIRED = "PERMIT_EXPIRED"
    PERMIT_SCOPE_MISMATCH = "PERMIT_SCOPE_MISMATCH"
    PERMIT_SUBJECT_MISMATCH = "PERMIT_SUBJECT_MISMATCH"
    PERMIT_REVOKED = "PERMIT_REVOKED"
    UNKNOWN_ACTION_BLOCKED = "UNKNOWN_ACTION_BLOCKED"


@dataclass
class ActionPolicyDecision:
    """动作策略决策"""
    action: str
    allowed: bool
    category: ActionCategory
    permit_required: bool
    block_reason: ExecutionBlockReason | None = None
    permit_check_result: PermitCheckResult | None = None

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "allowed": self.allowed,
            "category": self.category.value,
            "permit_required": self.permit_required,
            "block_reason": self.block_reason.value if self.block_reason else None,
            "permit_check_result": self.permit_check_result.to_dict() if self.permit_check_result else None,
        }


class ExternalActionPolicy:
    """
    外部动作策略

    职责：
    1. 分类关键/非关键动作
    2. 检查 permit 要求
    3. 阻断不允许的动作
    4. 不负责 permit 生成
    5. 不负责 Evidence 生成
    6. 不负责外部动作真实执行

    安全约束：
    - 关键动作集合不可变（使用模块级 frozenset）
    - UNKNOWN 类别默认阻断（安全优先）
    """

    def __init__(self):
        """初始化策略"""
        # 不维护内部状态，使用模块级不可变常量

    def is_critical_action(self, action: str) -> bool:
        """
        判断是否为关键动作

        使用模块级不可变常量 CRITICAL_ACTIONS。

        Args:
            action: 动作名称

        Returns:
            True if critical, False otherwise
        """
        return action in CRITICAL_ACTIONS

    def requires_permit(self, action: str) -> bool:
        """
        检查动作是否需要 permit

        关键动作必须持 permit。

        Args:
            action: 动作名称

        Returns:
            True if permit required
        """
        return self.is_critical_action(action)

    def classify(self, action: str) -> ActionCategory:
        """
        分类动作

        Args:
            action: 动作名称

        Returns:
            动作类别
        """
        return classify_action(action)

    def evaluate_action(
        self,
        action: str,
        permit_token: str | dict | None = None,
        execution_context: dict | None = None,
    ) -> ActionPolicyDecision:
        """
        评估动作是否允许执行

        Args:
            action: 动作名称
            permit_token: permit token（可选）
            execution_context: 执行上下文（repo_url, commit_sha, run_id）

        Returns:
            策略决策
        """
        category = self.classify(action)
        permit_required = self.requires_permit(action)

        # UNKNOWN 类别：默认阻断（安全优先）
        if category == ActionCategory.UNKNOWN:
            return ActionPolicyDecision(
                action=action,
                allowed=False,
                category=category,
                permit_required=True,  # 未知动作视为需要 permit
                block_reason=ExecutionBlockReason.UNKNOWN_ACTION_BLOCKED,
            )

        # 非关键动作：允许
        if category == ActionCategory.NON_CRITICAL:
            return ActionPolicyDecision(
                action=action,
                allowed=True,
                category=category,
                permit_required=False,
            )

        # 关键动作：必须检查 permit
        if not permit_token:
            return ActionPolicyDecision(
                action=action,
                allowed=False,
                category=category,
                permit_required=True,
                block_reason=ExecutionBlockReason.PERMIT_REQUIRED,
            )

        # 检查 permit
        permit_check = check_permit_for_action(
            action=action,
            permit_token=permit_token,
            execution_context=execution_context or {},
        )

        if not permit_check.valid:
            # 映射错误码到阻断原因
            block_reason_map = {
                "E001": ExecutionBlockReason.PERMIT_REQUIRED,
                "E002": ExecutionBlockReason.PERMIT_INVALID,
                "E003": ExecutionBlockReason.PERMIT_INVALID,
                "E004": ExecutionBlockReason.PERMIT_EXPIRED,
                "E005": ExecutionBlockReason.PERMIT_SCOPE_MISMATCH,
                "E006": ExecutionBlockReason.PERMIT_SUBJECT_MISMATCH,
                "E007": ExecutionBlockReason.PERMIT_REVOKED,
            }
            block_reason = block_reason_map.get(
                permit_check.error_code or "E001",
                ExecutionBlockReason.PERMIT_REQUIRED
            )

            return ActionPolicyDecision(
                action=action,
                allowed=False,
                category=category,
                permit_required=True,
                block_reason=block_reason,
                permit_check_result=permit_check,
            )

        # Permit 有效，允许执行
        return ActionPolicyDecision(
            action=action,
            allowed=True,
            category=category,
            permit_required=True,
            permit_check_result=permit_check,
        )

    def get_critical_actions(self) -> frozenset[str]:
        """
        获取所有关键动作列表

        返回不可变集合，禁止运行时修改。
        """
        return CRITICAL_ACTIONS


# 全局策略实例
_policy: ExternalActionPolicy | None = None


def get_policy() -> ExternalActionPolicy:
    """获取全局策略实例"""
    global _policy
    if _policy is None:
        _policy = ExternalActionPolicy()
    return _policy


def evaluate_action(
    action: str,
    permit_token: str | dict | None = None,
    execution_context: dict | None = None,
) -> ActionPolicyDecision:
    """
    评估动作是否允许执行（便捷函数）

    Args:
        action: 动作名称
        permit_token: permit token（可选）
        execution_context: 执行上下文

    Returns:
        策略决策
    """
    policy = get_policy()
    return policy.evaluate_action(action, permit_token, execution_context)


def is_critical_action(action: str) -> bool:
    """
    判断是否为关键动作（便捷函数）

    Args:
        action: 动作名称

    Returns:
        True if critical
    """
    policy = get_policy()
    return policy.is_critical_action(action)


def requires_permit(action: str) -> bool:
    """
    检查动作是否需要 permit（便捷函数）

    Args:
        action: 动作名称

    Returns:
        True if permit required
    """
    policy = get_policy()
    return policy.requires_permit(action)


__all__ = [
    "CRITICAL_ACTIONS",
    "ExternalActionPolicy",
    "ActionPolicyDecision",
    "ExecutionBlockReason",
    "ActionCategory",
    "get_policy",
    "evaluate_action",
    "is_critical_action",
    "requires_permit",
]
