task_id: "T54"
executor: "Kior-A"
reviewer: "vs--cc3"
compliance_officer: "Kior-C"
wave: "Wave 2"
depends_on: ["T51", "T52"]
estimated_minutes: 90

input:
  description: "P1-1 审计结果页 MVP：总览卡+明细表+结论限制区，读取 reports/skill-audit/*.json"
  context_files:
    - path: "ui/app/src/app/router.tsx"
      purpose: "接入路由"
    - path: "ui/app/src/pages"
      purpose: "新增页面"
  constants:
    job_id: "L3-CLOSING-20260222-001"
    task_scope: "P1-1"

output:
  deliverables:
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      type: "新建"
    - path: "ui/app/src/app/router.tsx"
      type: "修改"
  constraints:
    - "桌面/移动端可用"
    - "支持按 Gate/Score/Domain 排序"

deny:
  - "不得用假数据替代真实 JSON"

gate:
  auto_checks:
    - command: "npm --prefix ui/app run build"
      expect: "passed"
  manual_checks:
    - "页面可见 summary + results + limitations"
