"""
Tests for Feature Flag Loader - SEEDS P2 Environment-Aware

Tests verify:
1. Flag reading from YAML file works correctly
2. Environment profiles (dev/staging/prod) work correctly
3. Default values prevent half-finished capabilities from polluting main flow
4. Disabled flags produce auditable evidence (not silent)
5. Flags are not hardcoded in code
6. Missing profile results in fail-closed behavior
7. prod profile is most restrictive

Job ID: L45-D6-SEEDS-P2-20260220-006
Skill ID: l45_seeds_p2_operationalization
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from contracts.governance.feature_flag_loader import (
    FeatureFlagLoader,
    FeatureFlagEvidence,
    FeatureFlagResult,
    get_loader,
    is_enabled,
    check_with_evidence,
    get_disabled_evidence,
    reload_flags,
    get_current_environment,
    is_valid_environment,
    get_all_flags,
    get_all_profiles,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_config_v2():
    """Sample feature flags configuration with environment profiles."""
    return {
        "version": 2,
        "schema_ref": "SEEDS P2-8 feature_flags_env_profiles",
        "defaults": {
            "enable_sandbox_test": False,
            "enable_n8n_execution": False,
            "enable_github_intake_external": False,
            "enable_advanced_analytics": False,
        },
        "profiles": {
            "dev": {
                "description": "Development environment",
                "flags": {
                    "enable_sandbox_test": True,
                    "enable_n8n_execution": True,
                    "enable_github_intake_external": True,
                    "enable_advanced_analytics": False,
                },
            },
            "staging": {
                "description": "Staging environment",
                "flags": {
                    "enable_sandbox_test": True,
                    "enable_n8n_execution": True,
                    "enable_github_intake_external": False,
                    "enable_advanced_analytics": False,
                },
            },
            "prod": {
                "description": "Production environment",
                "flags": {
                    "enable_sandbox_test": False,
                    "enable_n8n_execution": False,
                    "enable_github_intake_external": False,
                    "enable_advanced_analytics": False,
                },
            },
        },
        "audit_policy": {
            "disabled_flag_behavior": "LOG_AND_BLOCK",
            "evidence_required": True,
        },
        "environment_config": {
            "env_var_name": "SKILLFORGE_ENV",
            "valid_environments": ["dev", "staging", "prod"],
            "default_if_missing": "unknown",
        },
    }


@pytest.fixture
def temp_config_file_v2(sample_config_v2):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yml",
        delete=False,
        encoding="utf-8"
    ) as f:
        yaml.dump(sample_config_v2, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def loader_dev(temp_config_file_v2):
    """Create a FeatureFlagLoader with temp config for dev environment."""
    loader = FeatureFlagLoader(config_path=temp_config_file_v2, environment="dev")
    return loader


@pytest.fixture
def loader_staging(temp_config_file_v2):
    """Create a FeatureFlagLoader with temp config for staging environment."""
    loader = FeatureFlagLoader(config_path=temp_config_file_v2, environment="staging")
    return loader


@pytest.fixture
def loader_prod(temp_config_file_v2):
    """Create a FeatureFlagLoader with temp config for prod environment."""
    loader = FeatureFlagLoader(config_path=temp_config_file_v2, environment="prod")
    return loader


@pytest.fixture
def loader_unknown(temp_config_file_v2):
    """Create a FeatureFlagLoader with temp config for unknown environment."""
    loader = FeatureFlagLoader(config_path=temp_config_file_v2, environment="unknown")
    return loader


# ============================================================================
# Test: Environment Detection
# ============================================================================

class TestEnvironmentDetection:
    """Tests for environment detection."""

    def test_get_current_environment_from_env_var(self):
        """Test that environment is read from SKILLFORGE_ENV."""
        with patch.dict(os.environ, {"SKILLFORGE_ENV": "dev"}):
            assert get_current_environment() == "dev"

        with patch.dict(os.environ, {"SKILLFORGE_ENV": "staging"}):
            assert get_current_environment() == "staging"

        with patch.dict(os.environ, {"SKILLFORGE_ENV": "prod"}):
            assert get_current_environment() == "prod"

    def test_get_current_environment_unknown_if_not_set(self):
        """Test that environment is 'unknown' if not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove SKILLFORGE_ENV if present
            os.environ.pop("SKILLFORGE_ENV", None)
            assert get_current_environment() == "unknown"

    def test_get_current_environment_invalid_value(self):
        """Test that invalid environment values result in 'unknown'."""
        with patch.dict(os.environ, {"SKILLFORGE_ENV": "invalid"}):
            assert get_current_environment() == "unknown"

    def test_is_valid_environment(self):
        """Test environment validation."""
        assert is_valid_environment("dev") is True
        assert is_valid_environment("staging") is True
        assert is_valid_environment("prod") is True
        assert is_valid_environment("unknown") is False
        assert is_valid_environment("invalid") is False
        assert is_valid_environment("") is False

    def test_loader_environment_property(self, temp_config_file_v2):
        """Test that loader respects explicit environment."""
        loader = FeatureFlagLoader(config_path=temp_config_file_v2, environment="prod")
        assert loader.environment == "prod"


