"""
Membership Policy Middleware - 会员策略中间件

提供三个关键挂点：
- 审计入队前：check_audit_enqueue
- 发布前：check_publish_listing
- n8n 执行前：check_execute_via_n8n

Usage:
    from contracts.policy.membership_middleware import (
        check_audit_enqueue,
        check_publish_listing,
        check_execute_via_n8n,
    )
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .membership_policy_enforcer import (
    MembershipPolicyEnforcer,
    MembershipPolicyError,
    QuotaExceededError,
    RateLimitedError,
    CapabilityDeniedError,
    RequiredCheckFailedError,
    get_enforcer,
)


@dataclass
class MiddlewareResult:
    """Result of a middleware check."""
    allowed: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    tier: Optional[str] = None
    action: Optional[str] = None


def check_audit_enqueue(
    tier: str,
    audit_level: str,
    current_usage: dict[str, int],
    recent_request_timestamps: Optional[list[float]] = None,
    enabled_addons: Optional[list[str]] = None,
) -> MiddlewareResult:
    """
    审计入队前检查。

    检查项：
    1. capability: AUDIT_L3 / AUDIT_L4 / AUDIT_L5
    2. quota: l*_audit_runs_per_month
    3. rate_limit: audit_jobs_per_hour

    Args:
        tier: 会员层级 (FREE, PRO, STUDIO, ENTERPRISE)
        audit_level: 审计级别 (L3, L4, L5)
        current_usage: 当前用量 {"l3_audit_runs_per_month": 5, ...}
        recent_request_timestamps: 最近请求时间戳列表
        enabled_addons: 已启用的插件

    Returns:
        MiddlewareResult with allowed=True or error details
    """
    enforcer = get_enforcer()
    action = f"AUDIT_{audit_level}"
    quota_key = f"{audit_level.lower()}_audit_runs_per_month"

    try:
        # 1. Check capability
        enforcer.check_capability(tier, action, enabled_addons)

        # 2. Check quota
        usage = current_usage.get(quota_key, 0)
        enforcer.check_quota(tier, quota_key, usage)

        # 3. Check rate limit
        if recent_request_timestamps:
            enforcer.check_rate_limit(
                tier, "audit_jobs_per_hour", recent_request_timestamps, window_seconds=3600
            )

        return MiddlewareResult(allowed=True, tier=tier, action=action)

    except CapabilityDeniedError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action=action,
        )
    except QuotaExceededError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action=action,
        )
    except RateLimitedError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action=action,
        )


def check_publish_listing(
    tier: str,
    gate_decision: dict[str, Any],
    permit_status: str,
    audit_pack: dict[str, Any],
    provenance: dict[str, Any],
    tombstone_state: Optional[str] = None,
    current_listing_count: int = 0,
) -> MiddlewareResult:
    """
    发布前检查。

    检查项：
    1. required_checks: publish_listing
    2. quota: listing_slots

    注意：此检查不会改写 GateDecision，仅做访问控制。

    Args:
        tier: 会员层级
        gate_decision: Gate 决策 {"decision": "PASS", "level_min": "L3"}
        permit_status: Permit 状态 ("VALID", "INVALID", etc.)
        audit_pack: AuditPack 信息 {"present": True, "hash_present": True}
        provenance: 来源信息 {"present": True}
        tombstone_state: Tombstone 状态 (None or "TOMBSTONED")
        current_listing_count: 当前已发布的 listing 数量

    Returns:
        MiddlewareResult with allowed=True or error details
    """
    enforcer = get_enforcer()

    try:
        # 1. Check required checks (does NOT modify gate_decision)
        context = {
            "gate_decision": gate_decision,
            "permit": {"status": permit_status},
            "audit_pack": audit_pack,
            "provenance": provenance,
            "tombstone": {"state": tombstone_state or "ACTIVE"},
        }
        enforcer.check_required_checks("publish_listing", context, tier_name=tier)

        # 2. Check listing quota
        enforcer.check_quota(tier, "listing_slots", current_listing_count)

        return MiddlewareResult(allowed=True, tier=tier, action="PUBLISH_LISTING")

    except RequiredCheckFailedError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action="PUBLISH_LISTING",
        )
    except QuotaExceededError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action="PUBLISH_LISTING",
        )


def check_execute_via_n8n(
    tier: str,
    permit_status: str,
    execution_contract_present: bool,
    tombstone_state: Optional[str] = None,
    enabled_addons: Optional[list[str]] = None,
    current_concurrent_jobs: int = 0,
) -> MiddlewareResult:
    """
    n8n 执行前检查。

    检查项：
    1. capability: EXECUTE_VIA_N8N
    2. required_checks: execute_via_n8n
    3. quota: max_concurrent_exec_jobs

    Args:
        tier: 会员层级
        permit_status: Permit 状态
        execution_contract_present: 是否有执行合同
        tombstone_state: Tombstone 状态
        enabled_addons: 已启用的插件
        current_concurrent_jobs: 当前并发执行数

    Returns:
        MiddlewareResult with allowed=True or error details
    """
    enforcer = get_enforcer()
    enabled_addons = enabled_addons or []

    try:
        # 1. Check capability (with add-ons)
        enforcer.check_capability(tier, "EXECUTE_VIA_N8N", enabled_addons)

        # 2. Check required checks
        context = {
            "permit": {"status": permit_status},
            "execution_contract": {"present": execution_contract_present},
            "tombstone": {"state": tombstone_state or "ACTIVE"},
        }
        enforcer.check_required_checks("execute_via_n8n", context, tier_name=tier)

        # 3. Check concurrent job quota (with add-ons applied)
        # Get merged quota if addon is enabled
        quota_limit = enforcer.get_quota_limit(tier, "max_concurrent_exec_jobs")
        for addon_name in enabled_addons:
            merged = enforcer.apply_addon(tier, addon_name)
            if merged.get("quotas", {}).get("max_concurrent_exec_jobs", 0) > quota_limit:
                quota_limit = merged["quotas"]["max_concurrent_exec_jobs"]

        if current_concurrent_jobs >= quota_limit:
            raise QuotaExceededError(
                code="MEMBERSHIP_QUOTA_EXCEEDED",
                message=f"Quota exceeded: max_concurrent_exec_jobs (limit={quota_limit}, usage={current_concurrent_jobs})",
                tier=tier,
                action="max_concurrent_exec_jobs",
            )

        return MiddlewareResult(allowed=True, tier=tier, action="EXECUTE_VIA_N8N")

    except CapabilityDeniedError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action="EXECUTE_VIA_N8N",
        )
    except RequiredCheckFailedError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action="EXECUTE_VIA_N8N",
        )
    except QuotaExceededError as e:
        return MiddlewareResult(
            allowed=False,
            error_code=e.code,
            error_message=e.message,
            tier=tier,
            action="EXECUTE_VIA_N8N",
        )
