task_id: "T1"
executor: "Antigravity-1"
reviewer: "vs--cc3"
compliance_officer: "Antigravity-2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "将 constitution_risk_gate 接入 publish 前硬拦截，并输出结构化 ruling 证据"
  context_files:
    - path: "skillforge-spec-pack/skillforge/src/orchestration/engine.py"
      purpose: "确保 gate 决策能阻断 pack_audit_and_publish"
    - path: "skillforge-spec-pack/skillforge/src/nodes/constitution_gate.py"
      purpose: "产出裁决与条款引用"
    - path: "scripts/l3_gap_closure/test_constitution_hard_gate.py"
      purpose: "以 killer test A 作为验收"
  constants:
    suite: "L3_gap_closure_killer_tests"

output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/src/orchestration/engine.py"
      type: "修改"
    - path: "skillforge-spec-pack/skillforge/src/nodes/constitution_gate.py"
      type: "修改"
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      type: "修改"
    - path: "docs/2026-02-25/verification/T1_execution_report.yaml"
      type: "新建"
  constraints:
    - "违规请求必须 BLOCK/DENY"
    - "必须阻断 publish_result.status=published"
    - "输出包含 ruling 或 ruling_path"

deny:
  - "不得修改 T2/T3 任务文件"
  - "不得删除现有测试"

gate:
  auto_checks:
    - command: "python scripts/l3_gap_closure/test_constitution_hard_gate.py --report reports/l3_gap_closure/adhoc/T1_report.json"
      expect: "exit_code=0"
  manual_checks:
    - "gate_decisions 非空"

compliance:
  required: true
  attestation_path: "docs/2026-02-25/verification/T1_compliance_attestation.json"
  permit_required_for_side_effects: true