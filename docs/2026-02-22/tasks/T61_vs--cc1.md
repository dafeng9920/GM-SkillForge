task_id: "T61"
executor: "vs--cc1"
reviewer: "Kior-B"
compliance_officer: "Kior-C"
wave: "Wave 1"
depends_on: ["T60"]
estimated_minutes: 60

input:
  description: "P1-2 契约校验：定义审计报告 schema，并在前端加载前校验，坏数据必须可读报错"
  context_files:
    - path: "reports/skill-audit/*.json"
      purpose: "样本结构"
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      purpose: "接入校验"
  constants:
    job_id: "L4-P1-FOUNDATION-20260222-002"
    scope: "P1-2"

output:
  deliverables:
    - path: "schemas/skill_audit_report.schema.json"
      type: "新建"
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      type: "修改"
  constraints:
    - "字段缺失时显示可读错误，禁止静默失败"
    - "summary/results 最小契约必须覆盖"

deny:
  - "不得将校验错误吞掉"

gate:
  auto_checks:
    - command: "npm --prefix ui/app run build"
      expect: "passed"
  manual_checks:
    - "构造坏 JSON 时页面出现明确错误提示"

compliance:
  required: true
  attestation_path: "docs/2026-02-22/verification/T61_compliance_attestation.json"
  permit_required_for_side_effects: false
