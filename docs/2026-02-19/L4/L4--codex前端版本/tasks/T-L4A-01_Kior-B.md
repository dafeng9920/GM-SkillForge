# Task Skill Spec: T-L4A-01
# Executor: Kior-B

# 元信息
task_id: "T-L4A-01"
executor: "Kior-B"
wave: "L4-A"
depends_on: []
estimated_minutes: 30

# 输入合同 (Input Contract)
input:
  description: "Define the JSON Schemas and Contracts for L4-A Frontend logic."
  context_files:
    - path: "docs/2026-02-19/L4/L4--codex前端版本/task_dispatch.md"
      purpose: "Context"
  constants:
    schema_version: "v1.0"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge/src/contracts/cognition/10d_schema.json"
      type: "新建"
      description: "Schema for the 10-dimensional cognition output."
    - path: "skillforge/src/contracts/governance/work_item_schema.json"
      type: "新建"
      description: "Schema for the strict Work Item structure (work_item_id, inputs, constraints, etc.)."
    - path: "skillforge/src/contracts/api/l4_endpoints.yaml"
      type: "新建"
      description: "API definition for /cognition/10d and /governance/adopt."

  constraints:
    - "Must include all 7 required fields for Work Item (id, intent, inputs, constraints, acceptance, evidence, adopted_from)."
    - "10D schema must be a container for at least 10 distinct, named dimensions."

# 红线 (Deny List)
deny:
  - "不得复用旧版 contract"
  - "不得允许 undefined 字段"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python -m json.tool skillforge/src/contracts/cognition/10d_schema.json"
      expect: "valid json"
  manual_checks:
    - "Verify Work Item schema enforces 'adopted_from_reason_card_id' requirement."
