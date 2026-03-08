# GM-SkillForge 5-Layer Audit Report (Finance+Legal Top10)

- Date: 2026-02-21
- Scope: knowledge-work-plugins finance+legal top10 by SKILL.md size
- Sample size: 10
- Gate counts: PASS 1 | WARN 9 | FAIL 0
- Avg overall score: 80.8
- Avg estimated tokens per skill: 2903.9
- High-cost skills (>=3000 est tokens): 3
- High-redundancy skills (repeat_ratio>=0.26): 0

## 5-Layer Definition (Static Template v1)
- L1 Cost: prompt footprint by estimated tokens (chars/4).
- L2 Redundancy: repeated non-empty line ratio.
- L3 Safety: presence of disclaimer/review warnings in high-stakes domains.
- L4 Structure: frontmatter completeness + heading structure.
- L5 Evidence-ready: checklist/steps/table density + broken relative links.

## Result Table
| Skill | Domain | Gate | Score | Est Tokens | Repeat Ratio | L1 | L2 | L3 | L4 | L5 |
|---|---|---:|---:|---:|---:|---|---|---|---|---|
| canned-responses | legal | PASS | 85.1 | 2892 | 0.074 | WARN | PASS | PASS | PASS | PASS |
| legal-risk-assessment | legal | WARN | 74.1 | 3145 | 0.078 | FAIL | PASS | WARN | PASS | WARN |
| audit-support | finance | WARN | 74.8 | 4158 | 0.035 | FAIL | PASS | PASS | PASS | PASS |
| contract-review | legal | WARN | 78.9 | 2715 | 0.082 | WARN | PASS | WARN | PASS | WARN |
| nda-triage | legal | WARN | 81.6 | 2871 | 0.008 | WARN | PASS | WARN | PASS | PASS |
| financial-statements | finance | WARN | 81.6 | 2501 | 0.044 | WARN | PASS | WARN | PASS | PASS |
| meeting-briefing | legal | WARN | 81.6 | 2248 | 0.042 | WARN | PASS | WARN | PASS | PASS |
| compliance | legal | WARN | 82.5 | 3204 | 0.012 | FAIL | PASS | PASS | PASS | PASS |
| variance-analysis | finance | WARN | 83.7 | 2787 | 0.104 | WARN | PASS | WARN | PASS | PASS |
| close-management | finance | WARN | 83.7 | 2518 | 0.024 | WARN | PASS | WARN | PASS | PASS |

## Publishable Conclusion (v1)
- Hypothesis status: PARTIALLY CONFIRMED.
- Evidence indicates quality risk is concentrated in token efficiency and prompt footprint, while baseline safety language is mostly present.
- Recommendation: prioritize semantic compression + regression tests before broad systemic safety claims.

## Limitations
- This run is static-only; no runtime latency/memory/async deadlock testing.
- Token values are estimated, not model-specific tokenizer counts.
- Thresholds are deterministic policy rules and should be versioned with benchmark validation.