# ============================================================================
# Test: Environment Profiles
# ============================================================================

class TestEnvironmentProfiles:
    """Tests for environment-specific flag profiles."""

    def test_dev_profile_flags(self, loader_dev):
        """Test that dev profile has expected flags."""
        assert loader_dev.is_enabled("enable_sandbox_test") is True
        assert loader_dev.is_enabled("enable_n8n_execution") is True
        assert loader_dev.is_enabled("enable_github_intake_external") is True
        assert loader_dev.is_enabled("enable_advanced_analytics") is False

    def test_staging_profile_flags(self, loader_staging):
        """Test that staging profile has expected flags."""
        assert loader_staging.is_enabled("enable_sandbox_test") is True
        assert loader_staging.is_enabled("enable_n8n_execution") is True
        assert loader_staging.is_enabled("enable_github_intake_external") is False
        assert loader_staging.is_enabled("enable_advanced_analytics") is False

    def test_prod_profile_flags(self, loader_prod):
        """Test that prod profile is most restrictive."""
        # prod should have all flags disabled
        assert loader_prod.is_enabled("enable_sandbox_test") is False
        assert loader_prod.is_enabled("enable_n8n_execution") is False
        assert loader_prod.is_enabled("enable_github_intake_external") is False
        assert loader_prod.is_enabled("enable_advanced_analytics") is False

    def test_prod_most_restrictive(self, loader_dev, loader_staging, loader_prod):
        """Test that prod profile is more restrictive than dev and staging."""
        dev_flags = loader_dev.get_all_flags()
        staging_flags = loader_staging.get_all_flags()
        prod_flags = loader_prod.get_all_flags()

        # prod should have fewer or equal enabled flags than staging
        for flag_name, prod_value in prod_flags.items():
            staging_value = staging_flags.get(flag_name, False)
            # If staging has it disabled, prod should too
            if not staging_value:
                assert prod_value is False, (
                    f"prod has {flag_name}=True but staging has it disabled"
                )

        # staging should have fewer or equal enabled flags than dev
        for flag_name, staging_value in staging_flags.items():
            dev_value = dev_flags.get(flag_name, False)
            # If dev has it disabled, staging should too
            if not dev_value:
                assert staging_value is False, (
                    f"staging has {flag_name}=True but dev has it disabled"
                )

    def test_get_all_profiles(self, loader_dev):
        """Test getting all profiles."""
        profiles = loader_dev.get_all_profiles()
        assert "dev" in profiles
        assert "staging" in profiles
        assert "prod" in profiles

    def test_get_specific_profile(self, loader_dev):
        """Test getting a specific profile."""
        profile = loader_dev.get_profile("prod")
        assert profile is not None
        assert "flags" in profile


# ============================================================================
# Test: Fail-Closed for Unknown Environment
# ============================================================================

