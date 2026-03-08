# Task Skill Spec

```yaml
task_id: "T3"
executor: "Kior-B"
wave: "Wave 1"
depends_on: ["T2"]
estimated_minutes: 60

input:
  description: "按边界合同落地 n8n 最小工作流，仅做触发/路由/重试/通知"
  context_files:
    - path: "skillforge/src/contracts/api/n8n_boundary_v1.yaml"
      purpose: "对齐允许字段与禁止字段"
    - path: "docs/2026-02-20/L45_N8N_BOUNDARY_CONTRACT_v1.md"
      purpose: "对齐边界策略与错误分支"
    - path: "docs/2026-02-20/L4.5 启动清单 v2（2026-02-20）.md"
      purpose: "对齐 Day-1 验收项"
  constants:
    job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
    skill_id: "l45_n8n_orchestration_boundary"

output:
  deliverables:
    - path: "docs/2026-02-20/n8n/l45_day1_workflow.json"
      type: "新建"
      schema_ref: "n8n workflow export JSON"
    - path: "docs/2026-02-20/n8n/l45_day1_runbook.md"
      type: "新建"
      schema_ref: "执行步骤 + 重试策略 + 回滚说明"
    - path: "docs/2026-02-20/L45_N8N_WORKFLOW_RUN_REPORT_v1.md"
      type: "新建"
      schema_ref: "一次真实运行记录"
  constraints:
    - "工作流必须调用 run_intent -> fetch_pack -> query_rag(at_time)"
    - "IF/Route 节点只能消费 SkillForge 返回的 gate_decision，不得自造"
    - "重试只允许网络/超时错误，业务错误(E001/E003)不得自动重试"
    - "运行报告必须包含 run_id/evidence_ref/gate_decision"

deny:
  - "不得在 n8n 节点内生成 release_allowed 决策"
  - "不得绕开 SkillForge API 直接写 registry 或证据"
  - "不得修改后端 Python 业务代码"

gate:
  auto_checks:
    - command: "python -m json.tool docs/2026-02-20/n8n/l45_day1_workflow.json > nul"
      expect: "valid json"
  manual_checks:
    - "流程图可见 trigger/route/retry/notify 四类职责"
    - "真实 run 报告中字段完整且可追溯"
```

