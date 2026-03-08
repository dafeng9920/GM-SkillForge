task_id: "T55"
executor: "vs--cc1"
reviewer: "Kior-B"
compliance_officer: "Kior-C"
wave: "Wave 2"
depends_on: ["T54"]
estimated_minutes: 60

input:
  description: "P1-2 前后端数据契约：定义 summary/results schema 并在前端加载前校验"
  context_files:
    - path: "reports/skill-audit"
      purpose: "审计 JSON 样本"
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      purpose: "接入校验"
  constants:
    job_id: "L3-CLOSING-20260222-001"
    task_scope: "P1-2"

output:
  deliverables:
    - path: "schemas/skill_audit_report.schema.json"
      type: "新建"
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      type: "修改"
  constraints:
    - "字段缺失必须显示可读错误"

deny:
  - "不得静默吞掉校验失败"

gate:
  auto_checks:
    - command: "npm --prefix ui/app run build"
      expect: "passed"
  manual_checks:
    - "坏 JSON 输入时出现错误提示"
