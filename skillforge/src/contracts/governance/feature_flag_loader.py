"""
Feature Flag Loader - SEEDS P2 Environment-Aware

Provides runtime feature flag loading with environment profiles (dev/staging/prod).

Key Principles:
1. Never hardcode flag values in code - always read from config file.
2. Default to FALSE (fail-closed) for any missing or unreadable flags.
3. Environment-aware: different profiles for dev/staging/prod.
4. When a flag blocks execution, produce auditable evidence (not silent).
5. prod profile is most restrictive; missing profile is fail-closed.

Contract: docs/SEEDS_v0.md (P1-8 Feature Flags + P2 Environment Profiles)
Job ID: L45-D6-SEEDS-P2-20260220-006
Skill ID: l45_seeds_p2_operationalization

Environment Detection:
- Read SKILLFORGE_ENV environment variable
- Valid values: dev, staging, prod
- If missing or unknown: use fail-closed defaults

Integration Point: skillforge/src/api/routes/n8n_orchestration.py
- Use is_enabled("enable_n8n_execution") to gate n8n execution
- When disabled: return error with evidence_ref (not silent)

Usage:
    from .feature_flag_loader import (
        FeatureFlagLoader,
        is_enabled,
        get_disabled_evidence,
        get_current_environment,
    )

    # Check environment
    env = get_current_environment()  # dev/staging/prod/unknown

    # Simple check (environment-aware)
    if is_enabled("enable_n8n_execution"):
        # proceed with n8n execution
        pass
    else:
        # Return auditable evidence
        evidence = get_disabled_evidence("enable_n8n_execution", run_id)
        return {"error": "FEATURE_DISABLED", "evidence": evidence}
"""
from __future__ import annotations

import hashlib
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml


# ============================================================================
# Logging Setup
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# Constants
# ============================================================================

DEFAULT_FLAGS_PATH = "orchestration/feature_flags.yml"
ENV_VAR_NAME = "SKILLFORGE_ENV"
VALID_ENVIRONMENTS = frozenset(["dev", "staging", "prod"])
DEFAULT_ENVIRONMENT_IF_MISSING = "unknown"

# Per-path cache for loaded flags (simple in-memory cache)
# Keyed by config path to avoid sharing cache across different files
_FLAGS_CACHE: dict[str, dict[str, Any]] = {}
_FLAGS_CACHE_TIMESTAMP: dict[str, float] = {}
_CACHE_TTL_SECONDS = 60  # Cache for 60 seconds


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class FeatureFlagEvidence:
    """
    Evidence record produced when a disabled flag blocks execution.

    Per SEEDS P1-8 constraints:
    - "开关关闭时要有可审计 evidence（不静默）"
    - Evidence must be non-silent and auditable.
    """
    issue_key: str
    source_locator: str
    content_hash: str
    timestamp: str
    flag_name: str
    enabled: bool
    action_taken: str
    reason: str
    environment: str = "unknown"
    run_id: Optional[str] = None
    additional_context: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "issue_key": self.issue_key,
            "source_locator": self.source_locator,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
            "flag_name": self.flag_name,
            "enabled": self.enabled,
            "action_taken": self.action_taken,
            "reason": self.reason,
            "environment": self.environment,
        }
        if self.run_id:
            result["run_id"] = self.run_id
        if self.additional_context:
            result["additional_context"] = self.additional_context
        return result


@dataclass
class FeatureFlagResult:
    """Result of feature flag evaluation."""
    flag_name: str
    enabled: bool
    source: str  # "profile", "default", "env_override", "error"
    environment: str
    evidence: Optional[FeatureFlagEvidence] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "flag_name": self.flag_name,
            "enabled": self.enabled,
            "source": self.source,
            "environment": self.environment,
            "evidence": self.evidence.to_dict() if self.evidence else None,
        }


# ============================================================================
# Environment Detection
# ============================================================================

def get_current_environment() -> str:
    """
    Get the current environment from SKILLFORGE_ENV.

    Returns:
        One of: dev, staging, prod, unknown
    """
    env = os.getenv(ENV_VAR_NAME, "").lower().strip()
    if env in VALID_ENVIRONMENTS:
        return env
    return DEFAULT_ENVIRONMENT_IF_MISSING


def is_valid_environment(env: str) -> bool:
    """Check if an environment string is valid."""
    return env.lower() in VALID_ENVIRONMENTS


# ============================================================================
# FeatureFlagLoader Class
# ============================================================================

