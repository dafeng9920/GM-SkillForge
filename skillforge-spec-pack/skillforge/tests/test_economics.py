"""
Tests for Economics Module (AEV Calculation)

Task: L4-04 - AEV 计算模块接入（四象限）
Executor: Kior-B
Model: gpt-5.1-mini
"""

import pytest
from skillforge.src.economics import (
    Currency,
    Period,
    EvidenceType,
    EvidenceRef,
    ConfidenceInterval,
    AEVComponent,
    AEVOutput,
    AEVBuilder,
    create_aev,
    validate_aev,
)


class TestEnums:
    """Test enum definitions."""

    def test_currency_values(self):
        assert Currency.USD.value == "USD"
        assert Currency.EUR.value == "EUR"
        assert Currency.CNY.value == "CNY"

    def test_period_values(self):
        assert Period.MONTH.value == "month"
        assert Period.QUARTER.value == "quarter"
        assert Period.YEAR.value == "year"

    def test_evidence_type_values(self):
        assert EvidenceType.DIAGNOSIS.value == "diagnosis"
        assert EvidenceType.METRIC.value == "metric"
        assert EvidenceType.LOG.value == "log"


class TestEvidenceRef:
    """Test EvidenceRef generation and serialization."""

    def test_generate_evidence_ref(self):
        ev = EvidenceRef.generate(
            evidence_type="AEV",
            sequence=1,
            ev_type=EvidenceType.METRIC,
            locator="aev.v_token"
        )
        assert ev.ref_id.startswith("EV-AEV-001-")
        assert len(ev.ref_id) == 19  # EV-AEV-001- (11) + 8 char hash = 19
        assert ev.type == EvidenceType.METRIC
        assert ev.source_locator == "aev.v_token"
        assert len(ev.content_hash) == 16

    def test_evidence_ref_to_dict(self):
        ev = EvidenceRef(
            ref_id="EV-AEV-001-A1B2C3D4",
            type=EvidenceType.METRIC,
            source_locator="aev.v_token",
            content_hash="a1b2c3d4e5f6",
            timestamp="2026-02-26T10:00:00Z"
        )
        data = ev.to_dict()
        assert data["ref_id"] == "EV-AEV-001-A1B2C3D4"
        assert data["type"] == "metric"
        assert data["source_locator"] == "aev.v_token"
        assert data["content_hash"] == "a1b2c3d4e5f6"
        assert data["timestamp"] == "2026-02-26T10:00:00Z"


class TestConfidenceInterval:
    """Test ConfidenceInterval."""

    def test_confidence_interval_to_dict(self):
        ci = ConfidenceInterval(lower=45000, upper=55000, confidence_level=0.95)
        data = ci.to_dict()
        assert data["lower"] == 45000
        assert data["upper"] == 55000
        assert data["confidence_level"] == 0.95


class TestAEVComponent:
    """Test AEVComponent."""

    def test_component_to_dict(self):
        comp = AEVComponent(
            value=10000.0,
            description="Token rewards",
            evidence_ref="EV-AEV-001-A1B2C3D4",
            source_description="Staking APR * amount",
            calculation_method="V_token = 0.08 * 250000"
        )
        data = comp.to_dict()
        assert data["value"] == 10000.0
        assert data["description"] == "Token rewards"
        assert data["evidence_ref"] == "EV-AEV-001-A1B2C3D4"
        assert data["source_description"] == "Staking APR * amount"
        assert data["calculation_method"] == "V_token = 0.08 * 250000"


