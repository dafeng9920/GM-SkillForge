# Task Skill Spec

```yaml
task_id: "T16"
executor: "Kior-C"
wave: "Wave 2"
depends_on: ["T12", "T13", "T14", "T15"]
estimated_minutes: 90

input:
  description: "完成 T12-T15 最终验收并输出外部 Skill 治理导入 Gate Decision"
  context_files:
    - path: "docs/2026-02-20/task_dispatch_T12-T16_external_skill_governance.md"
      purpose: "批次规则与目标口径"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T12-T16.md"
      purpose: "读取各小队执行事实"
    - path: "docs/2026-02-20/L45_FAIL_CLOSED_AT_TIME_DRILL_REPORT_v1.md"
      purpose: "引用 fail-closed + at-time 基线"
  constants:
    job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
    skill_id: "l45_external_skill_governance_batch1"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_EXTERNAL_SKILL_GOV_INTEGRATION_REPORT_v1.md"
      type: "新建"
      schema_ref: "Batch-1 收口报告"
    - path: "docs/2026-02-20/verification/T16_gate_decision.json"
      type: "新建"
      schema_ref: "ALLOW|REQUIRES_CHANGES|DENY"
    - path: "docs/2026-02-20/verification/T16_execution_report.yaml"
      type: "新建"
      schema_ref: "Execution Report"
  constraints:
    - "必须逐条核验外部 Skill 导入入口、包校验、RAG回放、治理矩阵"
    - "必须确认 fail-closed 与 at-time 一致性无漂移"
    - "任一关键项失败时不得给 ALLOW"
    - "报告需包含 blocking_issues 与 next_actions"

deny:
  - "不得跳过自动化检查直接签发 ALLOW"
  - "不得替上游任务补写实现代码"
  - "不得修改 T12-T15 依赖关系"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_n8n_import_external_skill.py skillforge/tests/test_external_skill_package_adapter.py skillforge/tests/test_external_skill_rag_adapter.py"
      expect: "passed"
  manual_checks:
    - "确认最终报告可直接用于主控签核"
    - "确认 decision 文件与执行事实一致"
```

