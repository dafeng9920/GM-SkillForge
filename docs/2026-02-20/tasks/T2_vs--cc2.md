# Task Skill Spec

```yaml
task_id: "T2"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 70

input:
  description: "定义并实现 n8n -> SkillForge 编排边界适配层（参数白名单 + 越权字段拦截）"
  context_files:
    - path: "skillforge/src/contracts/api/l4_endpoints.yaml"
      purpose: "继承现有 API 合同风格"
    - path: "skillforge/src/contracts/policy/membership_middleware.py"
      purpose: "执行前 n8n 能力检查"
    - path: "docs/2026-02-20/L4.5 启动清单 v2（2026-02-20）.md"
      purpose: "输入/输出边界条款对齐"
  constants:
    job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
    skill_id: "l45_n8n_orchestration_boundary"

output:
  deliverables:
    - path: "skillforge/src/contracts/api/n8n_boundary_v1.yaml"
      type: "新建"
      schema_ref: "n8n 边界合同"
    - path: "skillforge/src/api/routes/n8n_boundary_adapter.py"
      type: "新建"
      schema_ref: "白名单过滤 + forbidden fields deny"
    - path: "docs/2026-02-20/L45_N8N_BOUNDARY_CONTRACT_v1.md"
      type: "新建"
      schema_ref: "边界说明文档"
  constraints:
    - "n8n 允许输入仅限 repo_url/commit_sha/at_time/requester_id/intent_id/n8n_execution_id"
    - "禁止 n8n 传入 gate_decision/release_allowed/evidence_ref/permit_id"
    - "所有拒绝分支必须返回结构化 error envelope"
    - "保持 at_time 为固定输入，不得自动 latest"

deny:
  - "不得修改 GatePermit 核心签名校验逻辑"
  - "不得改变 membership policy 的 tier 规则"
  - "不得修改与本任务无关测试用例断言"

gate:
  auto_checks:
    - command: "pytest -q skillforge/tests/test_membership_regression.py"
      expect: "passed"
    - command: "pytest -q skillforge/tests/test_membership_policy.py"
      expect: "passed"
  manual_checks:
    - "边界合同文档与 machine contract 字段一致"
    - "forbidden 字段命中时返回 fail-closed"
```