class TestAEVBuilder:
    """Test AEVBuilder."""

    def test_builder_basic(self):
        aev = (AEVBuilder()
            .with_skill("skill-001", "My Skill", "DX-L4-001-ABC12345")
            .set_v_token(10000)
            .set_v_compute(5000)
            .set_v_risk(2000)
            .set_v_trust(3000)
            .build())

        assert aev.skill_id == "skill-001"
        assert aev.skill_name == "My Skill"
        assert aev.diagnosis_id == "DX-L4-001-ABC12345"
        assert aev.aev_total == 20000.0  # 10000 + 5000 + 2000 + 3000
        assert len(aev.components) == 4
        assert "v_token" in aev.components
        assert "v_compute" in aev.components
        assert "v_risk" in aev.components
        assert "v_trust" in aev.components

    def test_builder_with_currency_and_period(self):
        aev = (AEVBuilder()
            .with_skill("skill-001")
            .with_currency(Currency.EUR)
            .with_period(Period.QUARTER)
            .set_v_token(10000)
            .build())

        assert aev.currency == Currency.EUR
        assert aev.period == Period.QUARTER

    def test_builder_partial_components(self):
        aev = (AEVBuilder()
            .with_skill("skill-001")
            .set_v_token(10000)
            .set_v_compute(5000)
            .build())

        assert aev.aev_total == 15000.0
        assert len(aev.components) == 2

    def test_builder_confidence_interval(self):
        aev = (AEVBuilder()
            .with_skill("skill-001")
            .set_v_token(10000)
            .set_v_compute(5000)
            .set_v_risk(2000)
            .set_v_trust(3000)
            .build())

        assert aev.confidence_interval.lower < aev.aev_total
        assert aev.confidence_interval.upper > aev.aev_total
        assert aev.confidence_interval.confidence_level == 0.95

    def test_builder_without_skill_raises(self):
        with pytest.raises(ValueError, match="skill_id is required"):
            AEVBuilder().build()

    def test_component_custom_descriptions(self):
        aev = (AEVBuilder()
            .with_skill("skill-001")
            .set_v_token(
                value=10000,
                description="Custom token desc",
                source_description="Custom source",
                calculation_method="Custom method"
            )
            .build())

        comp = aev.components["v_token"]
        assert comp.description == "Custom token desc"
        assert comp.source_description == "Custom source"
        assert comp.calculation_method == "Custom method"

    def test_builder_evidence_refs(self):
        aev = (AEVBuilder()
            .with_skill("skill-001")
            .set_v_token(10000)
            .set_v_compute(5000)
            .build())

        assert len(aev.evidence_refs) == 2
        for ev in aev.evidence_refs:
            assert ev.ref_id.startswith("EV-AEV-")
            assert ev.type == EvidenceType.METRIC


class TestAEVOutput:
    """Test AEVOutput serialization and deserialization."""

    def test_aev_to_dict(self):
        aev = create_aev(
            skill_id="skill-001",
            diagnosis_id="DX-L4-001-ABC",
            v_token=10000,
            v_compute=5000
        )
        data = aev.to_dict()

        assert data["skill_id"] == "skill-001"
        assert data["diagnosis_id"] == "DX-L4-001-ABC"
        assert data["aev_total"] == 15000.0
        assert data["currency"] == "USD"
        assert data["period"] == "year"
        assert "components" in data
        assert "evidence_refs" in data
        assert data["formula"] == "AEV = V_token + V_compute + V_risk + V_trust"

    def test_aev_from_dict(self):
        data = {
            "aev_id": "AEV-L4-001-A1B2C3D4",
            "skill_id": "skill-001",
            "skill_name": "My Skill",
            "diagnosis_id": "DX-L4-001-ABC",
            "aev_total": 15000.0,
            "confidence_interval": {
                "lower": 14000,
                "upper": 16000,
                "confidence_level": 0.95
            },
            "currency": "USD",
            "period": "year",
            "components": {
                "v_token": {
                    "value": 10000,
                    "description": "Token rewards",
                    "evidence_ref": "EV-AEV-001",
                    "source_description": "Staking",
                    "calculation_method": "V_token = 10000"
                },
                "v_compute": {
                    "value": 5000,
                    "description": "Compute value",
                    "evidence_ref": "EV-AEV-002",
                    "source_description": "Execution",
                    "calculation_method": "V_compute = 5000"
                }
            },
            "formula": "AEV = V_token + V_compute + V_risk + V_trust",
            "evidence_refs": [
                {
                    "ref_id": "EV-AEV-001",
                    "type": "metric",
                    "source_locator": "aev.v_token",
                    "content_hash": "abc123",
                    "timestamp": "2026-02-26T10:00:00Z"
                }
            ],
            "generated_at": "2026-02-26T10:00:00Z",
            "metadata": {}
        }

        aev = AEVOutput.from_dict(data)
        assert aev.skill_id == "skill-001"
        assert aev.skill_name == "My Skill"
        assert aev.aev_total == 15000.0
        assert len(aev.components) == 2
        assert len(aev.evidence_refs) == 1

    def test_aev_to_json(self):
        aev = create_aev(
            skill_id="skill-001",
            diagnosis_id="DX-L4-001-ABC"
        )
        json_str = aev.to_json()

        assert "skill_id" in json_str
        assert "aev_total" in json_str
        assert "components" in json_str


class TestCreateAEV:
    """Test convenience function create_aev."""

    def test_create_aev_basic(self):
        aev = create_aev(
            skill_id="skill-001",
            diagnosis_id="DX-L4-001-ABC",
            v_token=10000,
            v_compute=5000,
            v_risk=2000,
            v_trust=3000
        )

        assert aev.skill_id == "skill-001"
        assert aev.aev_total == 20000.0
        assert len(aev.components) == 4

    def test_create_aev_with_name(self):
        aev = create_aev(
            skill_id="skill-001",
            diagnosis_id="DX-L4-001-ABC",
            skill_name="My Skill"
        )

        assert aev.skill_name == "My Skill"

    def test_create_aev_different_currency_period(self):
        aev = create_aev(
            skill_id="skill-001",
            diagnosis_id="DX-L4-001-ABC",
            currency=Currency.EUR,
            period=Period.QUARTER
        )

        assert aev.currency == Currency.EUR
        assert aev.period == Period.QUARTER

    def test_create_aev_zero_components(self):
        aev = create_aev(
            skill_id="skill-001",
            diagnosis_id="DX-L4-001-ABC"
        )

        assert aev.aev_total == 0.0
        assert len(aev.components) == 0


