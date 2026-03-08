"""
Membership Policy Enforcer - 会员策略执行器

从 membership_tiers.yml 加载策略并在运行时执行检查。

核心原则：
- 会员层级 NEVER 改变 GateDecision
- 仅控制访问/配额/速率/保留

错误码：
- MEMBERSHIP_QUOTA_EXCEEDED: 配额超限
- MEMBERSHIP_RATE_LIMITED: 速率限制
- MEMBERSHIP_CAPABILITY_DENIED: 能力缺失
- MEMBERSHIP_REQUIRED_CHECK_FAILED: 检查失败

Usage:
    enforcer = MembershipPolicyEnforcer()
    enforcer.check_capability("PRO", "AUDIT_L3")  # True or raise
    enforcer.check_quota("PRO", "l3_audit_runs_per_month", 15)  # True or raise
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


# Error codes (aligned with membership_tiers.yml)
MEMBERSHIP_ERROR_CODES = {
    "QUOTA_EXCEEDED": "MEMBERSHIP_QUOTA_EXCEEDED",
    "RATE_LIMITED": "MEMBERSHIP_RATE_LIMITED",
    "CAPABILITY_DENIED": "MEMBERSHIP_CAPABILITY_DENIED",
    "REQUIRED_CHECK_FAILED": "MEMBERSHIP_REQUIRED_CHECK_FAILED",
}


class MembershipPolicyError(Exception):
    """Base exception for membership policy violations."""

    def __init__(self, code: str, message: str, tier: str, action: str):
        self.code = code
        self.message = message
        self.tier = tier
        self.action = action
        super().__init__(f"[{code}] {message} (tier={tier}, action={action})")


class QuotaExceededError(MembershipPolicyError):
    """Quota exceeded error."""
    pass


class RateLimitedError(MembershipPolicyError):
    """Rate limited error."""
    pass


class CapabilityDeniedError(MembershipPolicyError):
    """Capability denied error."""
    pass


class RequiredCheckFailedError(MembershipPolicyError):
    """Required check failed error."""
    pass


@dataclass
class TierConfig:
    """Configuration for a single tier."""
    name: str
    description: str
    quotas: dict[str, int]
    capabilities: dict[str, bool]
    retention: dict[str, int]
    rate_limit: dict[str, int]
    required_checks_overrides: dict[str, Any] = field(default_factory=dict)


@dataclass
class AddonConfig:
    """Configuration for an add-on."""
    name: str
    description: str
    applies_to_tiers: list[str]
    toggles: dict[str, Any]
    required_checks: dict[str, Any] = field(default_factory=dict)


class MembershipPolicyEnforcer:
    """
    会员策略执行器。

    从 YAML 配置加载策略，提供配额/能力/速率限制检查。
    """

    DEFAULT_CONFIG_PATH = Path(__file__).parent / "membership_tiers.yml"

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the enforcer.

        Args:
            config_path: Path to membership_tiers.yml. Defaults to bundled config.
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: dict[str, Any] = {}
        self._tiers: dict[str, TierConfig] = {}
        self._addons: dict[str, AddonConfig] = {}
        self._required_checks: dict[str, Any] = {}
        self._rate_limit_defaults: dict[str, int] = {}
        self._deny_error_codes: dict[str, str] = {}
        self._accounting: dict[str, Any] = {}

        self._load_config()

    def _load_config(self) -> None:
        """Load and validate configuration from YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Membership config not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

        self._validate_schema()
        self._parse_tiers()
        self._parse_addons()
        self._parse_required_checks()
        self._parse_enforcement()

    def _validate_schema(self) -> None:
        """Validate required top-level keys exist."""
        required_keys = ["version", "tiers", "required_checks", "enforcement"]
        for key in required_keys:
            if key not in self._config:
                raise ValueError(f"Missing required key in membership config: {key}")

    def _parse_tiers(self) -> None:
        """Parse tier configurations."""
        tiers_data = self._config.get("tiers", {})
        for tier_name, tier_data in tiers_data.items():
            self._tiers[tier_name] = TierConfig(
                name=tier_name,
                description=tier_data.get("description", ""),
                quotas=tier_data.get("quotas", {}),
                capabilities=tier_data.get("capabilities", {}),
                retention=tier_data.get("retention", {}),
                rate_limit=tier_data.get("rate_limit", {}),
                required_checks_overrides=tier_data.get("required_checks_overrides", {}),
            )

    def _parse_addons(self) -> None:
        """Parse add-on configurations."""
        addons_data = self._config.get("addons", {})
        for addon_name, addon_data in addons_data.items():
            self._addons[addon_name] = AddonConfig(
                name=addon_name,
                description=addon_data.get("description", ""),
                applies_to_tiers=addon_data.get("applies_to_tiers", []),
                toggles=addon_data.get("toggles", {}),
                required_checks=addon_data.get("required_checks", {}),
            )

    def _parse_required_checks(self) -> None:
        """Parse required checks."""
        self._required_checks = self._config.get("required_checks", {})
        self._rate_limit_defaults = self._config.get("rate_limit_defaults", {})

    def _parse_enforcement(self) -> None:
        """Parse enforcement configuration."""
        enforcement = self._config.get("enforcement", {})
        self._deny_error_codes = enforcement.get("deny_error_codes", {})
        self._accounting = enforcement.get("accounting", {})

    # =========================================================================
    # Public API
    # =========================================================================

    def get_tier(self, tier_name: str) -> Optional[TierConfig]:
        """Get tier configuration by name."""
        return self._tiers.get(tier_name)

    def get_tier_names(self) -> list[str]:
        """Get list of valid tier names."""
        return list(self._tiers.keys())

    def check_capability(
        self,
        tier_name: str,
        action: str,
        enabled_addons: Optional[list[str]] = None,
    ) -> bool:
        """
        Check if tier has the specified capability.

        Args:
            tier_name: Tier name (FREE, PRO, STUDIO, ENTERPRISE)
            action: Action to check (e.g., AUDIT_L3, EXECUTE_VIA_N8N)
            enabled_addons: List of enabled add-ons for this account

        Returns:
            True if capability is allowed

        Raises:
            CapabilityDeniedError: If capability is not available
        """
        tier = self._tiers.get(tier_name)
        if not tier:
            raise CapabilityDeniedError(
                code=MEMBERSHIP_ERROR_CODES["CAPABILITY_DENIED"],
                message=f"Unknown tier: {tier_name}",
                tier=tier_name,
                action=action,
            )

        # Check base capability
        if tier.capabilities.get(action, False):
            return True

        # Check add-ons
        enabled_addons = enabled_addons or []
        for addon_name in enabled_addons:
            addon = self._addons.get(addon_name)
            if addon and tier_name in addon.applies_to_tiers:
                addon_capabilities = addon.toggles.get("capabilities", {})
                if addon_capabilities.get(action, False):
                    return True

        raise CapabilityDeniedError(
            code=MEMBERSHIP_ERROR_CODES["CAPABILITY_DENIED"],
            message=f"Tier {tier_name} does not have capability: {action}",
            tier=tier_name,
            action=action,
        )

    def check_quota(
        self,
        tier_name: str,
        quota_key: str,
        current_usage: int,
    ) -> bool:
        """
        Check if quota is available.

        Args:
            tier_name: Tier name
            quota_key: Quota key (e.g., l3_audit_runs_per_month)
            current_usage: Current usage count

        Returns:
            True if quota is available

        Raises:
            QuotaExceededError: If quota is exceeded
        """
        tier = self._tiers.get(tier_name)
        if not tier:
            raise QuotaExceededError(
                code=MEMBERSHIP_ERROR_CODES["QUOTA_EXCEEDED"],
                message=f"Unknown tier: {tier_name}",
                tier=tier_name,
                action=quota_key,
            )

        limit = tier.quotas.get(quota_key, 0)
        if current_usage < limit:
            return True

        raise QuotaExceededError(
            code=MEMBERSHIP_ERROR_CODES["QUOTA_EXCEEDED"],
            message=f"Quota exceeded: {quota_key} (limit={limit}, usage={current_usage})",
            tier=tier_name,
            action=quota_key,
        )

    def check_rate_limit(
        self,
        tier_name: str,
        rate_key: str,
        timestamps: list[float],
        window_seconds: int = 60,
    ) -> bool:
        """
        Check rate limit.

        Args:
            tier_name: Tier name
            rate_key: Rate limit key (e.g., api_requests_per_minute)
            timestamps: List of request timestamps
            window_seconds: Time window in seconds

        Returns:
            True if within rate limit

        Raises:
            RateLimitedError: If rate limit exceeded
        """
        tier = self._tiers.get(tier_name)
        if not tier:
            raise RateLimitedError(
                code=MEMBERSHIP_ERROR_CODES["RATE_LIMITED"],
                message=f"Unknown tier: {tier_name}",
                tier=tier_name,
                action=rate_key,
            )

        limit = tier.rate_limit.get(rate_key, self._rate_limit_defaults.get(rate_key, 30))
        now = time.time()
        window_start = now - window_seconds
        recent_count = sum(1 for ts in timestamps if ts >= window_start)

        if recent_count < limit:
            return True

        raise RateLimitedError(
            code=MEMBERSHIP_ERROR_CODES["RATE_LIMITED"],
            message=f"Rate limit exceeded: {rate_key} (limit={limit}/{window_seconds}s)",
            tier=tier_name,
            action=rate_key,
        )

    def check_required_checks(
        self,
        check_name: str,
        context: dict[str, Any],
        tier_name: Optional[str] = None,
    ) -> bool:
        """
        Check required conditions for an action.

        Args:
            check_name: Check name (e.g., publish_listing, execute_via_n8n)
            context: Context dict with values to check
            tier_name: Optional tier for tier-specific overrides

        Returns:
            True if all checks pass

        Raises:
            RequiredCheckFailedError: If any required check fails
        """
        checks = self._required_checks.get(check_name, {})

        # Apply tier-specific overrides
        if tier_name:
            tier = self._tiers.get(tier_name)
            if tier and tier.required_checks_overrides:
                checks = {**checks, **tier.required_checks_overrides.get(check_name, {})}

        # Check must_have conditions
        must_have = checks.get("must_have", [])
        for condition in must_have:
            if not self._evaluate_condition(condition, context):
                raise RequiredCheckFailedError(
                    code=MEMBERSHIP_ERROR_CODES["REQUIRED_CHECK_FAILED"],
                    message=f"Required condition not met: {condition}",
                    tier=tier_name or "unknown",
                    action=check_name,
                )

        # Check must_not_have conditions
        must_not_have = checks.get("must_not_have", [])
        for condition in must_not_have:
            if self._evaluate_condition(condition, context):
                raise RequiredCheckFailedError(
                    code=MEMBERSHIP_ERROR_CODES["REQUIRED_CHECK_FAILED"],
                    message=f"Prohibited condition present: {condition}",
                    tier=tier_name or "unknown",
                    action=check_name,
                )

        return True

    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """
        Evaluate a dot-notation condition against context.

        Args:
            condition: Condition like "gate_decision.decision: PASS"
            context: Context dict

        Returns:
            True if condition matches
        """
        if ":" not in condition:
            return False

        path, expected = condition.split(":", 1)
        path = path.strip()
        expected = expected.strip()

        # Navigate nested path
        parts = path.split(".")
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return False

        # Compare
        if isinstance(value, bool):
            return str(value).lower() == expected.lower()
        if isinstance(value, (int, float)):
            return str(value) == expected
        return str(value) == expected

    def get_quota_limit(self, tier_name: str, quota_key: str) -> int:
        """Get quota limit for a tier and key."""
        tier = self._tiers.get(tier_name)
        if not tier:
            return 0
        return tier.quotas.get(quota_key, 0)

    def get_rate_limit(self, tier_name: str, rate_key: str) -> int:
        """Get rate limit for a tier and key."""
        tier = self._tiers.get(tier_name)
        if not tier:
            return self._rate_limit_defaults.get(rate_key, 30)
        return tier.rate_limit.get(rate_key, self._rate_limit_defaults.get(rate_key, 30))

    def apply_addon(
        self,
        tier_name: str,
        addon_name: str,
    ) -> dict[str, Any]:
        """
        Apply add-on toggles to tier configuration.

        Returns merged capabilities and quotas with add-on applied.
        """
        tier = self._tiers.get(tier_name)
        addon = self._addons.get(addon_name)

        if not tier or not addon:
            return {"capabilities": {}, "quotas": {}}

        if tier_name not in addon.applies_to_tiers:
            return {"capabilities": {}, "quotas": {}}

        merged = {
            "capabilities": dict(tier.capabilities),
            "quotas": dict(tier.quotas),
        }

        merged["capabilities"].update(addon.toggles.get("capabilities", {}))
        merged["quotas"].update(addon.toggles.get("quotas", {}))

        return merged


