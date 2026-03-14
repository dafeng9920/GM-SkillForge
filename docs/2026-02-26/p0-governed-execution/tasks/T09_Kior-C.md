task_id: "T09"
executor: "Kior-C"
reviewer: "Antigravity-1"
compliance_officer: "Antigravity-2"
wave: "Wave 3"
depends_on: ["T04","T05","T06","T07","T08"]
estimated_minutes: 45

input:
  description: "补齐 T1-T5 协议测试集与错误码断言"
  context_files:
    - path: "docs/2026-02-26/P0-issues/P0-10-issue-任务清单.md"
      purpose: "对齐 issue 目标与 DoD"
    - path: "docs/2026-02-26/p0-governed-execution/task_dispatch.md"
      purpose: "对齐依赖关系与角色分工"
  constants:
    stage: "P0"
    track: "L6-authenticity"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    - "multi-ai-collaboration.md"

output:
  deliverables:
    - path: "docs/2026-02-26/p0-governed-execution/verification/T09_protocol_tests_report.md"
      type: "新建|修改"
      schema_ref: "n/a"
  constraints:
    - "不得越权修改其他任务输出文件"
    - "无 EvidenceRef 不得宣称完成"


deny:
  - "不得绕过 Compliance PASS 直接执行"
  - "不得跳过 depends_on"
  - "不得无证据宣称完成"

gate:
  auto_checks:
    - command: "rg --files docs/2026-02-26/p0-governed-execution"
      expect: "任务文件与验证目录存在"
  manual_checks:
    - "交付物与 issue 目标一致"
    - "三权记录路径完整"

compliance:
  required: true
  attestation_path: "docs/2026-02-26/p0-governed-execution/verification/T09_compliance_attestation.json"
  permit_required_for_side_effects: true
