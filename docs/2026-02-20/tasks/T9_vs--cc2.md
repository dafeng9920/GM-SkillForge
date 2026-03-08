# Task Skill Spec

```yaml
task_id: "T9"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "生产化 query_rag：接入可替换 RAG adapter，强制 at_time 查询并输出可回放指针"
  context_files:
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      purpose: "现有 query_rag 路由逻辑"
    - path: "docs/2026-02-20/L45_N8N_BOUNDARY_CONTRACT_v1.md"
      purpose: "输入边界与 fail-closed 要求"
    - path: "docs/2026-02-20/task_dispatch_T7-T11.md"
      purpose: "全局常量与收口要求"
  constants:
    job_id: "L45-D2-ORCH-MINCAP-20260220-002"
    skill_id: "l45_orchestration_min_capabilities"

output:
  deliverables:
    - path: "skillforge/src/adapters/rag_adapter.py"
      type: "新建"
      schema_ref: "统一 RAG adapter 接口"
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      type: "修改"
      schema_ref: "query_rag 调用 adapter + at_time 固定校验"
    - path: "skillforge/tests/test_n8n_query_rag_production.py"
      type: "新建"
      schema_ref: "at_time 缺失/漂移值/成功查询用例"
    - path: "docs/2026-02-20/L45_QUERY_RAG_PRODUCTION_REPORT_v1.md"
      type: "新建"
      schema_ref: "实现与验证报告"
  constraints:
    - "必须拒绝 latest/now/today 等漂移时间表达"
    - "query_rag 响应必须包含 replay_pointer"
    - "支持 repo_url + commit_sha + at_time 组合查询"
    - "adapter 必须可替换（mock 与真实实现可切换）"

deny:
  - "不得将 query_rag 做成直接放行裁决入口"
  - "不得在 adapter 中写入最终 gate_decision"
  - "不得引入外部在线依赖作为必需条件"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_n8n_query_rag_production.py"
      expect: "passed"
    - command: "python -m pytest -q skillforge/tests/test_l4_api_smoke.py"
      expect: "passed"
  manual_checks:
    - "query_rag 输出可被 fetch_pack 证据链引用"
    - "at_time 固定输入策略在报告中有明示证据"
```

