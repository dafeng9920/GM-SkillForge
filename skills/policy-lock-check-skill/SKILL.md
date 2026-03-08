---
name: policy-lock-check-skill
description: Verify policy hash matches frozen index before release. DENY release if policy hash differs from freeze index. Part of Execution Guard compliance chain.
---

# policy-lock-check-skill

Use this skill to verify that policy files have not been tampered with since freeze.

## Purpose

Ensure execution军团 always uses the correct, frozen policy configuration:
- Verify SHA256 hash of policy files matches frozen index records
- Block any release if policy hash mismatch is detected
- Provide audit trail for policy integrity checks

## Required Inputs

1. `policy_file` - Path to the policy JSON file (e.g., `configs/audit_policy_v1.json`)
2. `freeze_report` - Policy lock report containing frozen hashes (e.g., `docs/2026-02-22/verification/policy_lock_report.json`)
3. `execution_contract` (optional) - For integration with Execution Guard chain

## Gate Rule

```
通过条件 = policy hash 与冻结索引一致
不一致必须阻断发布 (DENY)
```

## Verification Steps

1. **Load Freeze Report**: Read policy_lock_report.json to get expected hashes
2. **Calculate Current Hash**: Compute SHA256 of policy file
3. **Compare Hashes**: Match calculated hash against frozen_policies[].sha256
4. **Decision**: PASS if match, DENY if mismatch

## Output Schema

### Gate Decision (gate_decision.json)
```json
{
  "decision": "PASS | DENY",
  "policy_id": "POLICY-001",
  "policy_name": "string",
  "expected_hash": "sha256:...",
  "actual_hash": "sha256:...",
  "hash_match": true | false,
  "reasons": ["string"],
  "timestamp": "ISO8601"
}
```

### Compliance Attestation
Follows B-skill format:
```json
{
  "decision": "PASS | FAIL",
  "reasons": ["string"],
  "evidence_refs": [...],
  "contract_hash": "string",
  "reviewed_at": "ISO8601"
}
```

## RED Conditions (Immediate DENY)

1. Policy file not found
2. Freeze report not found
3. Hash mismatch (tampering detected)
4. Policy version mismatch
5. Missing required fields in freeze report

## GREEN Conditions (PASS)

1. Policy file exists and readable
2. Freeze report exists and valid
3. SHA256 hash matches exactly
4. Version strings match
5. All required metadata present

## Fail Codes

- `SF_VALIDATION_ERROR` - Policy file or freeze report format invalid
- `SF_RISK_CONSTITUTION_BLOCKED` - Hash mismatch, potential tampering
- `SF_POLICY_NOT_FROZEN` - No freeze record found for policy

## Integration Points

1. **Preflight Check**: Run before any audit execution
2. **Release Gate**: Mandatory check before deployment
3. **Execution Guard B**: Use as compliance checkpoint

## Script Usage

```bash
# Basic check
python scripts/check_policy_lock.py \
  --policy configs/audit_policy_v1.json \
  --freeze-report docs/2026-02-22/verification/policy_lock_report.json

# With gate decision output
python scripts/check_policy_lock.py \
  --policy configs/audit_policy_v1.json \
  --freeze-report docs/2026-02-22/verification/policy_lock_report.json \
  --gate-decision docs/2026-02-22/verification/L4-SKILL-04_gate_decision.json

# Full compliance mode
python scripts/check_policy_lock.py \
  --policy configs/audit_policy_v1.json \
  --freeze-report docs/2026-02-22/verification/policy_lock_report.json \
  --compliance-attestation docs/2026-02-22/verification/L4-SKILL-04_compliance_attestation.json \
  --execution-report docs/2026-02-22/verification/L4-SKILL-04_execution_report.yaml
```

## One-line Doctrine

"没有哈希一致性，就不放行；哈希不匹配，必须阻断发布。"

## References

- `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` - Proposal constraints
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` - Execution compliance
- `configs/audit_policy_v1.json` - Current audit policy
- `docs/2026-02-22/verification/policy_lock_report.json` - Freeze index