# Convenience function
def get_enforcer(config_path: Optional[Path] = None) -> MembershipPolicyEnforcer:
    """Get or create a singleton enforcer instance."""
    global _enforcer_instance
    if "_enforcer_instance" not in globals():
        _enforcer_instance = MembershipPolicyEnforcer(config_path)
    return _enforcer_instance


# CLI entry point
def main():
    """CLI entry point for membership policy enforcer."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Membership Policy Enforcer")
    parser.add_argument("--config", help="Path to membership_tiers.yml")
    parser.add_argument("--check-capability", nargs=2, metavar=("TIER", "ACTION"),
                        help="Check capability for tier")
    parser.add_argument("--check-quota", nargs=3, metavar=("TIER", "KEY", "USAGE"),
                        help="Check quota for tier")
    parser.add_argument("--list-tiers", action="store_true", help="List all tiers")
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    enforcer = MembershipPolicyEnforcer(config_path)

    if args.list_tiers:
        print(json.dumps(enforcer.get_tier_names(), indent=2))
        return

    if args.check_capability:
        tier, action = args.check_capability
        try:
            enforcer.check_capability(tier, action)
            print(json.dumps({"allowed": True, "tier": tier, "action": action}))
        except CapabilityDeniedError as e:
            print(json.dumps({"allowed": False, "error": e.code, "message": e.message}))
        return

    if args.check_quota:
        tier, key, usage = args.check_quota
        try:
            enforcer.check_quota(tier, key, int(usage))
            print(json.dumps({"allowed": True, "tier": tier, "key": key}))
        except QuotaExceededError as e:
            print(json.dumps({"allowed": False, "error": e.code, "message": e.message}))
        return


if __name__ == "__main__":
    main()
