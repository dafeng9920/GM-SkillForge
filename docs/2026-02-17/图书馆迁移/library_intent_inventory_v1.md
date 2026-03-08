# Library Intent Inventory v1
# Source: D:\NEW-GM (Scan Date: 2026-02-18)
# Scanner: A1-A8 Legions

## 1. Principles (A1 Scan)
| Component ID | Source Ref | Intent Summary | Value | Risk |
|---|---|---|---|---|
| `const_survival` | `AUDIT/CONSTITUTION.md#L3` | Primary Objective: Survival. Nuclear Button. | High | Critical |
| `const_default_deny` | `AUDIT/CONSTITUTION.md#L12` | Default Deny Principle. Zero Trust. | High | Critical |
| `const_evidence` | `AUDIT/CONSTITUTION.md#L22` | Evidence Chain. Crypto Audit. | High | Critical |

## 2. Strategies (A2 Scan)
| Component ID | Source Ref | Intent Summary | Value | Risk |
|---|---|---|---|---|
| `strat_trend_follow` | `strategies/template_trend_following.py` | Trend Following based on MA/ATR. | Medium | Low |
| `strat_mean_revert` | `strategies/template_mean_reversion.py` | Mean Reversion Strategy. | Medium | Low |
| `strat_multi_factor` | `strategies/template_multi_factor.py` | Multi-Factor Model. | High | Medium |

## 3. Core Runtime (A3 Scan)
| Component ID | Source Ref | Intent Summary | Value | Risk |
|---|---|---|---|---|
| `core_time_machine` | `gm-core/gm_core/time.py` (Inferred) | Time Semantics (Event vs Available). | High | High |
| `core_permit_gate` | `gm_os/inner/permit.py` (Inferred) | Permit Token Generation. | High | Critical |

## 4. Audit Tools (A4 Scan)
| Component ID | Source Ref | Intent Summary | Value | Risk |
|---|---|---|---|---|
| `audit_evidence_schema` | `AUDIT/EVIDENCE_SCHEMA.md` | Schema definition for evidence. | High | Medium |
