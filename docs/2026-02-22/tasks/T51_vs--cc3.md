task_id: "T51"
executor: "vs--cc3"
reviewer: "Kior-A"
compliance_officer: "Kior-C"
wave: "Wave 1"
depends_on: ["T50"]
estimated_minutes: 75

input:
  description: "P0-1 审计入口产品化：统一命令入口 skillforge audit run --profile l5-static"
  context_files:
    - path: "docs/2026-02-22/TODO.md"
      purpose: "对齐 P0-1 目标"
    - path: "scripts/run_skill_5layer_audit.py"
      purpose: "复用审计能力"
  constants:
    job_id: "L3-CLOSING-20260222-001"
    task_scope: "P0-1"

output:
  deliverables:
    - path: "scripts/skillforge_audit.py"
      type: "新建"
  constraints:
    - "必须支持: audit run --profile l5-static --domains --top-n --output-dir"
    - "不得破坏原脚本直接运行能力"

deny:
  - "不得硬编码固定 domain"
  - "不得移除 profile 参数"

gate:
  auto_checks:
    - command: "python scripts/skillforge_audit.py audit run --profile l5-static --domains finance,legal --top-n 3"
      expect: "exit 0"
  manual_checks:
    - "非作者按单命令可复跑"
