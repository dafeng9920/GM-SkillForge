# GM-SkillForge 5-Layer Audit Report

- Date: 2026-02-22
- Profile: l5-static
- Policy version: v1.0.0-20260222
- Scope: domains=finance top_n=1 size_rank=chars
- Run ID: `L5S-20260222045724Z-56E64A7F`
- Evidence Ref: `EV-L5S-L5S-20260222045724Z-56E64A7F`
- Input Hash: `8b9ee8ff5424a45b2b01b8f34c78cc492d95899875b3d421b1c0d6a400a1b1c7`
- Result Hash: `2b3be2e37930567b3193e7d8b96bdebd9cc5df5c9da78f7c3915b00cda3ab83f`
- Sample size: 1
- Gate counts: PASS 1 | WARN 0 | FAIL 0
- Avg overall score: 74.0
- Avg estimated tokens per skill: 4158.0

## Result Table
| Skill | Domain | Gate | Score | Est Tokens | Evidence Ref |
|---|---|---:|---:|---:|---|
| audit-support | finance | PASS | 74.0 | 4158 | `EV-L5S-L5S-20260222045724Z-56E64A7F-finance-audit-support` |

## Conclusion
- Overall: PASS (all sampled skills passed gate).

## Limitations
- Static-only audit; no runtime GPU/memory/latency stress checks.
- Token count is policy estimator unless tokenizer adapter is enabled.