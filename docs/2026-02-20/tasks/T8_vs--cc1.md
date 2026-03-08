# Task Skill Spec

```yaml
task_id: "T8"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "生产化 fetch_pack：从 mock 返回升级为真实 AuditPack/证据读取与一致性校验"
  context_files:
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      purpose: "现有 fetch_pack 路由逻辑"
    - path: "skillforge/src/contracts/governance/n8n_execution_receipt.schema.json"
      purpose: "对齐 run_id/evidence_ref/gate_decision 字段"
    - path: "docs/2026-02-20/L45_EVIDENCE_CHAIN_REQUIREMENTS_v1.md"
      purpose: "证据链字段与规则"
  constants:
    job_id: "L45-D2-ORCH-MINCAP-20260220-002"
    skill_id: "l45_orchestration_min_capabilities"

output:
  deliverables:
    - path: "skillforge/src/storage/audit_pack_store.py"
      type: "新建"
      schema_ref: "run_id/evidence_ref 索引读取接口"
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      type: "修改"
      schema_ref: "fetch_pack 真实读取 + 一致性校验"
    - path: "skillforge/tests/test_n8n_fetch_pack_production.py"
      type: "新建"
      schema_ref: "缺标识/不一致/成功读取用例"
    - path: "docs/2026-02-20/L45_FETCH_PACK_PRODUCTION_REPORT_v1.md"
      type: "新建"
      schema_ref: "实现与验证报告"
  constraints:
    - "run_id 与 evidence_ref 任一给定时必须能做一致性校验"
    - "读取失败必须 fail-closed 并返回结构化错误信封"
    - "返回体必须包含 replay_pointer（可空但字段存在）"
    - "不得破坏 T4 定义的 receipt schema 兼容性"

deny:
  - "不得修改与存储读取无关的业务路由"
  - "不得新增非 append-only 的证据写入逻辑"
  - "不得绕过证据字段完整性检查"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_n8n_fetch_pack_production.py"
      expect: "passed"
    - command: "python -m pytest -q skillforge/tests/test_membership_regression.py"
      expect: "passed"
  manual_checks:
    - "fetch_pack 返回可直接被 n8n 工作流消费"
    - "错误分支具备可审计 evidence_ref"
```

