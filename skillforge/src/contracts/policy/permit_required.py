"""
Permit Required Policy Helper - 统一 permit_required(action) 规则

所有副作用动作统一走 permit_required(action) 检查。
确保 deny_without_permit_error_code 固定为 PERMIT_REQUIRED。
语义不得漂移 (E001 -> PERMIT_REQUIRED)。

Contract: docs/SEEDS_v0.md P0-3
Job ID: L45-D4-SEEDS-P0-20260220-004

Usage:
    from contracts.policy.permit_required import (
        permit_required,
        PermitRequiredError,
        is_action_requiring_permit,
    )

    # 检查动作是否需要 permit
    if permit_required("PUBLISH_LISTING"):
        if not has_valid_permit():
            raise PermitRequiredError("PUBLISH_LISTING")
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


# 固定的 deny 错误码 - 不得漂移
DENY_WITHOUT_PERMIT_ERROR_CODE = "PERMIT_REQUIRED"

# E001 错误码映射 - 语义基线来自 gate_permit.py
E001_ERROR_CODE = "E001"
E001_MAPPED_CODE = "PERMIT_REQUIRED"


@dataclass
class PermitPolicyConfig:
    """Permit policy configuration loaded from YAML."""
    version: int
    actions_requiring_permit: list[str]
    deny_without_permit_error_code: str

    @classmethod
    def from_dict(cls, data: dict) -> "PermitPolicyConfig":
        return cls(
            version=data.get("version", 1),
            actions_requiring_permit=data.get("actions_requiring_permit", []),
            deny_without_permit_error_code=data.get(
                "deny_without_permit_error_code", DENY_WITHOUT_PERMIT_ERROR_CODE
            ),
        )


class PermitRequiredError(Exception):
    """
    Raised when an action requires a permit but none is provided.

    Error code is ALWAYS "PERMIT_REQUIRED" (from E001 mapping).
    This ensures semantic consistency with gate_permit.py.
    """

    # 固定错误码 - 不得漂移
    code: str = DENY_WITHOUT_PERMIT_ERROR_CODE

    def __init__(self, action: str, message: Optional[str] = None):
        self.action = action
        self.message = message or f"Action '{action}' requires a valid permit. Error code: {self.code}"
        super().__init__(self.message)


def _load_policy_config() -> PermitPolicyConfig:
    """
    Load permit policy from YAML configuration file.

    Search order:
    1. SECURITY_PERMIT_POLICY_PATH environment variable
    2. security/permit_policy.yml (relative to project root)
    3. Default fallback config
    """
    # Try environment variable first
    env_path = os.environ.get("SECURITY_PERMIT_POLICY_PATH")
    if env_path:
        policy_path = Path(env_path)
        if policy_path.exists():
            return _load_yaml_config(policy_path)

    # Try default location (project root / security / permit_policy.yml)
    # Walk up from current file to find project root
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "security" / "permit_policy.yml"
        if candidate.exists():
            return _load_yaml_config(candidate)

    # Fallback to default config (matches SEEDS_v0.md template)
    return PermitPolicyConfig(
        version=1,
        actions_requiring_permit=[
            "PUBLISH_LISTING",
            "EXECUTE_VIA_N8N",
            "EXPORT_WHITELIST",
            "UPGRADE_REPLACE_ACTIVE",
        ],
        deny_without_permit_error_code=DENY_WITHOUT_PERMIT_ERROR_CODE,
    )


def _load_yaml_config(path: Path) -> PermitPolicyConfig:
    """Load configuration from YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return PermitPolicyConfig.from_dict(data)


# Global config instance (lazy loaded)
_config: Optional[PermitPolicyConfig] = None


def _get_config() -> PermitPolicyConfig:
    """Get or load the permit policy configuration."""
    global _config
    if _config is None:
        _config = _load_policy_config()
    return _config


def reload_config() -> None:
    """Force reload of configuration (useful for testing)."""
    global _config
    _config = None


def is_action_requiring_permit(action: str) -> bool:
    """
    Check if an action requires a permit.

    Args:
        action: The action name (e.g., "PUBLISH_LISTING", "EXECUTE_VIA_N8N")

    Returns:
        True if the action requires a permit, False otherwise.
    """
    config = _get_config()
    return action in config.actions_requiring_permit


def permit_required(action: str) -> bool:
    """
    Check if a permit is required for the given action.

    This is the main entry point for permit checks.
    All side-effect actions should call this function.

    Args:
        action: The action name (e.g., "PUBLISH_LISTING", "EXECUTE_VIA_N8N")

    Returns:
        True if permit is required for this action.

    Raises:
        PermitRequiredError: Never raised here, but consumers should raise it
                            when permit is required but not present.

    Example:
        if permit_required("PUBLISH_LISTING"):
            if not has_valid_permit():
                raise PermitRequiredError("PUBLISH_LISTING")
        # Proceed with action...
    """
    return is_action_requiring_permit(action)


def check_permit_or_raise(
    action: str,
    permit_valid: bool,
    permit_status: Optional[str] = None,
) -> None:
    """
    Check permit and raise PermitRequiredError if invalid.

    This is a convenience function that combines permit_required check
    with error raising.

    Args:
        action: The action to check
        permit_valid: Whether the permit is valid
        permit_status: Optional permit status for error message

    Raises:
        PermitRequiredError: If action requires permit and permit is invalid

    Example:
        check_permit_or_raise("PUBLISH_LISTING", permit_valid=True)
        # Proceed with publishing...
    """
    if permit_required(action):
        if not permit_valid:
            raise PermitRequiredError(
                action,
                message=(
                    f"Action '{action}' requires a valid permit. "
                    f"Status: {permit_status or 'MISSING'}. "
                    f"Error code: {DENY_WITHOUT_PERMIT_ERROR_CODE}"
                )
            )


def get_deny_error_code() -> str:
    """
    Get the fixed deny error code.

    This always returns "PERMIT_REQUIRED" to maintain semantic consistency
    with gate_permit.py E001 error code mapping.

    Returns:
        The fixed error code string "PERMIT_REQUIRED"
    """
    return DENY_WITHOUT_PERMIT_ERROR_CODE


def get_actions_requiring_permit() -> list[str]:
    """
    Get the list of actions that require a permit.

    Returns:
        List of action names requiring permit.
    """
    config = _get_config()
    return list(config.actions_requiring_permit)


# Export public API
__all__ = [
    "permit_required",
    "is_action_requiring_permit",
    "check_permit_or_raise",
    "PermitRequiredError",
    "get_deny_error_code",
    "get_actions_requiring_permit",
    "reload_config",
    "DENY_WITHOUT_PERMIT_ERROR_CODE",
]
