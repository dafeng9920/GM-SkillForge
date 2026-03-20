"""
Permit Check - Permit 校验

定义 permit 校验接口，委托给 gate_permit.py 实现。

Task ID: E4
Executor: Kior-B
Date: 2026-03-19
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PermitCheckResult:
    """Permit 校验结果"""
    valid: bool
    error_code: str | None = None
    error_message: str | None = None
    permit_id: str | None = None
    checked_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "permit_id": self.permit_id,
            "checked_at": self.checked_at,
        }


def check_permit_for_action(
    action: str,
    permit_token: str | dict | None,
    execution_context: dict[str, Any],
) -> PermitCheckResult:
    """
    检查动作的 permit 是否有效

    委托给 gate_permit.py 执行真实校验。

    Args:
        action: 动作名称
        permit_token: permit token（字符串或字典）
        execution_context: 执行上下文
            - repo_url: 仓库 URL
            - commit_sha: 提交 SHA
            - run_id: 运行 ID
            - current_time: 当前时间（可选）

    Returns:
        校验结果
    """
    import json
    import time
    from skillforge.src.skills.gates.gate_permit import validate_permit

    # 准备执行上下文
    repo_url = execution_context.get("repo_url", "")
    commit_sha = execution_context.get("commit_sha", "")
    run_id = execution_context.get("run_id", "")
    current_time = execution_context.get("current_time")

    # 调用 gate_permit 进行校验
    validation_result = validate_permit(
        permit_token=permit_token,
        repo_url=repo_url,
        commit_sha=commit_sha,
        run_id=run_id,
        requested_action=action,
        current_time=current_time,
    )

    # 提取结果
    return PermitCheckResult(
        valid=validation_result.get("release_allowed", False),
        error_code=validation_result.get("error_code"),
        error_message=validation_result.get("reason"),
        permit_id=validation_result.get("permit_id"),
        checked_at=validation_result.get("validation_timestamp") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


def check_permit_or_raise(
    action: str,
    permit_token: str | dict | None,
    execution_context: dict[str, Any],
) -> PermitCheckResult:
    """
    检查 permit，如果无效则抛出异常

    Args:
        action: 动作名称
        permit_token: permit token
        execution_context: 执行上下文

    Returns:
        校验结果

    Raises:
        PermitRequiredError: 如果 permit 缺失或无效
    """
    result = check_permit_for_action(action, permit_token, execution_context)

    if not result.valid:
        from skillforge.src.contracts.policy.permit_required import PermitRequiredError
        error_code = result.error_code or "E001"
        raise PermitRequiredError(
            action,
            message=result.error_message or f"Permit check failed for action '{action}'"
        )

    return result


__all__ = [
    "PermitCheckResult",
    "check_permit_for_action",
    "check_permit_or_raise",
]
