"""
Diagnosis Module for GM-SkillForge L4 Layer

This module provides standardized diagnosis output for skills,
following the L4-N8N-CONTRACT-20260226-001 specification.

Task: L4-03 - Diagnosis.json 标准输出（含 evidence_ref）
Executor: vs--cc3
"""

from __future__ import annotations

import json
import uuid
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional, List


# =============================================================================
# Enums
# =============================================================================
class HealthStatus(str, Enum):
    """Overall health status enumeration."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class CategoryName(str, Enum):
    """Diagnosis category enumeration."""
    CODE_QUALITY = "code_quality"
    TEST_COVERAGE = "test_coverage"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"


class CategoryStatus(str, Enum):
    """Category status enumeration."""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class Severity(str, Enum):
    """Finding severity enumeration."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Priority(str, Enum):
    """Recommendation priority enumeration."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# =============================================================================
# Evidence Reference
# =============================================================================
@dataclass
class EvidenceRef:
    """
    Evidence reference for traceability.

    Format: EV-{TYPE}-{SEQUENCE}-{HASH8}
    Types: DX (Diagnosis), AEV (AEV), MET (Metric), LOG (Log), ART (Artifact)
    """
    id: str
    kind: str  # FILE, SNIPPET, OUTPUT, METRIC, LOG
    locator: str  # Path or reference to the evidence
    description: str
    content_hash: Optional[str] = None

    @classmethod
    def generate(
        cls,
        evidence_type: str,
        sequence: int,
        kind: str,
        locator: str,
        description: str,
        content: Optional[str] = None
    ) -> "EvidenceRef":
        """Generate a new evidence reference with auto-generated ID."""
        hash_input = f"{evidence_type}-{sequence}-{locator}-{description}"
        hash8 = hashlib.sha256(hash_input.encode()).hexdigest()[:8].upper()
        evidence_id = f"EV-{evidence_type}-{sequence:03d}-{hash8}"

        content_hash = None
        if content:
            content_hash = hashlib.sha256(content.encode()).hexdigest()

        return cls(
            id=evidence_id,
            kind=kind,
            locator=locator,
            description=description,
            content_hash=content_hash
        )

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# =============================================================================
# Findings and Recommendations
# =============================================================================
@dataclass
class Finding:
    """A diagnostic finding with severity and evidence."""
    severity: Severity
    message: str
    evidence_ref: str  # EvidenceRef ID
    category: Optional[str] = None
    location: Optional[str] = None
    details: Optional[dict] = None

    def to_dict(self) -> dict:
        result = {
            "severity": self.severity.value,
            "message": self.message,
            "evidence_ref": self.evidence_ref,
        }
        if self.category:
            result["category"] = self.category
        if self.location:
            result["location"] = self.location
        if self.details:
            result["details"] = self.details
        return result


@dataclass
class Recommendation:
    """A recommendation with priority and supporting evidence."""
    priority: Priority
    action: str
    evidence_ref: str  # EvidenceRef ID
    impact: Optional[str] = None
    effort: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "priority": self.priority.value,
            "action": self.action,
            "evidence_ref": self.evidence_ref,
        }
        if self.impact:
            result["impact"] = self.impact
        if self.effort:
            result["effort"] = self.effort
        return result


# =============================================================================
# Category
# =============================================================================
@dataclass
class Category:
    """A diagnosis category with score and findings."""
    name: CategoryName
    status: CategoryStatus
    score: float
    findings: List[Finding] = field(default_factory=list)
    weight: float = 1.0

    def to_dict(self) -> dict:
        return {
            "name": self.name.value,
            "status": self.status.value,
            "score": self.score,
            "findings": [f.to_dict() for f in self.findings],
            "weight": self.weight,
        }


# =============================================================================
# Diagnosis Output
# =============================================================================
@dataclass
class DiagnosisOutput:
    """
    Standardized diagnosis output following L4-N8N-CONTRACT.

    Required fields:
    - diagnosis_id: Unique identifier (format: DX-L4-{sequence}-{hash8})
    - skill_id: Associated skill ID
    - overall_health: Health status enum
    - health_score: Score 0-100
    - categories: List of diagnostic categories
    - evidence_refs: List of evidence references
    """
    diagnosis_id: str
    skill_id: str
    overall_health: HealthStatus
    health_score: float
    categories: List[Category]
    evidence_refs: List[EvidenceRef]
    skill_name: Optional[str] = None
    recommendations: List[Recommendation] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "diagnosis_id": self.diagnosis_id,
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "overall_health": self.overall_health.value,
            "health_score": self.health_score,
            "categories": [c.to_dict() for c in self.categories],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "generated_at": self.generated_at,
            "metadata": self.metadata,
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "DiagnosisOutput":
        """Deserialize from dictionary."""
        categories = [
            Category(
                name=CategoryName(c["name"]),
                status=CategoryStatus(c["status"]),
                score=c["score"],
                findings=[
                    Finding(
                        severity=Severity(f["severity"]),
                        message=f["message"],
                        evidence_ref=f["evidence_ref"],
                        category=f.get("category"),
                        location=f.get("location"),
                        details=f.get("details"),
                    )
                    for f in c.get("findings", [])
                ],
                weight=c.get("weight", 1.0),
            )
            for c in data.get("categories", [])
        ]

        evidence_refs = [
            EvidenceRef(
                id=e["id"],
                kind=e["kind"],
                locator=e["locator"],
                description=e["description"],
                content_hash=e.get("content_hash"),
            )
            for e in data.get("evidence_refs", [])
        ]

        recommendations = [
            Recommendation(
                priority=Priority(r["priority"]),
                action=r["action"],
                evidence_ref=r["evidence_ref"],
                impact=r.get("impact"),
                effort=r.get("effort"),
            )
            for r in data.get("recommendations", [])
        ]

        return cls(
            diagnosis_id=data["diagnosis_id"],
            skill_id=data["skill_id"],
            skill_name=data.get("skill_name"),
            overall_health=HealthStatus(data["overall_health"]),
            health_score=data["health_score"],
            categories=categories,
            evidence_refs=evidence_refs,
            recommendations=recommendations,
            generated_at=data.get("generated_at", datetime.utcnow().isoformat() + "Z"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Diagnosis Builder
# =============================================================================
class DiagnosisBuilder:
    """
    Builder for creating standardized Diagnosis outputs.

    Example:
        diagnosis = (DiagnosisBuilder()
            .with_skill("skill-001", "My Skill")
            .add_category(CategoryName.CODE_QUALITY, CategoryStatus.PASS, 85)
            .add_finding(CategoryName.CODE_QUALITY, Severity.INFO, "Code looks good", "EV-DX-001-ABC12345")
            .build())
    """

    def __init__(self):
        self._skill_id: Optional[str] = None
        self._skill_name: Optional[str] = None
        self._categories: List[Category] = []
        self._evidence_refs: List[EvidenceRef] = []
        self._recommendations: List[Recommendation] = []
        self._metadata: dict = {}
        self._sequence: int = 1

    def with_skill(self, skill_id: str, skill_name: Optional[str] = None) -> "DiagnosisBuilder":
        """Set the skill ID and name."""
        self._skill_id = skill_id
        self._skill_name = skill_name
        return self

    def with_metadata(self, metadata: dict) -> "DiagnosisBuilder":
        """Set metadata."""
        self._metadata = metadata
        return self

    def add_category(
        self,
        name: CategoryName,
        status: CategoryStatus,
        score: float,
        weight: float = 1.0
    ) -> "DiagnosisBuilder":
        """Add a diagnostic category."""
        self._categories.append(Category(
            name=name,
            status=status,
            score=score,
            findings=[],
            weight=weight,
        ))
        return self

    def add_finding(
        self,
        category_name: CategoryName,
        severity: Severity,
        message: str,
        evidence_ref: str,
        location: Optional[str] = None,
        details: Optional[dict] = None
    ) -> "DiagnosisBuilder":
        """Add a finding to a category."""
        finding = Finding(
            severity=severity,
            message=message,
            evidence_ref=evidence_ref,
            category=category_name.value,
            location=location,
            details=details,
        )

        for cat in self._categories:
            if cat.name == category_name:
                cat.findings.append(finding)
                break

        return self

    def add_evidence_ref(
        self,
        kind: str,
        locator: str,
        description: str,
        content: Optional[str] = None
    ) -> "DiagnosisBuilder":
        """Add an evidence reference and return its ID."""
        ev = EvidenceRef.generate(
            evidence_type="DX",
            sequence=self._sequence,
            kind=kind,
            locator=locator,
            description=description,
            content=content,
        )
        self._sequence += 1
        self._evidence_refs.append(ev)
        return self

    def add_recommendation(
        self,
        priority: Priority,
        action: str,
        evidence_ref: str,
        impact: Optional[str] = None,
        effort: Optional[str] = None
    ) -> "DiagnosisBuilder":
        """Add a recommendation."""
        self._recommendations.append(Recommendation(
            priority=priority,
            action=action,
            evidence_ref=evidence_ref,
            impact=impact,
            effort=effort,
        ))
        return self

    def _calculate_overall_health(self) -> HealthStatus:
        """Calculate overall health based on categories."""
        if not self._categories:
            return HealthStatus.UNKNOWN

        # Weighted average score
        total_weight = sum(c.weight for c in self._categories)
        weighted_score = sum(c.score * c.weight for c in self._categories) / total_weight

        # Check for any FAIL status
        for cat in self._categories:
            if cat.status == CategoryStatus.FAIL:
                return HealthStatus.CRITICAL

        # Check for WARN status
        for cat in self._categories:
            if cat.status == CategoryStatus.WARN:
                return HealthStatus.DEGRADED

        # Score-based determination
        if weighted_score >= 80:
            return HealthStatus.HEALTHY
        elif weighted_score >= 60:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.CRITICAL

    def _calculate_health_score(self) -> float:
        """Calculate health score based on categories."""
        if not self._categories:
            return 0.0

        total_weight = sum(c.weight for c in self._categories)
        weighted_score = sum(c.score * c.weight for c in self._categories) / total_weight
        return round(weighted_score, 2)

    def _generate_diagnosis_id(self) -> str:
        """Generate a unique diagnosis ID."""
        hash_input = f"{self._skill_id}-{datetime.utcnow().isoformat()}"
        hash8 = hashlib.sha256(hash_input.encode()).hexdigest()[:8].upper()
        return f"DX-L4-{self._sequence:03d}-{hash8}"

    def build(self) -> DiagnosisOutput:
        """Build the DiagnosisOutput."""
        if not self._skill_id:
            raise ValueError("skill_id is required")

        overall_health = self._calculate_overall_health()
        health_score = self._calculate_health_score()
        diagnosis_id = self._generate_diagnosis_id()

        return DiagnosisOutput(
            diagnosis_id=diagnosis_id,
            skill_id=self._skill_id,
            skill_name=self._skill_name,
            overall_health=overall_health,
            health_score=health_score,
            categories=self._categories,
            evidence_refs=self._evidence_refs,
            recommendations=self._recommendations,
            metadata=self._metadata,
        )


# =============================================================================
# Convenience Functions
# =============================================================================
def create_diagnosis(
    skill_id: str,
    skill_name: Optional[str] = None,
    categories: Optional[List[dict]] = None,
) -> DiagnosisOutput:
    """
    Create a diagnosis output from simplified inputs.

    Args:
        skill_id: Skill identifier
        skill_name: Optional skill name
        categories: List of category dicts with name, status, score

    Returns:
        DiagnosisOutput instance
    """
    builder = DiagnosisBuilder().with_skill(skill_id, skill_name)

    if categories:
        for cat in categories:
            builder.add_category(
                name=CategoryName(cat["name"]),
                status=CategoryStatus(cat["status"]),
                score=cat["score"],
                weight=cat.get("weight", 1.0),
            )

    return builder.build()


def validate_diagnosis(diagnosis: dict) -> List[str]:
    """
    Validate a diagnosis dictionary against the schema.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Check required fields
    required = ["diagnosis_id", "skill_id", "overall_health", "health_score", "categories", "evidence_refs"]
    for field in required:
        if field not in diagnosis:
            errors.append(f"Missing required field: {field}")

    # Validate diagnosis_id format
    if "diagnosis_id" in diagnosis:
        import re
        if not re.match(r"^DX-L4-[0-9]+-[A-Z0-9]{8}$", diagnosis["diagnosis_id"]):
            errors.append("diagnosis_id must match format: DX-L4-{sequence}-{hash8}")

    # Validate overall_health enum
    if "overall_health" in diagnosis:
        valid_statuses = ["HEALTHY", "DEGRADED", "CRITICAL", "UNKNOWN"]
        if diagnosis["overall_health"] not in valid_statuses:
            errors.append(f"overall_health must be one of: {valid_statuses}")

    # Validate health_score range
    if "health_score" in diagnosis:
        score = diagnosis["health_score"]
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            errors.append("health_score must be a number between 0 and 100")

    # Validate categories
    if "categories" in diagnosis:
        for i, cat in enumerate(diagnosis["categories"]):
            if "name" not in cat:
                errors.append(f"Category {i}: missing name")
            if "status" not in cat:
                errors.append(f"Category {i}: missing status")
            if "score" not in cat:
                errors.append(f"Category {i}: missing score")

    # Validate evidence_refs
    if "evidence_refs" in diagnosis:
        for i, ev in enumerate(diagnosis["evidence_refs"]):
            if "id" not in ev:
                errors.append(f"EvidenceRef {i}: missing id")
            if "kind" not in ev:
                errors.append(f"EvidenceRef {i}: missing kind")
            if "locator" not in ev:
                errors.append(f"EvidenceRef {i}: missing locator")

    return errors


# =============================================================================
# Exports
# =============================================================================
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
