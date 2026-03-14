---
name: l3-killer-gate-runner-skill
description: 运行并裁决真L3 killer tests（A/B/C）并输出可审计结果。用于任何需要验证 Hard Gate/Integrity/Delta 是否回归的场景。
---

# l3-killer-gate-runner-skill

## 触发条件

- 需要验证 “真 L3” 是否保持通过
- 修改了 `engine.py` / `pack_publish.py` / `repository.py` / `skill_composer.py`
- PR 合并前、发布前、Final Gate 前

## 输入

```yaml
input:
  repo_root: "d:/GM-SkillForge"
  output_dir: "reports/l3_gap_closure/{date}"
  run_command: "python scripts/run_l3_gap_closure.py"
  require_all_pass: true
```

## 输出

```yaml
output:
  summary_json: "reports/l3_gap_closure/{date}/summary.json"
  summary_md: "reports/l3_gap_closure/{date}/summary.md"
  reports:
    - A_constitution_hard_gate.json
    - B_registry_graph_integrity.json
    - C_incremental_delta_enforced.json
  decision_hint: "PASS | FAIL"
```

## DoD

- [ ] A/B/C 三项测试均执行
- [ ] `summary.json` 生成且 `overall_status` 可读
- [ ] 失败项包含明确 `report_path`
- [ ] 可供 Final Gate 直接引用