class FeatureFlagLoader:
    """
    Loads feature flags from YAML configuration file with environment profiles.

    Design Principles:
    1. Fail-closed: Missing/invalid flags default to FALSE
    2. Config-driven: All flag values come from YAML, never hardcoded
    3. Environment-aware: Different profiles for dev/staging/prod
    4. Auditable: Disabled flags must produce evidence

    Thread Safety: This implementation is NOT thread-safe.
    For multi-threaded environments, use appropriate locking.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        """
        Initialize the feature flag loader.

        Args:
            config_path: Path to feature_flags.yml. If None, uses default path.
            environment: Environment to use. If None, reads from SKILLFORGE_ENV.
        """
        self.config_path = config_path or self._find_config_path()
        self._environment = environment
        self._flags: dict[str, Any] = {}
        self._defaults: dict[str, Any] = {}
        self._profiles: dict[str, dict[str, Any]] = {}
        self._audit_policy: dict[str, Any] = {}
        self._env_config: dict[str, Any] = {}
        self._loaded = False
        self._load_error: Optional[str] = None

    @property
    def environment(self) -> str:
        """Get the current environment (lazy evaluation)."""
        if self._environment is None:
            self._environment = get_current_environment()
        return self._environment

    def _find_config_path(self) -> str:
        """Find the configuration file path."""
        # Try environment variable first
        env_path = os.getenv("FEATURE_FLAGS_PATH")
        if env_path and Path(env_path).exists():
            return env_path

        # Try relative to current working directory
        cwd_path = Path.cwd() / DEFAULT_FLAGS_PATH
        if cwd_path.exists():
            return str(cwd_path)

        # Try relative to this file's location (walk up to find project root)
        current = Path(__file__).resolve()
        for _ in range(10):  # Max 10 levels up
            candidate = current / DEFAULT_FLAGS_PATH
            if candidate.exists():
                return str(candidate)
            if current.parent == current:
                break
            current = current.parent

        # Default fallback (will fail on load, producing fail-closed behavior)
        return DEFAULT_FLAGS_PATH

    def _load_config(self, force_reload: bool = False) -> None:
        """
        Load configuration from YAML file.

        Uses per-path caching to avoid repeated file reads.
        """
        global _FLAGS_CACHE, _FLAGS_CACHE_TIMESTAMP

        current_time = time.time()
        cache_key = f"{self.config_path}:{self.environment}"

        # Use cached value if valid and not forcing reload
        if not force_reload and cache_key in _FLAGS_CACHE:
            if current_time - _FLAGS_CACHE_TIMESTAMP.get(cache_key, 0) < _CACHE_TTL_SECONDS:
                cached = _FLAGS_CACHE[cache_key]
                self._flags = cached.get("flags", {})
                self._defaults = cached.get("defaults", {})
                self._profiles = cached.get("profiles", {})
                self._audit_policy = cached.get("audit_policy", {})
                self._env_config = cached.get("environment_config", {})
                self._loaded = True
                return

        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                self._load_error = f"Config file not found: {self.config_path}"
                self._set_fail_closed_defaults()
                self._loaded = True
                return

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

            # Load all config sections
            self._defaults = config.get("defaults", {})
            self._profiles = config.get("profiles", {})
            self._audit_policy = config.get("audit_policy", {})
            self._env_config = config.get("environment_config", {})

            # Resolve flags for current environment
            self._flags = self._resolve_flags_for_environment(self.environment)

            self._loaded = True
            self._load_error = None

            # Log environment detection if configured
            if self._env_config.get("log_environment_detection", True):
                logger.info(
                    f"Feature flags loaded for environment: {self.environment}, "
                    f"flags count: {len(self._flags)}"
                )

            # Update cache for this path+environment
            _FLAGS_CACHE[cache_key] = {
                "flags": self._flags,
                "defaults": self._defaults,
                "profiles": self._profiles,
                "audit_policy": self._audit_policy,
                "environment_config": self._env_config,
            }
            _FLAGS_CACHE_TIMESTAMP[cache_key] = current_time

        except yaml.YAMLError as e:
            self._load_error = f"YAML parse error: {e}"
            self._set_fail_closed_defaults()
            self._loaded = True
        except Exception as e:
            self._load_error = f"Error loading config: {e}"
            self._set_fail_closed_defaults()
            self._loaded = True

    def _set_fail_closed_defaults(self) -> None:
        """Set all flags to fail-closed (false) state."""
        self._flags = {}
        self._defaults = {}
        self._profiles = {}
        self._audit_policy = {}
        self._env_config = {}

    def _resolve_flags_for_environment(self, env: str) -> dict[str, Any]:
        """
        Resolve flags for a specific environment.

        Resolution order:
        1. If environment has a profile, use profile flags
        2. Otherwise, use defaults (fail-closed)

        Args:
            env: Environment name (dev/staging/prod/unknown)

        Returns:
            Dictionary of resolved flags
        """
        # Check if environment has a valid profile
        if env in self._profiles and "flags" in self._profiles[env]:
            return dict(self._profiles[env]["flags"])

        # Fall back to defaults (fail-closed)
        # This handles "unknown" environment and missing profiles
        logger.warning(
            f"Environment '{env}' has no profile, using fail-closed defaults"
        )
        return dict(self._defaults) if self._defaults else {}

    def is_enabled(self, flag_name: str, default: bool = False) -> bool:
        """
        Check if a feature flag is enabled for the current environment.

        Fail-closed behavior:
        - If config not loaded, returns default (typically False)
        - If flag not found, returns default
        - If flag value is invalid, returns default
        - If environment is unknown, uses fail-closed defaults

        Args:
            flag_name: Name of the feature flag (e.g., "enable_n8n_execution")
            default: Default value if flag cannot be determined (default: False)

        Returns:
            True if flag is explicitly enabled, False otherwise
        """
        if not self._loaded:
            self._load_config()

        # Get flag value, defaulting to the provided default
        value = self._flags.get(flag_name, default)

        # Coerce to boolean (handle various truthy/falsy values)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "enabled")
        if isinstance(value, (int, float)):
            return bool(value)

        return default

    def get_flag(self, flag_name: str, default: Any = None) -> Any:
        """
        Get raw flag value without boolean coercion.

        Args:
            flag_name: Name of the feature flag
            default: Default value if flag not found

        Returns:
            Raw flag value or default
        """
        if not self._loaded:
            self._load_config()

        return self._flags.get(flag_name, default)

    def get_all_flags(self) -> dict[str, Any]:
        """
        Get all loaded feature flags for current environment.

        Returns:
            Dictionary of all flag names to values
        """
        if not self._loaded:
            self._load_config()

        return dict(self._flags)

    def get_defaults(self) -> dict[str, Any]:
        """
        Get default flag values (fail-closed fallback).

        Returns:
            Dictionary of default flag values
        """
        if not self._loaded:
            self._load_config()

        return dict(self._defaults)

    def get_profile(self, env: str) -> Optional[dict[str, Any]]:
        """
        Get a specific environment profile.

        Args:
            env: Environment name

        Returns:
            Profile dict or None if not found
        """
        if not self._loaded:
            self._load_config()

        return self._profiles.get(env)

    def get_all_profiles(self) -> dict[str, dict[str, Any]]:
        """
        Get all environment profiles.

        Returns:
            Dictionary of environment name to profile
        """
        if not self._loaded:
            self._load_config()

        return dict(self._profiles)

    def get_audit_policy(self) -> dict[str, Any]:
        """
        Get audit policy configuration.

        Returns:
            Dictionary of audit policy settings
        """
        if not self._loaded:
            self._load_config()

        return dict(self._audit_policy)

    def create_disabled_evidence(
        self,
        flag_name: str,
        run_id: Optional[str] = None,
        additional_context: Optional[dict] = None,
    ) -> FeatureFlagEvidence:
        """
        Create evidence record for a disabled flag that blocked execution.

        Per SEEDS P1-8 constraint:
        "开关关闭时要有可审计 evidence（不静默）"

        Args:
            flag_name: Name of the disabled flag
            run_id: Optional run ID for correlation
            additional_context: Optional additional context

        Returns:
            FeatureFlagEvidence record for audit trail
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        uid = uuid.uuid4().hex[:8].upper()

        if run_id is None:
            run_id = f"AUTO-{int(time.time())}-{uid}"

        issue_key = f"FEATURE-DISABLED-{flag_name.upper()}-{uid}"
        source_locator = f"feature_flag://{flag_name}?env={self.environment}"

        # Build evidence content for hash
        content = {
            "flag_name": flag_name,
            "enabled": False,
            "environment": self.environment,
            "run_id": run_id,
            "timestamp": timestamp,
        }
        if additional_context:
            content["additional_context"] = additional_context

        content_str = str(sorted(content.items()))
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()[:16]

        return FeatureFlagEvidence(
            issue_key=issue_key,
            source_locator=source_locator,
            content_hash=content_hash,
            timestamp=timestamp,
            flag_name=flag_name,
            enabled=False,
            action_taken="BLOCKED_BY_DISABLED_FLAG",
            reason=f"Feature '{flag_name}' is disabled in '{self.environment}' environment.",
            environment=self.environment,
            run_id=run_id,
            additional_context=additional_context or {},
        )

    def check_with_evidence(
        self,
        flag_name: str,
        run_id: Optional[str] = None,
        default: bool = False,
    ) -> FeatureFlagResult:
        """
        Check flag and return result with evidence if disabled.

        This is the recommended method for gates that need auditable evidence.

        Args:
            flag_name: Name of the feature flag
            run_id: Optional run ID for correlation
            default: Default value if flag cannot be determined

        Returns:
            FeatureFlagResult with flag state and evidence (if disabled)
        """
        enabled = self.is_enabled(flag_name, default=default)

        # Determine source
        if not self._loaded:
            self._load_config()

        if self.environment in self._profiles and flag_name in self._flags:
            source = "profile"
        elif flag_name in self._defaults:
            source = "default"
        elif self._load_error:
            source = "error"
        else:
            source = "default"

        # Create evidence if disabled
        evidence = None
        if not enabled:
            evidence = self.create_disabled_evidence(flag_name, run_id)

        return FeatureFlagResult(
            flag_name=flag_name,
            enabled=enabled,
            source=source,
            environment=self.environment,
            evidence=evidence,
        )

    def reload(self) -> None:
        """Force reload configuration from file."""
        global _FLAGS_CACHE, _FLAGS_CACHE_TIMESTAMP
        cache_key = f"{self.config_path}:{self.environment}"
        if cache_key in _FLAGS_CACHE:
            del _FLAGS_CACHE[cache_key]
        if cache_key in _FLAGS_CACHE_TIMESTAMP:
            del _FLAGS_CACHE_TIMESTAMP[cache_key]
        self._loaded = False
        self._load_config(force_reload=True)


