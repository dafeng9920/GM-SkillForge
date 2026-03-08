# GM-SkillForge 5-Layer Audit Report

- Date: 2026-02-22
- Profile: l5-static
- Policy version: v1.0.0-20260222
- Scope: domains=finance,legal top_n=3 size_rank=chars
- Run ID: `L5S-20260222053653Z-E93D9286`
- Evidence Ref: `EV-L5S-L5S-20260222053653Z-E93D9286`
- Input Hash: `ae2b9c980e9c3d27c5e7d95acc4a883cf5855a59336dffa8a59fdfca8a773a66`
- Result Hash: `5ac54c406076febf16bd5034002acd327f36a97b23675fcbea7d2b194b2fe4d7`
- Sample size: 3
- Gate counts: PASS 3 | WARN 0 | FAIL 0
- Avg overall score: 75.3
- Avg estimated tokens per skill: 3502.3

## Result Table
| Skill | Domain | Gate | Score | Est Tokens | Evidence Ref |
|---|---|---:|---:|---:|---|
| audit-support | finance | PASS | 74.0 | 4158 | `EV-L5S-L5S-20260222053653Z-E93D9286-finance-audit-support` |
| legal-risk-assessment | legal | PASS | 74.0 | 3145 | `EV-L5S-L5S-20260222053653Z-E93D9286-legal-legal-risk-assessment` |
| compliance | legal | PASS | 78.0 | 3204 | `EV-L5S-L5S-20260222053653Z-E93D9286-legal-compliance` |

## Conclusion
- Overall: PASS (all sampled skills passed gate).

## Limitations
- Static-only audit; no runtime GPU/memory/latency stress checks.
- Token count is policy estimator unless tokenizer adapter is enabled.