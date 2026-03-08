# Library Migration Batch Top 10 v1
# Exec Phase: Wave 4 Batch 1

## Criteria
- Value Score: High
- Risk Level: Low/Medium
- Dependency: Resolved

## Batch List

1. **Audit Repo Skill** (`audit_repo_skill`)
   - Source: `scripts/audit_tools_v0_5.ps1` (Inferred)
   - Target: `skills/audit_repo.py`
   - Gate: `repo_scan_fit_score`

2. **Generate Skill** (`generate_skill_from_repo`)
   - Source: `scripts/scaffold_skill.py` (Inferred)
   - Target: `skills/generate_skill.py`
   - Gate: `draft_skill_spec`

3. **Upgrade Skill** (`upgrade_skill_revision`)
   - Source: `scripts/update_revision.py` (Inferred)
   - Target: `skills/upgrade_skill.py`
   - Gate: `regression_test`

4. **Tombstone Skill** (`tombstone_skill`)
   - Source: `AUDIT/CONSTITUTION.md` (Revocation Logic)
   - Target: `skills/tombstone.py`
   - Gate: `constitution_risk_gate`

5. **Evidence Schema** (`contract_audit_schema`)
   - Source: `AUDIT/EVIDENCE_SCHEMA.md`
   - Target: `contracts/evidence.yaml`
   - Gate: `schema_validation`

*(Remaining slots reserved for Strategy adaptation in Batch 2)*
