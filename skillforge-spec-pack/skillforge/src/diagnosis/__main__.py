"""
Diagnosis Package for GM-SkillForge L4 Layer.

This package provides standardized diagnosis output following
the L4-N8N-CONTRACT-20260226-001 specification.
"""

from . import __init__ as diagnosis_module

# Re-export all public symbols
from .__init__ import (
    HealthStatus,
    CategoryName,
    CategoryStatus,
    Severity,
    Priority,
    EvidenceRef,
    Finding,
    Recommendation,
    Category,
    DiagnosisOutput,
    DiagnosisBuilder,
    create_diagnosis,
    validate_diagnosis,
)

__all__ = [
    "HealthStatus",
    "CategoryName",
    "CategoryStatus",
    "Severity",
    "Priority",
    "EvidenceRef",
    "Finding",
    "Recommendation",
    "Category",
    "DiagnosisOutput",
    "DiagnosisBuilder",
    "create_diagnosis",
    "validate_diagnosis",
]
