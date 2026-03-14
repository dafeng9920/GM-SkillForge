#!/usr/bin/env python3
"""L4-06: Execute Diagnosis -> AEV full chain review."""

import json
import sys
from pathlib import Path

# Add skillforge to path
sys.path.insert(0, str(Path(__file__).parent))

from skillforge.src.diagnosis import DiagnosisOutput
from skillforge.src.economics import AEVBuilder, Currency, Period


def main():
    # Load sample diagnosis
    with open('skillforge/src/diagnosis/sample_diagnosis.json', 'r') as f:
        diagnosis_data = json.load(f)

    diagnosis = DiagnosisOutput.from_dict(diagnosis_data)

    print('=== Diagnosis Loaded ===')
    print(f'Diagnosis ID: {diagnosis.diagnosis_id}')
    print(f'Skill ID: {diagnosis.skill_id}')
    print(f'Skill Name: {diagnosis.skill_name}')
    print(f'Overall Health: {diagnosis.overall_health.value}')
    print(f'Health Score: {diagnosis.health_score}')
    print(f'Categories: {len(diagnosis.categories)}')
    print(f'Evidence Refs: {len(diagnosis.evidence_refs)}')
    print(f'Recommendations: {len(diagnosis.recommendations)}')

    # Create AEV from diagnosis
    aev = (AEVBuilder()
        .with_skill(
            skill_id=diagnosis.skill_id,
            skill_name=diagnosis.skill_name,
            diagnosis_id=diagnosis.diagnosis_id
        )
        .with_currency(Currency.USD)
        .with_period(Period.YEAR)
        .set_v_token(
            value=12000.0,
            description='Token staking rewards from SEO audit skill usage',
            source_description='Protocol APR 8% * staked amount of 150,000 tokens',
            calculation_method='V_token = 0.08 * 150000 * token_price'
        )
        .set_v_compute(
            value=8000.0,
            description='Compute cost savings from optimized SEO analysis',
            source_description='Execution metrics: 5000 audits/year * $1.60 per audit',
            calculation_method='V_compute = execution_count * cost_per_unit * efficiency_multiplier(1.0)'
        )
        .set_v_risk(
            value=3500.0,
            description='Risk mitigation from automated SEO issue detection',
            source_description='Risk exposure: $50,000 * 7% probability * (1 - 0% failure_rate)',
            calculation_method='V_risk = incident_probability * incident_cost * (1 - failure_rate)'
        )
        .set_v_trust(
            value=2500.0,
            description='Trust score premium from high user ratings',
            source_description='Trust score 4.7/5 * 1000 users * $0.53 premium_rate',
            calculation_method='V_trust = trust_score * user_count * premium_rate'
        )
        .with_metadata({
            'diagnosis_health_score': diagnosis.health_score,
            'diagnosis_overall_health': diagnosis.overall_health.value,
            'source_diagnosis_id': diagnosis.diagnosis_id,
            'contract_id': 'L4-N8N-CONTRACT-20260226-001',
            'task_id': 'L4-06'
        })
        .build())

    print()
    print('=== AEV Generated ===')
    print(f'AEV ID: {aev.aev_id}')
    print(f'Diagnosis ID: {aev.diagnosis_id}')
    print(f'Total AEV: ${aev.aev_total:,.2f}')
    print(f'Currency: {aev.currency.value}')
    print(f'Period: {aev.period.value}')
    print(f'Components: {len(aev.components)}')
    print(f'Evidence Refs: {len(aev.evidence_refs)}')

    # Verify evidence traceability
    print()
    print('=== Evidence Traceability Check ===')
    for comp_name, comp in aev.components.items():
        print(f'{comp_name}: value=${comp.value:,.2f}, evidence_ref={comp.evidence_ref}')

    print()
    print('=== Evidence Refs Detail ===')
    for ev in aev.evidence_refs:
        print(f'  {ev.ref_id}: {ev.type.value} -> {ev.source_locator}')

    # Save outputs
    output_dir = Path('skillforge/src/economics/l4_06_run_output')
    output_dir.mkdir(exist_ok=True)

    aev_output_path = output_dir / 'l4_06_aev_output.json'
    diagnosis_output_path = output_dir / 'l4_06_diagnosis_input.json'

    with open(aev_output_path, 'w') as f:
        f.write(aev.to_json())

    with open(diagnosis_output_path, 'w') as f:
        f.write(diagnosis.to_json())

    print()
    print(f'=== Outputs Saved ===')
    print(f'Diagnosis input saved: {diagnosis_output_path}')
    print(f'AEV output saved: {aev_output_path}')

    # Full chain verification
    print()
    print('=== Full Chain Verification ===')
    chain_checks = {
        'diagnosis_id_matches_aev': diagnosis.diagnosis_id == aev.diagnosis_id,
        'skill_id_matches': diagnosis.skill_id == aev.skill_id,
        'skill_name_matches': diagnosis.skill_name == aev.skill_name,
        'evidence_refs_populated': len(aev.evidence_refs) > 0,
        'all_components_have_evidence_ref': all(c.evidence_ref for c in aev.components.values()),
        'diagnosis_format_valid': diagnosis.diagnosis_id.startswith('DX-L4-'),
        'aev_format_valid': aev.aev_id.startswith('AEV-L4-'),
        'aev_total_positive': aev.aev_total > 0,
        'four_components_present': len(aev.components) == 4,
        'confidence_interval_present': aev.confidence_interval is not None,
    }

    for check, result in chain_checks.items():
        status = 'PASS' if result else 'FAIL'
        print(f'  [{status}] {check}: {result}')

    all_passed = all(chain_checks.values())
    print()
    print(f'Chain Verification Result: {"PASS - All checks passed" if all_passed else "FAIL - Some checks failed"}')

    # Return summary as JSON for scripting
    summary = {
        'task_id': 'L4-06',
        'run_id': aev.aev_id,
        'diagnosis_id': diagnosis.diagnosis_id,
        'aev_id': aev.aev_id,
        'skill_id': diagnosis.skill_id,
        'skill_name': diagnosis.skill_name,
        'health_score': diagnosis.health_score,
        'overall_health': diagnosis.overall_health.value,
        'aev_total': aev.aev_total,
        'currency': aev.currency.value,
        'period': aev.period.value,
        'components': {
            'v_token': aev.components['v_token'].value,
            'v_compute': aev.components['v_compute'].value,
            'v_risk': aev.components['v_risk'].value,
            'v_trust': aev.components['v_trust'].value,
        },
        'confidence_interval': {
            'lower': aev.confidence_interval.lower,
            'upper': aev.confidence_interval.upper,
            'confidence_level': aev.confidence_interval.confidence_level,
        },
        'diagnosis_evidence_refs_count': len(diagnosis.evidence_refs),
        'aev_evidence_refs_count': len(aev.evidence_refs),
        'chain_verification': chain_checks,
        'chain_verified': all_passed,
        'outputs': {
            'diagnosis': str(diagnosis_output_path),
            'aev': str(aev_output_path),
        }
    }

    # Save summary
    summary_path = output_dir / 'l4_06_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f'Summary saved: {summary_path}')
    print()
    print(json.dumps(summary, indent=2))

    return summary


if __name__ == '__main__':
    main()