class TestFailClosedUnknownEnvironment:
    """Tests that unknown/missing environment results in fail-closed behavior."""

    def test_unknown_environment_uses_defaults(self, loader_unknown):
        """Test that unknown environment uses fail-closed defaults."""
        # All flags should be disabled (using defaults)
        assert loader_unknown.is_enabled("enable_sandbox_test") is False
        assert loader_unknown.is_enabled("enable_n8n_execution") is False
        assert loader_unknown.is_enabled("enable_github_intake_external") is False

    def test_missing_profile_uses_defaults(self, temp_config_file_v2):
        """Test that missing profile falls back to defaults."""
        loader = FeatureFlagLoader(
            config_path=temp_config_file_v2,
            environment="nonexistent_env"
        )
        # Should use defaults (all false)
        assert loader.is_enabled("enable_n8n_execution") is False


# ============================================================================
# Test: Flag Reading from YAML
# ============================================================================

class TestFlagReading:
    """Tests for reading flags from YAML configuration."""

    def test_load_config_success(self, loader_dev):
        """Test that configuration loads successfully."""
        assert loader_dev._loaded is False
        loader_dev._load_config()
        assert loader_dev._loaded is True

    def test_read_enabled_flag(self, loader_dev):
        """Test reading an enabled flag."""
        enabled = loader_dev.is_enabled("enable_sandbox_test")
        assert enabled is True

    def test_read_disabled_flag(self, loader_prod):
        """Test reading a disabled flag."""
        enabled = loader_prod.is_enabled("enable_n8n_execution")
        assert enabled is False

    def test_read_nonexistent_flag_defaults_false(self, loader_dev):
        """Test that non-existent flags default to False (fail-closed)."""
        enabled = loader_dev.is_enabled("nonexistent_flag")
        assert enabled is False

    def test_read_nonexistent_flag_custom_default(self, loader_dev):
        """Test custom default for non-existent flags."""
        enabled = loader_dev.is_enabled("nonexistent_flag", default=True)
        assert enabled is True

    def test_get_all_flags(self, loader_dev):
        """Test getting all flags."""
        flags = loader_dev.get_all_flags()
        assert "enable_sandbox_test" in flags
        assert "enable_n8n_execution" in flags
        assert flags["enable_sandbox_test"] is True
        assert flags["enable_n8n_execution"] is True

    def test_get_raw_flag_value(self, loader_dev):
        """Test getting raw flag value without boolean coercion."""
        value = loader_dev.get_flag("enable_sandbox_test")
        assert value is True


# ============================================================================
# Test: Default Values Prevent Pollution
# ============================================================================

class TestFailClosedDefaults:
    """Tests that default strategy prevents half-finished capabilities."""

    def test_missing_config_file_defaults_to_false(self):
        """Test that missing config file results in all flags disabled."""
        loader = FeatureFlagLoader(
            config_path="/nonexistent/path/flags.yml",
            environment="dev"
        )
        assert loader.is_enabled("enable_n8n_execution") is False
        assert loader.is_enabled("any_other_flag") is False

    def test_invalid_yaml_defaults_to_false(self):
        """Test that invalid YAML results in all flags disabled."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yml",
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            loader = FeatureFlagLoader(config_path=temp_path, environment="dev")
            assert loader.is_enabled("enable_n8n_execution") is False
        finally:
            os.unlink(temp_path)

    def test_empty_config_defaults_to_false(self):
        """Test that empty config results in all flags disabled."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yml",
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write("")
            temp_path = f.name

        try:
            loader = FeatureFlagLoader(config_path=temp_path, environment="dev")
            assert loader.is_enabled("enable_n8n_execution") is False
        finally:
            os.unlink(temp_path)


# ============================================================================
# Test: Disabled Flag Evidence (Not Silent)
# ============================================================================

