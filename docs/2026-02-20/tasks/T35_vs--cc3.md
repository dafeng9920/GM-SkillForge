# Task Skill Spec

```yaml
task_id: "T35"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "前端骨架与信息架构收敛：落地 v1.0 五页路由与统一导航框架"
  context_files:
    - path: "docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md"
      purpose: "v1.7 冻结范围（v1.0 先行）"
    - path: "docs/2026-02-20/task_dispatch_T35-T40_frontend_v1.0.md"
      purpose: "批次规则与收口标准"
  constants:
    job_id: "L45-FE-V10-20260220-007"
    skill_id: "l45_frontend_v10_execution_pack"
  execution_guard:
    proposal_guard_ref: "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    execution_guard_ref: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    required_artifacts:
      - "docs/2026-02-20/verification/T35_execution_contract.json"
      - "docs/2026-02-20/verification/T35_compliance_attestation.json"
      - "docs/2026-02-20/verification/T35_evidence_refs.json"
    permit_required_when_side_effects:
      - "PUBLISH"
      - "EXTERNAL_API"
    must_pass:
      - "compliance_attestation.decision == PASS"
      - "compliance_attestation.evidence_refs is not empty"
      - "contract_hash matches execution_contract hash"

output:
  deliverables:
    - path: "ui/app/src/app/router.tsx"
      type: "新建或更新"
      schema_ref: "v1.0 路由：/execute/run-intent, /execute/import-skill, /audit/packs, /audit/rag-query, /system/health"
    - path: "ui/app/src/app/layout/AppShell.tsx"
      type: "新建或更新"
      schema_ref: "一级导航 3 组（执行/审计/系统）"
    - path: "docs/2026-02-20/L45_FE_T35_IA_ROUTING_REPORT_v1.md"
      type: "新建"
      schema_ref: "IA 与路由收敛报告"
  constraints:
    - "不得出现 n8n 顶层一级导航"
    - "v1.0 不新增 /governance/release 页面"
    - "Top Bar 必须预留 run_id 全局检索入口"

deny:
  - "不得引入超出 v1.0 范围的新业务页面"

gate:
  auto_checks:
    - command: "cd ui/app; npm run build"
      expect: "passed"
  deny_without_execution_guard: true
```
