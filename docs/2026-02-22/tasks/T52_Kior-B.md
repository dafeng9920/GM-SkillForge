task_id: "T52"
executor: "Kior-B"
reviewer: "vs--cc1"
compliance_officer: "Kior-C"
wave: "Wave 1"
depends_on: ["T50"]
estimated_minutes: 75

input:
  description: "P0-3 证据链标准输出：run_id/evidence_ref/input_hash/result_hash + runs/<run_id>/"
  context_files:
    - path: "docs/2026-02-22/TODO.md"
      purpose: "对齐 P0-3 目标"
    - path: "scripts/run_skill_5layer_audit.py"
      purpose: "加证据链落盘"
  constants:
    job_id: "L3-CLOSING-20260222-001"
    task_scope: "P0-3"

output:
  deliverables:
    - path: "scripts/run_skill_5layer_audit.py"
      type: "修改"
  constraints:
    - "每次运行生成 runs/<run_id>/run_meta.json"
    - "每条结果含 evidence_ref"

deny:
  - "不得伪造 hash"
  - "不得省略 run_id"

gate:
  auto_checks:
    - command: "python scripts/run_skill_5layer_audit.py --domains finance,legal --top-n 3"
      expect: "exit 0"
  manual_checks:
    - "run_meta.json 包含 run_id/evidence_ref/input_hash/result_hash"
