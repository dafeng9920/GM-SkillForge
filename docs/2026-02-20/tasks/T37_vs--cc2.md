# Task Skill Spec

```yaml
task_id: "T37"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "执行中心页：Import Skill 六步流水线 + Fail-Closed 断点恢复交互"
  context_files:
    - path: "docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md"
      purpose: "S1-S6 流水线与 required_changes 规则"
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      purpose: "import_external_skill 响应字段对齐"
  constants:
    job_id: "L45-FE-V10-20260220-007"
    page_route: "/execute/import-skill"
  execution_guard:
    proposal_guard_ref: "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    execution_guard_ref: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    required_artifacts:
      - "docs/2026-02-20/verification/T37_execution_contract.json"
      - "docs/2026-02-20/verification/T37_compliance_attestation.json"
      - "docs/2026-02-20/verification/T37_evidence_refs.json"
    permit_required_when_side_effects:
      - "PUBLISH"
      - "EXTERNAL_API"
    must_pass:
      - "compliance_attestation.decision == PASS"
      - "compliance_attestation.evidence_refs is not empty"
      - "contract_hash matches execution_contract hash"

output:
  deliverables:
    - path: "ui/app/src/pages/execute/ImportSkillPage.tsx"
      type: "新建或更新"
      schema_ref: "六步流水线可视化 + 每步详情抽屉"
    - path: "ui/app/src/components/governance/PipelineStepPanel.tsx"
      type: "新建"
      schema_ref: "失败原因+重试本步+回滚"
    - path: "docs/2026-02-20/L45_FE_T37_IMPORT_PIPELINE_REPORT_v1.md"
      type: "新建"
      schema_ref: "导入流水线验收报告"
  constraints:
    - "每个步骤 FAIL 时必须展示 evidence_ref"
    - "必须提供 重试本步/放弃并回滚 两个动作位"
    - "required_changes 列表必须可展开查看"

deny:
  - "不得仅做静态进度条而无断点恢复信息"

gate:
  auto_checks:
    - command: "cd ui/app; npm run build"
      expect: "passed"
  deny_without_execution_guard: true
```
