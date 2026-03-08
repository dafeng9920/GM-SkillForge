# Task Skill Spec

```yaml
task_id: "T14"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 85

input:
  description: "外部 Skill 的 RAG/证据检索治理接入：固定 at_time，返回可回放 replay_pointer"
  context_files:
    - path: "skillforge/src/adapters/rag_adapter.py"
      purpose: "现有 at_time 校验与 replay_pointer 模式"
    - path: "docs/2026-02-20/L45_QUERY_RAG_PRODUCTION_REPORT_v1.md"
      purpose: "已验证的 drift 阻断策略"
    - path: "docs/2026-02-20/task_dispatch_T12-T16_external_skill_governance.md"
      purpose: "读取全局常量"
  constants:
    job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
    skill_id: "l45_external_skill_governance_batch1"

output:
  deliverables:
    - path: "skillforge/src/adapters/external_skill_rag_adapter.py"
      type: "新建"
      schema_ref: "外部 Skill 检索适配器"
    - path: "skillforge/tests/test_external_skill_rag_adapter.py"
      type: "新建"
      schema_ref: "at_time 固定输入 + drift 阻断测试"
    - path: "docs/2026-02-20/L45_EXTERNAL_SKILL_RAG_REPORT_v1.md"
      type: "新建"
      schema_ref: "检索与回放一致性报告"
  constraints:
    - "at_time 缺失必须 fail-closed"
    - "latest/now/today 等漂移值必须阻断"
    - "返回体必须包含 replay_pointer"
    - "repo_url+commit_sha+at_time 组合必须可复核"

deny:
  - "不得接受相对时间输入"
  - "不得返回无 replay_pointer 的成功响应"
  - "不得隐式降级为当前时间"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_external_skill_rag_adapter.py"
      expect: "passed"
  manual_checks:
    - "确认 at_time 与 replay_pointer.at_time 一致性证据"
    - "确认错误码语义与 T9 一致"
```

