# Task Skill Spec

```yaml
task_id: "T38"
executor: "Kior-B"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "审计与查询页：Audit Packs + RAG Query 打通证据闭环"
  context_files:
    - path: "docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md"
      purpose: "fetch_pack/query_rag 字段与错误码口径"
    - path: "ui/app/src/mocks/orchestrationProjection.mock.ts"
      purpose: "Mock 数据对齐"
  constants:
    job_id: "L45-FE-V10-20260220-007"
    routes:
      - "/audit/packs"
      - "/audit/rag-query"
  execution_guard:
    proposal_guard_ref: "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    execution_guard_ref: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    required_artifacts:
      - "docs/2026-02-20/verification/T38_execution_contract.json"
      - "docs/2026-02-20/verification/T38_compliance_attestation.json"
      - "docs/2026-02-20/verification/T38_evidence_refs.json"
    permit_required_when_side_effects:
      - "PUBLISH"
      - "EXTERNAL_API"
    must_pass:
      - "compliance_attestation.decision == PASS"
      - "compliance_attestation.evidence_refs is not empty"
      - "contract_hash matches execution_contract hash"

output:
  deliverables:
    - path: "ui/app/src/pages/audit/AuditPacksPage.tsx"
      type: "新建或更新"
      schema_ref: "列表+详情+JSON/replay_pointer"
    - path: "ui/app/src/pages/audit/RagQueryPage.tsx"
      type: "新建或更新"
      schema_ref: "查询表单+结果片段+evidence_ref"
    - path: "ui/app/src/components/governance/EvidenceDrawer.tsx"
      type: "新建"
      schema_ref: "证据 JSON 抽屉（可复制）"
    - path: "docs/2026-02-20/L45_FE_T38_AUDIT_RAG_REPORT_v1.md"
      type: "新建"
      schema_ref: "审计与查询闭环验收报告"
  constraints:
    - "run_id/evidence_ref 在两页都必须可点击跳转"
    - "RAG 命中项必须显示 evidence_ref"
    - "at_time 漂移错误必须按 Fail-Closed 结构展示"

deny:
  - "不得出现 evidence_ref 无交互锚点"

gate:
  auto_checks:
    - command: "cd ui/app; npm run build"
      expect: "passed"
  deny_without_execution_guard: true
```
