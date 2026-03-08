task_id: "T50"
executor: "vs--cc1"
reviewer: "vs--cc2"
compliance_officer: "Kior-C"
wave: "Wave 1"
depends_on: []
estimated_minutes: 60

input:
  description: "P0-2 策略配置化与版本化：新增 audit_policy_v1，并让报告写入 policy_version"
  context_files:
    - path: "docs/2026-02-22/TODO.md"
      purpose: "对齐 P0-2 目标"
    - path: "scripts/run_skill_5layer_audit.py"
      purpose: "接入 policy 读取"
  constants:
    job_id: "L3-CLOSING-20260222-001"
    task_scope: "P0-2"

output:
  deliverables:
    - path: "configs/audit_policy_v1.json"
      type: "新建"
    - path: "scripts/run_skill_5layer_audit.py"
      type: "修改"
  constraints:
    - "报告 summary 必须出现 policy_version"
    - "阈值可改配置，不改代码"

deny:
  - "不得跳过 policy 版本字段"
  - "不得删除现有审计输出字段"

gate:
  auto_checks:
    - command: "python scripts/run_skill_5layer_audit.py --domains finance,legal --top-n 3"
      expect: "exit 0"
  manual_checks:
    - "json 输出包含 summary.policy_version"
