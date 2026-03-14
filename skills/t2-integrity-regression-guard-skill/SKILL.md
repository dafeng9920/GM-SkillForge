---
name: t2-integrity-regression-guard-skill
description: 保障 T2（Registry/Graph Integrity）不回退。用于篡改检测、冲突阻断和证据链校验的持续回归。
---

# t2-integrity-regression-guard-skill

## 触发条件

- 修改了 `repository.py`、`pack_publish.py`、`schema.py`
- 发现 `B_registry_graph_integrity` 失败或不稳定
- 发布前需要确认 tamper 一定触发 `DENY/rejected`

## 输入

```yaml
input:
  repo_root: "d:/GM-SkillForge"
  targeted_test:
    - "python scripts/l3_gap_closure/test_registry_graph_integrity.py"
  optional_full_run:
    - "python scripts/run_l3_gap_closure.py"
  expected_rules:
    tamper_must_block: true
    no_silent_pass: true
    ruling_required: true
```

## 输出

```yaml
output:
  primary_report: "reports/l3_gap_closure/{date}/B_registry_graph_integrity.json"
  optional_rerun_report: "reports/l3_gap_closure/{date}/B_rerun.json"
  required_assertions:
    - "tamper_applied=true"
    - "conflict_or_block_detected=true"
    - "publish_result.status=rejected"
    - "ruling.rule_id=INTEGRITY_TAMPER_DETECTED"
    - "evaluation.passed=true"
```

## DoD

- [ ] 篡改场景必定 `DENY`，且发布被阻断
- [ ] 报告中存在结构化 `ruling` 与证据字段
- [ ] 不存在 `silent pass`（冲突不可被吞掉）
- [ ] 回归脚本可重复执行并得到一致结论

