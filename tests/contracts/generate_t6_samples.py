"""
T6 Evidence Sample Generator

Generates sample findings.json from T3/T4/T5 evidence files.
This demonstrates the T6 deliverable: unified Finding structure.

Usage:
    python tests/contracts/generate_t6_samples.py
"""
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skillforge.src.contracts.finding_builder import FindingsReportBuilder


def main():
    """Generate sample findings.json from T3/T4/T5 evidence."""
    # Base paths
    base_dir = Path(__file__).parent.parent.parent / "run"
    run_id = "20260315_t6_sample"

    # Gather evidence files
    t3_reports = list(base_dir.glob("T*_evidence/positive_examples/validation_report.json"))
    # T4 reports are in rule_samples subdirectories
    t4_reports = list(base_dir.glob("T*_evidence/rule_samples/*/rule_scan_report.json"))
    # T5 reports are in pattern_samples subdirectories
    t5_reports = list(base_dir.glob("T*_evidence/pattern_samples/*/pattern_detection_report.json"))

    # Use first available report from each
    # For T4, prefer a report with findings (not clean_skill)
    t4_report = None
    for report in t4_reports:
        if "clean_skill" not in str(report):
            t4_report = report
            break
    if t4_report is None and t4_reports:
        t4_report = t4_reports[0]

    # For T5, prefer a report with findings
    t5_report = None
    for report in t5_reports:
        if "clean_sample" not in str(report):
            t5_report = report
            break
    if t5_report is None and t5_reports:
        t5_report = t5_reports[0]

    t3_report = t3_reports[0] if t3_reports else None

    print("T6 Evidence Sample Generation")
    print("=" * 50)
    print(f"T3 Report: {t3_report}")
    print(f"T4 Report: {t4_report}")
    print(f"T5 Report: {t5_report}")
    print()

    # Load reports
    validation_data = None
    rule_data = None
    pattern_data = None

    if t3_report:
        with open(t3_report, "r", encoding="utf-8") as f:
            validation_data = json.load(f)

    if t4_report:
        with open(t4_report, "r", encoding="utf-8") as f:
            rule_data = json.load(f)

    if t5_report:
        with open(t5_report, "r", encoding="utf-8") as f:
            pattern_data = json.load(f)

    # Create mock result objects
    class MockValidationResult:
        def __init__(self, data):
            self.is_valid = data.get("is_valid", False)
            self.failures = [
                type('obj', (object,), {**f, 'severity': 'ERROR'})()
                for f in data.get("failures", [])
            ]
            self.warnings = [
                type('obj', (object,), {**w, 'severity': 'WARNING'})()
                for w in data.get("warnings", [])
            ]

    class MockRuleResult:
        def __init__(self, data):
            all_hits = []
            for severity in ['critical', 'high', 'medium', 'low']:
                for hit in data.get('findings', {}).get(severity, []):
                    all_hits.append(type('obj', (object,), hit)())
            self.data = all_hits

        def get_all_hits(self):
            return self.data

    class MockPatternResult:
        def __init__(self, data):
            all_matches = []
            for severity in ['critical', 'high', 'medium']:
                for match in data.get('pattern_matches', {}).get(severity, []):
                    all_matches.append(type('obj', (object,), match)())
            self.matches = all_matches
            self.gaps_data = [
                type('obj', (object,), g)()
                for g in data.get('governance_gaps', [])
            ]

        def get_all_matches(self):
            return self.matches

        @property
        def governance_gaps(self):
            return self.gaps_data

    # Build mock results
    validation_result = MockValidationResult(validation_data) if validation_data else None
    rule_result = MockRuleResult(rule_data) if rule_data else None
    pattern_result = MockPatternResult(pattern_data) if pattern_data else None

    # Build findings report
    builder = FindingsReportBuilder(run_id=run_id)
    report = builder.build_from_reports(
        skill_id="sample-1.0.0-00000000",
        skill_name="sample",
        validation_result=validation_result,
        rule_result=rule_result,
        pattern_result=pattern_result,
        validation_report_path=str(t3_report) if t3_report else None,
        rule_scan_report_path=str(t4_report) if t4_report else None,
        pattern_detection_report_path=str(t5_report) if t5_report else None,
    )

    # Save report
    output_dir = base_dir / "T6_evidence"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "findings.json"

    report.save(output_path)

    print("Findings Report Summary")
    print("-" * 50)
    print(f"Total Findings: {report.summary['total_findings']}")
    print(f"\nBy Severity:")
    for severity, count in report.summary['by_severity'].items():
        if count > 0:
            print(f"  {severity}: {count}")
    print(f"\nBy Source:")
    for source, count in report.summary['by_source'].items():
        if count > 0:
            print(f"  {source}: {count}")
    print(f"\nBy Category:")
    for category, count in sorted(report.summary['by_category'].items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {category}: {count}")
    print(f"\nBy Confidence:")
    for range_name, count in report.summary['by_confidence'].items():
        if count > 0:
            print(f"  {range_name}: {count}")
    print()
    print(f"Report saved to: {output_path}")

    # Also generate a minimal sample
    minimal_report = FindingsReportBuilder(run_id=run_id).build_from_reports(
        skill_id="minimal-1.0.0-00000000",
        skill_name="minimal",
    )
    minimal_path = output_dir / "findings_minimal.json"
    minimal_report.save(minimal_path)
    print(f"Minimal sample saved to: {minimal_path}")


if __name__ == "__main__":
    main()