# ============================================================================
# Module-level convenience functions
# ============================================================================

# Global loader instance (lazy-initialized)
_loader: Optional[FeatureFlagLoader] = None


def get_loader(
    config_path: Optional[str] = None,
    environment: Optional[str] = None,
) -> FeatureFlagLoader:
    """
    Get or create the global feature flag loader.

    Args:
        config_path: Optional path to config file (only used on first call)
        environment: Optional environment override (only used on first call)

    Returns:
        FeatureFlagLoader instance
    """
    global _loader
    if _loader is None:
        _loader = FeatureFlagLoader(config_path, environment)
    return _loader


def is_enabled(flag_name: str, default: bool = False) -> bool:
    """
    Check if a feature flag is enabled for the current environment.

    Convenience function using the global loader.

    Args:
        flag_name: Name of the feature flag
        default: Default value if flag cannot be determined

    Returns:
        True if flag is enabled, False otherwise
    """
    return get_loader().is_enabled(flag_name, default=default)


def check_with_evidence(
    flag_name: str,
    run_id: Optional[str] = None,
    default: bool = False,
) -> FeatureFlagResult:
    """
    Check flag with evidence (recommended for gates).

    Convenience function using the global loader.

    Args:
        flag_name: Name of the feature flag
        run_id: Optional run ID for correlation
        default: Default value if flag cannot be determined

    Returns:
        FeatureFlagResult with flag state and evidence
    """
    return get_loader().check_with_evidence(flag_name, run_id, default)


def get_disabled_evidence(
    flag_name: str,
    run_id: Optional[str] = None,
) -> FeatureFlagEvidence:
    """
    Create evidence record for a disabled flag.

    Convenience function using the global loader.

    Args:
        flag_name: Name of the disabled flag
        run_id: Optional run ID for correlation

    Returns:
        FeatureFlagEvidence record
    """
    return get_loader().create_disabled_evidence(flag_name, run_id)


def get_all_flags() -> dict[str, Any]:
    """
    Get all feature flags for current environment.

    Convenience function using the global loader.

    Returns:
        Dictionary of flag names to values
    """
    return get_loader().get_all_flags()


def get_all_profiles() -> dict[str, dict[str, Any]]:
    """
    Get all environment profiles.

    Convenience function using the global loader.

    Returns:
        Dictionary of environment name to profile
    """
    return get_loader().get_all_profiles()


def reload_flags() -> None:
    """Reload all feature flags from configuration file."""
    global _FLAGS_CACHE, _FLAGS_CACHE_TIMESTAMP, _loader
    _FLAGS_CACHE = {}
    _FLAGS_CACHE_TIMESTAMP = {}
    if _loader is not None:
        _loader._loaded = False
        _loader.reload()
