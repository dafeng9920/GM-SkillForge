# Task Skill Spec

```yaml
task_id: "T11"
executor: "Kior-C"
wave: "Wave 3"
depends_on: ["T10"]
estimated_minutes: 90

input:
  description: "完成 T7-T10 最终验收并输出 Day-2 Gate Decision（ALLOW/REQUIRES_CHANGES/DENY）"
  context_files:
    - path: "docs/2026-02-20/task_dispatch_T7-T11.md"
      purpose: "核对收口清单与验收口径"
    - path: "docs/2026-02-20/L45_N8N_MINCAP_E2E_REPORT_v1.md"
      purpose: "核验三能力实流结果"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T7-T11.md"
      purpose: "汇总各执行者自检结果"
    - path: "skillforge/tests/test_gate_permit.py"
      purpose: "E001/E003 语义回归基线"
  constants:
    job_id: "L45-D2-ORCH-MINCAP-20260220-002"
    skill_id: "l45_orchestration_min_capabilities"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_DAY2_MINCAP_CLOSEOUT_v1.md"
      type: "新建"
      schema_ref: "Day-2 收口报告"
    - path: "docs/2026-02-20/verification/T11_gate_decision.json"
      type: "新建"
      schema_ref: "ALLOW|REQUIRES_CHANGES|DENY"
    - path: "docs/2026-02-20/verification/T11_execution_report.yaml"
      type: "新建"
      schema_ref: "Execution Report"
  constraints:
    - "必须逐条核验 run_intent/fetch_pack/query_rag 三能力是否生产可用"
    - "必须确认 E001/E003 语义无漂移（结论 + 证据）"
    - "必须核对证据链字段完整(run_id/evidence_ref/gate_decision)"
    - "任一关键项不满足时 Gate Decision 不得为 ALLOW"

deny:
  - "不得代替上游任务补写实现代码"
  - "不得跳过自动化检查直接签 ALLOW"
  - "不得修改 task_dispatch_T7-T11 依赖关系"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_n8n_run_intent_production.py skillforge/tests/test_n8n_fetch_pack_production.py skillforge/tests/test_n8n_query_rag_production.py"
      expect: "passed"
    - command: "python -m pytest -q skillforge/tests/test_gate_permit.py skillforge/tests/test_n8n_orchestration.py"
      expect: "passed"
  manual_checks:
    - "确认 n8n 未越权持有最终裁决权"
    - "确认 closeout 报告可直接用于主控签核"
```

