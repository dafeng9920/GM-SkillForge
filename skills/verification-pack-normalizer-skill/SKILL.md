---
name: verification-pack-normalizer-skill
description: Normalize verification evidence packs into stable naming and schema summaries. Use when verification files exist but naming/structure is inconsistent.
---

# verification-pack-normalizer-skill

## 触发条件

- 验证文件存在但命名/结构不一致
- 需要标准化执行/审查/合规/最终门控记录
- 最终裁决前需要规范化

## 输入

```yaml
input:
  verification_dir: "docs/2026-03-04/verification"
  prefix: "PR5"  # or "T-S1", "L4-01", etc.
  out: "docs/2026-03-04/verification/PR5_normalization_report.json"
  apply: false  # set true to write canonical alias files
```

## 输出

```yaml
output:
  normalized: true
  canonical_files:
    execution_report: "PR5_execution_report.yaml"
    review_decision: "PR5_review_decision.json"
    compliance_attestation: "PR5_compliance_attestation.json"
    final_gate_decision: "PR5_final_gate_decision.json"
  variants_detected:
    - "PR5_review_decision_AG2.json"
  aliases_created:
    - "PR5_review_decision.json" -> "PR5_review_decision_AG2.json"
  missing_canonical: []
  normalization_report: "path/to/report.json"
```

## 标准化目标

规范期望文件：

- `<PREFIX>_execution_report.yaml`
- `<PREFIX>_review_decision.json`
- `<PREFIX>_compliance_attestation.json`
- `<PREFIX>_final_gate_decision.json`

## 功能

- 检测并记录变体文件
- 如果规范文件缺失，生成规范别名文件 (`--apply`)
- 不覆盖现有规范文件
- 始终发出机器可读报告

## 决策规则

- 当别名逻辑后规范集完成时报告 `normalized=true`
- 不覆盖现有规范文件
- 始终发出机器可读报告

## 脚本模式

```powershell
python skills/verification-pack-normalizer-skill/scripts/normalize_pack.py --verification-dir docs/2026-03-04/verification --prefix PR5 --out docs/2026-03-04/verification/PR5_normalization_report.json --apply
```

## Non-goals

- Do not modify business execution artifacts
- Do not infer compliance status
- Do not adjudicate final gate decision

## DoD

- [ ] 所有变体文件已检测
- [ ] 规范别名文件已创建 (如 apply=true)
- [ ] 规范化报告已生成
- [ ] 缺失文件已记录
