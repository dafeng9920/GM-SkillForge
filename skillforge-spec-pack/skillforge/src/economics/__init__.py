"""
Economics Module for GM-SkillForge L4 Layer

This module provides Asset Economic Value (AEV) calculation for skills,
following the L4-N8N-CONTRACT-20260226-001 specification.

Task: L4-04 - AEV 计算模块接入（四象限）
Executor: Kior-B
Model: gpt-5.1-mini
"""

from __future__ import annotations

import json
import uuid
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional, List, Dict


# =============================================================================
# Enums
# =============================================================================
class Currency(str, Enum):
    """Currency enumeration for AEV calculations."""
    USD = "USD"
    EUR = "EUR"
    CNY = "CNY"


class Period(str, Enum):
    """Time period enumeration for AEV calculations."""
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class EvidenceType(str, Enum):
    """Evidence reference type enumeration."""
    DIAGNOSIS = "diagnosis"
    METRIC = "metric"
    LOG = "log"
    ARTIFACT = "artifact"
    REPORT = "report"
    SIGNATURE = "signature"


# =============================================================================
# Evidence Reference
# =============================================================================
@dataclass
class EvidenceRef:
    """
    Evidence reference for AEV traceability.

    Format: EV-{TYPE}-{SEQUENCE}-{HASH8}
    Types: DX (Diagnosis), AEV (AEV), MET (Metric), LOG (Log), ART (Artifact)
    """
    ref_id: str
    type: EvidenceType
    source_locator: str
    content_hash: str
    timestamp: str

    @classmethod
    def generate(
        cls,
        evidence_type: str,
        sequence: int,
        ev_type: EvidenceType,
        locator: str,
        content: Optional[str] = None
    ) -> "EvidenceRef":
        """Generate a new evidence reference with auto-generated ID."""
        hash_input = f"{evidence_type}-{sequence}-{locator}"
        hash8 = hashlib.sha256(hash_input.encode()).hexdigest()[:8].upper()
        evidence_id = f"EV-{evidence_type}-{sequence:03d}-{hash8}"

        content_hash = ""
        if content:
            content_hash = hashlib.sha256(content.encode()).hexdigest()
        else:
            content_hash = hashlib.sha256(locator.encode()).hexdigest()[:16]

        return cls(
            ref_id=evidence_id,
            type=ev_type,
            source_locator=locator,
            content_hash=content_hash,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    def to_dict(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "type": self.type.value,
            "source_locator": self.source_locator,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp
        }


# =============================================================================
# Confidence Interval
# =============================================================================
@dataclass
class ConfidenceInterval:
    """
    Confidence interval for AEV calculations.

    Provides statistical bounds for calculated values.
    """
    lower: float
    upper: float
    confidence_level: float  # e.g., 0.95 for 95% confidence

    def to_dict(self) -> dict:
        return {
            "lower": self.lower,
            "upper": self.upper,
            "confidence_level": self.confidence_level
        }


# =============================================================================
# AEV Component
# =============================================================================
@dataclass
class AEVComponent:
    """
    A single component of AEV calculation.

    Formula: AEV = V_token + V_compute + V_risk + V_trust
    """
    value: float
    description: str
    evidence_ref: str
    source_description: str  # Where this value comes from
    calculation_method: str  # How this value is calculated

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "description": self.description,
            "evidence_ref": self.evidence_ref,
            "source_description": self.source_description,
            "calculation_method": self.calculation_method
        }


