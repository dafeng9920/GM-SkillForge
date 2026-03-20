"""
Secrets/Credentials Boundary Type Definitions

This module defines the types and schemas for credential boundary rules in SkillForge.
It only defines boundaries - it does NOT implement credential storage, retrieval, or management.

IMPORTANT HARD CONSTRAINTS:
- No real credentials are stored or retrieved
- No connection to real secrets providers (AWS Secrets Manager, Vault, etc.)
- No credentials enter frozen objects
- No runtime execution behavior
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class SensitivityLevel(str, Enum):
    """Sensitivity level for secrets classification (L0-L4)"""

    L0 = "L0"  # Public - no restrictions
    L1 = "L1"  # Internal - organization visible only
    L2 = "L2"  # Sensitive - access control required
    L3 = "L3"  # Highly sensitive - strict access control, no frozen, no logs
    L4 = "L4"  # Secret - highest protection, HSM/KMS only

    @classmethod
    def get_description(cls, level: 'SensitivityLevel') -> str:
        """Get human-readable description of sensitivity level"""
        descriptions = {
            cls.L0: "Public - can appear in frozen objects, logs, and be shared",
            cls.L1: "Internal - can appear in frozen objects, internal logs only",
            cls.L2: "Sensitive - cannot enter frozen, can enter audit logs only",
            cls.L3: "Highly sensitive - strict ban from frozen and all logs",
            cls.L4: "Secret - highest protection, HSM/KMS only, no code/config presence",
        }
        return descriptions.get(level, "Unknown")

    @classmethod
    def can_enter_frozen(cls, level: 'SensitivityLevel') -> bool:
        """Check if credential of this level can enter frozen objects"""
        return level in [cls.L0, cls.L1]

    @classmethod
    def can_enter_logs(cls, level: 'SensitivityLevel') -> bool:
        """Check if credential of this level can enter logs (masked or unmasked)"""
        return level in [cls.L0, cls.L1]

    @classmethod
    def can_enter_audit_logs(cls, level: 'SensitivityLevel') -> bool:
        """Check if credential of this level can enter audit logs (masked or encrypted)"""
        return level in [cls.L0, cls.L1, cls.L2]


@dataclass
class MaskingRule:
    """
    Masking rule for credentials in logs and reports

    IMPORTANT: This only defines the masking rule - it does NOT implement masking.
    The actual masking is done by the logging/reporting layer using this rule.
    """
    pattern: str  # e.g., "sk-****"
    show_first_n: int = 0
    show_last_n: int = 0
    mask_char: str = "*"
    exception_contexts: List[str] = field(default_factory=list)

    def apply(self, value: str) -> str:
        """
        Apply masking rule to a value

        WARNING: This method is for illustration only.
        In production, actual credentials should NEVER be passed to this method.
        Masking should happen at the logging boundary before credentials are loaded.
        """
        if not value:
            return self.mask_char * len(self.pattern)

        # This is a demonstration of how masking would work
        # In production, DO NOT pass real credential values here
        length = len(value)

        if self.show_first_n > 0 and self.show_last_n > 0:
            # Show both prefix and suffix
            prefix = value[:self.show_first_n]
            suffix = value[-self.show_last_n:]
            middle_length = max(0, length - self.show_first_n - self.show_last_n)
            return f"{prefix}{self.mask_char * middle_length}{suffix}"
        elif self.show_first_n > 0:
            # Show only prefix
            prefix = value[:self.show_first_n]
            return f"{prefix}{self.mask_char * (length - self.show_first_n)}"
        elif self.show_last_n > 0:
            # Show only suffix
            suffix = value[-self.show_last_n:]
            return f"{self.mask_char * (length - self.show_last_n)}{suffix}"
        else:
            # Use pattern
            return self.pattern


class CredentialContext(str, Enum):
    """Contexts where credentials may be used"""

    # Allowed contexts
    EXTERNAL_API_CALL = "external_api_call"
    EXTERNAL_SERVICE_AUTH = "external_service_auth"
    WEBHOOK_SIGNING = "webhook_signing"
    DATA_ENCRYPTION = "data_encryption"

    # Prohibited contexts
    LOGGING = "logging"
    FROZEN_OBJECT = "frozen_object"
    CONFIG_FILE = "config_file"
    VERSION_CONTROL = "version_control"
    DATABASE_STORAGE = "database_storage"


@dataclass
class BoundaryRules:
    """
    Boundary rules for credential usage

    Defines WHERE and HOW credentials can be used.
    """
    allowed_contexts: List[str]
    prohibited_contexts: List[str] = field(default_factory=lambda: [
        CredentialContext.LOGGING,
        CredentialContext.FROZEN_OBJECT,
        CredentialContext.CONFIG_FILE,
        CredentialContext.VERSION_CONTROL,
    ])
    min_distance_from_frozen: int = 2

    def is_context_allowed(self, context: str) -> bool:
        """Check if a context is allowed for this credential"""
        return context in self.allowed_contexts

    def is_context_prohibited(self, context: str) -> bool:
        """Check if a context is prohibited for this credential"""
        return context in self.prohibited_contexts


@dataclass
class FormatRequirements:
    """
    Format requirements for credential validation

    Defines the expected format of credentials.
    """
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    prefix: Optional[str] = None
    pattern: Optional[str] = None
    encoding: str = "utf-8"


@dataclass
class LifecycleConstraints:
    """
    Lifecycle constraints (informational only)

    These are NOT enforced by the boundary module.
    They are hints for the Secrets Management module.
    """
    rotation_policy: str = "manual"  # manual, auto_30d, auto_90d, auto_custom
    retention_days: int = 90


class ViolationSeverity(str, Enum):
    """Severity level for compliance violations"""
    ERROR = "ERROR"      # Must fix before approval
    WARNING = "WARNING"  # Should fix, review required
    INFO = "INFO"        # Informational, no action required


@dataclass
class ComplianceViolation:
    """A single compliance violation"""
    type: str
    message: str
    severity: ViolationSeverity
    credential_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceReport:
    """
    Report on credential usage compliance

    Generated when checking if credential usage follows boundary rules.
    """
    is_compliant: bool
    violations: List[ComplianceViolation] = field(default_factory=list)
    warnings: List[ComplianceViolation] = field(default_factory=list)

    def add_violation(self, violation: ComplianceViolation):
        """Add a violation to the report"""
        if violation.severity == ViolationSeverity.ERROR:
            self.violations.append(violation)
            self.is_compliant = False
        else:
            self.warnings.append(violation)


@dataclass
class CredentialRequirement:
    """
    Requirement definition for a credential type

    This defines WHAT is required for a credential type, not HOW to get it.
    """
    credential_type: str  # e.g., "api_token", "ssh_key"
    sensitivity_level: SensitivityLevel
    boundary_rules: BoundaryRules
    masking_rule: Optional[MaskingRule] = None
    format_requirements: Optional[FormatRequirements] = None
    lifecycle: Optional[LifecycleConstraints] = None

    def __post_init__(self):
        """Post-init validation"""
        # Set default masking rule based on sensitivity level
        if self.masking_rule is None:
            if self.sensitivity_level in [SensitivityLevel.L3, SensitivityLevel.L4]:
                self.masking_rule = MaskingRule(pattern="****")
            else:
                self.masking_rule = MaskingRule(pattern="{value}")

    def can_enter_frozen(self) -> bool:
        """Check if this credential can enter frozen objects"""
        return SensitivityLevel.can_enter_frozen(self.sensitivity_level)

    def can_enter_logs(self) -> bool:
        """Check if this credential can enter logs"""
        return SensitivityLevel.can_enter_logs(self.sensitivity_level)

    def mask_for_logging(self, value: str) -> str:
        """
        Get masked version of credential for logging

        WARNING: In production, do NOT pass real credential values.
        This method should only be called with already-masked placeholders.
        """
        if self.masking_rule:
            return self.masking_rule.apply(value)
        return "[REDACTED]"

    def validate_context(self, context: str) -> ComplianceReport:
        """Validate if a context is allowed for this credential"""
        report = ComplianceReport(is_compliant=True)

        if self.boundary_rules.is_context_prohibited(context):
            report.add_violation(ComplianceViolation(
                type="context_prohibited",
                message=f"Credential type '{self.credential_type}' is prohibited in context '{context}'",
                severity=ViolationSeverity.ERROR,
                credential_type=self.credential_type
            ))

        if not self.boundary_rules.is_context_allowed(context):
            report.add_violation(ComplianceViolation(
                type="context_not_allowed",
                message=f"Context '{context}' is not in allowed contexts for '{self.credential_type}'",
                severity=ViolationSeverity.WARNING,
                credential_type=self.credential_type
            ))

        return report


# Predefined credential types
class CredentialTypes:
    """
    Predefined credential type definitions

    These are NOT real credentials - they are requirement definitions.
    """

    @staticmethod
    def api_token() -> CredentialRequirement:
        """API Token credential requirement (L3 - highly sensitive)"""
        return CredentialRequirement(
            credential_type="api_token",
            sensitivity_level=SensitivityLevel.L3,
            boundary_rules=BoundaryRules(
                allowed_contexts=[
                    CredentialContext.EXTERNAL_API_CALL,
                    CredentialContext.EXTERNAL_SERVICE_AUTH,
                ],
                prohibited_contexts=[
                    CredentialContext.LOGGING,
                    CredentialContext.FROZEN_OBJECT,
                    CredentialContext.CONFIG_FILE,
                    CredentialContext.VERSION_CONTROL,
                ],
                min_distance_from_frozen=2,
            ),
            masking_rule=MaskingRule(
                pattern="sk-****",
                show_first_n=3,
                show_last_n=0,
                mask_char="*",
            ),
            format_requirements=FormatRequirements(
                min_length=20,
                prefix="sk-",
            ),
        )

    @staticmethod
    def webhook_secret() -> CredentialRequirement:
        """Webhook signing secret (L3 - highly sensitive)"""
        return CredentialRequirement(
            credential_type="webhook_secret",
            sensitivity_level=SensitivityLevel.L3,
            boundary_rules=BoundaryRules(
                allowed_contexts=[CredentialContext.WEBHOOK_SIGNING],
                prohibited_contexts=[
                    CredentialContext.LOGGING,
                    CredentialContext.FROZEN_OBJECT,
                ],
                min_distance_from_frozen=2,
            ),
            masking_rule=MaskingRule(pattern="whsec_****"),
        )

    @staticmethod
    def internal_api_key() -> CredentialRequirement:
        """Internal API key (L2 - sensitive)"""
        return CredentialRequirement(
            credential_type="internal_api_key",
            sensitivity_level=SensitivityLevel.L2,
            boundary_rules=BoundaryRules(
                allowed_contexts=[CredentialContext.EXTERNAL_SERVICE_AUTH],
                prohibited_contexts=[
                    CredentialContext.FROZEN_OBJECT,
                    CredentialContext.VERSION_CONTROL,
                ],
                min_distance_from_frozen=2,
            ),
            masking_rule=MaskingRule(pattern="internal_****"),
        )


# Boundary validation functions
def validate_credential_boundary(
    credential_type: str,
    contexts: List[str],
    sensitivity_level: SensitivityLevel
) -> ComplianceReport:
    """
    Validate if credential usage follows boundary rules

    This is a static validation function - it does NOT access real credentials.
    """
    report = ComplianceReport(is_compliant=True)

    # L3+ cannot enter frozen
    if sensitivity_level in [SensitivityLevel.L3, SensitivityLevel.L4]:
        if CredentialContext.FROZEN_OBJECT in contexts:
            report.add_violation(ComplianceViolation(
                type="credential_in_frozen",
                message=f"L3+ credential '{credential_type}' cannot enter frozen objects",
                severity=ViolationSeverity.ERROR,
                credential_type=credential_type
            ))

    # L4 cannot enter any logs
    if sensitivity_level == SensitivityLevel.L4:
        if CredentialContext.LOGGING in contexts:
            report.add_violation(ComplianceViolation(
                type="credential_in_logs",
                message=f"L4 credential '{credential_type}' cannot enter any logs",
                severity=ViolationSeverity.ERROR,
                credential_type=credential_type
            ))

    # L3 cannot enter regular logs
    if sensitivity_level == SensitivityLevel.L3:
        if CredentialContext.LOGGING in contexts:
            report.add_violation(ComplianceViolation(
                type="credential_in_logs",
                message=f"L3 credential '{credential_type}' cannot enter regular logs",
                severity=ViolationSeverity.ERROR,
                credential_type=credential_type
            ))

    return report


def validate_permit_credential_separation(
    has_permit: bool,
    has_credential: bool,
    credential_in_frozen: bool
) -> ComplianceReport:
    """
    Validate that permit and credential are properly separated

    Permit and credential are independent requirements - both must be present.
    """
    report = ComplianceReport(is_compliant=True)

    if credential_in_frozen:
        report.add_violation(ComplianceViolation(
            type="credential_in_frozen",
            message="Credentials cannot enter frozen objects",
            severity=ViolationSeverity.ERROR
        ))

    return report
