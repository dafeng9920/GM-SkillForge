# Task Skill Spec

```yaml
task_id: "T39"
executor: "Kior-A"
wave: "Wave 1"
depends_on: []
estimated_minutes: 85

input:
  description: "系统运维页：Health 模块与全局统一错误拦截组件"
  context_files:
    - path: "docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md"
      purpose: "health 30s 轮询/阈值与 BlockReasonCard 规则"
  constants:
    job_id: "L45-FE-V10-20260220-007"
    page_route: "/system/health"
  execution_guard:
    proposal_guard_ref: "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    execution_guard_ref: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    required_artifacts:
      - "docs/2026-02-20/verification/T39_execution_contract.json"
      - "docs/2026-02-20/verification/T39_compliance_attestation.json"
      - "docs/2026-02-20/verification/T39_evidence_refs.json"
    permit_required_when_side_effects:
      - "PUBLISH"
      - "EXTERNAL_API"
    must_pass:
      - "compliance_attestation.decision == PASS"
      - "compliance_attestation.evidence_refs is not empty"
      - "contract_hash matches execution_contract hash"

output:
  deliverables:
    - path: "ui/app/src/pages/system/HealthPage.tsx"
      type: "新建或更新"
      schema_ref: "30s 轮询 + 红橙绿阈值 + 最近检查详情"
    - path: "ui/app/src/components/governance/BlockReasonCard.tsx"
      type: "新建"
      schema_ref: "拦截结论/触发规则/证据引用/建议修复"
    - path: "docs/2026-02-20/L45_FE_T39_HEALTH_BLOCKCARD_REPORT_v1.md"
      type: "新建"
      schema_ref: "系统运维与错误拦截验收报告"
  constraints:
    - "health 默认 30s 轮询且可配置"
    - "红橙绿阈值规则必须写在文档与代码常量"
    - "BLOCK 场景统一走 BlockReasonCard"

deny:
  - "不得在各页面散落自定义错误样式"

gate:
  auto_checks:
    - command: "cd ui/app; npm run build"
      expect: "passed"
  deny_without_execution_guard: true
```