# =============================================================================
# AEV Output
# =============================================================================
@dataclass
class AEVOutput:
    """
    Standardized AEV output following L4-N8N-CONTRACT.

    Required fields:
    - aev_id: Unique identifier (format: AEV-L4-{sequence}-{hash8})
    - skill_id: Associated skill ID
    - diagnosis_id: Related diagnosis ID
    - aev_total: Total economic value with confidence interval
    - components: Four quadrants (V_token, V_compute, V_risk, V_trust)
    - evidence_refs: List of evidence references
    """
    aev_id: str
    skill_id: str
    diagnosis_id: str
    aev_total: float
    confidence_interval: ConfidenceInterval
    currency: Currency
    period: Period
    components: Dict[str, AEVComponent]
    evidence_refs: List[EvidenceRef]
    skill_name: Optional[str] = None
    formula: str = "AEV = V_token + V_compute + V_risk + V_trust"
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "aev_id": self.aev_id,
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "diagnosis_id": self.diagnosis_id,
            "aev_total": self.aev_total,
            "confidence_interval": self.confidence_interval.to_dict(),
            "currency": self.currency.value,
            "period": self.period.value,
            "components": {
                k: v.to_dict() for k, v in self.components.items()
            },
            "formula": self.formula,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "generated_at": self.generated_at,
            "metadata": self.metadata,
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "AEVOutput":
        """Deserialize from dictionary."""
        components = {
            k: AEVComponent(
                value=v["value"],
                description=v["description"],
                evidence_ref=v["evidence_ref"],
                source_description=v.get("source_description", ""),
                calculation_method=v.get("calculation_method", "")
            )
            for k, v in data.get("components", {}).items()
        }

        ci_data = data.get("confidence_interval", {})
        confidence_interval = ConfidenceInterval(
            lower=ci_data.get("lower", 0.0),
            upper=ci_data.get("upper", 0.0),
            confidence_level=ci_data.get("confidence_level", 0.95)
        )

        evidence_refs = [
            EvidenceRef(
                ref_id=e["ref_id"],
                type=EvidenceType(e["type"]),
                source_locator=e["source_locator"],
                content_hash=e["content_hash"],
                timestamp=e.get("timestamp", datetime.utcnow().isoformat() + "Z")
            )
            for e in data.get("evidence_refs", [])
        ]

        return cls(
            aev_id=data["aev_id"],
            skill_id=data["skill_id"],
            skill_name=data.get("skill_name"),
            diagnosis_id=data["diagnosis_id"],
            aev_total=data["aev_total"],
            confidence_interval=confidence_interval,
            currency=Currency(data.get("currency", "USD")),
            period=Period(data.get("period", "year")),
            components=components,
            formula=data.get("formula", "AEV = V_token + V_compute + V_risk + V_trust"),
            evidence_refs=evidence_refs,
            generated_at=data.get("generated_at", datetime.utcnow().isoformat() + "Z"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# AEV Builder
# =============================================================================
class AEVBuilder:
    """
    Builder for creating standardized AEV outputs.

    Example:
        aev = (AEVBuilder()
            .with_skill("skill-001", "My Skill", "DX-L4-001-ABC12345")
            .set_v_token(10000, "Token staking rewards", "EV-AEV-001-...")
            .set_v_compute(5000, "Compute cost savings", "EV-AEV-002-...")
            .set_v_risk(2000, "Risk mitigation value", "EV-AEV-003-...")
            .set_v_trust(3000, "Trust score premium", "EV-AEV-004-...")
            .build())
    """

    def __init__(self):
        self._skill_id: Optional[str] = None
        self._skill_name: Optional[str] = None
        self._diagnosis_id: Optional[str] = None
        self._components: Dict[str, AEVComponent] = {}
        self._evidence_refs: List[EvidenceRef] = []
        self._metadata: dict = {}
        self._sequence: int = 1
        self._currency: Currency = Currency.USD
        self._period: Period = Period.YEAR

    def with_skill(
        self,
        skill_id: str,
        skill_name: Optional[str] = None,
        diagnosis_id: Optional[str] = None
    ) -> "AEVBuilder":
        """Set the skill ID, name, and related diagnosis ID."""
        self._skill_id = skill_id
        self._skill_name = skill_name
        self._diagnosis_id = diagnosis_id
        return self

    def with_currency(self, currency: Currency) -> "AEVBuilder":
        """Set the currency for AEV calculation."""
        self._currency = currency
        return self

    def with_period(self, period: Period) -> "AEVBuilder":
        """Set the time period for AEV calculation."""
        self._period = period
        return self

    def with_metadata(self, metadata: dict) -> "AEVBuilder":
        """Set metadata."""
        self._metadata = metadata
        return self

    def _add_component(
        self,
        name: str,
        value: float,
        description: str,
        source_description: str,
        calculation_method: str
    ) -> "AEVBuilder":
        """Add an AEV component and generate its evidence reference."""
        ev = EvidenceRef.generate(
            evidence_type="AEV",
            sequence=self._sequence,
            ev_type=EvidenceType.METRIC,
            locator=f"aev.{name}",
        )
        self._sequence += 1
        self._evidence_refs.append(ev)

        self._components[name] = AEVComponent(
            value=value,
            description=description,
            evidence_ref=ev.ref_id,
            source_description=source_description,
            calculation_method=calculation_method
        )
        return self

    def set_v_token(
        self,
        value: float,
        description: str = "",
        source_description: str = "",
        calculation_method: str = ""
    ) -> "AEVBuilder":
        """
        Set V_token - Token economic value component.

        Sources:
        - Staking rewards from protocol
        - Token appreciation from demand
        - Governance token value
        - Liquidity mining rewards
        """
        if not description:
            description = "Token staking and governance rewards"
        if not source_description:
            source_description = "Protocol staking APR * staked amount"
        if not calculation_method:
            calculation_method = "V_token = (staking_reward_rate * staked_tokens * token_price) + governance_value"

        return self._add_component("v_token", value, description, source_description, calculation_method)

    def set_v_compute(
        self,
        value: float,
        description: str = "",
        source_description: str = "",
        calculation_method: str = ""
    ) -> "AEVBuilder":
        """
        Set V_compute - Computational value component.

        Sources:
        - Compute cost savings from optimized execution
        - Resource utilization efficiency
        - Parallel processing gains
        - Caching and optimization benefits
        """
        if not description:
            description = "Compute resource optimization value"
        if not source_description:
            source_description = "Execution metrics * cost per compute unit"
        if not calculation_method:
            calculation_method = "V_compute = (execution_count * cost_per_unit) * efficiency_multiplier"

        return self._add_component("v_compute", value, description, source_description, calculation_method)

    def set_v_risk(
        self,
        value: float,
        description: str = "",
        source_description: str = "",
        calculation_method: str = ""
    ) -> "AEVBuilder":
        """
        Set V_risk - Risk mitigation value component.

        Sources:
        - Failure rate reduction
        - Security vulnerability prevention
        - Compliance cost avoidance
        - Downtime prevention
        """
        if not description:
            description = "Risk mitigation and security value"
        if not source_description:
            source_description = "Risk exposure * probability * mitigation_factor"
        if not calculation_method:
            calculation_method = "V_risk = (incident_probability * incident_cost) * (1 - failure_rate)"

        return self._add_component("v_risk", value, description, source_description, calculation_method)

    def set_v_trust(
        self,
        value: float,
        description: str = "",
        source_description: str = "",
        calculation_method: str = ""
    ) -> "AEVBuilder":
        """
        Set V_trust - Trust and reputation value component.

        Sources:
        - User rating premium
        - Reputation score bonus
        - Community trust value
        - Brand value enhancement
        """
        if not description:
            description = "Trust score and reputation value"
        if not source_description:
            source_description = "Trust score * user_base * trust_multiplier"
        if not calculation_method:
            calculation_method = "V_trust = (trust_score * user_count * premium_rate) + reputation_bonus"

        return self._add_component("v_trust", value, description, source_description, calculation_method)

    def _calculate_confidence_interval(self, total: float) -> ConfidenceInterval:
        """
        Calculate confidence interval based on component variance.

        Uses a simplified variance propagation model.
        """
        # Assumptions for MVP:
        # - 10% variance for V_token (market volatility)
        # - 5% variance for V_compute (usage predictability)
        # - 15% variance for V_risk (uncertainty in incidents)
        # - 5% variance for V_trust (user behavior)

        variances = {
            "v_token": 0.10,
            "v_compute": 0.05,
            "v_risk": 0.15,
            "v_trust": 0.05
        }

        weighted_variance = 0.0
        for name, component in self._components.items():
            variance = variances.get(name, 0.10)
            weighted_variance += (component.value * variance) ** 2

        std_dev = (weighted_variance ** 0.5) if weighted_variance > 0 else total * 0.08

        return ConfidenceInterval(
            lower=max(0, total - 1.96 * std_dev),  # 95% CI
            upper=total + 1.96 * std_dev,
            confidence_level=0.95
        )

    def _generate_aev_id(self) -> str:
        """Generate a unique AEV ID."""
        hash_input = f"{self._skill_id}-{self._diagnosis_id}-{datetime.utcnow().isoformat()}"
        hash8 = hashlib.sha256(hash_input.encode()).hexdigest()[:8].upper()
        return f"AEV-L4-{self._sequence:03d}-{hash8}"

    def build(self) -> AEVOutput:
        """Build the AEVOutput."""
        if not self._skill_id:
            raise ValueError("skill_id is required")

        # Calculate total
        aev_total = sum(c.value for c in self._components.values())

        # Generate confidence interval
        confidence_interval = self._calculate_confidence_interval(aev_total)

        # Generate AEV ID
        aev_id = self._generate_aev_id()

        return AEVOutput(
            aev_id=aev_id,
            skill_id=self._skill_id,
            skill_name=self._skill_name,
            diagnosis_id=self._diagnosis_id or "",
            aev_total=aev_total,
            confidence_interval=confidence_interval,
            currency=self._currency,
            period=self._period,
            components=self._components,
            evidence_refs=self._evidence_refs,
            metadata=self._metadata,
        )


# =============================================================================
# Convenience Functions
# =============================================================================
def create_aev(
    skill_id: str,
    diagnosis_id: str,
    v_token: float = 0.0,
    v_compute: float = 0.0,
    v_risk: float = 0.0,
    v_trust: float = 0.0,
    currency: Currency = Currency.USD,
    period: Period = Period.YEAR,
    skill_name: Optional[str] = None,
) -> AEVOutput:
    """
    Create an AEV output from simplified inputs.

    Args:
        skill_id: Skill identifier
        diagnosis_id: Related diagnosis ID
        v_token: Token economic value
        v_compute: Computational value
        v_risk: Risk mitigation value
        v_trust: Trust and reputation value
        currency: Currency for values
        period: Time period
        skill_name: Optional skill name

    Returns:
        AEVOutput instance
    """
    builder = AEVBuilder().with_skill(skill_id, skill_name, diagnosis_id)
    builder.with_currency(currency).with_period(period)

    if v_token > 0:
        builder.set_v_token(v_token)
    if v_compute > 0:
        builder.set_v_compute(v_compute)
    if v_risk > 0:
        builder.set_v_risk(v_risk)
    if v_trust > 0:
        builder.set_v_trust(v_trust)

    return builder.build()


def validate_aev(aev: dict) -> List[str]:
    """
    Validate an AEV dictionary against the schema.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Check required fields
    required = ["aev_id", "skill_id", "diagnosis_id", "aev_total", "currency", "period", "components", "evidence_refs"]
    for field in required:
        if field not in aev:
            errors.append(f"Missing required field: {field}")

    # Validate aev_id format
    if "aev_id" in aev:
        import re
        if not re.match(r"^AEV-L4-[0-9]+-[A-Z0-9]{8}$", aev["aev_id"]):
            errors.append("aev_id must match format: AEV-L4-{sequence}-{hash8}")

    # Validate aev_total
    if "aev_total" in aev:
        total = aev["aev_total"]
        if not isinstance(total, (int, float)) or total < 0:
            errors.append("aev_total must be a non-negative number")

    # Validate confidence_interval
    if "confidence_interval" in aev:
        ci = aev["confidence_interval"]
        if "lower" not in ci or "upper" not in ci or "confidence_level" not in ci:
            errors.append("confidence_interval must have lower, upper, confidence_level")

    # Validate components
    if "components" in aev:
        required_components = ["v_token", "v_compute", "v_risk", "v_trust"]
        for comp in required_components:
            if comp not in aev["components"]:
                errors.append(f"Missing required component: {comp}")

    # Validate evidence_refs
    if "evidence_refs" in aev:
        for i, ev in enumerate(aev["evidence_refs"]):
            if "ref_id" not in ev:
                errors.append(f"EvidenceRef {i}: missing ref_id")
            if "type" not in ev:
                errors.append(f"EvidenceRef {i}: missing type")
            if "source_locator" not in ev:
                errors.append(f"EvidenceRef {i}: missing source_locator")

    return errors


# =============================================================================
# Exports
# =============================================================================
__all__ = [
    "Currency",
    "Period",
    "EvidenceType",
    "EvidenceRef",
    "ConfidenceInterval",
    "AEVComponent",
    "AEVOutput",
    "AEVBuilder",
    "create_aev",
    "validate_aev",
]
