task_id: "T62"
executor: "Antigravity-2"
reviewer: "vs--cc2"
compliance_officer: "Kior-C"
wave: "Wave 2"
depends_on: ["T60", "T61"]
estimated_minutes: 45

input:
  description: "P1-3 演示链路闭环：5分钟复现步骤（审计命令 -> 产物 -> 前端查看）"
  context_files:
    - path: "docs/2026-02-22/task_dispatch_p1.md"
      purpose: "目标与依赖"
    - path: "scripts/skillforge_audit.py"
      purpose: "统一入口命令"
    - path: "ui/app/src/pages/audit/SkillAuditPage.tsx"
      purpose: "前端展示入口"
  constants:
    job_id: "L4-P1-FOUNDATION-20260222-002"
    scope: "P1-3"

output:
  deliverables:
    - path: "docs/2026-02-22/DEMO_STEPS_P1.md"
      type: "新建"
  constraints:
    - "5分钟内可复现"
    - "必须写明前置依赖与预期输出"

deny:
  - "不得省略失败分支说明"

gate:
  auto_checks:
    - command: "python scripts/skillforge_audit.py audit run --profile l5-static --domains finance,legal --top-n 3"
      expect: "exit 0"
  manual_checks:
    - "文档包含完整命令、产物路径、排错提示"

compliance:
  required: true
  attestation_path: "docs/2026-02-22/verification/T62_compliance_attestation.json"
  permit_required_for_side_effects: false
