"""
Tests for i18n Contract Loader

SEEDS-P1-7: UI 文案映射合同（i18n_key）
Contract: T24 (L45-D5-SEEDS-P1-20260220-005)
Coverage: key existence, fail-closed behavior, YAML parsing
"""
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from skillforge.src.contracts.ui.i18n_contract_loader import (
    DEFAULT_I18N_CONTRACT_PATH,
    ERROR_CODES,
    REQUIRED_KEYS,
    I18nContractError,
    I18nContractLoader,
    I18nContract,
    get_i18n_loader,
    get_text,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def loader():
    """Create loader instance."""
    return I18nContractLoader()


@pytest.fixture
def valid_contract_data():
    """Create valid contract data for testing."""
    return {
        "version": 1,
        "gates": {
            "intake_repo": {
                "title": {"en": "Repository Intake", "zh": "仓库接入"},
                "description": {"en": "Intake and validate", "zh": "接入验证"},
            },
            "license_gate": {
                "title": {"en": "License Check", "zh": "许可证检查"},
            },
            "repo_scan_fit_score": {
                "title": {"en": "Repository Scan", "zh": "仓库扫描"},
            },
            "draft_skill_spec": {
                "title": {"en": "Draft Skill Spec", "zh": "起草技能规范"},
            },
            "constitution_risk_gate": {
                "title": {"en": "Constitution Risk Gate", "zh": "宪法风险门禁"},
            },
            "scaffold_skill_impl": {
                "title": {"en": "Scaffold Implementation", "zh": "脚手架实现"},
            },
            "sandbox_test_and_trace": {
                "title": {"en": "Sandbox Test", "zh": "沙盒测试"},
            },
            "pack_audit_and_publish": {
                "title": {"en": "Pack & Publish", "zh": "打包与发布"},
            },
        },
        "errors": {
            "fallback": {
                "title": {"en": "Error", "zh": "错误"},
                "message": {"en": "An error occurred.", "zh": "发生错误。"},
            },
        },
        "common": {
            "loading": {"en": "Loading...", "zh": "加载中..."},
        },
        "status": {},
        "decisions": {},
        "metadata": {},
    }


# ============================================================================
# Contract File Tests
# ============================================================================

class TestContractFile:
    """Tests for contract file existence and structure."""

    def test_contract_file_exists(self):
        """Contract file must exist at default path."""
        assert DEFAULT_I18N_CONTRACT_PATH.exists(), \
            f"Contract not found at {DEFAULT_I18N_CONTRACT_PATH}"

    def test_contract_is_valid_yaml(self, loader):
        """Contract must be valid YAML."""
        with open(DEFAULT_I18N_CONTRACT_PATH, "r") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert isinstance(data, dict)

    def test_contract_has_version(self, loader):
        """Contract must have version field."""
        contract = loader.load()
        assert contract.version >= 1


# ============================================================================
# Required Keys Tests
# ============================================================================

class TestRequiredKeys:
    """Tests for required key coverage."""

    def test_required_keys_defined(self):
        """Required keys list must be defined."""
        assert len(REQUIRED_KEYS) >= 10, "Must have at least 10 required keys"

    def test_required_keys_cover_8_gates(self):
        """Required keys must cover all 8 gates."""
        gate_keys = [k for k in REQUIRED_KEYS if k.startswith("gate.") and k.endswith(".title")]
        assert len(gate_keys) == 8, f"Expected 8 gate title keys, got {len(gate_keys)}"

    def test_required_keys_cover_fallback(self):
        """Required keys must include fallback keys."""
        fallback_keys = [k for k in REQUIRED_KEYS if "fallback" in k]
        assert "error.fallback.title" in REQUIRED_KEYS
        assert "error.fallback.message" in REQUIRED_KEYS

    def test_all_required_keys_present_in_contract(self, loader):
        """All required keys must be present in the contract."""
        contract = loader.load()
        missing = contract.validate_required_keys()
        assert len(missing) == 0, f"Missing required keys: {missing}"


# ============================================================================
# Key Retrieval Tests
# ============================================================================

class TestKeyRetrieval:
    """Tests for key retrieval."""

    def test_get_gate_title(self, loader):
        """Should retrieve gate title."""
        text = loader.get("gate.intake_repo.title")
        assert text is not None
        assert len(text) > 0

    def test_get_gate_title_in_english(self, loader):
        """Should retrieve English gate title."""
        text = loader.get("gate.intake_repo.title", lang="en")
        assert "Intake" in text or "Repository" in text

    def test_get_gate_title_in_chinese(self, loader):
        """Should retrieve Chinese gate title."""
        text = loader.get("gate.intake_repo.title", lang="zh")
        assert len(text) > 0

    def test_get_error_fallback_title(self, loader):
        """Should retrieve error fallback title."""
        text = loader.get("error.fallback.title")
        assert text is not None

    def test_get_error_fallback_message(self, loader):
        """Should retrieve error fallback message."""
        text = loader.get("error.fallback.message")
        assert text is not None
        assert len(text) > 0

    def test_fallback_to_english(self, loader):
        """Should fallback to English if requested language not found."""
        # This depends on contract having English but not Klingon
        text = loader.get("gate.intake_repo.title", lang="xx")
        assert text is not None  # Should get English fallback

    def test_get_common_text(self, loader):
        """Should retrieve common text."""
        text = loader.get("common.loading")
        assert text is not None


# ============================================================================
# Fail-Closed Tests
# ============================================================================

class TestFailClosed:
    """Tests for fail-closed behavior."""

    def test_missing_key_raises_error(self, loader):
        """Missing key must raise I18nContractError (fail-closed)."""
        with pytest.raises(I18nContractError) as exc_info:
            loader.get("gate.nonexistent.title")
        assert exc_info.value.error_code == "I18N_KEY_MISSING"

    def test_invalid_key_format_raises_error(self, loader):
        """Invalid key format must raise error."""
        with pytest.raises(I18nContractError) as exc_info:
            loader.get("invalidkey")
        assert exc_info.value.error_code == "I18N_KEY_MISSING"

    def test_unknown_section_raises_error(self, loader):
        """Unknown section must raise error."""
        with pytest.raises(I18nContractError) as exc_info:
            loader.get("unknown.section.key")
        assert exc_info.value.error_code == "I18N_KEY_MISSING"

    def test_missing_file_raises_error(self, tmp_path):
        """Missing contract file must raise error."""
        nonexistent_path = tmp_path / "nonexistent.yml"
        loader = I18nContractLoader(contract_path=nonexistent_path)

        with pytest.raises(I18nContractError) as exc_info:
            loader.load()
        assert exc_info.value.error_code == "I18N_CONTRACT_NOT_FOUND"

    def test_invalid_yaml_raises_error(self, tmp_path):
        """Invalid YAML must raise error."""
        invalid_yaml = tmp_path / "invalid.yml"
        invalid_yaml.write_text("not: valid: yaml: [")

        loader = I18nContractLoader(contract_path=invalid_yaml)

        with pytest.raises(I18nContractError) as exc_info:
            loader.load()
        assert exc_info.value.error_code == "I18N_CONTRACT_PARSE_ERROR"

    def test_non_dict_contract_raises_error(self, tmp_path):
        """Non-dict contract must raise error."""
        non_dict = tmp_path / "list.yml"
        non_dict.write_text("- item1\n- item2")

        loader = I18nContractLoader(contract_path=non_dict)

        with pytest.raises(I18nContractError) as exc_info:
            loader.load()
        assert exc_info.value.error_code == "I18N_CONTRACT_PARSE_ERROR"


# ============================================================================
# Error Code Tests
# ============================================================================

class TestErrorCodes:
    """Tests for error codes."""

    def test_error_codes_defined(self):
        """Error codes must be defined."""
        assert "I18N_CONTRACT_NOT_FOUND" in ERROR_CODES
        assert "I18N_CONTRACT_PARSE_ERROR" in ERROR_CODES
        assert "I18N_KEY_MISSING" in ERROR_CODES
        assert "I18N_KEY_EMPTY" in ERROR_CODES

    def test_error_code_in_exception(self, loader):
        """Exception must include error code."""
        with pytest.raises(I18nContractError) as exc_info:
            loader.get("nonexistent.key")

        assert exc_info.value.error_code is not None
        assert exc_info.value.key is not None


# ============================================================================
# Validation Tests
# ============================================================================

class TestValidation:
    """Tests for contract validation."""

    def test_validate_returns_true_for_valid_contract(self, loader):
        """Validate should return True for valid contract."""
        is_valid, missing = loader.validate()
        assert is_valid is True
        assert len(missing) == 0

    def test_validate_returns_missing_keys(self, tmp_path, valid_contract_data):
        """Validate should return missing keys if incomplete."""
        # Create contract missing some required keys
        incomplete = valid_contract_data.copy()
        del incomplete["gates"]["intake_repo"]

        contract_path = tmp_path / "incomplete.yml"
        with open(contract_path, "w") as f:
            yaml.dump(incomplete, f)

        loader = I18nContractLoader(contract_path=contract_path)
        is_valid, missing = loader.validate()

        assert is_valid is False
        assert len(missing) > 0

    def test_has_key_returns_true_for_existing_key(self, loader):
        """has_key should return True for existing key."""
        assert loader.has_key("gate.intake_repo.title") is True

    def test_has_key_returns_false_for_missing_key(self, loader):
        """has_key should return False for missing key."""
        assert loader.has_key("nonexistent.key") is False


# ============================================================================
# Convenience Function Tests
# ============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_text_function(self):
        """get_text function should work."""
        text = get_text("gate.intake_repo.title")
        assert text is not None

    def test_get_i18n_loader_singleton(self):
        """get_i18n_loader should return singleton."""
        loader1 = get_i18n_loader()
        loader2 = get_i18n_loader()
        assert loader1 is loader2


# ============================================================================
# 8 Gates Coverage Tests
# ============================================================================

class Test8GatesCoverage:
    """Tests for 8 gates coverage."""

    @pytest.mark.parametrize("gate_name", [
        "intake_repo",
        "license_gate",
        "repo_scan_fit_score",
        "draft_skill_spec",
        "constitution_risk_gate",
        "scaffold_skill_impl",
        "sandbox_test_and_trace",
        "pack_audit_and_publish",
    ])
    def test_gate_title_exists(self, loader, gate_name):
        """Each gate must have a title."""
        key = f"gate.{gate_name}.title"
        assert loader.has_key(key), f"Missing key: {key}"

    @pytest.mark.parametrize("gate_name", [
        "intake_repo",
        "license_gate",
        "repo_scan_fit_score",
        "draft_skill_spec",
        "constitution_risk_gate",
        "scaffold_skill_impl",
        "sandbox_test_and_trace",
        "pack_audit_and_publish",
    ])
    def test_gate_title_not_empty(self, loader, gate_name):
        """Each gate title must not be empty."""
        text = loader.get(f"gate.{gate_name}.title")
        assert len(text) > 0, f"Empty title for gate: {gate_name}"


# ============================================================================
# Fallback Key Tests
# ============================================================================

class TestFallbackKeys:
    """Tests for fallback keys."""

    def test_fallback_title_exists(self, loader):
        """Fallback title must exist."""
        assert loader.has_key("error.fallback.title")

    def test_fallback_message_exists(self, loader):
        """Fallback message must exist."""
        assert loader.has_key("error.fallback.message")

    def test_fallback_title_not_empty(self, loader):
        """Fallback title must not be empty."""
        text = loader.get("error.fallback.title")
        assert len(text) > 0

    def test_fallback_message_not_empty(self, loader):
        """Fallback message must not be empty."""
        text = loader.get("error.fallback.message")
        assert len(text) > 0


# ============================================================================
# No Hardcoded Fallback Tests
# ============================================================================

class TestNoHardcodedFallback:
    """Tests ensuring no hardcoded fallbacks bypass contract."""

    def test_get_raises_error_not_returns_default(self, loader):
        """get must raise error, not return default string."""
        # This test ensures fail-closed behavior
        # The loader should NOT return a hardcoded default
        with pytest.raises(I18nContractError):
            loader.get("completely.nonexistent.key")

    def test_no_empty_string_on_missing_key(self, loader):
        """Missing key must not return empty string silently."""
        with pytest.raises(I18nContractError):
            result = loader.get("nonexistent.key")
            # If we get here, ensure it's not empty string
            assert result != "", "Should not return empty string for missing key"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, loader):
        """Full workflow should work."""
        # 1. Load contract
        contract = loader.load()
        assert contract is not None

        # 2. Validate
        is_valid, missing = loader.validate()
        assert is_valid is True

        # 3. Get text
        text = loader.get("gate.intake_repo.title")
        assert text is not None

    def test_contract_structured_correctly(self, loader):
        """Contract should have correct structure."""
        contract = loader.load()

        assert hasattr(contract, "gates")
        assert hasattr(contract, "errors")
        assert hasattr(contract, "common")
        assert len(contract.gates) >= 8

    def test_metadata_exists(self, loader):
        """Contract should have metadata."""
        contract = loader.load()
        assert contract.metadata is not None
        assert "version" in contract.metadata or contract.version >= 1
