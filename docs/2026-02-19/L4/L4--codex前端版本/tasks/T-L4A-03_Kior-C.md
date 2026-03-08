# Task Skill Spec: T-L4A-03
# Executor: Kior-C

# 元信息
task_id: "T-L4A-03"
executor: "Kior-C"
wave: "L4-A"
depends_on: ["T-L4A-02"]
estimated_minutes: 60

# 输入合同 (Input Contract)
input:
  description: "Execute E2E Verification for L4-A."
  context_files:
    - path: "ui/app/src/views/L4Workbench.tsx"
      purpose: "Test Target"
  constants:
    test_matrix: "T1-T7"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "docs/2026-02-19/L4A_e2e_drill_report_v1.md"
      type: "新建"
      description: "Detailed report of T1-T7 execution."
    - path: "docs/2026-02-19/L4A_acceptance_checklist_v1.md"
      type: "新建"
      description: "Final checklist for L4-A signoff."

  constraints:
    - "Must include screenshots or logs for T6 (E001) and T7 (E003)."
    - "Must verify 'replay_pointer' is present in at least one case."

# 红线 (Deny List)
deny:
  - "不得跳过 T6/T7 阻断测试"

# 质量门禁 (Gate Check)
gate:
  manual_checks:
    - "Report contains evidence for all 7 test cases."
    - "Checklist 'Governance Consistency' section is fully checked."
