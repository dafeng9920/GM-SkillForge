task_id: "T3"
executor: "vs--cc2"
reviewer: "Kior-C"
compliance_officer: "Antigravity-2"
wave: "Wave 3"
depends_on: ["T1", "T2"]
estimated_minutes: 90

input:
  description: "强制增量机制：变更请求必须产生版本演化与图谱/发布清单产物"
  context_files:
    - path: "skillforge-spec-pack/skillforge/src/nodes/skill_composer.py"
      purpose: "区分基线与增量变更"
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      purpose: "输出 UpdatedGraph/ReleaseManifest"
    - path: "scripts/l3_gap_closure/test_incremental_delta_enforced.py"
      purpose: "killer test C 验收"

output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/src/nodes/skill_composer.py"
      type: "修改"
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      type: "修改"
    - path: "skillforge-spec-pack/skillforge/src/orchestration/engine.py"
      type: "修改"
    - path: "docs/2026-02-25/verification/T3_execution_report.yaml"
      type: "新建"
  constraints:
    - "增量需求必须新版本或子skill"
    - "输出 UpdatedGraph 字段"
    - "输出 ReleaseManifest 字段（含 rollback）"

deny:
  - "不得删除现有 publish_result 字段"

gate:
  auto_checks:
    - command: "python scripts/l3_gap_closure/test_incremental_delta_enforced.py --report reports/l3_gap_closure/adhoc/T3_report.json"
      expect: "exit_code=0"

compliance:
  required: true
  attestation_path: "docs/2026-02-25/verification/T3_compliance_attestation.json"
  permit_required_for_side_effects: true