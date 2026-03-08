# Evidence Chain Verify Skill

## Metadata
```yaml
skill_id: "evidence-chain-verify-skill"
skill_name: "Evidence Chain Verification"
version: "1.0.0"
layer: "L4"
domain: "verification"
created_at: "2026-02-22"
executor: "Kior-A"
reviewer: "vs--cc1"
compliance_officer: "Kior-C"
```

## Purpose
Verify the integrity of evidence chains across task execution reports, ensuring all SHA256 hashes are valid, references are intact, and the chain is unbroken.

## Triggers
- After task execution completion
- Before gate decision approval
- During compliance attestation review
- On-demand evidence chain audit

## Gate Rule
**FAIL-CLOSED**: 任一 hash/引用断裂时 FAIL，证据链完整时 PASS

```yaml
pass_condition:
  - All evidence_sha256 hashes match actual file content
  - All chain_hash values are correctly computed
  - All prev_hash values link correctly to previous entry
  - All referenced files exist and are accessible
  - No tampering detected

fail_condition:
  - Any SHA256 hash mismatch
  - Missing referenced file
  - Chain link broken (prev_hash != expected)
  - Index sequence error
  - Tampering evidence detected
```

## Inputs

### Required
| Name | Type | Description |
|------|------|-------------|
| `execution_report` | yaml/json | Task execution report with evidence references |
| `evidence_chain_report` | json | Evidence chain with SHA256 hashes |
| `guard_spec_a` | md | Guard A specification document |
| `guard_spec_b` | md | Guard B specification document |

### Optional
| Name | Type | Description |
|------|------|-------------|
| `additional_evidence_dir` | path | Directory with additional evidence files |
| `skip_existence_check` | boolean | Skip file existence verification |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `verification_result` | json | Verification result with PASS/FAIL status |
| `chain_integrity_report` | json | Detailed chain integrity analysis |
| `broken_links` | array | List of broken hash/reference links (if any) |

## Verification Steps

### Step 1: Load Evidence Chain
```python
# Load evidence_chain_report.json
chain = EvidenceChain(chain_path)
entries = chain.chain_data["entries"]
```

### Step 2: Validate Chain Integrity
```python
# Check prev_hash linkage
for i, entry in enumerate(entries):
    expected_prev = genesis_hash if i == 0 else entries[i-1]["chain_hash"]
    if entry["prev_hash"] != expected_prev:
        return FAIL("Chain link broken at index {i}")
```

### Step 3: Verify File Hashes
```python
# Verify each evidence file's SHA256
for entry in entries:
    actual_sha256 = compute_sha256(entry["evidence_path"])
    if actual_sha256 != entry["evidence_sha256"]:
        return FAIL("Hash mismatch for {entry['evidence_id']}")
```

### Step 4: Verify Chain Hashes
```python
# Verify chain_hash computation
for entry in entries:
    expected_chain_hash = compute_chain_hash(entry)
    if entry["chain_hash"] != expected_chain_hash:
        return FAIL("Chain hash tampered at index {entry['index']}")
```

### Step 5: Generate Report
```python
# Generate verification report
report = {
    "valid": True,
    "entries_checked": len(entries),
    "chain_integrity": chain_validation,
    "evidence_existence": existence_check
}
```

## Guard A Implementation (Automated)

```yaml
guard_a_checks:
  - id: "GA-EVC-001"
    check: "Evidence chain file exists"
    auto: true
    command: "test -f evidence_chain_report.json"

  - id: "GA-EVC-002"
    check: "Chain has valid JSON structure"
    auto: true
    command: "jq . evidence_chain_report.json"

  - id: "GA-EVC-003"
    check: "All entries have required fields"
    auto: true
    required_fields: ["index", "evidence_id", "evidence_path", "evidence_sha256", "chain_hash", "prev_hash"]

  - id: "GA-EVC-004"
    check: "SHA256 hash format valid"
    auto: true
    pattern: "^sha256:[a-f0-9]{64}$"

  - id: "GA-EVC-005"
    check: "Chain integrity validated"
    auto: true
    command: "python scripts/verify_evidence_chain.py --validate"
```

## Guard B Implementation (Manual/Review)

```yaml
guard_b_checks:
  - id: "GB-EVC-001"
    check: "Evidence files are from valid tasks"
    manual: true
    reviewer: "vs--cc1"

  - id: "GB-EVC-002"
    check: "No unauthorized modifications to chain"
    manual: true
    reviewer: "vs--cc1"

  - id: "GB-EVC-003"
    check: "Timestamps are chronologically ordered"
    manual: true
    reviewer: "vs--cc1"

  - id: "GB-EVC-004"
    check: "Metadata is accurate and complete"
    manual: true
    reviewer: "vs--cc1"
```

## Error Codes

| Code | Description | Action |
|------|-------------|--------|
| `E_CHAIN_001` | Chain file not found | Initialize new chain or provide correct path |
| `E_CHAIN_002` | Invalid JSON structure | Fix JSON syntax errors |
| `E_CHAIN_003` | Missing required field | Add missing field to entry |
| `E_CHAIN_004` | Chain link broken | Verify prev_hash linkage |
| `E_CHAIN_005` | Hash mismatch | Re-compute hash or restore file |
| `E_CHAIN_006` | File not found | Restore evidence file or update path |
| `E_CHAIN_007` | Index sequence error | Renumber entries |

## Example Usage

### Command Line
```bash
# Initialize new chain
python scripts/verify_evidence_chain.py --init

# Add evidence file
python scripts/verify_evidence_chain.py --add docs/2026-02-22/verification/T71_execution_report.yaml

# Validate chain
python scripts/verify_evidence_chain.py --validate

# Full integrity check
python scripts/verify_evidence_chain.py --chain-integrity

# Generate report
python scripts/verify_evidence_chain.py --report
```

### Programmatic
```python
from scripts.verify_evidence_chain import EvidenceChain

chain = EvidenceChain("evidence_chain_report.json")

# Add evidence
entry = chain.add_evidence("path/to/evidence.json", metadata={"task_id": "T71"})

# Validate
result = chain.validate_chain()
if not result["valid"]:
    print("Chain broken:", result["errors"])

# Full check
full_result = chain.full_integrity_check()
print("Valid:", full_result["valid"])
```

## Compliance Requirements

- **SHA256 Algorithm**: Must use SHA256 for all hash computations
- **Chain Linkage**: Each entry must link to previous via prev_hash
- **Timestamps**: All timestamps must be ISO 8601 format
- **Audit Trail**: All additions to chain must be logged
- **Immutability**: Once added, entries cannot be modified

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-22 | Initial implementation |

## References

- [EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md](../docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md)
- [EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md](../docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md)
- [T71_execution_report.yaml](../docs/2026-02-22/verification/T71_execution_report.yaml)
