"""
Membership Policy Module

Provides membership tier enforcement for GM-SkillForge.

Core principle: Membership NEVER modifies GateDecision.
Only controls: access / quotas / rate limits / retention.
"""
from .membership_policy_enforcer import (
    MembershipPolicyEnforcer,
    MembershipPolicyError,
    QuotaExceededError,
    RateLimitedError,
    CapabilityDeniedError,
    RequiredCheckFailedError,
    MEMBERSHIP_ERROR_CODES,
    get_enforcer,
)
from .membership_middleware import (
    check_audit_enqueue,
    check_publish_listing,
    check_execute_via_n8n,
    MiddlewareResult,
)

__all__ = [
    # Enforcer
    "MembershipPolicyEnforcer",
    "MembershipPolicyError",
    "QuotaExceededError",
    "RateLimitedError",
    "CapabilityDeniedError",
    "RequiredCheckFailedError",
    "MEMBERSHIP_ERROR_CODES",
    "get_enforcer",
    # Middleware
    "check_audit_enqueue",
    "check_publish_listing",
    "check_execute_via_n8n",
    "MiddlewareResult",
]
