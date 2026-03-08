#!/usr/bin/env python3
"""
Policy Lock Check Script (L4-SKILL-04)

Verifies that policy file SHA256 hash matches the frozen index.
Gate Rule: PASS if hash matches, DENY if mismatch (must block release).

Usage:
    python check_policy_lock.py --policy <path> --freeze-report <path> [options]

Exit Codes:
    0 - PASS (hash match)
    1 - DENY (hash mismatch or validation error)
    2 - Configuration error
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class PolicyLockChecker:
    """Check policy file hash against frozen index."""

    def __init__(self, policy_path: str, freeze_report_path: str):
        self.policy_path = Path(policy_path)
        self.freeze_report_path = Path(freeze_report_path)
        self.policy_data: Optional[Dict] = None
        self.freeze_data: Optional[Dict] = None
        self.actual_hash: Optional[str] = None
        self.frozen_policy: Optional[Dict] = None

    def load_policy(self) -> Tuple[bool, str]:
        """Load and parse policy JSON file."""
        if not self.policy_path.exists():
            return False, f"Policy file not found: {self.policy_path}"

        try:
            with open(self.policy_path, 'r', encoding='utf-8') as f:
                self.policy_data = json.load(f)
            return True, "Policy file loaded successfully"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in policy file: {e}"
        except Exception as e:
            return False, f"Error reading policy file: {e}"

    def load_freeze_report(self) -> Tuple[bool, str]:
        """Load and parse freeze report JSON file."""
        if not self.freeze_report_path.exists():
            return False, f"Freeze report not found: {self.freeze_report_path}"

        try:
            with open(self.freeze_report_path, 'r', encoding='utf-8') as f:
                self.freeze_data = json.load(f)
            return True, "Freeze report loaded successfully"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in freeze report: {e}"
        except Exception as e:
            return False, f"Error reading freeze report: {e}"

    def calculate_hash(self) -> Tuple[bool, str, Optional[str]]:
        """Calculate SHA256 hash of policy file."""
        if not self.policy_path.exists():
            return False, "Policy file not found", None

        try:
            sha256_hash = hashlib.sha256()
            with open(self.policy_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            self.actual_hash = sha256_hash.hexdigest()
            return True, "Hash calculated successfully", self.actual_hash
        except Exception as e:
            return False, f"Error calculating hash: {e}", None

    def find_frozen_policy(self) -> Tuple[bool, str, Optional[Dict]]:
        """Find matching frozen policy entry."""
        if not self.freeze_data:
            return False, "Freeze report not loaded", None

        frozen_policies = self.freeze_data.get('frozen_policies', [])
        if not frozen_policies:
            return False, "No frozen policies found in report", None

        # Try to match by file path
        policy_name = self.policy_path.name
        for fp in frozen_policies:
            file_path = fp.get('file_path', '')
            if policy_name in file_path or file_path.endswith(policy_name):
                self.frozen_policy = fp
                return True, f"Found frozen policy: {fp.get('name', 'Unknown')}", fp

        return False, f"No frozen policy found for: {policy_name}", None

    def verify_hash(self) -> Tuple[bool, str, Dict]:
        """Verify policy hash matches frozen index."""
        result = {
            'hash_match': False,
            'expected_hash': None,
            'actual_hash': self.actual_hash,
            'policy_name': None,
            'policy_version': None,
            'frozen_version': None
        }

        if not self.frozen_policy:
            return False, "No frozen policy to compare", result

        expected_hash = self.frozen_policy.get('sha256', '')
        result['expected_hash'] = expected_hash
        result['policy_name'] = self.frozen_policy.get('name', 'Unknown')
        result['frozen_version'] = self.frozen_policy.get('version', 'Unknown')

        if self.policy_data:
            result['policy_version'] = self.policy_data.get('policy_version', 'Unknown')

        if not expected_hash:
            return False, "No expected hash in frozen policy", result

        if not self.actual_hash:
            return False, "Actual hash not calculated", result

        result['hash_match'] = (expected_hash.lower() == self.actual_hash.lower())

        if result['hash_match']:
            return True, "Hash verification PASSED", result
        else:
            return False, "Hash MISMATCH - potential tampering detected", result

    def generate_gate_decision(self, task_id: str = "L4-SKILL-04") -> Dict:
        """Generate gate decision JSON."""
        timestamp = datetime.now(timezone.utc).isoformat()

        reasons = []
        decision = "DENY"

        # Check all conditions
        if not self.policy_data:
            reasons.append("Policy file could not be loaded")
        elif not self.freeze_data:
            reasons.append("Freeze report could not be loaded")
        elif not self.frozen_policy:
            reasons.append("No matching frozen policy found")
        elif self.actual_hash and self.frozen_policy:
            expected = self.frozen_policy.get('sha256', '')
            if self.actual_hash.lower() == expected.lower():
                decision = "PASS"
                reasons.append("Policy hash matches frozen index")
            else:
                reasons.append(f"Hash mismatch: expected {expected[:16]}..., got {self.actual_hash[:16]}...")
        else:
            reasons.append("Hash verification failed")

        gate_decision = {
            "decision": decision,
            "task_id": task_id,
            "policy_id": self.frozen_policy.get('id') if self.frozen_policy else None,
            "policy_name": self.frozen_policy.get('name') if self.frozen_policy else None,
            "policy_file": str(self.policy_path),
            "expected_hash": self.frozen_policy.get('sha256') if self.frozen_policy else None,
            "actual_hash": self.actual_hash,
            "hash_match": decision == "PASS",
            "reasons": reasons,
            "timestamp": timestamp,
            "gate_rule": "通过条件=policy hash 与冻结索引一致；不一致必须阻断发布",
            "freeze_report": str(self.freeze_report_path),
            "freeze_index_version": self.freeze_data.get('freeze_index', {}).get('version') if self.freeze_data else None
        }

        return gate_decision

    def generate_compliance_attestation(self, task_id: str = "L4-SKILL-04",
                                        executor: str = "vs--cc1") -> Dict:
        """Generate compliance attestation following B-skill format."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Calculate contract hash (hash of the verification result)
        contract_data = {
            "policy_path": str(self.policy_path),
            "freeze_report_path": str(self.freeze_report_path),
            "actual_hash": self.actual_hash
        }
        contract_hash = hashlib.sha256(
            json.dumps(contract_data, sort_keys=True).encode()
        ).hexdigest()[:16]

        decision = "FAIL"
        reasons = []
        evidence_refs = []

        if self.actual_hash and self.frozen_policy:
            expected = self.frozen_policy.get('sha256', '')
            if self.actual_hash.lower() == expected.lower():
                decision = "PASS"
                reasons.append("Policy hash verified successfully")
                reasons.append(f"SHA256 match: {self.actual_hash[:32]}...")
            else:
                reasons.append("POLICY_HASH_MISMATCH")
                reasons.append(f"Expected: {expected}")
                reasons.append(f"Actual: {self.actual_hash}")
        else:
            reasons.append("POLICY_VERIFICATION_FAILED")
            if not self.policy_data:
                reasons.append("Policy file could not be loaded")
            if not self.freeze_data:
                reasons.append("Freeze report could not be loaded")
            if not self.frozen_policy:
                reasons.append("No matching frozen policy entry")

        # Evidence references
        evidence_refs.append({
            "id": f"EV-{task_id}-001",
            "kind": "FILE",
            "locator": str(self.policy_path),
            "sha256": self.actual_hash,
            "description": "Policy file analyzed"
        })
        evidence_refs.append({
            "id": f"EV-{task_id}-002",
            "kind": "FILE",
            "locator": str(self.freeze_report_path),
            "description": "Freeze report used for verification"
        })

        attestation = {
            "decision": decision,
            "task_id": task_id,
            "executor": executor,
            "reasons": reasons,
            "evidence_refs": evidence_refs,
            "contract_hash": f"sha256:{contract_hash}",
            "reviewed_at": timestamp,
            "compliance_standard": "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md",
            "gate_rule_enforced": "通过条件=policy hash 与冻结索引一致；不一致必须阻断发布",
            "verification_details": {
                "policy_file": str(self.policy_path),
                "policy_version": self.policy_data.get('policy_version') if self.policy_data else None,
                "frozen_version": self.frozen_policy.get('version') if self.frozen_policy else None,
                "hash_algorithm": "SHA256",
                "expected_hash": self.frozen_policy.get('sha256') if self.frozen_policy else None,
                "actual_hash": self.actual_hash,
                "hash_match": decision == "PASS"
            },
            "audit_trail": [
                {
                    "timestamp": timestamp,
                    "action": "POLICY_LOCK_CHECK",
                    "actor": executor,
                    "result": decision
                }
            ]
        }

        return attestation

    def generate_execution_report(self, task_id: str = "L4-SKILL-04",
                                  executor: str = "vs--cc1",
                                  scope: str = "P2-04") -> str:
        """Generate execution report in YAML format."""
        timestamp = datetime.now(timezone.utc).isoformat()

        decision = "DENY"
        status = "failed"

        if self.actual_hash and self.frozen_policy:
            expected = self.frozen_policy.get('sha256', '')
            if self.actual_hash.lower() == expected.lower():
                decision = "PASS"
                status = "完成"

        report = f'''# {task_id} Execution Report - Policy Lock Check
# Generated: {timestamp}

task_id: "{task_id}"
executor: "{executor}"
status: "{status}"
job_id: "L4-P2-HARDENING-20260222-002"
scope: "{scope}"
skill_name: "policy-lock-check-skill"

deliverables:
  - path: "skills/policy-lock-check-skill/SKILL.md"
    action: "新建"
    description: "Policy Lock Check Skill Definition"
  - path: "skills/policy-lock-check-skill/scripts/check_policy_lock.py"
    action: "新建"
    description: "Policy Lock Verification Script"

gate_self_check:
  - check: "Policy file exists"
    result: {"PASS" if self.policy_data else "FAIL"}
    evidence: "{str(self.policy_path)}"
  - check: "Freeze report exists"
    result: {"PASS" if self.freeze_data else "FAIL"}
    evidence: "{str(self.freeze_report_path)}"
  - check: "Frozen policy entry found"
    result: {"PASS" if self.frozen_policy else "FAIL"}
    evidence: "{self.frozen_policy.get('name', 'N/A') if self.frozen_policy else 'N/A'}"
  - check: "Hash verification"
    result: "{decision}"
    expected_hash: "{self.frozen_policy.get('sha256', 'N/A') if self.frozen_policy else 'N/A'}"
    actual_hash: "{self.actual_hash or 'N/A'}"

constraints_verified:
  - constraint: "Policy hash must match frozen index"
    status: "{"PASS" if decision == "PASS" else "FAIL"}"
    evidence: {"Hash match confirmed" if decision == "PASS" else "Hash mismatch detected"}
  - constraint: "Release must be blocked on mismatch"
    status: "PASS"
    evidence: "Gate decision set to DENY on mismatch"

evidence_refs:
  - id: "EV-{task_id}-001"
    kind: "FILE"
    locator: "{str(self.policy_path)}"
    description: "Policy file"
    sha256: "{self.actual_hash or 'N/A'}"
  - id: "EV-{task_id}-002"
    kind: "FILE"
    locator: "{str(self.freeze_report_path)}"
    description: "Freeze report"

gate_rule:
  rule: "通过条件=policy hash 与冻结索引一致；不一致必须阻断发布"
  result: "{decision}"
  action: {"ALLOW" if decision == "PASS" else "DENY"}

notes: |
  {task_id} Policy Lock Check:
  - Policy: {str(self.policy_path)}
  - Freeze Report: {str(self.freeze_report_path)}
  - Expected Hash: {self.frozen_policy.get('sha256', 'N/A') if self.frozen_policy else 'N/A'}
  - Actual Hash: {self.actual_hash or 'N/A'}
  - Decision: {decision}
'''
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Verify policy file hash against frozen index'
    )
    parser.add_argument(
        '--policy', '-p',
        required=True,
        help='Path to policy JSON file'
    )
    parser.add_argument(
        '--freeze-report', '-f',
        required=True,
        help='Path to policy lock report JSON'
    )
    parser.add_argument(
        '--gate-decision', '-g',
        help='Output path for gate decision JSON'
    )
    parser.add_argument(
        '--compliance-attestation', '-c',
        help='Output path for compliance attestation JSON'
    )
    parser.add_argument(
        '--execution-report', '-e',
        help='Output path for execution report YAML'
    )
    parser.add_argument(
        '--task-id', '-t',
        default='L4-SKILL-04',
        help='Task ID for reports'
    )
    parser.add_argument(
        '--executor',
        default='vs--cc1',
        help='Executor identifier'
    )
    parser.add_argument(
        '--scope',
        default='P2-04',
        help='Scope identifier'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output except errors'
    )

    args = parser.parse_args()

    # Initialize checker
    checker = PolicyLockChecker(args.policy, args.freeze_report)

    # Run verification steps
    success, msg = checker.load_policy()
    if not success:
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(2)

    success, msg = checker.load_freeze_report()
    if not success:
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(2)

    success, msg, hash_val = checker.calculate_hash()
    if not success:
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(2)

    success, msg, frozen = checker.find_frozen_policy()
    if not success:
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(2)

    # Verify hash
    success, msg, result = checker.verify_hash()

    if not args.quiet:
        print(f"Policy Lock Check: {args.policy}")
        print(f"Frozen Policy: {result.get('policy_name', 'Unknown')}")
        print(f"Policy Version: {result.get('policy_version', 'Unknown')}")
        print(f"Frozen Version: {result.get('frozen_version', 'Unknown')}")
        print(f"Expected Hash: {result.get('expected_hash', 'N/A')}")
        print(f"Actual Hash: {result.get('actual_hash', 'N/A')}")
        print(f"Hash Match: {result.get('hash_match', False)}")
        print(f"Result: {msg}")

    # Generate outputs
    gate_decision = checker.generate_gate_decision(args.task_id)

    if args.gate_decision:
        Path(args.gate_decision).parent.mkdir(parents=True, exist_ok=True)
        with open(args.gate_decision, 'w', encoding='utf-8') as f:
            json.dump(gate_decision, f, indent=2, ensure_ascii=False)
        if not args.quiet:
            print(f"Gate decision written to: {args.gate_decision}")

    if args.compliance_attestation:
        attestation = checker.generate_compliance_attestation(args.task_id, args.executor)
        Path(args.compliance_attestation).parent.mkdir(parents=True, exist_ok=True)
        with open(args.compliance_attestation, 'w', encoding='utf-8') as f:
            json.dump(attestation, f, indent=2, ensure_ascii=False)
        if not args.quiet:
            print(f"Compliance attestation written to: {args.compliance_attestation}")

    if args.execution_report:
        report = checker.generate_execution_report(args.task_id, args.executor, args.scope)
        Path(args.execution_report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.execution_report, 'w', encoding='utf-8') as f:
            f.write(report)
        if not args.quiet:
            print(f"Execution report written to: {args.execution_report}")

    # Exit with appropriate code
    if gate_decision['decision'] == 'PASS':
        print("\n[PASS] Policy hash verified - release allowed")
        sys.exit(0)
    else:
        print("\n[DENY] Policy hash mismatch - release blocked", file=sys.stderr)
        for reason in gate_decision.get('reasons', []):
            print(f"  - {reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
