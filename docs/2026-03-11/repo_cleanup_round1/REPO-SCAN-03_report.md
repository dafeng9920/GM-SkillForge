# REPO-SCAN-03: Temporary/Backup Files Without Evidence

**Scan ID**: REPO-SCAN-03
**Scan Date**: 2026-03-11
**Review Mode**: Fail-Closed
**Scope**: Archives, backups, and temporary files lacking deployment receipts

---

## Decision

**FAIL**

---

## Executive Summary

Multiple archive and backup files exist without:
1. Original task_id references
2. Artifact digests/manifests
3. Gate decisions authorizing creation
4. Retention permits (if applicable)

This violates N2 Artifact Completeness requirements of Antigravity-1.

---

## Violations

| Violation ID | Severity | Description |
|--------------|----------|-------------|
| V-03-001 | CRITICAL | Missing deployment receipts for .tar.gz archives |
| V-03-002 | CRITICAL | No contract_hash or artifact_digest references |
| V-03-003 | HIGH | N2 Artifact Incompleteness: Unverifiable provenance |
| V-03-004 | MEDIUM | Unknown authorization for archive creation |
| V-03-005 | MEDIUM | No retention permits for long-term storage |

---

## Affected Items

### Archive Files

```
?? lobster-p2a.tar.gz
?? skillforge_src.tar.gz
```

| File | Size | Last Modified | Purpose | Receipt |
|------|------|---------------|---------|---------|
| lobster-p2a.tar.gz | Unknown | Unknown | UNKNOWN | MISSING |
| skillforge_src.tar.gz | Unknown | Unknown | UNKNOWN | MISSING |

### Backup Files

```
?? docs/2026-02-22/量化/2026-02-22-todo.backup.md
```

### Other Temporary Files

```
?? export-seo/
?? dropzone/
```

---

## Required Changes

### For Each Archive File

**Required Evidence Package**:

1. **archive_receipt.json**
   ```json
   {
     "archive_id": "<filename>",
     "created_at": "<ISO8601_timestamp>",
     "original_task_id": "<task_that_produced_this>",
     "contract_hash": "<sha256_of_original_contract>",
     "artifact_digest": "<sha256_of_archive>",
     "creation_authorized_by": "<gate_decision_id>",
     "retention_permit": "<permit_id_if_long_term>",
     "contents_manifest": [
       {"path": "relative/path/in/archive", "sha256": "<hash>"}
     ]
   }
   ```

2. **Gate Decision Reference**
   - Which gate authorized this archive creation?
   - Entry gate decision ID: `GATE-XXX`

3. **Retention Justification** (if keeping long-term)
   - Business justification
   - Retention period
   - Stakeholder approval

### Option A: Retroactive Receipt Generation

If archives contain valuable data:
1. Generate receipt with all required fields
2. Compute SHA256 of archive
3. Link to original task/gate
4. Submit compliance attestation

### Option B: Formal Deletion

If archives are stale/unneeded:
1. Verify no active references in codebase
2. Submit deletion permit through governance
3. Obtain stakeholder sign-off
4. Execute deletion with evidence recording

---

## Detailed Analysis

### lobster-p2a.tar.gz

**Hypothesis**: "p2a" = "production to archive" or Phase 2 Archive?

**Investigation Required**:
- Contents of archive?
- Original task reference?
- Still referenced by any workflows?

**Action**: Extract and inventory contents OR delete with permit

### skillforge_src.tar.gz

**Hypothesis**: Backup of skillforge source code

**Concern**: Source should be in git, not tarball

**Investigation Required**:
- What version/source is this?
- Why not in git history?
- Is it a git export?

**Action**: Verify git contains same content, then delete with permit

### 2026-02-22-todo.backup.md

**Hypothesis**: Backup of todo document

**Action**: Check if current version exists, then assess necessity

---

## Evidence Required

| Evidence Type | lobster-p2a.tar.gz | skillforge_src.tar.gz | todo.backup.md |
|---------------|-------------------|----------------------|----------------|
| archive_receipt.json | MISSING | MISSING | MISSING |
| original_task_id | UNKNOWN | UNKNOWN | UNKNOWN |
| gate_decision_ref | UNKNOWN | UNKNOWN | UNKNOWN |
| artifact_digest (SHA256) | MISSING | MISSING | MISSING |
| contents_manifest | MISSING | MISSING | N/A |
| retention_permit | MISSING | MISSING | MISSING |

---

## Recommendations

1. **Immediate Audit**: Extract each archive to a temporary location and inventory contents
2. **Git Verification**: For skillforge_src.tar.gz, verify git has equivalent content
3. **Permit Generation**: Either create receipts or deletion permits
4. **Policy**: Establish policy requiring immediate receipt generation for any archive creation

---

## References

- N2 Artifact Completeness: Antigravity-1 Contract Section 3.2
- Archive Receipt Schema: `skillforge/src/contracts/artifacts/archive_receipt.yaml`
- Template: `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`
