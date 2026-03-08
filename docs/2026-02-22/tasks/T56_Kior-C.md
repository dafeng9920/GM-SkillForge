task_id: "T56"
executor: "Kior-C"
reviewer: "vs--cc2"
compliance_officer: "Kior-B"
wave: "Wave 3"
depends_on: ["T53", "T54", "T55"]
estimated_minutes: 45

input:
  description: "P1-3 Demo 脚本：5 分钟链路（跑审计 -> 产物 -> 前端展示）"
  context_files:
    - path: "docs/2026-02-22/TODO.md"
      purpose: "对齐 P1-3"
  constants:
    job_id: "L3-CLOSING-20260222-001"
    task_scope: "P1-3"

output:
  deliverables:
    - path: "docs/2026-02-22/DEMO_STEPS.md"
      type: "新建"
  constraints:
    - "5 分钟内可复现"

deny:
  - "不得遗漏前置依赖说明"

gate:
  auto_checks:
    - command: "python scripts/run_skill_5layer_audit.py --domains finance,legal --top-n 3"
      expect: "exit 0"
  manual_checks:
    - "文档含完整命令与预期输出"

# 改派记录
reassignment:
  from_executor: "Kior-B"
  to_executor: "Kior-C"
  from_compliance: "Kior-C"
  to_compliance: "Kior-B"
  reason: "任务执行者改派"
  timestamp: "2026-02-22T00:00:00Z"
