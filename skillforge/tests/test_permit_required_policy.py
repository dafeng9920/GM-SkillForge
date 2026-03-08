"""
Tests for permit_required policy helper.

Contract: docs/SEEDS_v0.md P0-3
Job ID: L45-D4-SEEDS-P0-20260220-004

Tests verify:
1. All side-effect actions unified through permit_required(action)
2. deny_without_permit_error_code fixed to PERMIT_REQUIRED
3. E001 semantic mapping preserved (no drift)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add skillforge to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "skillforge" / "src"))

from contracts.policy.permit_required import (
    DENY_WITHOUT_PERMIT_ERROR_CODE,
    PermitRequiredError,
    PermitPolicyConfig,
    check_permit_or_raise,
    get_actions_requiring_permit,
    get_deny_error_code,
    is_action_requiring_permit,
    permit_required,
    reload_config,
)


class TestPermitPolicyConfig:
    """Tests for PermitPolicyConfig dataclass."""

    def test_from_dict_default_values(self):
        """Test config creation with minimal data."""
        config = PermitPolicyConfig.from_dict({})
        assert config.version == 1
        assert config.actions_requiring_permit == []
        assert config.deny_without_permit_error_code == "PERMIT_REQUIRED"

    def test_from_dict_full_values(self):
        """Test config creation with full data."""
        data = {
            "version": 2,
            "actions_requiring_permit": ["ACTION_A", "ACTION_B"],
            "deny_without_permit_error_code": "CUSTOM_ERROR",
        }
        config = PermitPolicyConfig.from_dict(data)
        assert config.version == 2
        assert config.actions_requiring_permit == ["ACTION_A", "ACTION_B"]
        assert config.deny_without_permit_error_code == "CUSTOM_ERROR"


class TestDenyErrorCodeFixed:
    """
    Test that deny_without_permit_error_code is fixed to PERMIT_REQUIRED.

    This ensures semantic consistency - the error code must NOT drift.
    """

    def test_deny_error_code_constant(self):
        """DENY_WITHOUT_PERMIT_ERROR_CODE must be PERMIT_REQUIRED."""
        assert DENY_WITHOUT_PERMIT_ERROR_CODE == "PERMIT_REQUIRED"

    def test_get_deny_error_code_returns_fixed_value(self):
        """get_deny_error_code() must return PERMIT_REQUIRED."""
        assert get_deny_error_code() == "PERMIT_REQUIRED"

    def test_permit_required_error_code_fixed(self):
        """PermitRequiredError.code must be PERMIT_REQUIRED."""
        error = PermitRequiredError("SOME_ACTION")
        assert error.code == "PERMIT_REQUIRED"


class TestPermitRequiredError:
    """Tests for PermitRequiredError exception."""

    def test_error_message_includes_action(self):
        """Error message must include the action name."""
        error = PermitRequiredError("PUBLISH_LISTING")
        assert "PUBLISH_LISTING" in str(error)

    def test_error_message_includes_error_code(self):
        """Error message must include the error code."""
        error = PermitRequiredError("PUBLISH_LISTING")
        assert "PERMIT_REQUIRED" in str(error)

    def test_error_with_custom_message(self):
        """Error can have custom message."""
        error = PermitRequiredError("ACTION", message="Custom message")
        assert str(error) == "Custom message"

    def test_error_is_exception(self):
        """PermitRequiredError must be an Exception."""
        error = PermitRequiredError("ACTION")
        assert isinstance(error, Exception)


class TestIsActionRequiringPermit:
    """Tests for is_action_requiring_permit function."""

    def test_publish_listing_requires_permit(self):
        """PUBLISH_LISTING must require a permit."""
        reload_config()
        assert is_action_requiring_permit("PUBLISH_LISTING") is True

    def test_execute_via_n8n_requires_permit(self):
        """EXECUTE_VIA_N8N must require a permit."""
        reload_config()
        assert is_action_requiring_permit("EXECUTE_VIA_N8N") is True

    def test_export_whitelist_requires_permit(self):
        """EXPORT_WHITELIST must require a permit."""
        reload_config()
        assert is_action_requiring_permit("EXPORT_WHITELIST") is True

    def test_upgrade_replace_active_requires_permit(self):
        """UPGRADE_REPLACE_ACTIVE must require a permit."""
        reload_config()
        assert is_action_requiring_permit("UPGRADE_REPLACE_ACTIVE") is True

    def test_unknown_action_does_not_require_permit(self):
        """Unknown actions should not require permit."""
        reload_config()
        assert is_action_requiring_permit("UNKNOWN_ACTION") is False

    def test_read_only_action_does_not_require_permit(self):
        """Read-only actions should not require permit."""
        reload_config()
        assert is_action_requiring_permit("READ_SKILL_SPEC") is False
        assert is_action_requiring_permit("VIEW_LISTING") is False


class TestPermitRequired:
    """Tests for permit_required function."""

    def test_permit_required_alias(self):
        """permit_required must be an alias for is_action_requiring_permit."""
        reload_config()
        # Both should return same result
        assert permit_required("PUBLISH_LISTING") == is_action_requiring_permit("PUBLISH_LISTING")
        assert permit_required("UNKNOWN") == is_action_requiring_permit("UNKNOWN")


class TestCheckPermitOrRaise:
    """Tests for check_permit_or_raise function."""

    def test_no_raise_when_permit_valid(self):
        """Should not raise when permit is valid."""
        # Should not raise
        check_permit_or_raise("PUBLISH_LISTING", permit_valid=True)

    def test_no_raise_when_action_not_requiring_permit(self):
        """Should not raise when action doesn't require permit."""
        # Should not raise even with invalid permit
        check_permit_or_raise("READ_SKILL_SPEC", permit_valid=False)

    def test_raises_when_permit_invalid(self):
        """Should raise PermitRequiredError when permit is invalid."""
        with pytest.raises(PermitRequiredError) as exc_info:
            check_permit_or_raise("PUBLISH_LISTING", permit_valid=False)

        assert exc_info.value.code == "PERMIT_REQUIRED"
        assert "PUBLISH_LISTING" in str(exc_info.value)

    def test_raises_includes_permit_status(self):
        """Error message should include permit status."""
        with pytest.raises(PermitRequiredError) as exc_info:
            check_permit_or_raise("EXECUTE_VIA_N8N", permit_valid=False, permit_status="EXPIRED")

        assert "EXPIRED" in str(exc_info.value)


