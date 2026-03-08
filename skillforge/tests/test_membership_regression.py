"""
Membership Policy 回归测试

核心验证：
1. 会员层级 NEVER 改写 GateDecision
2. tier=FREE + gate_decision=PASS@L3 + permit=VALID 可发布
3. 发布受 listing_slots 限制

这是"生产可接入"的关键回归测试。
"""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from contracts.policy.membership_middleware import (
    check_audit_enqueue,
    check_publish_listing,
    check_execute_via_n8n,
    MiddlewareResult,
)
from contracts.policy.membership_policy_enforcer import (
    get_enforcer,
)


class TestMembershipPolicyRegression(unittest.TestCase):
    """
    回归测试：验证会员策略核心行为不变。

    关键不变量：
    - 会员层级 NEVER 改写 GateDecision
    - 仅控制访问/配额/速率/保留
    """

    def test_free_tier_can_publish_with_valid_gate_decision(self):
        """
        REG-001: FREE 层级 + gate_decision=PASS@L3 + permit=VALID 可以发布

        验证：会员策略不阻断合规发布。
        """
        result = check_publish_listing(
            tier="FREE",
            gate_decision={"decision": "PASS", "level_min": "L3"},
            permit_status="VALID",
            audit_pack={"present": True, "hash_present": True},
            provenance={"present": True},
            tombstone_state=None,
            current_listing_count=0,
        )

        self.assertTrue(result.allowed)
        self.assertIsNone(result.error_code)

    def test_free_tier_publish_blocked_by_listing_slots(self):
        """
        REG-002: FREE 层级发布受 listing_slots 限制

        验证：listing_slots=1，第二次发布应被阻断。
        """
        # 第一次发布成功
        result_1 = check_publish_listing(
            tier="FREE",
            gate_decision={"decision": "PASS", "level_min": "L3"},
            permit_status="VALID",
            audit_pack={"present": True, "hash_present": True},
            provenance={"present": True},
            current_listing_count=0,
        )
        self.assertTrue(result_1.allowed)

        # 第二次发布失败（配额用尽）
        result_2 = check_publish_listing(
            tier="FREE",
            gate_decision={"decision": "PASS", "level_min": "L3"},
            permit_status="VALID",
            audit_pack={"present": True, "hash_present": True},
            provenance={"present": True},
            current_listing_count=1,  # 已用完 1 个 slot
        )
        self.assertFalse(result_2.allowed)
        self.assertEqual(result_2.error_code, "MEMBERSHIP_QUOTA_EXCEEDED")

    def test_membership_never_modifies_gate_decision(self):
        """
        REG-003: 会员策略检查不改变 GateDecision

        这是核心不变量：会员策略只做访问控制，不改写任何业务决策。
        """
        original_gate_decision = {"decision": "PASS", "level_min": "L3"}

        # 执行检查
        result = check_publish_listing(
            tier="FREE",
            gate_decision=original_gate_decision,
            permit_status="VALID",
            audit_pack={"present": True, "hash_present": True},
            provenance={"present": True},
        )

        # GateDecision 未被修改
        self.assertEqual(original_gate_decision, {"decision": "PASS", "level_min": "L3"})

        # 检查结果也不包含修改后的 GateDecision
        self.assertNotIn("gate_decision", result.__dict__)

    def test_gate_decision_fail_still_blocked_regardless_of_tier(self):
        """
        REG-004: Gate 决策为 FAIL 时，任何层级都不能发布

        验证：ENTERPRISE 层级也不能绕过 Gate 失败。
        """
        result = check_publish_listing(
            tier="ENTERPRISE",
            gate_decision={"decision": "FAIL", "level_min": "L3"},
            permit_status="VALID",
            audit_pack={"present": True, "hash_present": True},
            provenance={"present": True},
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.error_code, "MEMBERSHIP_REQUIRED_CHECK_FAILED")

    def test_free_tier_cannot_execute_via_n8n(self):
        """
        REG-005: FREE 层级不能使用 n8n 执行
        """
        result = check_execute_via_n8n(
            tier="FREE",
            permit_status="VALID",
            execution_contract_present=True,
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.error_code, "MEMBERSHIP_CAPABILITY_DENIED")

    def test_pro_tier_can_execute_via_n8n_with_addon(self):
        """
        REG-006: PRO 层级启用 hosted_execution 插件后可以执行 n8n
        """
        result = check_execute_via_n8n(
            tier="PRO",
            permit_status="VALID",
            execution_contract_present=True,
            enabled_addons=["hosted_execution"],
            current_concurrent_jobs=0,
        )

        self.assertTrue(result.allowed)

    def test_audit_L4_blocked_for_free_tier(self):
        """
        REG-007: FREE 层级不能执行 L4 审计
        """
        result = check_audit_enqueue(
            tier="FREE",
            audit_level="L4",
            current_usage={"l4_audit_runs_per_month": 0},
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.error_code, "MEMBERSHIP_CAPABILITY_DENIED")

    def test_audit_L3_blocked_after_quota_exhausted(self):
        """
        REG-008: FREE 层级 L3 审计配额用尽后被阻断

        FREE 层级 l3_audit_runs_per_month=1
        """
        # 配额未用尽时通过
        result_1 = check_audit_enqueue(
            tier="FREE",
            audit_level="L3",
            current_usage={"l3_audit_runs_per_month": 0},
        )
        self.assertTrue(result_1.allowed)

        # 配额用尽后阻断
        result_2 = check_audit_enqueue(
            tier="FREE",
            audit_level="L3",
            current_usage={"l3_audit_runs_per_month": 1},
        )
        self.assertFalse(result_2.allowed)
        self.assertEqual(result_2.error_code, "MEMBERSHIP_QUOTA_EXCEEDED")


