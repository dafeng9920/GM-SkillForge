---
name: v0-seal-adjudicator-skill
description: Execute GM-SkillForge v0 seal adjudication with three-power separation records. Use when finalizing PR1-PR5 governance closure.
---

# v0-seal-adjudicator-skill

## 触发条件

- 完成 PR1-PR5 治理周期
- 需要发布正式 V0_SEAL 决策工件
- 需要验证所需验证文件并关闭门控

## 输入

```yaml
input:
  verification_dir: "docs/2026-03-04/verification"
  date: "2026-03-04"
  source_of_truth: "docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md"
  expected_pr_gates: ["PR1", "PR2", "PR3", "PR4", "PR5"]
```

## 输出

```yaml
output:
  final_decision: "ALLOW|DENY"
  v0_seal_status: "GRANTED|DENIED"
  verification_results:
    PR1: "ALLOW"
    PR2: "ALLOW"
    PR3: "ALLOW"
    PR4: "ALLOW"
    PR5: "ALLOW"
  compliance_attestation: "VALID"
  artifacts:
    decision_json: "V0_SEAL_DECISION_2026-03-04.json"
    board_md: "V0_SEAL_BOARD_2026-03-04.md"
  blocking_reasons: []
```

## 所需文件

- `PR1_final_gate_decision.json`
- `PR2_final_gate_decision.json`
- `PR3_final_gate_decision.json`
- `PR4_final_gate_decision.json`
- `PR5_final_gate_decision.json`
- `PR5_compliance_attestation.json`

## 决策规则

- 如果任何必需文件缺失: `FINAL_DECISION=DENY` (fail-closed)
- 如果任何 PR 最终决策不是 `ALLOW`: `FINAL_DECISION=DENY`
- 如果所有检查通过: `FINAL_DECISION=ALLOW` and `V0_SEAL=GRANTED`

## 执行步骤

1. 验证验证目录中存在必需文件
2. 解析 PR1-PR5 最终门控文件并确认 `final_verdict` 或 `decision` 是 `ALLOW`
3. 生成两个工件：
   - `V0_SEAL_DECISION_<date>.json` (机器可读)
   - `V0_SEAL_BOARD_<date>.md` (人类可读)
4. 仅在 ALLOW 后手动更新 `docs/<date>/v0-L5/index.md` 状态行

## 脚本模式

```powershell
python skills/v0-seal-adjudicator-skill/scripts/issue_v0_seal.py --date 2026-03-04 --verification-dir docs/2026-03-04/verification
```

## Non-goals

- Do not modify business contracts (P5-*)
- Do not trigger cloud execution
- Do not bypass compliance missing states

## DoD

- [ ] 所需文件已验证存在
- [ ] 所有 PR 最终决策已确认
- [ ] V0_SEAL 决策工件已生成
- [ ] 状态文档已更新 (ALLOW 后)
- [ ] Fail-closed 规则已应用
