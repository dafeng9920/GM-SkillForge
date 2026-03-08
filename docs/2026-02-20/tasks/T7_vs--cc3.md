# Task Skill Spec

```yaml
task_id: "T7"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "生产化 run_intent：将 n8n 入口升级为真实编排执行入口并固化最终裁决归 SkillForge"
  context_files:
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      purpose: "现有 run_intent 路由基础"
    - path: "skillforge/src/api/l4_api.py"
      purpose: "现有 generate/adopt/execute 信封与语义"
    - path: "skillforge/src/skills/gates/gate_permit.py"
      purpose: "E001/E003 阻断语义基线"
    - path: "docs/2026-02-20/task_dispatch_T7-T11.md"
      purpose: "读取全局常量和收口目标"
  constants:
    job_id: "L45-D2-ORCH-MINCAP-20260220-002"
    skill_id: "l45_orchestration_min_capabilities"

output:
  deliverables:
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      type: "修改"
      schema_ref: "run_intent 统一成功/失败信封"
    - path: "skillforge/tests/test_n8n_run_intent_production.py"
      type: "新建"
      schema_ref: "成功 + E001 + E003 + forbidden field 覆盖"
    - path: "docs/2026-02-20/L45_RUN_INTENT_PRODUCTION_REPORT_v1.md"
      type: "新建"
      schema_ref: "实现与验证报告"
  constraints:
    - "run_id 必须由 SkillForge 内部生成，不信任外部 run_id"
    - "不得允许 n8n 注入 gate_decision/release_allowed/evidence_ref/permit_id"
    - "输出必须包含 run_id/gate_decision/evidence_ref/release_allowed"
    - "保持 E001/E003 错误码语义不漂移"

deny:
  - "不得引入新依赖"
  - "不得删除既有 /api/v1/n8n/run_intent 路径"
  - "不得绕过 GatePermit"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_n8n_run_intent_production.py"
      expect: "passed"
    - command: "python -m pytest -q skillforge/tests/test_gate_permit.py"
      expect: "passed"
  manual_checks:
    - "run_intent 成功分支可追溯到 permit 校验结果"
    - "失败分支均 fail-closed，且返回结构化错误信封"
```