class TestValidateAEV:
    """Test validate_aev function."""

    def test_validate_valid_aev(self):
        # A valid AEV should have all four components per the contract
        aev = create_aev(
            skill_id="skill-001",
            diagnosis_id="DX-L4-001-ABC",
            v_token=10000,
            v_compute=5000,
            v_risk=2000,
            v_trust=3000
        )
        errors = validate_aev(aev.to_dict())
        assert len(errors) == 0

    def test_validate_missing_skill_id(self):
        data = {"aev_id": "AEV-L4-001-ABC12345"}
        errors = validate_aev(data)
        assert any("skill_id" in e for e in errors)

    def test_validate_missing_aev_total(self):
        data = {"skill_id": "skill-001", "diagnosis_id": "DX-001"}
        errors = validate_aev(data)
        assert any("aev_total" in e for e in errors)

    def test_validate_missing_components(self):
        data = {
            "aev_id": "AEV-L4-001-ABC12345",
            "skill_id": "skill-001",
            "diagnosis_id": "DX-001",
            "aev_total": 10000,
            "currency": "USD",
            "period": "year",
            "components": {},
            "evidence_refs": []
        }
        errors = validate_aev(data)
        assert any("v_token" in e for e in errors)

    def test_validate_invalid_aev_id_format(self):
        aev = create_aev(skill_id="skill-001", diagnosis_id="DX-001")
        data = aev.to_dict()
        data["aev_id"] = "INVALID-ID"
        errors = validate_aev(data)
        assert any("aev_id must match format" in e for e in errors)

    def test_validate_negative_aev_total(self):
        aev = create_aev(skill_id="skill-001", diagnosis_id="DX-001")
        data = aev.to_dict()
        data["aev_total"] = -1000
        errors = validate_aev(data)
        assert any("aev_total must be a non-negative" in e for e in errors)


class TestAEVIntegration:
    """Integration tests for full AEV calculation flow."""

    def test_full_aev_calculation(self):
        """Test complete AEV calculation with all four components."""
        aev = (AEVBuilder()
            .with_skill(
                skill_id="skillforge-seo-analyzer",
                skill_name="SEO Analysis Skill",
                diagnosis_id="DX-L4-001-A1B2C3D4"
            )
            .with_currency(Currency.USD)
            .with_period(Period.YEAR)
            .set_v_token(
                value=20000.0,
                description="Token staking rewards",
                source_description="8% APR * $250,000 staked",
                calculation_method="V_token = 0.08 * 250000"
            )
            .set_v_compute(
                value=15000.0,
                description="Compute optimization",
                source_description="50,000 runs * $0.30/unit",
                calculation_method="V_compute = 50000 * 0.30"
            )
            .set_v_risk(
                value=8000.0,
                description="Risk mitigation",
                source_description="$100k exposure * 10% * 80%",
                calculation_method="V_risk = 100000 * 0.10 * 0.80"
            )
            .set_v_trust(
                value=7000.0,
                description="Trust premium",
                source_description="85 score * 1000 users * $0.082",
                calculation_method="V_trust = 0.85 * 1000 * 0.082"
            )
            .build())

        # Verify total calculation
        assert aev.aev_total == 50000.0

        # Verify confidence interval
        assert aev.confidence_interval.lower < 50000
        assert aev.confidence_interval.upper > 50000
        assert aev.confidence_interval.confidence_level == 0.95

        # Verify all components present with correct values
        assert aev.components["v_token"].value == 20000.0
        assert aev.components["v_compute"].value == 15000.0
        assert aev.components["v_risk"].value == 8000.0
        assert aev.components["v_trust"].value == 7000.0

        # Verify each component has evidence_ref
        for comp in aev.components.values():
            assert comp.evidence_ref.startswith("EV-AEV-")

        # Verify evidence_refs list
        assert len(aev.evidence_refs) == 4

        # Validate output
        errors = validate_aev(aev.to_dict())
        assert len(errors) == 0

        # Verify JSON serialization
        json_str = aev.to_json()
        assert "aev_id" in json_str
        assert "50000" in json_str
        assert "V_token + V_compute + V_risk + V_trust" in json_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
