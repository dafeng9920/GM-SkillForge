# Task Skill Spec

```yaml
task_id: "T17"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "SEEDS-P0-1 Registry：落盘 registry/skills.jsonl，并接入最小写入点+读取点"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "Registry 规范与DoD"
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      purpose: "导入/执行前读取点参考"
  constants:
    job_id: "L45-D4-SEEDS-P0-20260220-004"
    skill_id: "l45_seeds_p0_foundation"

output:
  deliverables:
    - path: "registry/skills.jsonl"
      type: "新建"
      schema_ref: "append-only registry line"
    - path: "skillforge/src/storage/registry_store.py"
      type: "新建"
      schema_ref: "append + read latest ACTIVE"
    - path: "skillforge/tests/test_registry_store.py"
      type: "新建"
      schema_ref: "append-only/read-latest 测试"
  constraints:
    - "必须 append-only"
    - "必须支持按 skill_id 读取最新 ACTIVE revision"
    - "至少一处写入点与一处读取点可执行"

deny:
  - "不得覆盖历史记录"
  - "不得跳过 ACTIVE 过滤"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_registry_store.py"
      expect: "passed"
```

