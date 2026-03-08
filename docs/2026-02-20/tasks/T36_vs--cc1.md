# Task Skill Spec

```yaml
task_id: "T36"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "执行中心页：Run Intent（先结论后细节）+ OrchestrationProjection 映射接入"
  context_files:
    - path: "docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md"
      purpose: "Run Intent 字段与展示规则"
    - path: "ui/app/src/types/orchestrationProjection.ts"
      purpose: "前端统一投影类型"
    - path: "ui/app/src/mappers/orchestrationProjectionMapper.ts"
      purpose: "真实 API -> Projection 转换"
  constants:
    job_id: "L45-FE-V10-20260220-007"
    page_route: "/execute/run-intent"
  execution_guard:
    proposal_guard_ref: "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    execution_guard_ref: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    required_artifacts:
      - "docs/2026-02-20/verification/T36_execution_contract.json"
      - "docs/2026-02-20/verification/T36_compliance_attestation.json"
      - "docs/2026-02-20/verification/T36_evidence_refs.json"
    permit_required_when_side_effects:
      - "PUBLISH"
      - "EXTERNAL_API"
    must_pass:
      - "compliance_attestation.decision == PASS"
      - "compliance_attestation.evidence_refs is not empty"
      - "contract_hash matches execution_contract hash"

output:
  deliverables:
    - path: "ui/app/src/pages/execute/RunIntentPage.tsx"
      type: "新建或更新"
      schema_ref: "结论卡片 + 输入表单 + 时间线 + 证据抽屉"
    - path: "ui/app/src/components/governance/DecisionHeroCard.tsx"
      type: "新建"
      schema_ref: "gate_decision/release_allowed 首屏卡片"
    - path: "docs/2026-02-20/L45_FE_T36_RUN_INTENT_REPORT_v1.md"
      type: "新建"
      schema_ref: "Run Intent 页面验收报告"
  constraints:
    - "gate_decision + release_allowed 必须位于首屏第一视觉落点"
    - "evidence_ref 必须可点击并可复制 run_id+evidence_ref"
    - "所有错误分支必须复用 BlockReasonCard"

deny:
  - "不得把 evidence_ref 仅作为纯文本展示"

gate:
  auto_checks:
    - command: "cd ui/app; npm run build"
      expect: "passed"
  deny_without_execution_guard: true
```
