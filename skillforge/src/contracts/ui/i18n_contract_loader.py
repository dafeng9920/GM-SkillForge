"""
i18n Contract Loader - UI 文案映射合同读取器

SEEDS-P1-7: UI 文案映射合同（i18n_key）
提供读取与键存在性检查，确保所有 UI 文案通过合同映射。

Constraints:
- 合同必须覆盖 8 Gate title key + fallback key
- 读取器缺 key 时 fail-closed 报错
- keys 文件必须是可机器解析 YAML
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


# ============================================================================
# Constants
# ============================================================================

# Default path to i18n keys contract
DEFAULT_I18N_CONTRACT_PATH = Path(__file__).parent.parent.parent.parent.parent / "ui" / "contracts" / "i18n_keys.yml"

# Environment variable for custom path
I18N_CONTRACT_PATH_ENV = "SKILLFORGE_I18N_CONTRACT_PATH"

# Required keys per contract
REQUIRED_KEYS = [
    "gate.intake_repo.title",
    "gate.license_gate.title",
    "gate.repo_scan_fit_score.title",
    "gate.draft_skill_spec.title",
    "gate.constitution_risk_gate.title",
    "gate.scaffold_skill_impl.title",
    "gate.sandbox_test_and_trace.title",
    "gate.pack_audit_and_publish.title",
    "error.fallback.title",
    "error.fallback.message",
]

# Error codes
ERROR_CODES = {
    "I18N_CONTRACT_NOT_FOUND": "i18n contract file not found",
    "I18N_CONTRACT_PARSE_ERROR": "i18n contract is not valid YAML",
    "I18N_KEY_MISSING": "required key not found in contract",
    "I18N_KEY_EMPTY": "key exists but has empty value",
}


# ============================================================================
# Exceptions
# ============================================================================

class I18nContractError(Exception):
    """Base exception for i18n contract errors (fail-closed)."""

    def __init__(self, error_code: str, message: str, key: Optional[str] = None):
        self.error_code = error_code
        self.message = message
        self.key = key
        super().__init__(f"[{error_code}] {message}" + (f" (key: {key})" if key else ""))


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class I18nKey:
    """Represents an i18n key with its translations."""
    key: str
    translations: dict[str, str]

    def get(self, lang: str = "en") -> str:
        """Get translation for language, fallback to 'en' if not found."""
        if lang in self.translations:
            return self.translations[lang]
        if "en" in self.translations:
            return self.translations["en"]
        # Fail-closed: no fallback, raise error
        raise I18nContractError(
            error_code="I18N_KEY_EMPTY",
            message=f"No translation found for key '{self.key}'",
            key=self.key,
        )


@dataclass
class I18nContract:
    """Represents the loaded i18n contract."""
    version: int
    gates: dict[str, dict]
    errors: dict[str, dict]
    common: dict[str, dict]
    status: dict[str, dict]
    decisions: dict[str, dict]
    metadata: dict
    raw: dict

    def get_key(self, key_path: str, lang: str = "en") -> str:
        """
        Get a translation by key path.

        Key path format: "section.subsection.field"
        Examples:
          - "gate.intake_repo.title"
          - "error.fallback.message"
          - "common.loading"

        Args:
            key_path: Dot-separated key path
            lang: Language code (default: "en")

        Returns:
            Translation string

        Raises:
            I18nContractError: If key not found (fail-closed)
        """
        parts = key_path.split(".")
        if len(parts) < 2:
            raise I18nContractError(
                error_code="I18N_KEY_MISSING",
                message=f"Invalid key path format: '{key_path}'",
                key=key_path,
            )

        section = parts[0]
        subsection = ".".join(parts[1:-1]) if len(parts) > 2 else ""
        field = parts[-1]

        # Map section to contract data
        section_map = {
            "gate": self.gates,
            "error": self.errors,
            "common": self.common,
            "status": self.status,
            "decision": self.decisions,
        }

        if section not in section_map:
            raise I18nContractError(
                error_code="I18N_KEY_MISSING",
                message=f"Unknown section: '{section}'",
                key=key_path,
            )

        data = section_map[section]

        # Navigate subsections
        if subsection:
            for sub in subsection.split("."):
                if sub not in data:
                    raise I18nContractError(
                        error_code="I18N_KEY_MISSING",
                        message=f"Subsection '{sub}' not found in '{section}'",
                        key=key_path,
                    )
                data = data[sub]

        # Get field
        if field not in data:
            raise I18nContractError(
                error_code="I18N_KEY_MISSING",
                message=f"Field '{field}' not found in '{section}.{subsection}'",
                key=key_path,
            )

        field_data = data[field]

        # Handle direct string or dict with translations
        if isinstance(field_data, str):
            return field_data
        elif isinstance(field_data, dict):
            if lang in field_data:
                return field_data[lang]
            if "en" in field_data:
                return field_data["en"]
            raise I18nContractError(
                error_code="I18N_KEY_EMPTY",
                message=f"No translation for '{lang}' or 'en' in key",
                key=key_path,
            )

        raise I18nContractError(
            error_code="I18N_KEY_EMPTY",
            message=f"Invalid value type for key",
            key=key_path,
        )

    def has_key(self, key_path: str) -> bool:
        """Check if a key exists in the contract."""
        try:
            self.get_key(key_path)
            return True
        except I18nContractError:
            return False

    def validate_required_keys(self) -> list[str]:
        """
        Validate that all required keys are present.

        Returns:
            List of missing keys (empty if all present)
        """
        missing = []
        for key in REQUIRED_KEYS:
            if not self.has_key(key):
                missing.append(key)
        return missing


# ============================================================================
# I18n Contract Loader
# ============================================================================

class I18nContractLoader:
    """
    i18n 合同读取器。

    提供读取与键存在性检查，确保所有 UI 文案通过合同映射。

    Fail-closed behavior:
    - 缺 key 时抛出 I18nContractError
    - 不允许硬编码回退文案绕过合同
    """

    def __init__(self, contract_path: Optional[Path] = None):
        """
        Initialize the loader.

        Args:
            contract_path: Optional custom path to i18n contract file.
                          If None, uses default path or env variable.
        """
        if contract_path:
            self.contract_path = contract_path
        else:
            env_path = os.environ.get(I18N_CONTRACT_PATH_ENV)
            if env_path:
                self.contract_path = Path(env_path)
            else:
                self.contract_path = DEFAULT_I18N_CONTRACT_PATH

        self._contract: Optional[I18nContract] = None

    def load(self) -> I18nContract:
        """
        Load the i18n contract.

        Returns:
            I18nContract instance

        Raises:
            I18nContractError: If contract not found or invalid
        """
        if self._contract is not None:
            return self._contract

        if not self.contract_path.exists():
            raise I18nContractError(
                error_code="I18N_CONTRACT_NOT_FOUND",
                message=f"Contract file not found at: {self.contract_path}",
            )

        try:
            with open(self.contract_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise I18nContractError(
                error_code="I18N_CONTRACT_PARSE_ERROR",
                message=f"Failed to parse YAML: {e}",
            )

        if not isinstance(raw, dict):
            raise I18nContractError(
                error_code="I18N_CONTRACT_PARSE_ERROR",
                message="Contract must be a YAML mapping",
            )

        self._contract = I18nContract(
            version=raw.get("version", 1),
            gates=raw.get("gates", {}),
            errors=raw.get("errors", {}),
            common=raw.get("common", {}),
            status=raw.get("status", {}),
            decisions=raw.get("decisions", {}),
            metadata=raw.get("metadata", {}),
            raw=raw,
        )

        return self._contract

    def get(self, key_path: str, lang: str = "en") -> str:
        """
        Get a translation by key path.

        This is a convenience method that loads the contract if needed.

        Args:
            key_path: Dot-separated key path
            lang: Language code (default: "en")

        Returns:
            Translation string

        Raises:
            I18nContractError: If key not found (fail-closed)
        """
        contract = self.load()
        return contract.get_key(key_path, lang)

    def has_key(self, key_path: str) -> bool:
        """Check if a key exists in the contract."""
        contract = self.load()
        return contract.has_key(key_path)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate the contract.

        Returns:
            Tuple of (is_valid, missing_keys)
        """
        try:
            contract = self.load()
            missing = contract.validate_required_keys()
            return (len(missing) == 0, missing)
        except I18nContractError as e:
            return (False, [f"{e.error_code}: {e.message}"])

    @property
    def contract(self) -> I18nContract:
        """Get loaded contract, loading if necessary."""
        return self.load()


# ============================================================================
# Singleton Instance
# ============================================================================

_loader_instance: Optional[I18nContractLoader] = None


def get_i18n_loader() -> I18nContractLoader:
    """Get the singleton i18n loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = I18nContractLoader()
    return _loader_instance


def get_text(key_path: str, lang: str = "en") -> str:
    """
    Convenience function to get text by key path.

    This is the primary API for getting i18n text.
    Fail-closed: raises I18nContractError if key not found.

    Args:
        key_path: Dot-separated key path
        lang: Language code (default: "en")

    Returns:
        Translation string

    Raises:
        I18nContractError: If key not found
    """
    return get_i18n_loader().get(key_path, lang)