class TestMembershipTierQuotas(unittest.TestCase):
    """验证各层级配额正确。"""

    def test_free_tier_quotas(self):
        """FREE: l3=1, l4=0, l5=0"""
        enforcer = get_enforcer()
        self.assertEqual(enforcer.get_quota_limit("FREE", "l3_audit_runs_per_month"), 1)
        self.assertEqual(enforcer.get_quota_limit("FREE", "l4_audit_runs_per_month"), 0)
        self.assertEqual(enforcer.get_quota_limit("FREE", "l5_audit_runs_per_month"), 0)
        self.assertEqual(enforcer.get_quota_limit("FREE", "listing_slots"), 1)

    def test_pro_tier_quotas(self):
        """PRO: l3=20, l4=0, l5=0"""
        enforcer = get_enforcer()
        self.assertEqual(enforcer.get_quota_limit("PRO", "l3_audit_runs_per_month"), 20)
        self.assertEqual(enforcer.get_quota_limit("PRO", "l4_audit_runs_per_month"), 0)
        self.assertEqual(enforcer.get_quota_limit("PRO", "listing_slots"), 20)

    def test_studio_tier_quotas(self):
        """STUDIO: l3=100, l4=10, l5=0"""
        enforcer = get_enforcer()
        self.assertEqual(enforcer.get_quota_limit("STUDIO", "l3_audit_runs_per_month"), 100)
        self.assertEqual(enforcer.get_quota_limit("STUDIO", "l4_audit_runs_per_month"), 10)
        self.assertEqual(enforcer.get_quota_limit("STUDIO", "l5_audit_runs_per_month"), 0)

    def test_enterprise_tier_quotas(self):
        """ENTERPRISE: l3=500, l4=50, l5=10"""
        enforcer = get_enforcer()
        self.assertEqual(enforcer.get_quota_limit("ENTERPRISE", "l3_audit_runs_per_month"), 500)
        self.assertEqual(enforcer.get_quota_limit("ENTERPRISE", "l4_audit_runs_per_month"), 50)
        self.assertEqual(enforcer.get_quota_limit("ENTERPRISE", "l5_audit_runs_per_month"), 10)


if __name__ == "__main__":
    unittest.main()
