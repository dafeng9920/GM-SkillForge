# T2-F3-R5 Unified Terminology Specification

## Executive Summary

This document defines the unified terminology for evidence-related semantics in the GM-SkillForge repository, replacing the misleading `evidence-first` terminology.

## Problem Statement

The term `evidence-first` suggests that evidence must exist **before** a decision is made, which is:
1. **Semantically misleading**: Decisions and evidence are generated atomically in gate execution
2. **Inconsistent with actual implementation**: Gates generate decisions and evidence simultaneously
3. **Creates dual-track terminology**: Tests and documentation may reference historical terms while code uses current semantics

## Unified Terminology

### Code Comments (Python docstrings, inline comments)

| Old Term | New Term | Usage |
|----------|----------|-------|
| `evidence-first` | `evidence-mandatory` | Python code comments |

**Examples:**
- `gate_permit.py:9`: `- Evidence-Mandatory: 每次校验生成 EvidenceRef`
- `permit_issuer.py:6`: `- Evidence-Mandatory: 每次签发尝试都生成 EvidenceRef`
- `experience_capture.py:91`: `# Strong evidence-mandatory rule.`

### YAML Configuration (SKILL.md, config files)

| Old Term | New Term | Usage |
|----------|----------|-------|
| `evidence_first` | `evidence_traceability` | YAML boolean flags |

**Examples:**
- `ci-skill-validation-skill/SKILL.md`: `evidence_traceability: true`
- `permit-governance-skill/SKILL.md`: `evidence_traceability: true`

### Historical Term Handling

| Term | Status | Usage Restriction |
|------|--------|-------------------|
| `evidence-first` | **DEPRECATED** | Historical reference **ONLY** - NOT to be used as current rule name |

## Rationale

### Why `evidence-mandatory`?

- Accurately reflects that evidence is **required** for all gate operations
- No temporal ordering implication
- Clear semantic: "cannot proceed without evidence"
- Maintains the strong requirement without misleading chronology

### Why `evidence_traceability`?

- Accurately describes the **audit trail** requirement
- Reflects the ability to trace decisions back to their evidence
- No temporal ordering implication
- Standard industry terminology for audit systems

## Semantic Layer Consistency

### Layer 1: Implementation (Python code)
- Use `evidence-mandatory` in comments and docstrings
- Reflects the **requirement** that evidence must be generated

### Layer 2: Configuration (YAML)
- Use `evidence_traceability` for boolean flags
- Reflects the **capability** to trace decisions to evidence

### Layer 3: Documentation
- Avoid `evidence-first` except when describing historical terminology
- Use `evidence-mandatory` or `evidence_traceability` depending on context

## Migration Checklist

- [x] Replace `Evidence-First` → `Evidence-Mandatory` in gate_permit.py:9
- [x] Replace `Evidence-First` → `Evidence-Mandatory` in permit_issuer.py:6
- [x] Replace `evidence-first` → `evidence-mandatory` in experience_capture.py:91
- [x] Replace `evidence_first: true` → `evidence_traceability: true` in ci-skill-validation-skill/SKILL.md:27
- [x] Replace `evidence_first: true` → `evidence_traceability: true` in permit-governance-skill/SKILL.md:27
- [ ] Search remaining files for `evidence-first` (outside specified 5 locations)
- [ ] Update training materials and documentation
- [ ] Add terminology to code review checklist

## Enforcement

### Code Review
- Reject any new uses of `evidence-first` as a rule name
- Accept only historical references with explicit "(historical)" markers

### Linter Rules (Recommended)
```yaml
# Add to .gitleints or similar
no-evidence-first:
  pattern: "evidence[-_]first"
  exceptions:
    - "historical"
    - "legacy"
  message: "Use 'evidence-mandatory' or 'evidence_traceability' instead"
```

## Related Documents

- **T2-F3-R4 Review**: Original compliance failure
- **T2-F3-R5 Execution Report**: Remediation execution details
- **T2-F3-R5 Completion Record**: Completion verification
- **T2-F3-R5 EvidenceRef Mapping**: Location-by-location evidence

---

**Version**: 1.0.0
**Date**: 2026-03-06
**Maintainer**: T2 Governance
**Status**: ACTIVE