class TestDisabledFlagEvidence:
    """Tests that disabled flags produce auditable evidence (not silent)."""

    def test_check_with_evidence_returns_result(self, loader_prod):
        """Test that check_with_evidence returns a result."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="TEST-123")
        assert isinstance(result, FeatureFlagResult)
        assert result.flag_name == "enable_n8n_execution"
        assert result.enabled is False

    def test_disabled_flag_produces_evidence(self, loader_prod):
        """Test that disabled flags produce evidence."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="TEST-123")
        assert result.evidence is not None, (
            "Disabled flag must produce evidence (not silent)"
        )

    def test_evidence_has_required_fields(self, loader_prod):
        """Test that evidence has all required audit fields."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="TEST-123")
        evidence = result.evidence

        assert evidence.issue_key is not None
        assert evidence.source_locator is not None
        assert evidence.content_hash is not None
        assert evidence.timestamp is not None
        assert evidence.flag_name == "enable_n8n_execution"
        assert evidence.enabled is False
        assert evidence.action_taken is not None
        assert evidence.reason is not None

    def test_evidence_includes_environment(self, loader_prod):
        """Test that evidence includes environment context."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="TEST-123")
        evidence = result.evidence
        assert evidence.environment == "prod"
        assert "environment" in evidence.to_dict()

    def test_evidence_includes_run_id(self, loader_prod):
        """Test that evidence includes run_id for correlation."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="RUN-CORRELATE-123")
        assert result.evidence.run_id == "RUN-CORRELATE-123"

    def test_evidence_to_dict_serializable(self, loader_prod):
        """Test that evidence can be serialized to dict."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="TEST-123")
        evidence_dict = result.evidence.to_dict()

        assert isinstance(evidence_dict, dict)
        assert "issue_key" in evidence_dict
        assert "source_locator" in evidence_dict
        assert "flag_name" in evidence_dict
        assert "action_taken" in evidence_dict
        assert "environment" in evidence_dict

    def test_enabled_flag_no_evidence(self, loader_dev):
        """Test that enabled flags don't produce evidence."""
        result = loader_dev.check_with_evidence("enable_sandbox_test", run_id="TEST-123")
        assert result.enabled is True
        assert result.evidence is None

    def test_create_disabled_evidence_standalone(self, loader_prod):
        """Test creating evidence directly."""
        evidence = loader_prod.create_disabled_evidence(
            "enable_n8n_execution",
            run_id="TEST-456",
            additional_context={"reason": "test context"}
        )
        assert evidence.flag_name == "enable_n8n_execution"
        assert evidence.run_id == "TEST-456"
        assert evidence.environment == "prod"
        assert "test context" in evidence.additional_context.get("reason", "")


# ============================================================================
# Test: Flags Not Hardcoded
# ============================================================================

class TestFlagsNotHardcoded:
    """Tests that flags are read from config, not hardcoded."""

    def test_flags_change_when_config_changes(self, temp_config_file_v2, sample_config_v2):
        """Test that reloading config picks up changes."""
        loader = FeatureFlagLoader(config_path=temp_config_file_v2, environment="dev")

        # Initial read - dev has n8n enabled
        assert loader.is_enabled("enable_n8n_execution") is True

        # Modify config - disable n8n in dev
        sample_config_v2["profiles"]["dev"]["flags"]["enable_n8n_execution"] = False
        with open(temp_config_file_v2, "w", encoding="utf-8") as f:
            yaml.dump(sample_config_v2, f)

        # Reload and verify change
        loader.reload()
        assert loader.is_enabled("enable_n8n_execution") is False

    def test_different_environments_have_different_flags(self, temp_config_file_v2):
        """Test that different environments have different flag values."""
        loader_dev = FeatureFlagLoader(config_path=temp_config_file_v2, environment="dev")
        loader_prod = FeatureFlagLoader(config_path=temp_config_file_v2, environment="prod")

        # dev has n8n enabled, prod does not
        assert loader_dev.is_enabled("enable_n8n_execution") is True
        assert loader_prod.is_enabled("enable_n8n_execution") is False


