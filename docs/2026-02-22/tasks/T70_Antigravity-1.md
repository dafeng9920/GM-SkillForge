task_id: "T70"
executor: "Antigravity-1"
reviewer: "vs--cc2"
compliance_officer: "Kior-C"
wave: "Wave 3"
depends_on: ["T62"]
estimated_minutes: 60

input:
  description: "落实 guard_signature 校验：创建签名验证脚本，确保所有执行报告和门控决策具备有效签名"
  context_files:
    - path: "docs/2026-02-22/verification/T62_execution_report.yaml"
      purpose: "参考执行报告格式"
    - path: "docs/2026-02-22/verification/T62_gate_decision.json"
      purpose: "参考门控决策格式"
    - path: "docs/2026-02-22/verification/T62_compliance_attestation.json"
      purpose: "参考合规认证格式"
    - path: "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
      purpose: "Guard A 提案规范"
    - path: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
      purpose: "Guard B 执行规范"
  constants:
    job_id: "L4-P2-HARDENING-20260222-001"
    scope: "P2-1"

output:
  deliverables:
    - path: "scripts/verify_guard_signature.py"
      type: "新建"
      description: "Guard 签名校验脚本"
    - path: "docs/2026-02-22/verification/signature_verification_report.json"
      type: "新建"
      description: "签名验证结果报告"
  constraints:
    - "签名算法使用 SHA256 + HMAC"
    - "必须验证所有已存在的 execution_report.yaml 文件"
    - "必须验证所有已存在的 gate_decision.json 文件"
    - "输出报告必须包含通过率和失败详情"

deny:
  - "不得省略签名验证失败的处理逻辑"
  - "不得在签名无效时返回成功状态"

gate:
  auto_checks:
    - command: "python scripts/verify_guard_signature.py --verify-all --report docs/2026-02-22/verification/signature_verification_report.json"
      expect: "exit 0 or exit 1 (with report generated)"
  manual_checks:
    - "验证报告包含所有任务文件的签名状态"
    - "验证脚本包含完整的错误处理"

# A Guard: PreflightChecklist / ExecutionContract / RequiredChanges
preflight_checklist:
  - item: "确认依赖 T62 已完成"
    evidence_ref: "docs/2026-02-22/verification/T62_execution_report.yaml"
  - item: "确认现有报告文件可读"
    evidence_ref: "docs/2026-02-22/verification/*.yaml, *.json"
  - item: "确认签名密钥已配置"
    evidence_ref: "环境变量 GUARD_SIGNATURE_KEY"

execution_contract:
  contract_id: "EC-T70-20260222"
  signer: "Antigravity-1"
  valid_from: "2026-02-22T08:00:00Z"
  valid_until: "2026-02-22T10:00:00Z"
  scope: "guard_signature 校验实现"
  permissions:
    - "READ: docs/2026-02-22/verification/*"
    - "WRITE: scripts/verify_guard_signature.py"
    - "WRITE: docs/2026-02-22/verification/signature_verification_report.json"

required_changes:
  - change_id: "RC-T70-001"
    description: "创建签名校验脚本"
    file: "scripts/verify_guard_signature.py"
    priority: "HIGH"
  - change_id: "RC-T70-002"
    description: "生成签名验证报告"
    file: "docs/2026-02-22/verification/signature_verification_report.json"
    priority: "HIGH"

compliance:
  required: true
  attestation_path: "docs/2026-02-22/verification/T70_compliance_attestation.json"
  permit_required_for_side_effects: false
