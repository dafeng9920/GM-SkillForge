# Repository Cleanup Review - Round 1

**Review Date**: 2026-03-11
**Review Mode**: Fail-Closed
**Review Scope**: REPO-SCAN-01 through REPO-SCAN-04

---

## Executive Summary

**Overall Decision**: **FAIL**

The repository fails fail-closed compliance review across all four scan categories. Major evidence gaps exist that violate Antigravity-1 closed-loop contract standards.

---

## Scan Results Summary

| Scan ID | Category | Decision | Violation Count | Priority |
|---------|----------|----------|-----------------|----------|
| REPO-SCAN-01 | Untracked Skill Directories | FAIL | 5 | CRITICAL |
| REPO-SCAN-02 | Non-Skill Business Separation | FAIL | 4 | MEDIUM |
| REPO-SCAN-03 | Temporary/Backup Files | FAIL | 5 | HIGH |
| REPO-SCAN-04 | Core File Misclassification | FAIL | 5 | CRITICAL |

---

## Critical Findings

### 1. Massive Evidence Gap (REPO-SCAN-01)

- **80+ untracked skill directories** without gate decisions
- No compliance attestations (N1/N2/N3 checks)
- Missing evidence receipts with contract hashes
- **Impact**: Cannot verify any skill deployment legitimacy

### 2. Core Infrastructure Unclassified (REPO-SCAN-04)

- `core/` and `db/` directories lack T5 gate authorization
- Cannot determine if mainline core or skill artifacts
- N1 command allowlist not verified
- **Impact**: Potential permit bypass for production infrastructure

### 3. Archive Provenance Unknown (REPO-SCAN-03)

- `.tar.gz` files without receipts or task references
- Cannot verify artifact digests
- No retention permits
- **Impact**: N2 Artifact Completeness violation

### 4. Build Artifact Cleanup Incomplete (REPO-SCAN-02)

- Multiple `__pycache__` variants with conflicting timestamps
- No canonical manifest
- Evidence integrity cannot be verified
- **Impact**: N3 Time Window compliance unclear

---

## Cleanup Decision Matrix

### Immediate Actions (Critical)

| Action | Target | Evidence Required | Status |
|--------|--------|-------------------|--------|
| Generate gate decisions | 80+ skills | gate_decision.json + compliance_attestation.json | NOT STARTED |
| Classify core paths | core/, db/ | T5 gate decision | NOT STARTED |
| Audit archives | *.tar.gz | archive_receipt.json | NOT STARTED |
| Create manifest | __pycache__/ | artifact_manifest.yml | NOT STARTED |

### Classification Decisions

| Path | Classification | Action | Gate Required |
|------|----------------|--------|---------------|
| `core/` | MAINLINE CORE | Generate T5 gate | T5_master_control |
| `db/` | INFRASTRUCTURE | Generate T5 gate OR .gitignore | T5_master_control |
| `adapters/quant/` | EDGE LAYER | Move to separate repo | N/A |
| `skills/*[80+]` | SKILL ARTIFACTS | Generate T4 gates OR delete | T4_skill_deployment |
| `artifacts/` | BUILD OUTPUT | Add to .gitignore | N/A |
| `reports/` | OUTPUT | Add to .gitignore | N/A |
| `dropzone/` | TEMPORARY | Add to .gitignore | N/A |

---

## Execution Checklist

### Phase 1: Evidence Generation (Week 1)

- [ ] **REPO-SCAN-01**: Generate compliance package for each untracked skill
  - [ ] Create gate_decision.json
  - [ ] Create compliance_attestation.json
  - [ ] Create evidence_receipt.json
  - [ ] Link to original task (if exists) OR create deletion permit

- [ ] **REPO-SCAN-04**: Classify and generate evidence for core directories
  - [ ] Audit `core/` contents
  - [ ] Audit `db/` contents
  - [ ] Determine: mainline (T5) vs artifact (T4) vs ignore (.gitignore)
  - [ ] Generate corresponding gate decisions

### Phase 2: Archive Resolution (Week 2)

- [ ] **REPO-SCAN-03**: Resolve archive files
  - [ ] Extract and inventory `lobster-p2a.tar.gz`
  - [ ] Verify `skillforge_src.tar.gz` against git
  - [ ] Generate receipts OR submit deletion permits
  - [ ] Document retention justification

### Phase 3: Cleanup Execution (Week 3)

- [ ] **REPO-SCAN-02**: Clean up build artifacts
  - [ ] Generate artifact_manifest.yml
  - [ ] Remove stale `__pycache__` variants
  - [ ] Update .gitignore

- [ ] **Global**: Update .gitignore
  - [ ] Add artifacts/, reports/, dropzone/
  - [ ] Add data/, db/, demo_*_data/
  - [ ] Add *.tar.gz, Audit_Report_*

### Phase 4: Repository Restructuring (Week 4+)

- [ ] **REPO-SCAN-04**: Move edge layers to separate repos
  - [ ] Create `gm-skillforge-quant` for `adapters/quant/`
  - [ ] Create `gm-skillforge-ui` for `ui/`
  - [ ] Create `gm-openclaw-box` for `openclaw-box/`
  - [ ] Update submodule references

---

## Evidence Requirements Summary

| Evidence Type | Quantity Required | Current Status |
|---------------|-------------------|----------------|
| gate_decision.json | 80+ | 0% complete |
| compliance_attestation.json | 80+ | 0% complete |
| evidence_receipt.json | 80+ | 0% complete |
| archive_receipt.json | 2 | 0% complete |
| artifact_manifest.yml | 1 | 0% complete |
| T5 gate decision (core/) | 1 | 0% complete |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Unauthorized skill deployment | CRITICAL | Generate gate decisions for all skills |
| Permit bypass for infrastructure | CRITICAL | Audit core/, db/ with T5 gate |
| Evidence chain broken | HIGH | Generate receipts for all artifacts |
| Data loss from archive deletion | MEDIUM | Inventory contents before deletion |

---

## Governance Requirements

All cleanup actions require:

1. **Permit**: Formal cleanup permit signed by governance authority
2. **Evidence**: Evidence receipts for all changes
3. **Gate**: Entry/exit gate decisions for all modifications
4. **Attestation**: Compliance attestation with N1/N2/N3 verification

---

## References

- Individual Scan Reports:
  - [REPO-SCAN-01_report.md](./REPO-SCAN-01_report.md) - Untracked Skills
  - [REPO-SCAN-02_report.md](./REPO-SCAN-02_report.md) - Non-Skill Business
  - [REPO-SCAN-03_report.md](./REPO-SCAN-03_report.md) - Archives/Backups
  - [REPO-SCAN-04_report.md](./REPO-SCAN-04_report.md) - Core Classification
- Compliance Report: [COMPLIANCE_report.md](./COMPLIANCE_report.md)
- Antigravity-1 Contract: `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`

---

**Report Generated**: 2026-03-11
**Status**: FAIL - Evidence gaps require immediate remediation
**Next Review**: After Phase 1 completion