# ============================================================================
# Test: Module-Level Convenience Functions
# ============================================================================

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_is_enabled_function(self, temp_config_file_v2):
        """Test the is_enabled convenience function."""
        import contracts.governance.feature_flag_loader as ff_module
        ff_module._loader = None

        with patch.dict(os.environ, {
            "FEATURE_FLAGS_PATH": temp_config_file_v2,
            "SKILLFORGE_ENV": "dev"
        }):
            result = is_enabled("enable_sandbox_test")
            assert result is True

    def test_get_disabled_evidence_function(self, temp_config_file_v2):
        """Test the get_disabled_evidence convenience function."""
        import contracts.governance.feature_flag_loader as ff_module
        ff_module._loader = None

        with patch.dict(os.environ, {
            "FEATURE_FLAGS_PATH": temp_config_file_v2,
            "SKILLFORGE_ENV": "prod"
        }):
            evidence = get_disabled_evidence("enable_n8n_execution", run_id="TEST-789")
            assert isinstance(evidence, FeatureFlagEvidence)
            assert evidence.flag_name == "enable_n8n_execution"
            assert evidence.environment == "prod"

    def test_check_with_evidence_function(self, temp_config_file_v2):
        """Test the check_with_evidence convenience function."""
        import contracts.governance.feature_flag_loader as ff_module
        ff_module._loader = None

        with patch.dict(os.environ, {
            "FEATURE_FLAGS_PATH": temp_config_file_v2,
            "SKILLFORGE_ENV": "prod"
        }):
            result = check_with_evidence("enable_n8n_execution", run_id="TEST-789")
            assert isinstance(result, FeatureFlagResult)
            assert result.enabled is False
            assert result.evidence is not None
            assert result.environment == "prod"


# ============================================================================
# Test: Integration with n8n Orchestration
# ============================================================================

class TestN8nIntegration:
    """Tests for integration with n8n orchestration module."""

    def test_enable_n8n_execution_flag_exists(self, loader_dev):
        """Test that enable_n8n_execution flag is defined."""
        all_flags = loader_dev.get_all_flags()
        assert "enable_n8n_execution" in all_flags, (
            "enable_n8n_execution flag must be defined for n8n orchestration"
        )

    def test_enable_n8n_execution_prod_disabled(self, loader_prod):
        """Test that n8n execution is disabled in prod."""
        assert loader_prod.is_enabled("enable_n8n_execution") is False, (
            "enable_n8n_execution must be False in prod environment"
        )

    def test_n8n_disabled_produces_auditable_evidence(self, loader_prod):
        """
        Test that disabled n8n execution produces auditable evidence.

        This is the key requirement: "开关关闭时要有可审计 evidence（不静默）"
        """
        result = loader_prod.check_with_evidence(
            "enable_n8n_execution",
            run_id="N8N-TEST-RUN"
        )

        # Must not be enabled
        assert result.enabled is False

        # Must have evidence (not silent)
        assert result.evidence is not None, (
            "Disabled n8n execution must produce auditable evidence, not silent"
        )

        # Evidence must be meaningful
        evidence = result.evidence
        assert "enable_n8n_execution" in evidence.reason
        assert evidence.action_taken == "BLOCKED_BY_DISABLED_FLAG"
        assert evidence.environment == "prod"


# ============================================================================
# Test: Audit Policy
# ============================================================================

class TestAuditPolicy:
    """Tests for audit policy configuration."""

    def test_get_audit_policy(self, loader_dev):
        """Test getting audit policy."""
        policy = loader_dev.get_audit_policy()
        assert isinstance(policy, dict)

    def test_audit_policy_has_required_fields(self, loader_dev):
        """Test that audit policy has required configuration."""
        policy = loader_dev.get_audit_policy()
        assert "disabled_flag_behavior" in policy
        assert "evidence_required" in policy


# ============================================================================
# Test: Result Environment Field
# ============================================================================

class TestResultEnvironmentField:
    """Tests that results include environment information."""

    def test_result_includes_environment(self, loader_prod):
        """Test that FeatureFlagResult includes environment."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="TEST")
        assert result.environment == "prod"

    def test_result_to_dict_includes_environment(self, loader_prod):
        """Test that result serialization includes environment."""
        result = loader_prod.check_with_evidence("enable_n8n_execution", run_id="TEST")
        result_dict = result.to_dict()
        assert "environment" in result_dict
        assert result_dict["environment"] == "prod"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
