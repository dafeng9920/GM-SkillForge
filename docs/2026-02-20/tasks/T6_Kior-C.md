# Task Skill Spec

```yaml
task_id: "T6"
executor: "Kior-C"
wave: "Wave 3"
depends_on: ["T5"]
estimated_minutes: 90

input:
  description: "完成 L4.5 Day-1 最终验收：测试、审计、Gate Decision 输出"
  context_files:
    - path: "docs/2026-02-20/task_dispatch.md"
      purpose: "核对所有任务交付物是否齐全"
    - path: "docs/2026-02-20/L45_N8N_WORKFLOW_RUN_REPORT_v1.md"
      purpose: "核验真实工作流执行证据"
    - path: "docs/2026-02-20/L45_FRONT_BACK_N8N_INTEGRATION_REPORT_v1.md"
      purpose: "核验联调口径与失败分支"
    - path: "skillforge/tests/test_gate_permit.py"
      purpose: "E001/E003 语义回归基线"
  constants:
    job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
    skill_id: "l45_n8n_orchestration_boundary"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_DAY1_CLOSEOUT_v1.md"
      type: "新建"
      schema_ref: "Day-1 收口报告"
    - path: "docs/2026-02-20/verification/T6_gate_decision.json"
      type: "新建"
      schema_ref: "ALLOW|REQUIRES_CHANGES|DENY"
    - path: "docs/2026-02-20/verification/T6_execution_report.yaml"
      type: "新建"
      schema_ref: "Execution Report"
  constraints:
    - "必须给出 5 条 Day-1 验收项逐条结论"
    - "必须明确 E001/E003 是否漂移（结论 + 证据）"
    - "必须确认证据链字段完整(run_id/evidence_ref/gate_decision)"
    - "若任一项不满足，Gate Decision 只能是 REQUIRES_CHANGES 或 DENY"

deny:
  - "不得代替其他执行者补写业务实现代码"
  - "不得跳过自动化检查直接给 ALLOW"
  - "不得修改 task_dispatch 依赖关系"

gate:
  auto_checks:
    - command: "pytest -q skillforge/tests/test_gate_permit.py skillforge/tests/test_l4_api_smoke.py"
      expect: "passed"
    - command: "pytest -q skillforge/tests/test_membership_regression.py"
      expect: "passed"
  manual_checks:
    - "确认 n8n 仅触发/路由，不持有最终裁决"
    - "确认 closeout 报告可被主控官直接用于最终签核"
```

