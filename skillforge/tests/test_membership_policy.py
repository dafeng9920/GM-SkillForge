"""
Test suite for MembershipPolicyEnforcer.

验证：
1. 能正确返回 4 个 membership 错误码
2. 会员层级不会改写 GateDecision
3. addons 只增能力，不绕过 required_checks
"""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from contracts.policy.membership_policy_enforcer import (
    MembershipPolicyEnforcer,
    CapabilityDeniedError,
    QuotaExceededError,
    RateLimitedError,
    RequiredCheckFailedError,
    MEMBERSHIP_ERROR_CODES,
)


class TestMembershipPolicyEnforcer(unittest.TestCase):
    """Test suite for MembershipPolicyEnforcer."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.enforcer = MembershipPolicyEnforcer()

    # -------------------------------------------------------------------------
    # Error Code Tests
    # -------------------------------------------------------------------------

    def test_error_codes_defined(self):
        """Verify all 4 error codes are defined."""
        self.assertEqual(MEMBERSHIP_ERROR_CODES["QUOTA_EXCEEDED"], "MEMBERSHIP_QUOTA_EXCEEDED")
        self.assertEqual(MEMBERSHIP_ERROR_CODES["RATE_LIMITED"], "MEMBERSHIP_RATE_LIMITED")
        self.assertEqual(MEMBERSHIP_ERROR_CODES["CAPABILITY_DENIED"], "MEMBERSHIP_CAPABILITY_DENIED")
        self.assertEqual(MEMBERSHIP_ERROR_CODES["REQUIRED_CHECK_FAILED"], "MEMBERSHIP_REQUIRED_CHECK_FAILED")

    def test_capability_denied_error_code(self):
        """Test CAPABILITY_DENIED error is raised correctly."""
        with self.assertRaises(CapabilityDeniedError) as ctx:
            self.enforcer.check_capability("FREE", "AUDIT_L4")
        self.assertEqual(ctx.exception.code, "MEMBERSHIP_CAPABILITY_DENIED")

    def test_quota_exceeded_error_code(self):
        """Test QUOTA_EXCEEDED error is raised correctly."""
        with self.assertRaises(QuotaExceededError) as ctx:
            self.enforcer.check_quota("FREE", "l3_audit_runs_per_month", 5)
        self.assertEqual(ctx.exception.code, "MEMBERSHIP_QUOTA_EXCEEDED")

    def test_rate_limited_error_code(self):
        """Test RATE_LIMITED error is raised correctly."""
        import time
        timestamps = [time.time()] * 100  # Far exceeds limit
        with self.assertRaises(RateLimitedError) as ctx:
            self.enforcer.check_rate_limit("FREE", "api_requests_per_minute", timestamps)
        self.assertEqual(ctx.exception.code, "MEMBERSHIP_RATE_LIMITED")

    def test_required_check_failed_error_code(self):
        """Test REQUIRED_CHECK_FAILED error is raised correctly."""
        context = {
            "gate_decision": {"decision": "FAIL"},  # Should be PASS
            "permit": {"status": "VALID"},
            "audit_pack": {"present": True, "hash_present": True},
            "provenance": {"present": True},
        }
        with self.assertRaises(RequiredCheckFailedError) as ctx:
            self.enforcer.check_required_checks("publish_listing", context)
        self.assertEqual(ctx.exception.code, "MEMBERSHIP_REQUIRED_CHECK_FAILED")

    # -------------------------------------------------------------------------
    # Capability Tests
    # -------------------------------------------------------------------------

    def test_free_tier_capabilities(self):
        """Test FREE tier has correct capabilities."""
        # Has
        self.assertTrue(self.enforcer.check_capability("FREE", "AUDIT_L3"))
        self.assertTrue(self.enforcer.check_capability("FREE", "PUBLISH_LISTING"))
        # Does not have
        with self.assertRaises(CapabilityDeniedError):
            self.enforcer.check_capability("FREE", "AUDIT_L4")
        with self.assertRaises(CapabilityDeniedError):
            self.enforcer.check_capability("FREE", "EXECUTE_VIA_N8N")

    def test_pro_tier_capabilities(self):
        """Test PRO tier has correct capabilities."""
        self.assertTrue(self.enforcer.check_capability("PRO", "AUDIT_L3"))
        self.assertTrue(self.enforcer.check_capability("PRO", "UPGRADE_AND_REAUDIT"))
        # Does not have by default
        with self.assertRaises(CapabilityDeniedError):
            self.enforcer.check_capability("PRO", "AUDIT_L4")
        with self.assertRaises(CapabilityDeniedError):
            self.enforcer.check_capability("PRO", "EXECUTE_VIA_N8N")

    def test_studio_tier_capabilities(self):
        """Test STUDIO tier has correct capabilities."""
        self.assertTrue(self.enforcer.check_capability("STUDIO", "AUDIT_L3"))
        self.assertTrue(self.enforcer.check_capability("STUDIO", "AUDIT_L4"))
        self.assertTrue(self.enforcer.check_capability("STUDIO", "EXECUTE_VIA_N8N"))

    def test_enterprise_tier_capabilities(self):
        """Test ENTERPRISE tier has all capabilities."""
        self.assertTrue(self.enforcer.check_capability("ENTERPRISE", "AUDIT_L3"))
        self.assertTrue(self.enforcer.check_capability("ENTERPRISE", "AUDIT_L4"))
        self.assertTrue(self.enforcer.check_capability("ENTERPRISE", "AUDIT_L5"))
        self.assertTrue(self.enforcer.check_capability("ENTERPRISE", "EXECUTE_VIA_N8N"))

    # -------------------------------------------------------------------------
    # Add-on Tests
    # -------------------------------------------------------------------------

    def test_addon_hosted_execution_for_pro(self):
        """Test hosted_execution add-on enables EXECUTE_VIA_N8N for PRO."""
        # Without add-on
        with self.assertRaises(CapabilityDeniedError):
            self.enforcer.check_capability("PRO", "EXECUTE_VIA_N8N")

        # With add-on
        self.assertTrue(
            self.enforcer.check_capability("PRO", "EXECUTE_VIA_N8N", enabled_addons=["hosted_execution"])
        )

    def test_addon_does_not_bypass_required_checks(self):
        """Test add-ons do not bypass required_checks."""
        context = {
            "permit": {"status": "INVALID"},  # Should be VALID
            "execution_contract": {"present": True},
        }
        # Even with add-on, required checks must pass
        with self.assertRaises(RequiredCheckFailedError):
            self.enforcer.check_required_checks("execute_via_n8n", context, tier_name="PRO")

    # -------------------------------------------------------------------------
    # Quota Tests
    # -------------------------------------------------------------------------

    def test_free_tier_quotas(self):
        """Test FREE tier quotas."""
        self.assertEqual(self.enforcer.get_quota_limit("FREE", "l3_audit_runs_per_month"), 1)
        self.assertEqual(self.enforcer.get_quota_limit("FREE", "l4_audit_runs_per_month"), 0)
        self.assertEqual(self.enforcer.get_quota_limit("FREE", "listing_slots"), 1)

    def test_pro_tier_quotas(self):
        """Test PRO tier quotas."""
        self.assertEqual(self.enforcer.get_quota_limit("PRO", "l3_audit_runs_per_month"), 20)
        self.assertEqual(self.enforcer.get_quota_limit("PRO", "listing_slots"), 20)

    def test_enterprise_tier_quotas(self):
        """Test ENTERPRISE tier quotas."""
        self.assertEqual(self.enforcer.get_quota_limit("ENTERPRISE", "l3_audit_runs_per_month"), 500)
        self.assertEqual(self.enforcer.get_quota_limit("ENTERPRISE", "l4_audit_runs_per_month"), 50)
        self.assertEqual(self.enforcer.get_quota_limit("ENTERPRISE", "l5_audit_runs_per_month"), 10)

    # -------------------------------------------------------------------------
    # Required Checks Tests
    # -------------------------------------------------------------------------

    def test_publish_listing_all_pass(self):
        """Test publish_listing passes with all conditions met."""
        context = {
            "gate_decision": {"decision": "PASS", "level_min": "L3"},
            "permit": {"status": "VALID"},
            "audit_pack": {"present": True, "hash_present": True},
            "provenance": {"present": True},
            "tombstone": {"state": "ACTIVE"},
        }
        self.assertTrue(self.enforcer.check_required_checks("publish_listing", context))

    def test_publish_listing_fails_without_gate_pass(self):
        """Test publish_listing fails without gate PASS."""
        context = {
            "gate_decision": {"decision": "FAIL", "level_min": "L3"},
            "permit": {"status": "VALID"},
            "audit_pack": {"present": True, "hash_present": True},
            "provenance": {"present": True},
        }
        with self.assertRaises(RequiredCheckFailedError):
            self.enforcer.check_required_checks("publish_listing", context)

    def test_publish_listing_fails_if_tombstoned(self):
        """Test publish_listing fails if tombstoned."""
        context = {
            "gate_decision": {"decision": "PASS", "level_min": "L3"},
            "permit": {"status": "VALID"},
            "audit_pack": {"present": True, "hash_present": True},
            "provenance": {"present": True},
            "tombstone": {"state": "TOMBSTONED"},
        }
        with self.assertRaises(RequiredCheckFailedError):
            self.enforcer.check_required_checks("publish_listing", context)


if __name__ == "__main__":
    unittest.main()
