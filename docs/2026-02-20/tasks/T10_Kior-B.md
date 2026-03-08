# Task Skill Spec

```yaml
task_id: "T10"
executor: "Kior-B"
wave: "Wave 2"
depends_on: ["T7", "T8", "T9"]
estimated_minutes: 80

input:
  description: "将 run_intent/fetch_pack/query_rag 三能力接入 n8n 实流并完成最小 E2E 演练"
  context_files:
    - path: "docs/2026-02-20/n8n/l45_day1_workflow.json"
      purpose: "沿用 Day-1 工作流骨架"
    - path: "skillforge/src/contracts/api/n8n_boundary_v1.yaml"
      purpose: "边界字段与角色约束"
    - path: "docs/2026-02-20/L45_RUN_INTENT_PRODUCTION_REPORT_v1.md"
      purpose: "核对 run_intent 实际接口行为"
    - path: "docs/2026-02-20/L45_FETCH_PACK_PRODUCTION_REPORT_v1.md"
      purpose: "核对 fetch_pack 实际接口行为"
    - path: "docs/2026-02-20/L45_QUERY_RAG_PRODUCTION_REPORT_v1.md"
      purpose: "核对 query_rag 实际接口行为"
  constants:
    job_id: "L45-D2-ORCH-MINCAP-20260220-002"
    skill_id: "l45_orchestration_min_capabilities"

output:
  deliverables:
    - path: "docs/2026-02-20/n8n/l45_day2_mincap_workflow.json"
      type: "新建"
      schema_ref: "n8n workflow export JSON"
    - path: "docs/2026-02-20/n8n/l45_day2_mincap_runbook.md"
      type: "新建"
      schema_ref: "运行步骤 + 异常分支策略"
    - path: "docs/2026-02-20/L45_N8N_MINCAP_E2E_REPORT_v1.md"
      type: "新建"
      schema_ref: "1 成功 + 2 失败实流报告"
  constraints:
    - "必须跑通 1 条成功链路（run_intent->fetch_pack->query_rag）"
    - "必须覆盖 2 条失败链路（E001 与 E003）"
    - "业务错误(E001/E003)禁止自动重试"
    - "报告必须带 run_id/evidence_ref/gate_decision/replay_pointer"

deny:
  - "不得在 n8n 节点中生成最终裁决"
  - "不得跳过 boundary adapter 直接写后端内部模块"
  - "不得修改 T7/T8/T9 的接口合同字段名"

gate:
  auto_checks:
    - command: "python -m json.tool docs/2026-02-20/n8n/l45_day2_mincap_workflow.json > nul"
      expect: "valid json"
  manual_checks:
    - "流程中的 IF/Route 仅消费 SkillForge gate_decision"
    - "报告中明确给出失败分支未重试证据"
```

