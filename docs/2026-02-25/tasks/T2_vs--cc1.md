task_id: "T2"
executor: "vs--cc1"
reviewer: "Kior-A"
compliance_officer: "Kior-B"
wave: "Wave 2"
depends_on: ["T1"]
estimated_minutes: 90

input:
  description: "在发布前引入 registry/graph 完整性校验，篡改时冲突裁决并阻断"
  context_files:
    - path: "skillforge-spec-pack/skillforge/src/storage/repository.py"
      purpose: "append-only 与 hash 校验逻辑"
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      purpose: "发布前冲突拦截"
    - path: "scripts/l3_gap_closure/test_registry_graph_integrity.py"
      purpose: "killer test B 验收"

output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/src/storage/repository.py"
      type: "修改"
    - path: "skillforge-spec-pack/skillforge/src/storage/schema.py"
      type: "修改"
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      type: "修改"
    - path: "docs/2026-02-25/verification/T2_execution_report.yaml"
      type: "新建"
  constraints:
    - "篡改后必须 DENY/REQUIRES_CHANGES"
    - "必须返回 conflict 证据字段"

deny:
  - "不得改 T1/T3 deliverables"

gate:
  auto_checks:
    - command: "python scripts/l3_gap_closure/test_registry_graph_integrity.py --report reports/l3_gap_closure/adhoc/T2_report.json"
      expect: "exit_code=0"

compliance:
  required: true
  attestation_path: "docs/2026-02-25/verification/T2_compliance_attestation.json"
  permit_required_for_side_effects: true