task_id: "T60"
executor: "Kior-A"
reviewer: "vs--cc3"
compliance_officer: "Kior-C"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "P1-1 审计结果页 MVP 强化：真实 JSON 渲染、排序、结论与限制区可读可用"
  context_files:
    - path: "ui/app/src/app/router.tsx"
      purpose: "接入/确认路由"
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      purpose: "页面实现"
    - path: "reports/skill-audit/*.json"
      purpose: "真实数据源"
  constants:
    job_id: "L4-P1-FOUNDATION-20260222-002"
    scope: "P1-1"

output:
  deliverables:
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      type: "新建或修改"
    - path: "ui/app/src/app/router.tsx"
      type: "必要时修改"
  constraints:
    - "桌面与移动端可读可用"
    - "支持按 Gate/Score/Domain 排序"
    - "必须使用真实审计 JSON，不得仅 mock"

deny:
  - "不得删除现有 governance 组件"
  - "不得绕过错误显示逻辑"

gate:
  auto_checks:
    - command: "npm --prefix ui/app run build"
      expect: "passed"
  manual_checks:
    - "页面可见 summary/results/limitations"

compliance:
  required: true
  attestation_path: "docs/2026-02-22/verification/T60_compliance_attestation.json"
  permit_required_for_side_effects: false
