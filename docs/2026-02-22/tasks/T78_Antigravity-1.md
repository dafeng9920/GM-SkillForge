task_id: "T78"
executor: "Antigravity-1"
reviewer: "vs--cc2"
compliance_officer: "Kior-B"
wave: "Wave 3"
depends_on: ["T76"]
estimated_minutes: 45

input:
  description: "Skills 测试覆盖率基线：分析现有 skills 目录，建立测试覆盖率基线，设定最小阈值目标"
  context_files:
    - path: "skills/**"
      purpose: "待分析 skills 目录"
    - path: "skills/ci-skill-validation-skill/SKILL.md"
      purpose: "CI Skill 验证 Skill 规范"
    - path: "docs/2026-02-22/P2_HARDENING_TODO.md"
      purpose: "P2 任务定义"
  constants:
    job_id: "L4-P2-HARDENING-20260222-001"
    scope: "P2-9"

output:
  deliverables:
    - path: "docs/2026-02-22/verification/skills_test_coverage.json"
      type: "新建"
      description: "Skills 测试覆盖率基线报告"
    - path: "docs/2026-02-22/verification/T78_execution_report.yaml"
      type: "新建"
      description: "执行报告"
    - path: "docs/2026-02-22/verification/T78_gate_decision.json"
      type: "新建"
      description: "门禁决策"
    - path: "docs/2026-02-22/verification/T78_compliance_attestation.json"
      type: "新建"
      description: "合规认证"
  constraints:
    - "必须分析所有 skills 子目录"
    - "必须记录每个 skill 的测试状态"
    - "必须设定最小覆盖率阈值"
    - "必须提供改进路线图"

deny:
  - "不得遗漏任何已存在的 skill"
  - "不得在无测试文件时声称覆盖率非零"
  - "不得设定不切实际的阈值"

gate:
  auto_checks:
    - command: "cat docs/2026-02-22/verification/skills_test_coverage.json"
      expect: "JSON valid with skills array and baseline fields"
  manual_checks:
    - "验证覆盖率报告包含所有 skill 目录"
    - "验证最小阈值设定合理"
    - "验证改进路线图可执行"

# A Guard: PreflightChecklist / ExecutionContract / RequiredChanges
preflight_checklist:
  - item: "确认依赖 T76 已完成"
    evidence_ref: "docs/2026-02-22/verification/T76_execution_report.yaml"
  - item: "确认 skills 目录可访问"
    evidence_ref: "skills/*"
  - item: "确认 CI Skill 验证规范已冻结"
    evidence_ref: "skills/ci-skill-validation-skill/SKILL.md"

execution_contract:
  contract_id: "EC-T78-20260222"
  signer: "Antigravity-1"
  valid_from: "2026-02-22T09:00:00Z"
  valid_until: "2026-02-22T10:00:00Z"
  scope: "Skills 测试覆盖率基线建立"
  permissions:
    - "READ: skills/**"
    - "WRITE: docs/2026-02-22/verification/skills_test_coverage.json"
    - "WRITE: docs/2026-02-22/verification/T78_*.yaml"
    - "WRITE: docs/2026-02-22/verification/T78_*.json"

required_changes:
  - change_id: "RC-T78-001"
    description: "分析所有 skills 目录并记录测试状态"
    file: "docs/2026-02-22/verification/skills_test_coverage.json"
    priority: "HIGH"
  - change_id: "RC-T78-002"
    description: "生成执行报告"
    file: "docs/2026-02-22/verification/T78_execution_report.yaml"
    priority: "HIGH"
  - change_id: "RC-T78-003"
    description: "生成门禁决策"
    file: "docs/2026-02-22/verification/T78_gate_decision.json"
    priority: "HIGH"
  - change_id: "RC-T78-004"
    description: "生成合规认证"
    file: "docs/2026-02-22/verification/T78_compliance_attestation.json"
    priority: "HIGH"

compliance:
  required: true
  attestation_path: "docs/2026-02-22/verification/T78_compliance_attestation.json"
  permit_required_for_side_effects: false
