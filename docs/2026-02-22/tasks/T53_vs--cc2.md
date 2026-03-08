task_id: "T53"
executor: "vs--cc2"
reviewer: "Kior-A"
compliance_officer: "Kior-C"
wave: "Wave 2"
depends_on: ["T51", "T52"]
estimated_minutes: 50

input:
  description: "P0-4 CI smoke gate：新增 l5-static 审计门禁"
  context_files:
    - path: ".github/workflows/l5-gate.yml"
      purpose: "复用现有门禁"
    - path: "docs/2026-02-22/TODO.md"
      purpose: "对齐 P0-4"
  constants:
    job_id: "L3-CLOSING-20260222-001"
    task_scope: "P0-4"

output:
  deliverables:
    - path: ".github/workflows/l5-gate.yml"
      type: "修改"
  constraints:
    - "新增步骤执行 l5-static 审计 smoke"
    - "FAIL>0 直接 exit 1"

deny:
  - "不得将 gate 改为软失败"

gate:
  auto_checks:
    - command: "python scripts/run_skill_5layer_audit.py --domains finance,legal --top-n 3"
      expect: "exit 0"
  manual_checks:
    - "workflow 中存在 audit smoke step"
