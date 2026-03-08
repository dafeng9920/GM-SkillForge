# Task Skill Spec

```yaml
task_id: "T1"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "实现 SkillForge 侧 n8n 编排入口，并锁死最终裁决权在 SkillForge"
  context_files:
    - path: "skillforge/src/api/l4_api.py"
      purpose: "复用现有 generate/adopt/execute 链路与信封格式"
    - path: "skillforge/src/skills/gates/gate_permit.py"
      purpose: "保持 E001/E003 阻断语义不漂移"
    - path: "skillforge/src/contracts/policy/membership_middleware.py"
      purpose: "接入 execute_via_n8n 门禁"
    - path: "docs/2026-02-20/L4.5 启动清单 v2（2026-02-20）.md"
      purpose: "边界冻结条款对齐"
  constants:
    job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
    skill_id: "l45_n8n_orchestration_boundary"

output:
  deliverables:
    - path: "skillforge/src/api/l4_api.py"
      type: "修改"
      schema_ref: "统一 success/error envelope"
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      type: "新建"
      schema_ref: "run_intent/fetch_pack/query_rag 路由合同"
    - path: "skillforge/src/api/__init__.py"
      type: "修改"
      schema_ref: "路由注册完整"
  constraints:
    - "必须新增 run_intent 入口，且由 SkillForge 内部计算 run_id"
    - "n8n 传入 gate_decision/release_allowed 时必须拒绝或忽略并记证据"
    - "不得改变 E001/E003 语义与错误码映射"
    - "不得移除现有 /api/v1/cognition/generate /work/adopt /work/execute"

deny:
  - "不得新增外部依赖"
  - "不得修改其他任务专属文档文件"
  - "不得绕过 GatePermit 直接放行 execute"

gate:
  auto_checks:
    - command: "pytest -q skillforge/tests/test_gate_permit.py"
      expect: "passed"
    - command: "pytest -q skillforge/tests/test_l4_api_smoke.py"
      expect: "passed"
  manual_checks:
    - "run_intent 输出包含 run_id/gate_decision/evidence_ref/release_allowed"
    - "n8n 越权字段注入场景被阻断（fail-closed）"
```

