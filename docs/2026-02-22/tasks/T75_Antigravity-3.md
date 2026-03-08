task_id: "T75"
executor: "Antigravity-3"
reviewer: "Kior-A"
compliance_officer: "Kior-B"
wave: "Wave 3"
depends_on: ["T62", "T70"]
estimated_minutes: 45

input:
  description: "RAG 3D 能力探针：输出 RAG 3D 系统的当前状态 + 复现实验步骤"
  context_files:
    - path: "skillforge-spec-pack/skillforge/src/contracts/rag_3d.yaml"
      purpose: "3D RAG Contract 主合同定义"
    - path: "skillforge/src/adapters/rag_adapter.py"
      purpose: "RAG 适配器核心实现"
    - path: "skillforge/src/skills/experience_capture.py"
      purpose: "Experience Capture v0 实现"
    - path: "skillforge/tests/test_n8n_query_rag_production.py"
      purpose: "RAG 生产测试用例"
    - path: "AuditPack/experience/evolution.json"
      purpose: "Evolution 数据存储"
  constants:
    job_id: "L4-P2-HARDENING-20260222-003"
    scope: "P2-3"

output:
  deliverables:
    - path: "docs/2026-02-22/verification/rag3d_probe_report.json"
      type: "新建"
      description: "RAG 3D 能力探针报告"
    - path: "docs/2026-02-22/verification/T75_execution_report.yaml"
      type: "新建"
      description: "T75 执行报告"
    - path: "docs/2026-02-22/verification/T75_gate_decision.json"
      type: "新建"
      description: "T75 门控决策"
    - path: "docs/2026-02-22/verification/T75_compliance_attestation.json"
      type: "新建"
      description: "T75 合规认证"
  constraints:
    - "报告必须包含 RAG 3D 各组件的当前状态"
    - "必须提供可复现的实验步骤"
    - "必须验证 fail-closed 规则的执行状态"

deny:
  - "不得省略任何组件的状态检查"
  - "不得伪造测试结果"

gate:
  auto_checks:
    - command: "python -c 'from adapters.rag_adapter import MockRAGAdapter; a=MockRAGAdapter(); r=a.query(query=\"test\", at_time=\"2026-02-22T10:00:00Z\"); assert r.replay_pointer is not None'"
      expect: "exit 0"
  manual_checks:
    - "验证探针报告覆盖所有 RAG 3D 组件"
    - "验证复现实验步骤可执行"

# A Guard: PreflightChecklist / ExecutionContract / RequiredChanges
preflight_checklist:
  - item: "确认 rag_3d.yaml 存在且可读"
    evidence_ref: "skillforge-spec-pack/skillforge/src/contracts/rag_3d.yaml"
  - item: "确认 rag_adapter.py 存在且可导入"
    evidence_ref: "skillforge/src/adapters/rag_adapter.py"
  - item: "确认 experience_capture.py 存在且可导入"
    evidence_ref: "skillforge/src/skills/experience_capture.py"
  - item: "确认 evolution.json 存在"
    evidence_ref: "AuditPack/experience/evolution.json"

execution_contract:
  contract_id: "EC-T75-20260222"
  signer: "Antigravity-3"
  valid_from: "2026-02-22T15:00:00Z"
  valid_until: "2026-02-22T17:00:00Z"
  scope: "RAG 3D 能力探针"
  permissions:
    - "READ: skillforge-spec-pack/skillforge/src/contracts/*"
    - "READ: skillforge/src/adapters/*"
    - "READ: skillforge/src/skills/*"
    - "READ: skillforge/tests/*"
    - "READ: AuditPack/experience/*"
    - "WRITE: docs/2026-02-22/verification/rag3d_probe_report.json"
    - "WRITE: docs/2026-02-22/verification/T75_*.yaml"
    - "WRITE: docs/2026-02-22/verification/T75_*.json"

required_changes:
  - change_id: "RC-T75-001"
    description: "创建 RAG 3D 能力探针报告"
    file: "docs/2026-02-22/verification/rag3d_probe_report.json"
    priority: "HIGH"
  - change_id: "RC-T75-002"
    description: "生成执行报告和门控决策"
    file: "docs/2026-02-22/verification/T75_*"
    priority: "HIGH"

compliance:
  required: true
  attestation_path: "docs/2026-02-22/verification/T75_compliance_attestation.json"
  permit_required_for_side_effects: false
