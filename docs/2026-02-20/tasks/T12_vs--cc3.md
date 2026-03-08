# Task Skill Spec

```yaml
task_id: "T12"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "外部 Skill 导入入口治理：新增 import_external_skill 编排入口，固化 n8n 仅触发/路由，最终裁决归 SkillForge"
  context_files:
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      purpose: "现有 n8n 编排入口"
    - path: "docs/2026-02-19/contracts/external_skill_governance_contract_v1.yaml"
      purpose: "外部 Skill 治理合同基线"
    - path: "docs/2026-02-20/task_dispatch_T12-T16_external_skill_governance.md"
      purpose: "读取全局常量和收口要求"
  constants:
    job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
    skill_id: "l45_external_skill_governance_batch1"

output:
  deliverables:
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      type: "修改"
      schema_ref: "新增 /api/v1/n8n/import_external_skill"
    - path: "skillforge/tests/test_n8n_import_external_skill.py"
      type: "新建"
      schema_ref: "成功 + fail-closed + forbidden 注入测试"
    - path: "docs/2026-02-20/L45_IMPORT_EXTERNAL_SKILL_REPORT_v1.md"
      type: "新建"
      schema_ref: "实现与验证报告"
  constraints:
    - "run_id/evidence_ref 必须由 SkillForge 内部生成"
    - "外部输入不得注入 gate_decision/release_allowed/evidence_ref/run_id"
    - "失败分支必须 fail-closed"
    - "响应必须带 gate_decision + required_changes（失败时）"

deny:
  - "不得绕过现有 gate 链直接放行"
  - "不得修改既有 run_intent/fetch_pack/query_rag 合同字段语义"
  - "不得在 n8n 层生成最终裁决"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_n8n_import_external_skill.py"
      expect: "passed"
  manual_checks:
    - "确认 import_external_skill 输出结构可审计"
    - "确认 fail-closed 分支均返回结构化错误信封"
```

