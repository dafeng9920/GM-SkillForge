# Task Skill Spec: T-L4A-02
# Executor: vs--cc3

# 元信息
task_id: "T-L4A-02"
executor: "vs--cc3"
wave: "L4-A"
depends_on: ["T-L4A-01"]
estimated_minutes: 90

# 输入合同 (Input Contract)
input:
  description: "Implement the L4-A Dual Window Frontend."
  context_files:
    - path: "skillforge/src/contracts/cognition/10d_schema.json"
      purpose: "For 10D Panel"
    - path: "skillforge/src/contracts/governance/work_item_schema.json"
      purpose: "For Adopt Logic"
  constants:
    frontend_root: "ui/app"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "ui/app/src/views/L4Workbench.tsx"
      type: "新建"
      description: "Main layout component with Divergence (Left) and Work (Right) windows."
    - path: "ui/app/src/components/CognitionPanel.tsx"
      type: "新建"
      description: "Renders 10D output in Divergence Window."
    - path: "ui/app/src/components/WorkItemPanel.tsx"
      type: "新建"
      description: "Renders Adopted Work Item in Work Window."
    - path: "ui/app/src/store/l4Slice.ts"
      type: "新建"
      description: "Redux slice for managing dual-window state."
    - path: "docs/2026-02-19/L4A_frontend_application_implementation_report_v1.md"
      type: "新建"
      description: "Implementation details."

  constraints:
    - "Strict separation: Divergence content cannot stay in state unless Adopted."
    - "Fail-Closed: 'Adopt' button disabled if required 10D fields are missing."
    - "Visual Feedback: Must show 'Blocked' state in Work Window for E001/E003."

# 红线 (Deny List)
deny:
  - "不得允许手动在 Work Window 输入非结构化文本"
  - "不得绕过 'Adopt' 动作直接写入 Work Window"

# 质量门禁 (Gate Check)
gate:
  manual_checks:
    - "Check T1: Free text in Left does NOT appear in Right."
    - "Check T4: Deleting a field disables the Adopt button (or fails validation)."
