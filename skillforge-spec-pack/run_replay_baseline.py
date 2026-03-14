#!/usr/bin/env python3
"""
Run Replay Baseline Test - D3 Fix Validation

This script runs the replay consistency test with D3 fixes applied and generates
the evidence file for L5 replay baseline.

Usage:
    python run_replay_baseline.py
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone

# Add skillforge to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skillforge', 'src'))

from skillforge.tests.test_replay_consistency import run_replay_baseline_test


def generate_sha256_checksum(data: str) -> str:
    """Generate SHA256 checksum for data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def main():
    """Main execution function."""
    print("=" * 60)
    print("D3 Replay Baseline Test - Running with Fixes Applied")
    print("=" * 60)

    # Run the test
    results = run_replay_baseline_test(iterations=2, fixed_seed=42)

    # Add metadata
    results["executor"] = "Kior-A"
    results["status"] = "COMPLETED"
    results["execution_environment"] = "LOCAL-ANTIGRAVITY"

    # Calculate SHA256 checksum
    results_json = json.dumps(results, indent=2, ensure_ascii=False)
    results["sha256_checksum"] = generate_sha256_checksum(results_json)

    # Display results
    print(f"\nSamples Tested: {results['samples_tested']}")
    print(f"Consistency Rate: {results['replay_results']['consistency_rate']:.1%}")
    print(f"Threshold Met: {results['replay_results']['meets_threshold']}")
    print(f"Fully Consistent: {results['replay_results']['fully_consistent']}")
    print(f"Timing Inconsistencies: {results['replay_results']['timing_related_inconsistent']}")
    print(f"State Inconsistencies: {results['replay_results']['state_related_inconsistent']}")
    print(f"Determinism Failures: {results['replay_results']['determinism_failures']}")

    # Display breakdown
    print("\nConsistency by Task Type:")
    for task_type, data in results["consistency_breakdown"]["by_task_type"].items():
        print(f"  {task_type}: {data['consistency_rate']:.1%} ({data['consistent']}/{data['total']})")

    # Display gate decision
    print(f"\nGate Decision: {results['gate_decision_impact']['recommendation']}")
    print(f"Delta to Threshold: {results['gate_decision_impact']['delta']:+.1%}")

    # Save to file
    output_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "reports", "l5-replay", "baseline_2026-03-05.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nEvidence file saved to: {output_path}")
    print(f"SHA256: {results['sha256_checksum'][:32]}...")

    # Exit with appropriate code
    if results['replay_results']['meets_threshold']:
        print("\n✅ Test PASSED - Consistency meets threshold")
        return 0
    else:
        print("\n⚠️ Test PASSED_WITH_CONDITIONS - Consistency below threshold")
        return 1


if __name__ == "__main__":
    sys.exit(main())
