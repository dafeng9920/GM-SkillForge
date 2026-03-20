"""
Secrets/Credentials Boundary Submodule

This module defines the boundary rules for secrets and credentials in SkillForge's
external execution and integration preparation layer.

HARD CONSTRAINTS:
- No real credential storage or retrieval
- No connection to real secrets providers
- No credentials enter frozen objects
- No runtime execution behavior
"""

from .credential_boundary_types import (
    SensitivityLevel,
    MaskingRule,
    CredentialContext,
    BoundaryRules,
    FormatRequirements,
    LifecycleConstraints,
    ViolationSeverity,
    ComplianceViolation,
    ComplianceReport,
    CredentialRequirement,
    CredentialTypes,
    validate_credential_boundary,
    validate_permit_credential_separation,
)

__all__ = [
    "SensitivityLevel",
    "MaskingRule",
    "CredentialContext",
    "BoundaryRules",
    "FormatRequirements",
    "LifecycleConstraints",
    "ViolationSeverity",
    "ComplianceViolation",
    "ComplianceReport",
    "CredentialRequirement",
    "CredentialTypes",
    "validate_credential_boundary",
    "validate_permit_credential_separation",
]
