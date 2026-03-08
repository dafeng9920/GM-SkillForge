# Task Skill Spec

```yaml
task_id: "T4"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 60

input:
  description: "固化 n8n 编排执行的证据与契约字段，确保审计链可回放"
  context_files:
    - path: "docs/2026-02-19/contracts/external_skill_governance_contract_v1.yaml"
      purpose: "对齐 governance wrapper 约束"
    - path: "skillforge/src/contracts/gates/gate_interface_v1.yaml"
      purpose: "对齐 gate 输出字段"
    - path: "skillforge/src/contracts/governance/work_item_schema.json"
      purpose: "补齐编排执行回执字段"
  constants:
    job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
    skill_id: "l45_n8n_orchestration_boundary"

output:
  deliverables:
    - path: "skillforge/src/contracts/governance/n8n_execution_receipt.schema.json"
      type: "新建"
      schema_ref: "run_id/evidence_ref/gate_decision/replay_pointer"
    - path: "docs/2026-02-20/L45_EVIDENCE_CHAIN_REQUIREMENTS_v1.md"
      type: "新建"
      schema_ref: "证据链字段与最小样例"
    - path: "skillforge/src/contracts/governance/work_item_schema.json"
      type: "修改"
      schema_ref: "引用 execution receipt"
  constraints:
    - "必须要求 run_id、evidence_ref、gate_decision 为必填"
    - "通过分支必须要求 audit_pack_ref"
    - "支持 replay_pointer 可空但结构固定"
    - "不破坏已有 work_item schema 必填字段"

deny:
  - "不得改动 L4 已发布 schema 的字段语义"
  - "不得删除历史兼容字段"
  - "不得修改 API 路由实现代码"

gate:
  auto_checks:
    - command: "python -m json.tool skillforge/src/contracts/governance/n8n_execution_receipt.schema.json > nul"
      expect: "valid json"
  manual_checks:
    - "新 schema 能映射到 L4.5 启动清单的证据边界"
    - "与 T1/T2 输出字段名称一致"
```

