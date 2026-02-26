---
name: library-intent-mainline-mapper-skill
description: 将图书馆迁移映射表中的 accept 条目接入主链 intent_map，并校验覆盖率与合同可解析性。
---

# library-intent-mainline-mapper-skill

## 触发条件

- 已有 `library_intent_mapping_v2.md`
- 需要把 `accept` 条目接入 `intent_map.yml`
- 需要替换 placeholder 报告为真实执行报告

## 输入

```yaml
input:
  mapping_doc: "docs/2026-02-17/图书馆迁移/library_intent_mapping_v2.md"
  target_map: "skillforge/src/orchestration/intent_map.yml"
  check_script: "scripts/run_library_migration_e2e_check.py"
```

## 输出

```yaml
output:
  - "skillforge/src/orchestration/intent_map.yml"
  - "docs/2026-02-17/图书馆迁移/audit_repo_e2e_dry_run_report_v1.md"
  - "coverage_result: accept_coverage=100%"
```

## DoD

- [ ] `accept` 条目全部进 `intent_map.yml`
- [ ] 合同路径可解析（missing_contract_paths=0）
- [ ] E2E 报告状态为 `EXECUTED`（非 PLACEHOLDER）
- [ ] 结论与映射统计一致

