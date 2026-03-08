# Library Intent Mapping v1
# Status: Mapped & Validated

| Source Component | Target Intent ID | Mapping Target | Evidence Ref | Migration Decision |
|---|---|---|---|---|
| **Principles** |
| `const_survival` | `constitution_principle_survival` | `docs/constitution_v1.md` (Appendix) | `ref:AUDIT/CONSTITUTION.md` | ACCEPT |
| `const_default_deny` | `constitution_principle_deny` | `docs/constitution_v1.md` (Clause) | `ref:AUDIT/CONSTITUTION.md` | ACCEPT |

| **Strategies** |
| `strat_trend_follow` | `skill_strat_trend_follow` | `skills/strategy_trend.py` | `ref:strategies/template_trend_following.py` | ACCEPT (Batch 2) |
| `strat_multi_factor` | `skill_strat_multi_factor` | `skills/strategy_multi_factor.py` | `ref:strategies/template_multi_factor.py` | DEFER |

| **Core Runtime** |
| `core_time_machine` | `kernel_time_semantics` | `skillforge/src/core/time.py` | `ref:gm-core/gm_core/time.py` | ACCEPT (Wave 3 Existing) |
| `core_permit_gate` | `kernel_permit_issuer` | `skillforge/src/core/referendum.py` | `ref:gm_os/inner/permit.py` | REJECT (Use Spec-Pack Referendum) |

| **Audit Tools** |
| `audit_evidence_schema` | `contract_audit_schema` | `skillforge/src/contracts/evidence.yaml` | `ref:AUDIT/EVIDENCE_SCHEMA.md` | ACCEPT (Wave 4 Batch 1) |