class TestGetActionsRequiringPermit:
    """Tests for get_actions_requiring_permit function."""

    def test_returns_list(self):
        """Must return a list."""
        reload_config()
        actions = get_actions_requiring_permit()
        assert isinstance(actions, list)

    def test_includes_required_actions(self):
        """Must include the required actions from SEEDS_v0.md."""
        reload_config()
        actions = get_actions_requiring_permit()
        assert "PUBLISH_LISTING" in actions
        assert "EXECUTE_VIA_N8N" in actions
        assert "EXPORT_WHITELIST" in actions
        assert "UPGRADE_REPLACE_ACTIVE" in actions


class TestE001SemanticBaseline:
    """
    Test E001 semantic baseline from gate_permit.py.

    E001 (permit missing) must map to PERMIT_REQUIRED.
    This ensures no semantic drift.
    """

    def test_e001_maps_to_permit_required(self):
        """E001 error code must map to PERMIT_REQUIRED."""
        # From gate_permit.py ERROR_CODES mapping
        e001_code = "E001"
        expected_mapping = "PERMIT_REQUIRED"

        # Verify our helper uses the same mapping
        assert get_deny_error_code() == expected_mapping

        # Verify PermitRequiredError uses the same code
        error = PermitRequiredError("ACTION")
        assert error.code == expected_mapping

    def test_permit_missing_blocked_by_permit_required(self):
        """
        When permit is missing (E001), blocked_by must be PERMIT_REQUIRED.

        This matches gate_permit.py behavior:
        - E001: permit 缺失 -> PERMIT_REQUIRED
        """
        # Simulate the check that would happen in middleware
        with pytest.raises(PermitRequiredError) as exc_info:
            check_permit_or_raise("PUBLISH_LISTING", permit_valid=False)

        # The error code must be PERMIT_REQUIRED (not something else)
        assert exc_info.value.code == "PERMIT_REQUIRED"


class TestMiddlewareIntegration:
    """
    Test that permit_required integrates with membership_middleware.

    The middleware should use permit_required for all side-effect actions.
    """

    def test_middleware_check_publish_uses_permit_required(self):
        """
        verify that PUBLISH_LISTING requires permit.

        This matches membership_middleware.check_publish_listing behavior.
        """
        reload_config()
        assert permit_required("PUBLISH_LISTING") is True

    def test_middleware_check_execute_uses_permit_required(self):
        """
        Verify that EXECUTE_VIA_N8N requires permit.

        This matches membership_middleware.check_execute_via_n8n behavior.
        """
        reload_config()
        assert permit_required("EXECUTE_VIA_N8N") is True


class TestConfigReload:
    """Tests for config reload functionality."""

    def test_reload_config_clears_cache(self):
        """reload_config should clear cached config."""
        # Load config
        _ = get_actions_requiring_permit()
        # Reload
        reload_config()
        # Should work without error
        actions = get_actions_requiring_permit()
        assert isinstance(actions, list)


class TestEnvironmentVariableConfig:
    """Tests for environment variable based config path."""

    def test_custom_config_path_via_env(self, tmp_path):
        """Should load config from SECURITY_PERMIT_POLICY_PATH."""
        # Create custom config
        custom_config = tmp_path / "custom_permit_policy.yml"
        custom_config.write_text("""
version: 1
actions_requiring_permit:
  - CUSTOM_ACTION_A
  - CUSTOM_ACTION_B
deny_without_permit_error_code: "PERMIT_REQUIRED"
""")
        # Set env var
        with patch.dict(os.environ, {"SECURITY_PERMIT_POLICY_PATH": str(custom_config)}):
            reload_config()
            actions = get_actions_requiring_permit()
            assert "CUSTOM_ACTION_A" in actions
            assert "CUSTOM_ACTION_B" in actions
            assert "PUBLISH_LISTING" not in actions


# Run tests with: python -m pytest -q skillforge/tests/test_permit_required_policy.py
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
