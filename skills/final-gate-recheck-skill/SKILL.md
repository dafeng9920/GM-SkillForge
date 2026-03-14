---
name: final-gate-recheck-skill
description: Recheck final gate denial causes and produce minimal remediation actions. Use when execution/review look successful but final decision is DENY or inconsistent.
---

# final-gate-recheck-skill

## 触发条件

- 执行/审查看起来成功但最终决策是 DENY
- 最终门控决策不一致
- 需要解释门控拒绝原因并生成最小修复动作

## 输入

```yaml
input:
  verification_dir: "docs/2026-03-04/verification"
  prefix: "PR5"  # or "T-S2", "L4-01", etc.
  out: "docs/2026-03-04/verification/PR5_recheck_report.json"
```

## 输出

```yaml
output:
  recheck_status: "CONSISTENT|INCONSISTENT"
  blockers:
    - "Missing file: PR5_compliance_attestation.json"
    - "Review decision: DENY"
  required_changes:
    - "Generate compliance attestation"
    - "Address review feedback"
  decision_path:
    execution: "PASS"
    review: "DENY"
    compliance: "MISSING"
    final_gate: "DENY"
  is_inconsistent: true
```

## 检查项

1. **必需记录存在性**:
   - execution report
   - review decision
   - compliance attestation
   - final gate decision

2. **决策一致性**:
   - 如果 execution 完成 + review 允许 + compliance 通过，最终门控不应是 deny

3. **阻塞提取**:
   - 缺失文件
   - review/final 中的非 ALLOW 决策
   - compliance 中的非 PASS 决策

## 脚本模式

```powershell
python skills/final-gate-recheck-skill/scripts/recheck_final_gate.py --verification-dir docs/2026-03-04/verification --prefix PR5 --out docs/2026-03-04/verification/PR5_recheck_report.json
```

## Non-goals

- Do not rewrite gate decisions
- Do not auto-approve failed compliance
- Do not execute cloud-side actions

## DoD

- [ ] 所需记录已检查
- [ ] 决策一致性已验证
- [ ] 阻塞因素已识别
- [ ] 最小修复动作已生成
- [ ] 机器可读报告已输出
