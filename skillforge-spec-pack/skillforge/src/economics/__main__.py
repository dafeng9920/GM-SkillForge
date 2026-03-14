"""
Economics Module Entry Point

Provides CLI access to AEV calculations.
"""

import sys
import json
from . import AEVBuilder, create_aev, validate_aev, Currency, Period


def main():
    """Main entry point for economics module CLI."""
    # Example: Create a sample AEV calculation
    aev = (AEVBuilder()
        .with_skill(
            skill_id="skillforge-example-skill",
            skill_name="Example SEO Analysis Skill",
            diagnosis_id="DX-L4-001-A1B2C3D4"
        )
        .with_currency(Currency.USD)
        .with_period(Period.YEAR)
        .set_v_token(
            value=20000.0,
            description="Token staking rewards from protocol",
            source_description="Protocol staking APR (8%) * staked amount ($250,000)",
            calculation_method="V_token = 0.08 * 250000 = $20,000/year"
        )
        .set_v_compute(
            value=15000.0,
            description="Compute cost savings from optimized execution",
            source_description="Execution metrics: 50,000 runs/year * $0.30/compute unit",
            calculation_method="V_compute = 50000 * 0.30 = $15,000/year"
        )
        .set_v_risk(
            value=8000.0,
            description="Risk mitigation from automated validation",
            source_description="Risk exposure ($100,000) * incident probability (10%) * mitigation factor (80%)",
            calculation_method="V_risk = 100000 * 0.10 * 0.80 = $8,000/year"
        )
        .set_v_trust(
            value=7000.0,
            description="Trust score premium from high reliability",
            source_description="Trust score (85/100) * user base (1000) * premium rate ($0.082/user)",
            calculation_method="V_trust = 0.85 * 1000 * 0.082 = $7,000/year"
        )
        .build())

    # Print the result
    print(aev.to_json())

    # Validate
    errors = validate_aev(aev.to_dict())
    if errors:
        print(f"\nValidation errors: {errors}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
