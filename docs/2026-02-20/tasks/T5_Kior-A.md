# Task Skill Spec

```yaml
task_id: "T5"
executor: "Kior-A"
wave: "Wave 2"
depends_on: ["T1", "T3", "T4"]
estimated_minutes: 75

input:
  description: "完成前端动作 -> n8n 编排 -> SkillForge 裁决 -> 证据回写 的胶合联调"
  context_files:
    - path: "skillforge/src/api/l4_api.py"
      purpose: "沿用 L4 成功/失败信封"
    - path: "docs/2026-02-20/n8n/l45_day1_workflow.json"
      purpose: "对接已落地编排流"
    - path: "skillforge/src/contracts/governance/n8n_execution_receipt.schema.json"
      purpose: "对齐回执结构"
    - path: "docs/2026-02-19/L4/l4_front_backend_integration_report_v1.md"
      purpose: "继承 L4 联调验证口径"
  constants:
    job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
    skill_id: "l45_n8n_orchestration_boundary"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_FRONT_BACK_N8N_INTEGRATION_REPORT_v1.md"
      type: "新建"
      schema_ref: "链路联调报告"
    - path: "docs/2026-02-20/integration/l45_request_response_samples.json"
      type: "新建"
      schema_ref: "成功/失败样例信封"
  constraints:
    - "至少覆盖 1 条成功链路与 2 条失败链路(E001,E003)"
    - "失败链路必须体现 fail-closed，不得隐式降级"
    - "样例中必须体现 at_time 固定输入"
    - "报告中必须给出 replay_pointer 或其为空的原因"

deny:
  - "不得修改 T1/T2/T4 已冻结合同字段名"
  - "不得新增非治理路径执行分支"
  - "不得篡改测试基线结果"

gate:
  auto_checks:
    - command: "pytest -q skillforge/tests/test_l4_api_smoke.py"
      expect: "passed"
  manual_checks:
    - "报告明确声明 n8n 无最终裁决权"
    - "前后端链路中的 gate_decision 来源为 SkillForge"
```

